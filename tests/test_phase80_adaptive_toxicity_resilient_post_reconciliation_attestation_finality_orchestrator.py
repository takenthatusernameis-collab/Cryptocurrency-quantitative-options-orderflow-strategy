from __future__ import annotations

from src.hedging.phase80_adaptive_toxicity_resilient_post_reconciliation_attestation_finality_orchestrator import (
    Phase80AdaptiveToxicityResilientPostReconciliationAttestationFinalityConfig,
    Phase80AdaptiveToxicityResilientPostReconciliationAttestationFinalityOrchestrator,
)


def test_phase80_post_reconciliation_attestation_finality_orchestrator_smoke() -> None:
    cfg = Phase80AdaptiveToxicityResilientPostReconciliationAttestationFinalityConfig(seed=80080, paper_only=True, cycles=8)
    orch = Phase80AdaptiveToxicityResilientPostReconciliationAttestationFinalityOrchestrator(cfg)
    rep = orch.run_post_reconciliation_attestation_finality_orchestration(cycles=8)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["phase"] == "PHASE80_ADAPTIVE_TOXICITY_RESILIENT_POST_RECONCILIATION_ATTESTATION_FINALITY_ORCHESTRATOR"
    assert rep["cycles"] == 8
    assert rep["n_venue_finalities"] > 0
    assert rep["n_hedging_finalities"] > 0
    assert "composes" in rep
