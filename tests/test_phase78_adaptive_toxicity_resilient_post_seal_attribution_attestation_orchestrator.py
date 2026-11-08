from __future__ import annotations

from src.hedging.phase78_adaptive_toxicity_resilient_post_seal_attribution_attestation_orchestrator import (
    Phase78AdaptiveToxicityResilientPostSealAttributionAttestationConfig,
    Phase78AdaptiveToxicityResilientPostSealAttributionAttestationOrchestrator,
)


def test_phase78_post_seal_attribution_attestation_orchestrator_smoke() -> None:
    cfg = Phase78AdaptiveToxicityResilientPostSealAttributionAttestationConfig(seed=78078, paper_only=True, cycles=8)
    orch = Phase78AdaptiveToxicityResilientPostSealAttributionAttestationOrchestrator(cfg)
    rep = orch.run_post_seal_attribution_attestation_orchestration(cycles=8)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["phase"] == "PHASE78_ADAPTIVE_TOXICITY_RESILIENT_POST_SEAL_ATTRIBUTION_ATTESTATION_ORCHESTRATOR"
    assert rep["cycles"] == 8
    assert rep["n_venue_attestations"] > 0
    assert rep["n_hedging_attestations"] > 0
    assert "composes" in rep
