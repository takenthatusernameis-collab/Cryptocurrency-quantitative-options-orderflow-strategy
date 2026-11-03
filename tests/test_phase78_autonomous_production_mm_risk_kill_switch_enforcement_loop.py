import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.integration.phase78_autonomous_production_mm_risk_kill_switch_enforcement_loop import (
    Phase78AutonomousProductionMmRiskKillSwitchEnforcementLoop,
    Phase78AutonomousProductionMmRiskKillSwitchEnforcementLoopConfig,
)


def test_phase78_autonomous_production_mm_risk_kill_switch_enforcement_loop_smoke():
    eng = Phase78AutonomousProductionMmRiskKillSwitchEnforcementLoop(
        Phase78AutonomousProductionMmRiskKillSwitchEnforcementLoopConfig(seed=7803, cycles=40)
    )
    rep = eng.run_production_mm_risk_kill_switch_enforcement(cycles=40)
    assert rep["phase"] == "PHASE78_AUTONOMOUS_PRODUCTION_MM_RISK_KILL_SWITCH_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["pretrade_enforced"] is True
    assert rep["gates"]["kill_switch_attestation_ok"] is True
    assert rep["gates"]["auto_derisk_on_breach"] is True
