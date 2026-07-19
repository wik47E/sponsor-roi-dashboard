from app.simulator import PlacementSimulator


def test_tick_returns_all_placements_and_zones():
    sim = PlacementSimulator(seed=42)
    snapshot = sim.tick()
    assert len(snapshot.placements) == 7
    assert len(snapshot.zones) == 5


def test_visibility_stays_within_bounds():
    sim = PlacementSimulator(seed=1)
    for _ in range(20):
        snapshot = sim.tick()
        for p in snapshot.placements:
            assert 0.0 <= p.broadcast_visibility <= 1.0


def test_foot_traffic_non_negative():
    sim = PlacementSimulator(seed=3)
    for _ in range(20):
        snapshot = sim.tick()
        for z in snapshot.zones:
            assert z.foot_traffic >= 0


def test_deterministic_with_seed():
    sim_a = PlacementSimulator(seed=99)
    sim_b = PlacementSimulator(seed=99)
    snap_a = sim_a.tick()
    snap_b = sim_b.tick()
    assert [p.broadcast_visibility for p in snap_a.placements] == [
        p.broadcast_visibility for p in snap_b.placements
    ]
