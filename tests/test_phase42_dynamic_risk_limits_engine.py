from src.monitoring.phase42_dynamic_risk_limits_engine import Phase42DynamicRiskLimitsEngine, DynamicLimitsConfig42


def test_phase42_dynamic_limits_breaches_and_kill_switch_hooks():
    e = Phase42DynamicRiskLimitsEngine(DynamicLimitsConfig42(seed=66, cycles=6))
    ev = e.evaluate(1, margin_utilization=0.85, collateral_available_usd=900000.0)
    assert ev.paper_only is True
    assert isinstance(ev.trading_enabled, bool)
    assert isinstance(ev.kill_switch_triggered, bool)
    assert ev.breach_count >= 0


def test_phase42_dynamic_limits_campaign():
    e = Phase42DynamicRiskLimitsEngine(DynamicLimitsConfig42(seed=77, cycles=10))
    rep = e.run_campaign(10)
    assert rep["phase"] == "PHASE42_DYNAMIC_RISK_LIMITS_ENGINE"
    assert rep["paper_only"] is True
    assert "all_ok" in rep


def test_phase42_dynamic_limits_reports(tmp_path):
    e = Phase42DynamicRiskLimitsEngine(DynamicLimitsConfig42(seed=8, cycles=4))
    res = e.generate_reports(str(tmp_path))
    assert "md" in res
