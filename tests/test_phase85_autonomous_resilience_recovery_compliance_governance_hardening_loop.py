import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.risk.phase85_autonomous_resilience_recovery_compliance_governance_hardening_loop import (
    Phase85AutonomousResilienceRecoveryComplianceGovernanceLoop,
    Phase85AutonomousResilienceRecoveryComplianceGovernanceConfig,
)


def test_phase85_autonomous_resilience_recovery_compliance_governance_hardening_smoke():
    eng = Phase85AutonomousResilienceRecoveryComplianceGovernanceLoop(
        Phase85AutonomousResilienceRecoveryComplianceGovernanceConfig(seed=85001, cycles=55)
    )
    rep = eng.run_autonomous_resilience_recovery_compliance_governance_hardening(cycles=55)
    assert rep["phase"] == "PHASE85_AUTONOMOUS_RESILIENCE_RECOVERY_COMPLIANCE_GOVERNANCE_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["evidence_chain_ok"] is True
    assert rep["gates"]["evidence_chain_tamper_evident"] is True
    assert rep["gates"]["compliance_attestation_ok"] is True
    assert rep["gates"]["governance_quorum_ok"] is True
    assert rep["gates"]["resilience_failover_ok"] is True
    assert rep["gates"]["recovery_guardrails_enforced"] is True
    assert rep["gates"]["slo_attestation_ok"] is True
    assert rep["gates"]["slo_attestation_quorum_ok"] is True
    assert rep["gates"]["validation_pass_rate_ok"] is True
    assert rep["gates"]["deterministic_paper_execution_ok"] is True
    assert rep["gates"]["live_paths_hard_gated_paper_only"] is True
    assert rep["gates"]["cross_venue_circuit_breaker_ok"] is True
    assert rep["gates"]["cross_venue_kill_switch_ok"] is True
    assert rep["gates"]["manual_reset_required"] is True
    assert rep["metrics"]["pass_rate"] >= 0.96
    assert rep["metrics"]["evidence_chain_len"] > 0
    assert rep["metrics"]["paper_executions"] > 0
