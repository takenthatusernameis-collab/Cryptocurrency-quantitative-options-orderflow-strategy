"""Phase 63 tests: Adaptive Toxicity-Resilient Deployment Orchestrator."""
from src.hedging.phase63_adaptive_toxicity_resilient_deployment_orchestrator import (
    Phase63AdaptiveToxicityResilientDeploymentOrchestrator,
    Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig,
)


def test_phase63_adaptive_toxicity_resilient_deployment_orchestrator_basic():
    cfg = Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig(seed=63061, cycles=40)
    e = Phase63AdaptiveToxicityResilientDeploymentOrchestrator(cfg)
    rep = e.orchestrate_deployment(cycles=40)
    assert rep["phase"] == "PHASE63_ADAPTIVE_TOXICITY_RESILIENT_DEPLOYMENT_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_rollout_gates"], int)
    assert isinstance(rep["n_failovers"], int)


def test_phase63_adaptive_toxicity_resilient_deployment_orchestrator_artifacts(tmp_path):
    e = Phase63AdaptiveToxicityResilientDeploymentOrchestrator(Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig(seed=63161, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase63_adaptive_toxicity_resilient_deployment_orchestrator_finite_and_paper_only():
    e = Phase63AdaptiveToxicityResilientDeploymentOrchestrator(Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig(seed=63261, cycles=30))
    rep = e.orchestrate_deployment(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["gate_open_rate"], float)
