"""Phase 65 tests: Autonomous Production Risk Enforcement Loop."""
from src.integration.phase65_autonomous_production_risk_enforcement_loop import (
    Phase65AutonomousProductionRiskEnforcementLoop,
    Phase65AutonomousProductionRiskEnforcementConfig,
)


def test_phase65_autonomous_production_risk_enforcement_basic():
    cfg = Phase65AutonomousProductionRiskEnforcementConfig(seed=65062, cycles=40)
    c = Phase65AutonomousProductionRiskEnforcementLoop(cfg)
    rep = c.run_risk_enforcement(cycles=40)
    assert rep["phase"] == "PHASE65_AUTONOMOUS_PRODUCTION_RISK_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_risk_checks"], int)
    assert isinstance(rep["n_attestations"], int)


def test_phase65_autonomous_production_risk_enforcement_artifacts(tmp_path):
    c = Phase65AutonomousProductionRiskEnforcementLoop(
        Phase65AutonomousProductionRiskEnforcementConfig(seed=65162, cycles=20)
    )
    rep = c.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase65_autonomous_production_risk_enforcement_finite_and_paper_only():
    c = Phase65AutonomousProductionRiskEnforcementLoop(
        Phase65AutonomousProductionRiskEnforcementConfig(seed=65262, cycles=30)
    )
    rep = c.run_risk_enforcement(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["risk_pass_rate"], float)


def test_phase65_autonomous_production_risk_enforcement_live_path_gated():
    try:
        Phase65AutonomousProductionRiskEnforcementLoop(
            Phase65AutonomousProductionRiskEnforcementConfig(seed=65062, paper_only=False)
        )
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
