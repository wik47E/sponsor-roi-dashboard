from app.ai_roi import _fallback_report, _estimate_impressions, _fallback_verdict
from app.models import Placement, PlacementType, FootfallZone, PlacementSnapshot


def make_snapshot():
    zones = [FootfallZone(id="z1", name="Zone 1", foot_traffic=3000, avg_dwell_seconds=20)]
    placements = [
        Placement(
            id="p1", name="Test Board", type=PlacementType.LED_BOARD, zone_id="z1",
            x=0.5, y=0.5, broadcast_visibility=0.5, monthly_cost=10000,
        )
    ]
    return PlacementSnapshot(timestamp="2026-01-01T00:00:00Z", placements=placements, zones=zones)


def test_estimate_impressions_positive():
    snapshot = make_snapshot()
    p = snapshot.placements[0]
    impressions = _estimate_impressions(p, 3000, 20)
    assert impressions > 0


def test_fallback_verdict_thresholds():
    assert _fallback_verdict(1.0)[0] == "undervalued"
    assert _fallback_verdict(5.0)[0] == "fair"
    assert _fallback_verdict(10.0)[0] == "overpriced"


def test_fallback_report_produces_scores_for_all_placements():
    snapshot = make_snapshot()
    report = _fallback_report(snapshot)
    assert len(report.scores) == len(snapshot.placements)
    assert report.scores[0].verdict in ("undervalued", "fair", "overpriced")


def test_fallback_report_sorted_by_exposure_descending():
    zones = [
        FootfallZone(id="z1", name="Z1", foot_traffic=5000, avg_dwell_seconds=30),
        FootfallZone(id="z2", name="Z2", foot_traffic=100, avg_dwell_seconds=5),
    ]
    placements = [
        Placement(id="low", name="Low", type=PlacementType.CONCOURSE_BANNER, zone_id="z2", x=0, y=0, broadcast_visibility=0.01, monthly_cost=1000),
        Placement(id="high", name="High", type=PlacementType.JERSEY_PATCH, zone_id="z1", x=0, y=0, broadcast_visibility=0.9, monthly_cost=50000),
    ]
    snapshot = PlacementSnapshot(timestamp="2026-01-01T00:00:00Z", placements=placements, zones=zones)
    report = _fallback_report(snapshot)
    assert report.scores[0].placement_id == "high"
