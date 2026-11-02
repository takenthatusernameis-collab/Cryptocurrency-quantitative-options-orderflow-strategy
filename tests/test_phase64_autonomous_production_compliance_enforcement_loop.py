"""Phase 64 tests: Autonomous Production Compliance Enforcement Loop."""
from src.integration.phase64_autonomous_production_compliance_enforcement_loop import (
    Phase64AutonomousProductionComplianceEnforcementLoop,
    Phase64AutonomousProductionComplianceEnforcementConfig,
)


def test_phase64_autonomous_production_compliance_enforcement_basic():
    cfg = Phase64AutonomousProductionComplianceEnforcementConfig(seed=64062, cycles=40)
    c = Phase64AutonomousProductionComplianceEnforcementLoop(cfg)
    rep = c.run_compliance_enforcement(cycles=40)
    assert rep["phase"] == "PHASE64_AUTONOMOUS_PRODUCTION_COMPLIANCE_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_compliance_checks"], int)
    assert isinstance(rep["n_attestations"], int)


def test_phase64_autonomous_production_compliance_enforcement_artifacts(tmp_path):
    c = Phase64AutonomousProductionComplianceEnforcementLoop(
        Phase64AutonomousProductionComplianceEnforcementConfig(seed=64162, cycles=20)
    )
    rep = c.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase64_autonomous_production_compliance_enforcement_finite_and_paper_only():
    c = Phase64AutonomousProductionComplianceEnforcementLoop(
        Phase64AutonomousProductionComplianceEnforcementConfig(seed=64262, cycles=30)
    )
    rep = c.run_compliance_enforcement(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["compliance_pass_rate"], float)


def test_phase64_autonomous_production_compliance_enforcement_live_path_gated():
    try:
        Phase64AutonomousProductionComplianceEnforcementLoop(
            Phase64AutonomousProductionComplianceEnforcementConfig(seed=64062, paper_only=False)
        )
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
