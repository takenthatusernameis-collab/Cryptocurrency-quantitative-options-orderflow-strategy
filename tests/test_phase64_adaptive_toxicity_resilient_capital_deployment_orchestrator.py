"""Phase 64 tests: Adaptive Toxicity-Resilient Capital Deployment Orchestrator."""
from src.hedging.phase64_adaptive_toxicity_resilient_capital_deployment_orchestrator import (
    Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator,
    Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestratorConfig,
)


def test_phase64_adaptive_toxicity_resilient_capital_deployment_basic():
    cfg = Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestratorConfig(seed=64061, cycles=40)
    o = Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator(cfg)
    rep = o.orchestrate_capital_deployment(cycles=40)
    assert rep["phase"] == "PHASE64_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_DEPLOYMENT_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_capital_deployments"], int)
    assert isinstance(rep["n_failovers"], int)


def test_phase64_adaptive_toxicity_resilient_capital_deployment_artifacts(tmp_path):
    o = Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator(
        Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestratorConfig(seed=64161, cycles=20)
    )
    rep = o.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase64_adaptive_toxicity_resilient_capital_deployment_finite_and_paper_only():
    o = Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator(
        Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestratorConfig(seed=64261, cycles=30)
    )
    rep = o.orchestrate_capital_deployment(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["deploy_allowed_rate"], float)


def test_phase64_adaptive_toxicity_resilient_capital_deployment_live_path_gated():
    try:
        Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator(
            Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestratorConfig(seed=64061, paper_only=False)
        )
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
