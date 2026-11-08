from __future__ import annotations

from src.hedging.phase79_adaptive_toxicity_resilient_post_attestation_reconciliation_attestation_orchestrator import (
    Phase79AdaptiveToxicityResilientPostAttestationReconciliationAttestationConfig,
    Phase79AdaptiveToxicityResilientPostAttestationReconciliationAttestationOrchestrator,
)


def test_phase79_post_attestation_reconciliation_attestation_orchestrator_smoke() -> None:
    cfg = Phase79AdaptiveToxicityResilientPostAttestationReconciliationAttestationConfig(seed=79079, paper_only=True, cycles=8)
    orch = Phase79AdaptiveToxicityResilientPostAttestationReconciliationAttestationOrchestrator(cfg)
    rep = orch.run_post_attestation_reconciliation_attestation_orchestration(cycles=8)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["phase"] == "PHASE79_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTESTATION_RECONCILIATION_ATTESTATION_ORCHESTRATOR"
    assert rep["cycles"] == 8
    assert rep["n_venue_reconciliation_attestations"] > 0
    assert rep["n_hedging_reconciliation_attestations"] > 0
    assert "composes" in rep
