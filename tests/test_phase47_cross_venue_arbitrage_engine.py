from src.errors import RiskLimitError
from src.execution.phase47_cross_venue_arbitrage_engine import Phase47CrossVenueArbitrageEngine, Phase47Config


def test_phase47_arb_constructs_paper_only():
    eng = Phase47CrossVenueArbitrageEngine(seed=47, paper_only=True)
    assert eng.paper_only is True


def test_phase47_arb_live_path_hard_gated():
    try:
        Phase47CrossVenueArbitrageEngine(Phase47Config(seed=47, paper_only=False))
    except (ValueError, RiskLimitError):
        pass
    else:
        raise AssertionError("live path must be hard-gated")


def test_phase47_arb_campaign_gates_ok_and_structure():
    eng = Phase47CrossVenueArbitrageEngine(seed=471, paper_only=True)
    rep = eng.run_campaign(cycles=20)
    assert rep["phase"] == "PHASE47_CROSS_VENUE_ARBITRAGE_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["n_opps"] > 0
    assert rep["n_exploitable"] > 0
    assert rep["n_routes"] > 0
    assert rep["n_tca_reports"] > 0
    assert isinstance(rep["avg_net_edge_bps"], float)
    assert isinstance(rep["avg_toxicity"], float)
    assert isinstance(rep["slo_evaluations"], int)


def test_phase47_arb_toxicity_adjusted_sor_and_tca():
    eng = Phase47CrossVenueArbitrageEngine(seed=472, paper_only=True)
    rep = eng.run_campaign(cycles=15)
    assert rep["n_routes"] == rep["n_opps"]
    assert rep["n_tca_reports"] == rep["n_opps"] * 2  # buy + sell
    # Check routes have toxicity-adjusted priority
    for r in eng.routes[:5]:
        assert "toxicity_adjusted_priority" in r.to_dict()
        assert "order_slicing" in r.to_dict()
        assert r.expected_fill_rate > 0
    # Check TCA has all components
    for t in eng.tca_reports[:4]:
        td = t.to_dict()
        for k in ["realized_slippage_bps", "timing_cost_bps", "fee_bps", "market_impact_bps",
                  "toxicity_cost_bps", "total_cost_bps", "implementation_shortfall_bps"]:
            assert k in td


def test_phase47_arb_determinism():
    e1 = Phase47CrossVenueArbitrageEngine(seed=123, paper_only=True)
    e2 = Phase47CrossVenueArbitrageEngine(seed=123, paper_only=True)
    r1 = e1.run_campaign(cycles=10)
    r2 = e2.run_campaign(cycles=10)
    assert r1["n_opps"] == r2["n_opps"]
    assert r1["n_exploitable"] == r2["n_exploitable"]
    assert abs(r1["avg_net_edge_bps"] - r2["avg_net_edge_bps"]) < 1e-9


def test_phase47_arb_all_artifacts_jsonable():
    eng = Phase47CrossVenueArbitrageEngine(seed=5, paper_only=True)
    rep = eng.run_campaign(cycles=10)
    import json
    json.dumps(rep, allow_nan=False)
    eng.generate_reports(outdir="research_state")
