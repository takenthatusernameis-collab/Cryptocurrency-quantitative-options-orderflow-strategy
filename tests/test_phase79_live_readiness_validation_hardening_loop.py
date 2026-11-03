import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.risk.phase79_live_readiness_validation_hardening_loop import (
    Phase79LiveReadinessValidationHardeningLoop,
    Phase79LiveReadinessValidationHardeningConfig,
)


def test_phase79_live_readiness_validation_hardening_loop_smoke():
    eng = Phase79LiveReadinessValidationHardeningLoop(
        Phase79LiveReadinessValidationHardeningConfig(seed=7903, cycles=40)
    )
    rep = eng.run_live_readiness_validation_hardening(cycles=40)
    assert rep["phase"] == "PHASE79_LIVE_READINESS_VALIDATION_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["margin_collateral_reconciled"] is True
    assert rep["gates"]["risk_limits_enforced"] is True
    assert rep["gates"]["realtime_risk_monitor_ok"] is True
    assert rep["gates"]["capital_rollout_ok"] is True
    assert rep["gates"]["kill_switch_not_halted"] is True
    assert rep["gates"]["compliance_gates_passed"] is True
    assert rep["counts"]["margin_reports"] > 0
    assert rep["counts"]["compliance_gates"] > 0
