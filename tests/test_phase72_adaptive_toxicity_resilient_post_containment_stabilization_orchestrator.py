from src.hedging.phase72_adaptive_toxicity_resilient_post_containment_stabilization_orchestrator import (
    Phase72AdaptiveToxicityResilientPostContainmentStabilizationOrchestrator,
    Phase72AdaptiveToxicityResilientPostContainmentStabilizationConfig,
)


def test_phase72_post_containment_stabilization_orchestrator_smoke():
    orch = Phase72AdaptiveToxicityResilientPostContainmentStabilizationOrchestrator(
        Phase72AdaptiveToxicityResilientPostContainmentStabilizationConfig(seed=7272, cycles=40)
    )
    rep = orch.run_post_containment_stabilization_orchestration(cycles=40)
    assert rep["phase"] == "PHASE72_ADAPTIVE_TOXICITY_RESILIENT_POST_CONTAINMENT_STABILIZATION_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["stabilization_pass_rate"] >= 0.0
    arts = orch.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
