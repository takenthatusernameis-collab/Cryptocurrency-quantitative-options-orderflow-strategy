from src.integration.phase62_autonomous_production_deployment_validation_loop import (
    Phase62AutonomousProductionDeploymentValidationLoop,
    Phase62AutonomousProductionDeploymentValidationConfig,
)


def test_phase62_autonomous_production_deployment_validation_basic():
    cfg = Phase62AutonomousProductionDeploymentValidationConfig(seed=62062, cycles=40)
    e = Phase62AutonomousProductionDeploymentValidationLoop(cfg)
    rep = e.run_deployment_validation(cycles=40)
    assert rep["phase"] == "PHASE62_AUTONOMOUS_PRODUCTION_DEPLOYMENT_VALIDATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_canaries"], int)
    assert isinstance(rep["n_rollbacks"], int)
    assert isinstance(rep["canary_pass_rate"], float)


def test_phase62_autonomous_production_deployment_validation_artifacts(tmp_path):
    e = Phase62AutonomousProductionDeploymentValidationLoop(Phase62AutonomousProductionDeploymentValidationConfig(seed=62162, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase62_autonomous_production_deployment_validation_finite_and_paper_only():
    e = Phase62AutonomousProductionDeploymentValidationLoop(Phase62AutonomousProductionDeploymentValidationConfig(seed=62262, cycles=30))
    rep = e.run_deployment_validation(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_deployments"], int)
    assert isinstance(rep["n_circuit_checks"], int)
    assert isinstance(rep["n_attestations"], int)
