from src.integration.phase70_autonomous_production_recovery_compliance_enforcement_loop import (
    Phase70AutonomousProductionRecoveryComplianceEnforcementLoop,
    Phase70AutonomousProductionRecoveryComplianceEnforcementLoopConfig,
)


def test_phase70_recovery_compliance_enforcement_loop_smoke():
    loop = Phase70AutonomousProductionRecoveryComplianceEnforcementLoop(
        Phase70AutonomousProductionRecoveryComplianceEnforcementLoopConfig(seed=7072, cycles=40)
    )
    rep = loop.run_recovery_compliance_enforcement(cycles=40)
    assert rep["phase"] == "PHASE70_AUTONOMOUS_PRODUCTION_RECOVERY_COMPLIANCE_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["compliance_pass_rate"] >= 0.0
    arts = loop.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
