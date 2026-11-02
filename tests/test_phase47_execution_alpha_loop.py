from src.errors import RiskLimitError
from src.integration.phase47_execution_alpha_loop import Phase47ExecutionAlphaLoop


def test_phase47_loop_constructs_paper_only():
    loop = Phase47ExecutionAlphaLoop(seed=47, cycles=12, paper_only=True, outdir="research_state")
    assert loop.paper_only is True
    assert loop.arb.paper_only is True
    assert loop.mm46.paper_only is True


def test_phase47_loop_live_path_hard_gated():
    try:
        Phase47ExecutionAlphaLoop(seed=47, cycles=12, paper_only=False, outdir="research_state")
    except (ValueError, RiskLimitError):
        pass
    else:
        raise AssertionError("live path must be hard-gated")


def test_phase47_loop_run_gates_ok_and_structure():
    loop = Phase47ExecutionAlphaLoop(seed=471, cycles=14, paper_only=True, outdir="research_state")
    rep = loop.run()
    assert rep["phase"] == "PHASE47_EXECUTION_ALPHA_LOOP"
    assert rep["paper_only"] is True
    assert rep["modes"] == "paper"
    assert rep["gates_ok"] is True
    assert rep["n_arbitrage_opps"] > 0
    assert rep["n_exploitable_arbs"] > 0
    assert rep["n_sor_routes"] > 0
    assert rep["n_tca_reports"] > 0
    assert isinstance(rep["n_mm_quotes"], int)


def test_phase47_loop_composes_phases_28_to_46():
    loop = Phase47ExecutionAlphaLoop(seed=472, cycles=10, paper_only=True, outdir="research_state")
    rep = loop.run()
    iw = rep["integrated_with"]
    assert "PHASE28_CROSS_VENUE_MM" in iw
    assert "PHASE32_EXECUTION_QUALITY" in iw
    assert "PHASE32_ORDERFLOW_ALPHA" in iw
    assert "PHASE39_KILL_SWITCHES" in iw
    assert "PHASE42_RISK_HEDGE" in iw
    assert "PHASE44_LIVE_CAPITAL_DEPLOYMENT" in iw
    assert "PHASE45_RESILIENCE_CHAOS_FAILOVER" in iw
    assert "PHASE46_ADAPTIVE_MM" in iw
    assert "PHASE47_CROSS_VENUE_ARBITRAGE" in iw
    assert "MONITORING_SLO" in iw


def test_phase47_loop_all_artifacts_jsonable():
    loop = Phase47ExecutionAlphaLoop(seed=3, cycles=10, paper_only=True, outdir="research_state")
    rep = loop.run()
    import json
    json.dumps(rep, allow_nan=False)
