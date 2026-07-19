"""Pydantic models for the Sponsorship & Ad ROI Dashboard."""
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class PlacementType(str, Enum):
    LED_BOARD = "led_board"
    JUMBOTRON = "jumbotron"
    CONCOURSE_BANNER = "concourse_banner"
    JERSEY_PATCH = "jersey_patch"
    GATE_BRANDING = "gate_branding"
    NAMING_RIGHTS = "naming_rights"


class Placement(BaseModel):
    id: str
    name: str
    type: PlacementType
    zone_id: str
    x: float  # normalized 0-1 position for map rendering
    y: float
    # broadcast_visibility: fraction of live broadcast minutes this placement
    # is estimated to be in-frame (0-1), derived from camera angle analysis
    broadcast_visibility: float = Field(ge=0, le=1)
    monthly_cost: float = Field(gt=0)  # what the sponsor currently pays


class FootfallZone(BaseModel):
    id: str
    name: str
    foot_traffic: int = Field(ge=0)  # people passing per hour
    avg_dwell_seconds: float = Field(ge=0)  # avg time spent looking/lingering


class PlacementSnapshot(BaseModel):
    timestamp: str
    placements: list[Placement]
    zones: list[FootfallZone]


class ValueScore(BaseModel):
    placement_id: str
    placement_name: str
    zone_name: str
    exposure_score: float  # 0-100, composite of footfall x dwell x broadcast
    estimated_monthly_impressions: int
    cost_per_thousand_impressions: float
    verdict: str  # "undervalued" | "fair" | "overpriced"
    rationale: str
    recommended_monthly_value: float
    negotiation_angle: str = "N/A"
    risk_flag: str = "none"
    confidence: int = 50
    source: str = "fallback"  # "anthropic" | "ollama" | "fallback"


class ROIReport(BaseModel):
    id: str
    timestamp: str
    scores: list[ValueScore]
    top_recommendation: str
