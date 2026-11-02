from src.integration.phase60_autonomous_production_rollout_validation_loop import Phase60AutonomousProductionRolloutValidationLoop, Phase60AutonomousProductionRolloutConfig


def test_phase60_autonomous_production_rollout_basic():
    cfg = Phase60AutonomousProductionRolloutConfig(seed=60062, cycles=40)
    e = Phase60AutonomousProductionRolloutValidationLoop(cfg)
    rep = e.run_rollout_validation(cycles=40)
    assert rep["phase"] == "PHASE60_AUTONOMOUS_PRODUCTION_ROLLOUT_VALIDATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["rollout_score"], float)
    assert isinstance(rep["reconciliation_rate"], float)


def test_phase60_autonomous_production_rollout_artifacts(tmp_path):
    e = Phase60AutonomousProductionRolloutValidationLoop(Phase60AutonomousProductionRolloutConfig(seed=60162, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase60_autonomous_production_rollout_finite_and_paper_only():
    e = Phase60AutonomousProductionRolloutValidationLoop(Phase60AutonomousProductionRolloutConfig(seed=60262, cycles=30))
    rep = e.run_rollout_validation(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_failovers"], int)
    assert isinstance(rep["n_drills"], int)
