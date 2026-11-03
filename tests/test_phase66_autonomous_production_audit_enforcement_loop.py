"""Phase 66 tests: Autonomous Production Audit Enforcement Loop."""
from src.integration.phase66_autonomous_production_audit_enforcement_loop import (
    Phase66AutonomousProductionAuditEnforcementLoop,
    Phase66AutonomousProductionAuditEnforcementConfig,
)


def test_phase66_autonomous_production_audit_enforcement_basic():
    cfg = Phase66AutonomousProductionAuditEnforcementConfig(seed=66062, cycles=40)
    e = Phase66AutonomousProductionAuditEnforcementLoop(cfg)
    rep = e.run_audit_enforcement(cycles=40)
    assert rep["phase"] == "PHASE66_AUTONOMOUS_PRODUCTION_AUDIT_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_audit_checks"], int)
    assert isinstance(rep["n_attestations"], int)


def test_phase66_autonomous_production_audit_enforcement_artifacts(tmp_path):
    e = Phase66AutonomousProductionAuditEnforcementLoop(
        Phase66AutonomousProductionAuditEnforcementConfig(seed=66162, cycles=20)
    )
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase66_autonomous_production_audit_enforcement_audit_finite():
    e = Phase66AutonomousProductionAuditEnforcementLoop(
        Phase66AutonomousProductionAuditEnforcementConfig(seed=66262, cycles=30)
    )
    rep = e.run_audit_enforcement(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["audit_pass_rate"], float)
    assert isinstance(rep["risk_ok"], bool)


def test_phase66_autonomous_production_audit_enforcement_live_path_gated():
    try:
        Phase66AutonomousProductionAuditEnforcementLoop(
            Phase66AutonomousProductionAuditEnforcementConfig(seed=66062, paper_only=False)
        )
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
