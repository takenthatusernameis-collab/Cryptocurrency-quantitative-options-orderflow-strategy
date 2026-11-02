from src.errors import RiskLimitError
from src.integration.phase46_execution_intelligence_loop import Phase46ExecutionIntelligenceLoop


def test_phase46_loop_constructs_paper_only():
    loop = Phase46ExecutionIntelligenceLoop(seed=46, cycles=12, paper_only=True, outdir="research_state")
    assert loop.paper_only is True
    assert loop.mm.paper_only is True
    assert loop.deployment.paper_only is True
    assert loop.risk_hedge.cfg.paper_only is True
    assert loop.resilience.paper_only is True


def test_phase46_loop_live_path_hard_gated():
    try:
        Phase46ExecutionIntelligenceLoop(seed=46, cycles=12, paper_only=False, outdir="research_state")
    except (ValueError, RiskLimitError):
        pass
    else:
        raise AssertionError("live path must be hard-gated")


def test_phase46_loop_run_gates_ok_and_structure():
    loop = Phase46ExecutionIntelligenceLoop(seed=47, cycles=14, paper_only=True, outdir="research_state")
    rep = loop.run()
    assert rep["phase"] == "PHASE46_EXECUTION_INTELLIGENCE_LOOP"
    assert rep["paper_only"] is True
    assert rep["modes"] == "paper"
    assert rep["gates_ok"] is True
    assert rep["mm_campaign"]["gates_ok"] is True
    assert rep["orderflow_alpha_campaign"]["paper_only"] is True
    assert rep["risk_hedge_campaign"]["gates_ok"] is True
    assert rep["resilience_campaign"]["gates_ok"] is True
    assert rep["phase39_kill_switches"]["paper_only"] is True
    assert isinstance(rep["n_mm_quotes"], int) and rep["n_mm_quotes"] > 0
    assert isinstance(rep["n_dislocations"], int)
    assert isinstance(rep["n_exploitable_dislocations"], int)
    assert isinstance(rep["halt_executed"], bool)
    assert isinstance(rep["halt_events"], list)
    assert isinstance(rep["slo_evaluations"], int)


def test_phase46_loop_composes_phases_28_to_45():
    loop = Phase46ExecutionIntelligenceLoop(seed=51, cycles=10, paper_only=True, outdir="research_state")
    rep = loop.run()
    iw = rep["integrated_with"]
    assert "PHASE28_CROSS_VENUE_MM" in iw
    assert "PHASE32_ORDERFLOW_ALPHA" in iw
    assert "PHASE39_KILL_SWITCHES" in iw
    assert "PHASE42_RISK_HEDGE" in iw
    assert "PHASE44_LIVE_CAPITAL_DEPLOYMENT" in iw
    assert "PHASE45_RESILIENCE_CHAOS_FAILOVER" in iw
    assert "PHASE46_ADAPTIVE_MM" in iw
    assert "MONITORING_SLO" in iw


def test_phase46_loop_all_artifacts_jsonable():
    loop = Phase46ExecutionIntelligenceLoop(seed=3, cycles=10, paper_only=True, outdir="research_state")
    rep = loop.run()
    import json
    json.dumps(rep, allow_nan=False)
