from src.hedging.phase71_adaptive_toxicity_resilient_containment_certification_orchestrator import (
    Phase71AdaptiveToxicityResilientContainmentCertificationOrchestrator,
    Phase71AdaptiveToxicityResilientContainmentCertificationConfig,
)


def test_phase71_containment_certification_orchestrator_smoke():
    orch = Phase71AdaptiveToxicityResilientContainmentCertificationOrchestrator(
        Phase71AdaptiveToxicityResilientContainmentCertificationConfig(seed=7171, cycles=40)
    )
    rep = orch.run_containment_certification_orchestration(cycles=40)
    assert rep["phase"] == "PHASE71_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_CERTIFICATION_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["containment_certification_pass_rate"] >= 0.0
    arts = orch.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
