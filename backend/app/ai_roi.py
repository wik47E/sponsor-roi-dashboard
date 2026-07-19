"""Analyzes footfall + broadcast visibility data to score sponsor placement
value and recommend pricing, using an LLM. This is the core Gen AI component
of the project.

Supports two providers, selected via the AI_PROVIDER env var:
  - "anthropic" (default if ANTHROPIC_API_KEY is set): uses the Claude API
  - "ollama": uses a local Ollama model (free, no API key, runs on your
    machine) -- set AI_PROVIDER=ollama and optionally OLLAMA_MODEL /
    OLLAMA_BASE_URL

A deterministic fallback computes the same exposure metrics without any LLM
call, so the dashboard still functions with no AI provider configured at
all -- the model is used specifically for the judgment call (verdict +
rationale + recommended price), not for arithmetic that doesn't need one.
"""
from __future__ import annotations
import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone

import anthropic
import requests
from app.models import Placement, PlacementSnapshot, ROIReport, ValueScore

_CLIENT: anthropic.Anthropic | None = None
_MODEL = "claude-sonnet-4-6"

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

_BROADCAST_MINUTES_PER_MONTH = 6 * 90
_BROADCAST_AUDIENCE = 850_000
_EVENT_HOURS_PER_MONTH = 6 * 3


def _active_provider() -> str:
    explicit = os.environ.get("AI_PROVIDER", "").strip().lower()
    if explicit in ("anthropic", "ollama", "none"):
        return explicit
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "ollama"


def _client() -> anthropic.Anthropic | None:
    global _CLIENT
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    if _CLIENT is None:
        _CLIENT = anthropic.Anthropic(api_key=api_key)
    return _CLIENT


def _parse_judgments(text: str) -> dict[str, dict]:
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = json.loads(text)

    if isinstance(parsed, dict) and "placement_id" in parsed:
        parsed = [parsed]
    elif isinstance(parsed, dict):
        for value in parsed.values():
            if isinstance(value, list):
                parsed = value
                break

    result: dict[str, dict] = {}
    for item in parsed:
        if isinstance(item, dict) and "placement_id" in item:
            result[item["placement_id"]] = item
    return result


_SYSTEM_PROMPT = """You are a sponsorship analytics consultant for a stadium \
operations team. Given computed exposure metrics for each sponsor placement \
(estimated monthly impressions and cost-per-thousand-impressions), your job \
is to produce the judgment layer: classify each placement's pricing and \
write a sharp, specific one-sentence rationale a sales team could use in a \
renewal conversation.

Rules:
- verdict must be one of: "undervalued", "fair", "overpriced"
- rationale: one sentence, under 30 words, specific to the numbers given, no \
generic filler
- recommended_monthly_value: a concrete dollar figure (number, not a range)
- Output MUST be a JSON array where EVERY element is an OBJECT (not a plain \
string) with exactly these four keys: placement_id, verdict, rationale, \
recommended_monthly_value.
- Return ONLY the JSON array. No prose, no markdown fences, no explanation \
before or after it.

Example of the exact shape required:
[{"placement_id": "p-example", "verdict": "fair", "rationale": "CPM aligns with comparable pitch-side inventory.", "recommended_monthly_value": 42000}]
"""


def _call_claude(base_metrics: list[dict]) -> dict[str, dict]:
    client = _client()
    if client is None:
        raise RuntimeError("ANTHROPIC_API_KEY not configured")
    response = client.messages.create(
        model=_MODEL,
        max_tokens=1500,
        system=_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Placement metrics:\n{json.dumps(base_metrics)}"}
        ],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return _parse_judgments(text)


_SINGLE_SYSTEM_PROMPT = """You are a sponsorship analytics consultant for a stadium \
operations team. Given computed exposure metrics for ONE sponsor placement, \
classify its pricing and produce actionable output a sales team could use \
directly in a renewal conversation.

Rules:
- verdict must be exactly one of: "undervalued", "fair", "overpriced"
- rationale: one sentence, under 30 words, specific to the numbers given, no \
generic filler
- negotiation_angle: one sentence, a concrete talking point or lever for the \
renewal conversation (e.g. what to offer, what to push back on, what \
comparison to cite) -- must reference the actual numbers, not be generic
- risk_flag: one of "none", "sponsor_may_churn", "underpriced_leaving_money", \
"reposition_recommended" -- pick based on the verdict and the numbers given
- confidence: an integer 0-100 reflecting how clear-cut this call is given \
the data provided
- recommended_monthly_value: a concrete dollar figure (number, not a range)
- Return ONLY a single JSON object with exactly these seven keys: \
placement_id, verdict, rationale, negotiation_angle, risk_flag, confidence, \
recommended_monthly_value. No prose, no markdown fences, nothing else.

Example: {"placement_id": "p-example", "verdict": "fair", "rationale": "CPM aligns with comparable pitch-side inventory.", "negotiation_angle": "Offer a 6-month lock-in at current rate to secure renewal before Q3 rate review.", "risk_flag": "none", "confidence": 82, "recommended_monthly_value": 42000}
"""


def _call_ollama_single(metric: dict) -> dict:
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": _SINGLE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Placement metrics:\n{json.dumps(metric)}"},
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0, "num_predict": 400},
        },
        timeout=60,
    )
    resp.raise_for_status()
    text = resp.json()["message"]["content"]
    judgments = _parse_judgments(text)
    if not judgments:
        raise ValueError(f"No usable judgment. Raw: {text[:300]}")
    return next(iter(judgments.values()))


def _call_ollama(base_metrics: list[dict]) -> dict[str, dict]:
    """Calls Ollama once per placement rather than once for the whole batch.

    Small local models are unreliable at producing a long, correctly-shaped
    JSON array in one shot -- they tend to truncate or drop items. One
    focused call per placement is slower but far more consistent.
    """
    judgments: dict[str, dict] = {}
    for metric in base_metrics:
        try:
            judgments[metric["placement_id"]] = _call_ollama_single(metric)
        except Exception as e:
            print(f"[DEBUG] Ollama failed for {metric['placement_id']}: {e}")
            continue
    if not judgments:
        raise ValueError("Ollama returned no usable judgments for any placement.")
    return judgments


def _zone_lookup(snapshot: PlacementSnapshot) -> dict[str, str]:
    return {z.id: z.name for z in snapshot.zones}


def _zone_traffic(snapshot: PlacementSnapshot) -> dict[str, tuple[int, float]]:
    return {z.id: (z.foot_traffic, z.avg_dwell_seconds) for z in snapshot.zones}


def _estimate_impressions(placement: Placement, traffic: int, dwell: float) -> int:
    in_person = traffic * _EVENT_HOURS_PER_MONTH * min(1.0, dwell / 15)
    broadcast = placement.broadcast_visibility * _BROADCAST_AUDIENCE * (
        _BROADCAST_MINUTES_PER_MONTH / 90
    )
    return int(in_person + broadcast)


def _fallback_verdict(cpm: float) -> tuple[str, str]:
    if cpm < 2.0:
        return "undervalued", "CPM is well below typical stadium sponsorship benchmarks; price has room to increase."
    if cpm > 8.0:
        return "overpriced", "CPM is high relative to estimated reach; renegotiate or reposition."
    return "fair", "CPM sits within a reasonable range for this exposure level."


def _fallback_report(snapshot: PlacementSnapshot) -> ROIReport:
    zones = _zone_lookup(snapshot)
    traffic = _zone_traffic(snapshot)
    scores: list[ValueScore] = []

    for p in snapshot.placements:
        t, d = traffic.get(p.zone_id, (0, 0.0))
        impressions = _estimate_impressions(p, t, d)
        cpm = (p.monthly_cost / impressions) * 1000 if impressions else 0.0
        exposure = min(100.0, (impressions / 5_000_000) * 100)
        verdict, rationale = _fallback_verdict(cpm)
        recommended = round(
            p.monthly_cost * (1.25 if verdict == "undervalued" else 0.8 if verdict == "overpriced" else 1.0),
            -2,
        )

        scores.append(
            ValueScore(
                placement_id=p.id,
                placement_name=p.name,
                zone_name=zones.get(p.zone_id, p.zone_id),
                exposure_score=round(exposure, 1),
                estimated_monthly_impressions=impressions,
                cost_per_thousand_impressions=round(cpm, 2),
                verdict=verdict,
                rationale=rationale,
                recommended_monthly_value=recommended,
                negotiation_angle="N/A",
                risk_flag="none",
                confidence=50,
                source="fallback",
            )
        )

    scores.sort(key=lambda s: s.exposure_score, reverse=True)
    top = scores[0].placement_name if scores else "N/A"

    return ROIReport(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        scores=scores,
        top_recommendation=f"{top} delivers the highest exposure score this cycle." if scores else "No data.",
    )


_report_cache: ROIReport | None = None
_report_cache_time: float = 0.0
_report_lock = threading.Lock()
_CACHE_TTL_SECONDS = 25


def generate_roi_report(snapshot: PlacementSnapshot) -> ROIReport:
    global _report_cache, _report_cache_time

    now = time.monotonic()
    if _report_cache is not None and (now - _report_cache_time) < _CACHE_TTL_SECONDS:
        return _report_cache

    if not _report_lock.acquire(blocking=False):
        if _report_cache is not None:
            return _report_cache
        return _fallback_report(snapshot)

    try:
        report = _generate_roi_report_uncached(snapshot)
        _report_cache = report
        _report_cache_time = time.monotonic()
        return report
    finally:
        _report_lock.release()


def _generate_roi_report_uncached(snapshot: PlacementSnapshot) -> ROIReport:
    zones = _zone_lookup(snapshot)
    traffic = _zone_traffic(snapshot)

    base_metrics = []
    for p in snapshot.placements:
        t, d = traffic.get(p.zone_id, (0, 0.0))
        impressions = _estimate_impressions(p, t, d)
        cpm = (p.monthly_cost / impressions) * 1000 if impressions else 0.0
        exposure = min(100.0, (impressions / 5_000_000) * 100)
        base_metrics.append(
            {
                "placement_id": p.id,
                "placement_name": p.name,
                "zone_name": zones.get(p.zone_id, p.zone_id),
                "monthly_cost": p.monthly_cost,
                "estimated_monthly_impressions": impressions,
                "cost_per_thousand_impressions": round(cpm, 2),
                "exposure_score": round(exposure, 1),
            }
        )

    provider = _active_provider()
    judgments: dict[str, dict] = {}

    if provider == "anthropic":
        try:
            judgments = _call_claude(base_metrics)
        except Exception as e:
            print(f"[DEBUG] Claude call failed: {type(e).__name__}: {e}")
            return _fallback_report(snapshot)
    elif provider == "ollama":
        try:
            judgments = _call_ollama(base_metrics)
        except Exception as e:
            print(f"[DEBUG] Ollama call failed: {type(e).__name__}: {e}")
            return _fallback_report(snapshot)
    else:
        return _fallback_report(snapshot)

    scores: list[ValueScore] = []
    for m in base_metrics:
        j = judgments.get(m["placement_id"], {})
        had_ai_judgment = m["placement_id"] in judgments
        scores.append(
            ValueScore(
                placement_id=m["placement_id"],
                placement_name=m["placement_name"],
                zone_name=m["zone_name"],
                exposure_score=m["exposure_score"],
                estimated_monthly_impressions=m["estimated_monthly_impressions"],
                cost_per_thousand_impressions=m["cost_per_thousand_impressions"],
                verdict=j.get("verdict", "fair"),
                rationale=j.get("rationale", "No AI rationale available."),
                recommended_monthly_value=j.get("recommended_monthly_value", m["monthly_cost"]),
                negotiation_angle=j.get("negotiation_angle", "N/A"),
                risk_flag=j.get("risk_flag", "none"),
                confidence=j.get("confidence", 50),
                source=provider if had_ai_judgment else "fallback",
            )
        )

    scores.sort(key=lambda s: s.exposure_score, reverse=True)
    top = scores[0].placement_name if scores else "N/A"

    return ROIReport(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        scores=scores,
        top_recommendation=f"{top} delivers the highest exposure score this cycle." if scores else "No data.",
    )
