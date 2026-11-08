from src.hedging.phase74_adaptive_toxicity_resilient_post_attestation_reconciliation_finality_orchestrator import (
    Phase74AdaptiveToxicityResilientPostAttestationReconciliationFinalityOrchestrator,
    Phase74AdaptiveToxicityResilientPostAttestationReconciliationFinalityConfig,
)


def test_phase74_post_attestation_reconciliation_finality_orchestrator_smoke():
    orch = Phase74AdaptiveToxicityResilientPostAttestationReconciliationFinalityOrchestrator(
        Phase74AdaptiveToxicityResilientPostAttestationReconciliationFinalityConfig(seed=7474, cycles=40)
    )
    rep = orch.run_post_attestation_reconciliation_finality_orchestration(cycles=40)
    assert rep["phase"] == "PHASE74_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTESTATION_RECONCILIATION_FINALITY_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["finality_pass_rate"] >= 0.0
    arts = orch.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
