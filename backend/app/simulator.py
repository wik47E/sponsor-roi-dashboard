"""Simulates live footfall and sponsor placement data.

In production this would ingest real camera-based foot-traffic counters and
broadcast-feed analysis (e.g. computer vision on live camera minutes to
detect in-frame branding). For the demo we generate realistic, gradually
shifting numbers.
"""
from __future__ import annotations
import random
from datetime import datetime, timezone
from app.models import FootfallZone, Placement, PlacementSnapshot, PlacementType

_ZONE_SEED = [
    {"id": "z-main-concourse", "name": "Main Concourse", "base_traffic": 4200, "base_dwell": 25},
    {"id": "z-gate-entry", "name": "Gate Entry Plaza", "base_traffic": 3100, "base_dwell": 12},
    {"id": "z-pitch-side", "name": "Pitch-side Perimeter", "base_traffic": 900, "base_dwell": 180},
    {"id": "z-upper-tier", "name": "Upper Tier Concourse", "base_traffic": 1800, "base_dwell": 20},
    {"id": "z-fan-zone", "name": "Fan Zone Plaza", "base_traffic": 2600, "base_dwell": 40},
]

_PLACEMENT_SEED = [
    {"id": "p-led-1", "name": "Pitch-side LED Ring", "type": PlacementType.LED_BOARD, "zone_id": "z-pitch-side", "x": 0.5, "y": 0.55, "base_visibility": 0.62, "monthly_cost": 45000},
    {"id": "p-jumbo-1", "name": "North Jumbotron", "type": PlacementType.JUMBOTRON, "zone_id": "z-pitch-side", "x": 0.5, "y": 0.1, "base_visibility": 0.35, "monthly_cost": 60000},
    {"id": "p-banner-1", "name": "Main Concourse Banner", "type": PlacementType.CONCOURSE_BANNER, "zone_id": "z-main-concourse", "x": 0.3, "y": 0.4, "base_visibility": 0.04, "monthly_cost": 8000},
    {"id": "p-gate-1", "name": "Gate Entry Arch", "type": PlacementType.GATE_BRANDING, "zone_id": "z-gate-entry", "x": 0.1, "y": 0.5, "base_visibility": 0.08, "monthly_cost": 12000},
    {"id": "p-fanzone-1", "name": "Fan Zone Stage Backdrop", "type": PlacementType.CONCOURSE_BANNER, "zone_id": "z-fan-zone", "x": 0.75, "y": 0.7, "base_visibility": 0.18, "monthly_cost": 15000},
    {"id": "p-jersey-1", "name": "Home Kit Sleeve Patch", "type": PlacementType.JERSEY_PATCH, "zone_id": "z-pitch-side", "x": 0.5, "y": 0.5, "base_visibility": 0.71, "monthly_cost": 90000},
    {"id": "p-upper-1", "name": "Upper Tier Ring Board", "type": PlacementType.LED_BOARD, "zone_id": "z-upper-tier", "x": 0.6, "y": 0.25, "base_visibility": 0.15, "monthly_cost": 20000},
]


class PlacementSimulator:
    """Keeps in-memory footfall/visibility state and evolves it each tick."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._traffic = {z["id"]: z["base_traffic"] for z in _ZONE_SEED}
        self._visibility = {p["id"]: p["base_visibility"] for p in _PLACEMENT_SEED}

    def tick(self) -> PlacementSnapshot:
        zones: list[FootfallZone] = []
        for spec in _ZONE_SEED:
            zid = spec["id"]
            current = self._traffic[zid]
            drift = self._rng.randint(int(-spec["base_traffic"] * 0.05), int(spec["base_traffic"] * 0.07))
            current = max(0, current + drift)
            self._traffic[zid] = current
            dwell = max(1.0, spec["base_dwell"] + self._rng.uniform(-3, 3))
            zones.append(FootfallZone(id=zid, name=spec["name"], foot_traffic=current, avg_dwell_seconds=dwell))

        placements: list[Placement] = []
        for spec in _PLACEMENT_SEED:
            pid = spec["id"]
            vis = self._visibility[pid]
            vis = min(1.0, max(0.0, vis + self._rng.uniform(-0.03, 0.03)))
            self._visibility[pid] = vis
            placements.append(
                Placement(
                    id=pid,
                    name=spec["name"],
                    type=spec["type"],
                    zone_id=spec["zone_id"],
                    x=spec["x"],
                    y=spec["y"],
                    broadcast_visibility=round(vis, 3),
                    monthly_cost=spec["monthly_cost"],
                )
            )

        return PlacementSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            placements=placements,
            zones=zones,
        )


simulator = PlacementSimulator()
