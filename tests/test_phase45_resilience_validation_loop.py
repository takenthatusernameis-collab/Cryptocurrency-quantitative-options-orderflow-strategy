from src.errors import RiskLimitError
from src.integration.phase45_resilience_validation_loop import Phase45ResilienceValidationLoop


def test_phase45_loop_constructs_paper_only():
    loop = Phase45ResilienceValidationLoop(seed=45, cycles=12, paper_only=True, outdir="research_state")
    assert loop.paper_only is True
    assert loop.chaos.paper_only is True
    assert loop.deployment.paper_only is True


def test_phase45_loop_live_path_hard_gated():
    try:
        Phase45ResilienceValidationLoop(seed=45, cycles=12, paper_only=False, outdir="research_state")
    except (ValueError, RiskLimitError):
        pass
    else:
        raise AssertionError("live path must be hard-gated")


def test_phase45_loop_run_gates_ok_and_structure():
    loop = Phase45ResilienceValidationLoop(seed=47, cycles=14, paper_only=True, outdir="research_state")
    rep = loop.run()
    assert rep["phase"] == "PHASE45_RESILIENCE_VALIDATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["modes"] == "paper"
    assert rep["gates_ok"] is True
    assert rep["chaos_campaign"]["gates_ok"] is True
    assert rep["deployment_campaign"]["gates_ok"] is True
    assert rep["settlement_campaign"]["gates_ok"] is True
    assert rep["n_failovers"] >= 0
    assert isinstance(rep["rollback_executed"], bool)
    assert isinstance(rep["n_slo_burn_alerts"], int)
    assert isinstance(rep["n_slo_burn_alerts_fired"], int)


def test_phase45_loop_composes_phases_39_44():
    loop = Phase45ResilienceValidationLoop(seed=51, cycles=10, paper_only=True, outdir="research_state")
    rep = loop.run()
    iw = rep["integrated_with"]
    assert "PHASE39_KILL_SWITCHES" in iw
    assert "PHASE40_RECONCILIATION" in iw
    assert "PHASE41_SETTLEMENT" in iw
    assert "PHASE42_RISK_HEDGE" in iw
    assert "PHASE43_PNL_RISK" in iw
    assert "PHASE44_LIVE_CAPITAL_DEPLOYMENT" in iw
    assert "PHASE45_CHAOS_FAILOVER" in iw
    assert isinstance(rep["phase40_reconciled_all"], int) and rep["phase40_reconciled_all"] >= 0


def test_phase45_loop_all_artifacts_jsonable():
    loop = Phase45ResilienceValidationLoop(seed=3, cycles=10, paper_only=True, outdir="research_state")
    rep = loop.run()
    import json
    json.dumps(rep, allow_nan=False)
