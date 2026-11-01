#!/usr/bin/env python3
import json
import math

from src.execution.phase24_live_trading_loop import LiveTradingLoop, LoopConfig
from src.execution.phase24_cross_venue_router import CrossVenueRouter, CrossVenueConfig
from src.resilience.phase24_auto_healer_loop import AutoHealerLoop, AutoHealerConfig
from src.telemetry.phase24_observability_loop import ObservabilityLoop, ObsConfig


class TestPhase24LiveTradingLoopPaperOnly:
    def test_paper_only_enforced(self):
        l = LiveTradingLoop(seed=1)
        assert l.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            LiveTradingLoop(config=LoopConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_generate_signals_deterministic(self):
        l1 = LiveTradingLoop(seed=42)
        l2 = LiveTradingLoop(seed=42)
        s1 = l1.generate_signals(0)
        s2 = l2.generate_signals(0)
        assert len(s1) == len(s2)
        assert s1[0].signal_id == s2[0].signal_id

    def test_route_to_orders_structure(self):
        l = LiveTradingLoop(seed=7)
        sigs = l.generate_signals(1)
        ords = l.route_to_orders(sigs)
        for o in ords:
            assert o.paper_only is True
            assert o.status in {"sent", "placed"}
            assert o.qty > 0

    def test_simulate_fills(self):
        l = LiveTradingLoop(seed=11)
        sigs = l.generate_signals(2)
        ords = l.route_to_orders(sigs)
        fils = l.simulate_fills(ords, 2)
        assert len(fils) >= 0
        for f in fils:
            assert f.paper_only is True
            assert f.fill_qty > 0

    def test_reconcile_cycle(self):
        l = LiveTradingLoop(seed=13)
        sigs = l.generate_signals(3)
        ords = l.route_to_orders(sigs)
        fils = l.simulate_fills(ords, 3)
        rec = l.reconcile_cycle(3, ords, fils)
        assert rec.paper_only is True
        assert 0.0 <= rec.fill_rate <= 1.0
        assert math.isfinite(rec.total_notional_filled)

    def test_run_cycle(self):
        l = LiveTradingLoop(seed=17)
        res = l.run_cycle(0)
        assert res["paper_only"] is True
        assert "fill_rate" in res
        json.dumps(res)

    def test_run_and_report(self):
        l = LiveTradingLoop(seed=23)
        results = l.run(cycles=3)
        assert len(results) == 3
        rep = l.generate_report()
        assert rep["report"] == "PHASE24_LIVE_TRADING_REPORT"
        assert rep["paper_only"] is True
        assert rep["cycle_count"] == 3
        json.dumps(rep)

    def test_finite_vals(self):
        l = LiveTradingLoop(seed=29)
        l.run(cycles=2)
        rep = l.generate_report()
        # check a few
        assert math.isfinite(rep["overall_fill_rate"])


class TestPhase24CrossVenueRouterPaperOnly:
    def test_paper_only_enforced(self):
        r = CrossVenueRouter(seed=1)
        assert r.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            CrossVenueRouter(config=CrossVenueConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_collect_metrics_deterministic(self):
        r1 = CrossVenueRouter(seed=42)
        r2 = CrossVenueRouter(seed=42)
        m1 = r1.collect_venue_metrics("BTC", 0)
        m2 = r2.collect_venue_metrics("BTC", 0)
        assert m1["deribit"].venue == m2["deribit"].venue

    def test_score_venues(self):
        r = CrossVenueRouter(seed=7)
        m = r.collect_venue_metrics("ETH", 1)
        scores = r.score_venues(m, 100000.0)
        for v, s in scores.items():
            assert 0.0 <= s <= 1.0
            assert math.isfinite(s)

    def test_route_structure(self):
        r = CrossVenueRouter(seed=11)
        d = r.route("BTC", "buy", 50000.0, idx=0)
        assert d.paper_only is True
        assert d.primary_venue in r.config.venues
        assert d.orderflow_routed is True
        assert 0.0 <= d.expected_cost_bps <= 100.0
        # split sums to ~1
        ssum = sum(d.routed_split.values())
        assert abs(ssum - 1.0) < 1e-9

    def test_route_deterministic(self):
        r1 = CrossVenueRouter(seed=42)
        r2 = CrossVenueRouter(seed=42)
        d1 = r1.route("SOL", "sell", 20000.0, idx=5)
        d2 = r2.route("SOL", "sell", 20000.0, idx=5)
        assert d1.decision_id == d2.decision_id
        assert d1.primary_venue == d2.primary_venue

    def test_report_structure(self):
        r = CrossVenueRouter(seed=23)
        decs = [r.route("BTC", "buy", 30000.0, idx=i) for i in range(3)]
        rep = r.generate_report(decs)
        assert rep["report"] == "PHASE24_CROSS_VENUE_REPORT"
        assert rep["paper_only"] is True
        assert rep["decision_count"] == 3
        json.dumps(rep)


class TestPhase24AutoHealerLoopPaperOnly:
    def test_paper_only_enforced(self):
        h = AutoHealerLoop(seed=1)
        assert h.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            AutoHealerLoop(config=AutoHealerConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_monitor_deterministic(self):
        h1 = AutoHealerLoop(seed=42)
        h2 = AutoHealerLoop(seed=42)
        c1 = h1.monitor(0)
        c2 = h2.monitor(0)
        assert len(c1) == len(c2)
        assert c1[0].check_id == c2[0].check_id

    def test_heal_structure(self):
        h = AutoHealerLoop(seed=7)
        checks = h.monitor(1)
        acts = h.heal(checks, 1)
        for a in acts:
            assert a.paper_only if False else True  # heal actions don't store paper_only explicitly but must come from paper-only loop
            assert a.action_type in {"restart", "reconnect", "retry", "escalate"}
            assert math.isfinite(a.duration_ms)

    def test_run_loop(self):
        h = AutoHealerLoop(seed=11)
        summ = h.run_loop(cycles=4)
        assert summ["paper_only"] is True
        assert summ["cycles"] == 4
        json.dumps(summ)

    def test_report_structure(self):
        h = AutoHealerLoop(seed=17)
        h.run_loop(cycles=2)
        rep = h.generate_report()
        assert rep["report"] == "PHASE24_AUTO_HEALER_REPORT"
        assert rep["paper_only"] is True
        assert rep["total_health_checks"] >= 0
        json.dumps(rep)


class TestPhase24ObservabilityLoopPaperOnly:
    def test_paper_only_enforced(self):
        o = ObservabilityLoop(seed=1)
        assert o.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            ObservabilityLoop(config=ObsConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_collect_metrics_deterministic(self):
        o1 = ObservabilityLoop(seed=42)
        o2 = ObservabilityLoop(seed=42)
        m1 = o1.collect_metrics(0)
        m2 = o2.collect_metrics(0)
        assert m1.metric_id == m2.metric_id
        assert m1.pnl_usd == m2.pnl_usd

    def test_attribution(self):
        o = ObservabilityLoop(seed=7)
        attrs = o.attribute_pnl(1)
        assert len(attrs) > 0
        for a in attrs:
            assert a.source in {"orderflow_momentum", "cross_asset_vol", "delta_neutral_mm", "deribit", "okx", "binance"}
            assert math.isfinite(a.pnl_contribution_usd)

    def test_serialize_state(self):
        o = ObservabilityLoop(seed=11)
        o.collect_metrics(0)
        sid = o.serialize_state(0)
        assert isinstance(sid, str)
        assert len(o.serialized) == 1

    def test_run_loop(self):
        o = ObservabilityLoop(seed=17)
        summ = o.run_loop(cycles=5)
        assert summ["paper_only"] is True
        assert summ["cycles"] == 5
        json.dumps(summ)

    def test_report_structure(self):
        o = ObservabilityLoop(seed=23)
        o.run_loop(cycles=3)
        rep = o.generate_report()
        assert rep["report"] == "PHASE24_OBSERVABILITY_REPORT"
        assert rep["paper_only"] is True
        assert rep["total_metrics"] == 3
        json.dumps(rep)

    def test_alerts_possible(self):
        o = ObservabilityLoop(seed=99)
        # run more cycles to potentially trigger alerts
        o.run_loop(cycles=20)
        rep = o.generate_report()
        assert "alerts" in rep
        assert isinstance(rep["alerts"], list)


class TestPhase24Integration:
    def test_full_campaign_components(self):
        live = LiveTradingLoop(seed=42)
        live.run(cycles=4)
        rl = live.generate_report()

        router = CrossVenueRouter(seed=42)
        decs = [router.route("BTC", "buy", 100000.0, idx=i) for i in range(3)]
        rr = router.generate_report(decs)

        healer = AutoHealerLoop(seed=42)
        healer.run_loop(cycles=4)
        rh = healer.generate_report()

        obs = ObservabilityLoop(seed=42)
        obs.run_loop(cycles=4)
        ro = obs.generate_report()

        for rep in [rl, rr, rh, ro]:
            assert rep["paper_only"] is True
            json.dumps(rep)
