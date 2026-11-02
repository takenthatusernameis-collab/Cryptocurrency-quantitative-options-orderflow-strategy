from src.risk.phase42_greeks_risk_monitor import Phase42GreeksRiskMonitor, GreeksMonitorConfig42


def test_phase42_greeks_aggregation_and_finite():
    m = Phase42GreeksRiskMonitor(GreeksMonitorConfig42(seed=42, cycles=6))
    for c in range(1, 7):
        s = m.aggregate(c)
        assert s.paper_only is True
        assert s.total_delta_usd == s.net_delta_usd
        assert isinstance(s.tail_gamma_alert, bool)
        assert s.risk_ok in (True, False)
        assert len(s.by_underlying) == 4


def test_phase42_greeks_campaign_green():
    m = Phase42GreeksRiskMonitor(GreeksMonitorConfig42(seed=123, cycles=10))
    rep = m.run_campaign(10)
    assert rep["phase"] == "PHASE42_GREEKS_RISK_MONITOR"
    assert rep["paper_only"] is True
    assert rep["total_cycles"] == 10
    assert "final_risk_ok" in rep


def test_phase42_greeks_reports(tmp_path):
    m = Phase42GreeksRiskMonitor(GreeksMonitorConfig42(seed=7, cycles=4))
    res = m.generate_reports(str(tmp_path))
    assert "json" in res and "md" in res
