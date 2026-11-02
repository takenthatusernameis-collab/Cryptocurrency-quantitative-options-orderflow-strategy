from src.execution.phase50_cross_venue_relative_value_executor import Phase50CrossVenueRelativeValueExecutor, Phase50RVConfig


def test_p50_cross_venue_rv_paper_only_and_structure():
    eng = Phase50CrossVenueRelativeValueExecutor(Phase50RVConfig(seed=50051, paper_only=True))
    rep = eng.run_campaign(cycles=40)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts("research_state")
    assert arts["json"].endswith(".json")
    assert arts["report"]["phase"] == "PHASE50_CROSS_VENUE_RELATIVE_VALUE_EXECUTOR"


def test_p50_cross_venue_rv_opps_deterministic():
    eng = Phase50CrossVenueRelativeValueExecutor(Phase50RVConfig(seed=123, paper_only=True))
    opps = eng.detect_rv_opps(cycles=40)
    assert isinstance(opps, list)
    for o in opps:
        assert o["paper_only"] is True
        assert o["net_edge_bps"] >= 0
        assert o["slices"] >= 1
