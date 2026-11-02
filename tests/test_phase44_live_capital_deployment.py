from src.deployment.phase44_live_capital_deployment import Phase44LiveCapitalDeployment
from src.integration.phase44_live_validation_loop import Phase44LiveValidationLoop


def test_phase44_live_capital_deployment_paper_only():
    dep = Phase44LiveCapitalDeployment(seed=44044, paper_only=True)
    rep = dep.run_campaign(cycles=16, equity_usd=2000000.0)
    assert rep["phase"] == "PHASE44_LIVE_CAPITAL_DEPLOYMENT"
    assert rep["paper_only"] is True
    assert rep["modes"] == "paper"
    assert rep["gates_ok"] is True


def test_phase44_live_capital_deployment_ramp_and_rollbacks():
    dep = Phase44LiveCapitalDeployment(seed=144, paper_only=True)
    rep = dep.run_campaign(cycles=12, equity_usd=1500000.0)
    assert rep["campaign_ok"] is True
    assert rep["n_rollbacks"] == 0
    assert rep["final_stage"] >= 0


def test_phase44_live_validation_loop_integration():
    loop = Phase44LiveValidationLoop(seed=44044, cycles=12, paper_only=True, outdir="research_state")
    rep = loop.run()
    assert rep["phase"] == "PHASE44_LIVE_VALIDATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE39_KILL_SWITCHES" in rep["integrated_with"]
    assert "PHASE43_PNL_RISK" in rep["integrated_with"]
