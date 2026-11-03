from src.integration.phase75_autonomous_governance_audit_trail_hardening_loop import (
    Phase75AutonomousGovernanceAuditTrailHardeningLoop,
    Phase75AutonomousGovernanceAuditTrailHardeningLoopConfig,
)


def test_phase75_autonomous_governance_audit_trail_hardening_loop_smoke():
    eng = Phase75AutonomousGovernanceAuditTrailHardeningLoop(
        Phase75AutonomousGovernanceAuditTrailHardeningLoopConfig(seed=7572, cycles=40)
    )
    rep = eng.run_autonomous_governance_audit_trail_hardening_loop(cycles=40)
    assert rep["phase"] == "PHASE75_AUTONOMOUS_GOVERNANCE_AUDIT_TRAIL_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
