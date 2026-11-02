from src.integration.phase61_autonomous_production_resilience_drills_loop import (
    Phase61AutonomousProductionResilienceDrillsLoop,
    Phase61AutonomousProductionResilienceConfig,
)


def test_phase61_autonomous_production_resilience_drills_basic():
    cfg = Phase61AutonomousProductionResilienceConfig(seed=61062, cycles=40)
    d = Phase61AutonomousProductionResilienceDrillsLoop(cfg)
    rep = d.run_drills(cycles=40)
    assert rep["phase"] == "PHASE61_AUTONOMOUS_PRODUCTION_RESILIENCE_DRILLS_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_failovers"], int)
    assert isinstance(rep["n_drills"], int)
    assert isinstance(rep["n_chaos_events"], int)


def test_phase61_autonomous_production_resilience_drills_artifacts(tmp_path):
    d = Phase61AutonomousProductionResilienceDrillsLoop(Phase61AutonomousProductionResilienceConfig(seed=61162, cycles=20))
    rep = d.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase61_autonomous_production_resilience_drills_finite_and_paper_only():
    d = Phase61AutonomousProductionResilienceDrillsLoop(Phase61AutonomousProductionResilienceConfig(seed=61262, cycles=30))
    rep = d.run_drills(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_reconciliations"], int)
    assert isinstance(rep["n_containments"], int)
    assert isinstance(rep["n_rollbacks"], int)
    assert isinstance(rep["n_cb_drills"], int)
