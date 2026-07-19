"""Sponsorship & Ad ROI Dashboard - FastAPI backend.

Endpoints:
  GET  /api/health      liveness check
  GET  /api/snapshot     current footfall + placement snapshot
  GET  /api/roi-report   AI-generated sponsorship value analysis

Security: all /api/* routes require an X-API-Key header, plus a simple
in-memory sliding-window rate limiter per key.
"""
from __future__ import annotations
import os
import time
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.ai_roi import generate_roi_report
from app.models import PlacementSnapshot, ROIReport
from app.simulator import simulator

app = FastAPI(title="Sponsorship & Ad ROI Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

DEMO_API_KEY = os.environ.get("ROI_API_KEY", "demo-key-change-me")
RATE_LIMIT_MAX_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60
_request_log: dict[str, deque[float]] = defaultdict(deque)


def check_rate_limit(api_key: str) -> None:
    now = time.monotonic()
    log = _request_log[api_key]
    while log and now - log[0] > RATE_LIMIT_WINDOW_SECONDS:
        log.popleft()
    if len(log) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again shortly.")
    log.append(now)


def require_api_key(x_api_key: str = Header(default="")) -> str:
    if x_api_key != DEMO_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    check_rate_limit(x_api_key)
    return x_api_key


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/snapshot", response_model=PlacementSnapshot)
def get_snapshot(_: str = Depends(require_api_key)) -> PlacementSnapshot:
    return simulator.tick()


@app.get("/api/roi-report", response_model=ROIReport)
def get_roi_report(_: str = Depends(require_api_key)) -> ROIReport:
    snapshot = simulator.tick()
    return generate_roi_report(snapshot)
