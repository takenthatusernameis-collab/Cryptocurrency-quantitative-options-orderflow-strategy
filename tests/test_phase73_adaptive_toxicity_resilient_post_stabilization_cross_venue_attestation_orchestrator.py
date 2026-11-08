from src.hedging.phase73_adaptive_toxicity_resilient_post_stabilization_cross_venue_attestation_orchestrator import (
    Phase73AdaptiveToxicityResilientPostStabilizationCrossVenueAttestationOrchestrator,
    Phase73AdaptiveToxicityResilientPostStabilizationCrossVenueAttestationConfig,
)


def test_phase73_post_stabilization_cross_venue_attestation_orchestrator_smoke():
    orch = Phase73AdaptiveToxicityResilientPostStabilizationCrossVenueAttestationOrchestrator(
        Phase73AdaptiveToxicityResilientPostStabilizationCrossVenueAttestationConfig(seed=7373, cycles=40)
    )
    rep = orch.run_post_stabilization_cross_venue_attestation_orchestration(cycles=40)
    assert rep["phase"] == "PHASE73_ADAPTIVE_TOXICITY_RESILIENT_POST_STABILIZATION_CROSS_VENUE_ATTESTATION_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["attestation_pass_rate"] >= 0.0
    arts = orch.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
