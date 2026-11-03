from src.hedging.phase68_adaptive_toxicity_resilient_containment_orchestrator import (
    Phase68AdaptiveToxicityResilientContainmentOrchestrator,
    Phase68AdaptiveToxicityResilientContainmentOrchestratorConfig,
)


def test_phase68_containment_orchestrator_deterministic():
    orch = Phase68AdaptiveToxicityResilientContainmentOrchestrator(
        Phase68AdaptiveToxicityResilientContainmentOrchestratorConfig(seed=68061, cycles=40)
    )
    rep = orch.run_containment_orchestration(cycles=40)
    assert rep["phase"] == "PHASE68_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["n_hedging_contains"] > 0
    arts = orch.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
