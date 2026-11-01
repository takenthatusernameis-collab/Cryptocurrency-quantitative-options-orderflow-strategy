#!/usr/bin/env python3
import json
import math
from pathlib import Path

from src.risk.phase21_risk_aggregator import Phase21RiskAggregator, AggregationConfig
from src.risk.phase21_stress_tester import Phase21StressTester, StressConfig
from src.risk.phase21_pre_trade_validator import Phase21PreTradeValidator, PreTradeConfig, TradeIntent
from src.monitoring.phase21_risk_monitor import Phase21RiskMonitor, RiskMonitorConfig
from src.analytics.phase21_risk_attribution import Phase21RiskAttribution, AttributionConfig


class TestPhase21RiskAggregator:
    def test_paper_only_enforced(self):
        a = Phase21RiskAggregator(seed=1)
        assert a.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            Phase21RiskAggregator(config=AggregationConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_aggregate_exposures_deterministic(self):
        a1 = Phase21RiskAggregator(seed=42)
        a2 = Phase21RiskAggregator(seed=42)
        s1 = a1.aggregate_exposures(["vol_arb"], ["deribit"], ["BTC", "ETH"])
        s2 = a2.aggregate_exposures(["vol_arb"], ["deribit"], ["BTC", "ETH"])
        assert [s.snapshot_id for s in s1] == [s.snapshot_id for s in s2]
        assert len(s1) == 2

    def test_aggregate_exposures_no_nan_inf(self):
        a = Phase21RiskAggregator(seed=7)
        snaps = a.aggregate_exposures(["vol_arb", "mm"], ["deribit", "okx"], ["BTC", "ETH", "SOL"])
        for s in snaps:
            assert math.isfinite(s.notional_usd)
            assert math.isfinite(s.delta)
            assert math.isfinite(s.gamma)
            assert math.isfinite(s.vega)
            assert math.isfinite(s.theta)
        assert all(s.paper_only for s in snaps)

    def test_check_limits_structure(self):
        a = Phase21RiskAggregator(seed=11)
        snaps = a.aggregate_exposures(["vol_arb"], ["deribit"], ["BTC"])
        lim = a.check_limits(snaps)
        assert "totals" in lim
        assert "breaches" in lim
        assert "passed" in lim
        assert lim["paper_only"] is True

    def test_generate_report_serializable(self):
        a = Phase21RiskAggregator(seed=13)
        snaps = a.aggregate_exposures(["vol_arb"], ["deribit"], ["BTC", "ETH"])
        rep = a.generate_report(snaps)
        assert rep["report"] == "PHASE21_RISK_AGGREGATION_REPORT"
        assert rep["paper_only"] is True
        json.dumps(rep)


class TestPhase21StressTester:
    def test_paper_only_enforced(self):
        s = Phase21StressTester(seed=1)
        assert s.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            Phase21StressTester(config=StressConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_build_scenarios_deterministic(self):
        s1 = Phase21StressTester(seed=42)
        s2 = Phase21StressTester(seed=42)
        sc1 = s1.build_scenarios()
        sc2 = s2.build_scenarios()
        assert [sc.scenario_id for sc in sc1] == [sc.scenario_id for sc in sc2]
        assert len(sc1) == 5 * 5 * 5

    def test_run_stress_no_nan_inf(self):
        s = Phase21StressTester(seed=17)
        sc = s.build_scenarios()
        res = s.run_stress(sc)
        for r in res:
            assert math.isfinite(r.pnl_impact_usd)
            assert math.isfinite(r.delta_impact)
            assert math.isfinite(r.vega_impact)
            assert math.isfinite(r.gamma_impact)
            assert all(r.paper_only for r in res)

    def test_stress_breach_logic(self):
        s = Phase21StressTester(seed=23)
        sc = s.build_scenarios()
        res = s.run_stress(sc, base_notional=10000000.0)  # large
        # may produce breaches
        assert isinstance(res[0].breached, bool)

    def test_generate_report_serializable(self):
        s = Phase21StressTester(seed=29)
        sc = s.build_scenarios()
        res = s.run_stress(sc)
        rep = s.generate_report(sc, res)
        assert rep["report"] == "PHASE21_STRESS_TESTING_REPORT"
        json.dumps(rep)


class TestPhase21PreTradeValidator:
    def test_paper_only_enforced(self):
        v = Phase21PreTradeValidator(seed=1)
        assert v.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            Phase21PreTradeValidator(config=PreTradeConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_validate_blocks_large_notional(self):
        v = Phase21PreTradeValidator(seed=31)
        intents = [TradeIntent(intent_id="t1", symbol="BTC", venue="deribit", strategy="vol_arb", side="buy", qty=10.0, notional_usd=1000000.0, delta_est=10.0, vega_est=100.0, gamma_est=0.001, orderflow_confirmed=True, paper_only=True)]
        decs = v.validate(intents)
        assert decs[0].blocked is True
        assert "order_notional_exceeds_limit" in decs[0].block_reasons

    def test_validate_blocks_unconfirmed_orderflow(self):
        v = Phase21PreTradeValidator(seed=37)
        intents = [TradeIntent(intent_id="t2", symbol="BTC", venue="deribit", strategy="vol_arb", side="buy", qty=0.01, notional_usd=50000.0, delta_est=10.0, vega_est=100.0, gamma_est=0.001, orderflow_confirmed=False, paper_only=True)]
        decs = v.validate(intents)
        assert decs[0].blocked is True
        assert "orderflow_not_confirmed" in decs[0].block_reasons

    def test_validate_allows_confirmed_small(self):
        v = Phase21PreTradeValidator(seed=41)
        intents = [TradeIntent(intent_id="t3", symbol="BTC", venue="deribit", strategy="vol_arb", side="buy", qty=0.01, notional_usd=50000.0, delta_est=10.0, vega_est=100.0, gamma_est=0.001, orderflow_confirmed=True, paper_only=True)]
        decs = v.validate(intents)
        assert decs[0].approved is True
        assert decs[0].blocked is False

    def test_override_audited(self):
        v = Phase21PreTradeValidator(seed=43)
        intents = [TradeIntent(intent_id="t4", symbol="BTC", venue="deribit", strategy="vol_arb", side="buy", qty=10.0, notional_usd=1000000.0, delta_est=10.0, vega_est=100.0, gamma_est=0.001, orderflow_confirmed=True, paper_only=True)]
        decs = v.validate(intents, allow_override=True)
        assert decs[0].approved is True
        assert decs[0].blocked is False
        assert decs[0].override_audit_id is not None
        assert len(v.override_audit) == 1

    def test_generate_report_serializable(self):
        v = Phase21PreTradeValidator(seed=47)
        intents = [TradeIntent(intent_id="t5", symbol="BTC", venue="deribit", strategy="vol_arb", side="buy", qty=0.01, notional_usd=50000.0, delta_est=10.0, vega_est=100.0, gamma_est=0.001, orderflow_confirmed=True, paper_only=True)]
        decs = v.validate(intents)
        rep = v.generate_report(intents, decs)
        assert rep["report"] == "PHASE21_PRE_TRADE_VALIDATION_REPORT"
        json.dumps(rep)


class TestPhase21RiskMonitor:
    def test_paper_only_enforced(self):
        m = Phase21RiskMonitor(seed=1)
        assert m.config.paper_only is True

    def test_monitor_healthy(self):
        m = Phase21RiskMonitor(seed=53)
        agg_lim = {"totals": {"notional_usd": 100000.0, "delta": 10.0, "gamma": 1.0, "vega": 1000.0}, "breaches": [], "passed": True}
        mon = m.monitor(agg_lim)
        assert mon["paper_only"] is True
        assert "utilization" in mon
        assert "alerts" in mon

    def test_monitor_alerts_on_breaches(self):
        m = Phase21RiskMonitor(seed=59)
        agg_lim = {"totals": {"notional_usd": 100000.0, "delta": 10.0, "gamma": 1.0, "vega": 1000.0}, "breaches": [{"type": "x", "severity": "block"}], "passed": False}
        mon = m.monitor(agg_lim)
        assert any(a["type"] == "aggregation_breach" for a in mon["alerts"])

    def test_generate_report_serializable(self):
        m = Phase21RiskMonitor(seed=61)
        agg_lim = {"totals": {"notional_usd": 100000.0, "delta": 10.0, "gamma": 1.0, "vega": 1000.0}, "breaches": [], "passed": True}
        rep = m.generate_report(agg_lim)
        assert rep["report"] == "PHASE21_RISK_MONITORING_REPORT"
        json.dumps(rep)


class TestPhase21RiskAttribution:
    def test_paper_only_enforced(self):
        a = Phase21RiskAttribution(seed=1)
        assert a.config.paper_only is True

    def test_attribute_lines(self):
        agg = Phase21RiskAggregator(seed=67)
        snaps = agg.aggregate_exposures(["vol_arb"], ["deribit"], ["BTC", "ETH"])
        attr = Phase21RiskAttribution(seed=67)
        lines = attr.attribute(snaps)
        assert len(lines) == len(snaps)
        assert all(math.isfinite(l.pnl_attrib_usd) for l in lines)
        assert all(l.paper_only for l in lines)

    def test_generate_report_serializable(self):
        agg = Phase21RiskAggregator(seed=71)
        snaps = agg.aggregate_exposures(["vol_arb"], ["deribit"], ["BTC"])
        attr = Phase21RiskAttribution(seed=71)
        rep = attr.generate_report(snaps)
        assert rep["report"] == "PHASE21_RISK_ATTRIBUTION_REPORT"
        assert rep["line_count"] >= 1
        json.dumps(rep)
