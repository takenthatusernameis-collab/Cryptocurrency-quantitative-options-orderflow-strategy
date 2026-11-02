"""Phase 63 tests: Autonomous Production SLO Enforcement Loop."""
from src.integration.phase63_autonomous_production_slo_enforcement_loop import (
    Phase63AutonomousProductionSLOEnforcementLoop,
    Phase63AutonomousProductionSLOEnforcementConfig,
)


def test_phase63_autonomous_production_slo_enforcement_basic():
    cfg = Phase63AutonomousProductionSLOEnforcementConfig(seed=63062, cycles=40)
    e = Phase63AutonomousProductionSLOEnforcementLoop(cfg)
    rep = e.run_slo_enforcement(cycles=40)
    assert rep["phase"] == "PHASE63_AUTONOMOUS_PRODUCTION_SLO_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_burns"], int)
    assert isinstance(rep["n_rollbacks"], int)


def test_phase63_autonomous_production_slo_enforcement_artifacts(tmp_path):
    e = Phase63AutonomousProductionSLOEnforcementLoop(Phase63AutonomousProductionSLOEnforcementConfig(seed=63162, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase63_autonomous_production_slo_enforcement_finite_and_paper_only():
    e = Phase63AutonomousProductionSLOEnforcementLoop(Phase63AutonomousProductionSLOEnforcementConfig(seed=63262, cycles=30))
    rep = e.run_slo_enforcement(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["burn_rate_warn_count"], int)
    assert isinstance(rep["burn_rate_critical_count"], int)
