#!/usr/bin/env python3
import json
import math

from src.execution.phase22_smart_router import SmartOrderRouter, RouterConfig
from src.execution.phase22_fill_predictor import FillPredictor, FillConfig
from src.execution.phase22_slippage_model import SlippageModel, SlippageConfig
from src.execution.phase22_order_slicer import OrderSlicer, SlicerConfig
from src.analytics.phase22_tca import TCA, TCAConfig


class TestPhase22SmartRouterPaperOnly:
    def test_paper_only_enforced(self):
        r = SmartOrderRouter(seed=1)
        assert r.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            SmartOrderRouter(config=RouterConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_default_config_values(self):
        r = SmartOrderRouter(seed=5)
        assert r.config.max_latency_ms == 50.0
        assert r.config.max_spread_bps == 5.0
        assert r.config.min_depth_usd == 100000.0
        assert r.config.paper_only is True

    def test_quote_venue_deterministic(self):
        r1 = SmartOrderRouter(seed=42)
        r2 = SmartOrderRouter(seed=42)
        q1 = r1.quote_venue("deribit", "BTC", 0)
        q2 = r2.quote_venue("deribit", "BTC", 0)
        assert q1.venue == q2.venue
        assert q1.symbol == q2.symbol
        assert q1.bid == q2.bid
        assert q1.ask == q2.ask
        assert q1.mid == q2.mid
        assert q1.paper_only is True

    def test_quote_venue_finite(self):
        r = SmartOrderRouter(seed=7)
        for sym in ["BTC", "ETH", "SOL"]:
            for ven in ["deribit", "okx", "binance"]:
                q = r.quote_venue(ven, sym, 1)
                assert math.isfinite(q.bid)
                assert math.isfinite(q.ask)
                assert math.isfinite(q.mid)
                assert math.isfinite(q.spread_bps)
                assert math.isfinite(q.depth_usd)
                assert math.isfinite(q.latency_ms)
                assert math.isfinite(q.fee_bps)
                assert q.bid < q.ask

    def test_score_venue_range(self):
        r = SmartOrderRouter(seed=11)
        q = r.quote_venue("deribit", "BTC", 0)
        score = r.score_venue(q, 100000.0)
        assert 0.0 <= score <= 1.0
        assert math.isfinite(score)

    def test_route_deterministic(self):
        r1 = SmartOrderRouter(seed=42)
        r2 = SmartOrderRouter(seed=42)
        d1 = r1.route("BTC", "buy", 100000.0, venues=["deribit", "okx"], idx=0)
        d2 = r2.route("BTC", "buy", 100000.0, venues=["deribit", "okx"], idx=0)
        assert d1.decision_id == d2.decision_id
        assert d1.selected_venue == d2.selected_venue
        assert d1.score == d2.score
        assert d1.paper_only is True

    def test_route_structure(self):
        r = SmartOrderRouter(seed=13)
        d = r.route("ETH", "sell", 250000.0, venues=["binance", "bybit"], idx=1)
        assert d.symbol == "ETH"
        assert d.side == "sell"
        assert d.notional_usd == 250000.0
        assert d.selected_venue in {"binance", "bybit"}
        assert 0.0 <= d.score <= 1.0
        assert math.isfinite(d.expected_slippage_bps)
        assert math.isfinite(d.expected_latency_ms)
        assert math.isfinite(d.expected_fee_bps)
        assert isinstance(d.routed, bool)
        assert d.venue_scores

    def test_route_venue_scores_sum(self):
        r = SmartOrderRouter(seed=17)
        d = r.route("SOL", "buy", 100000.0, venues=["deribit", "okx", "binance"], idx=2)
        assert len(d.venue_scores) == 3
        for v, s in d.venue_scores.items():
            assert 0.0 <= s <= 1.0

    def test_route_paper_only_flag(self):
        r = SmartOrderRouter(seed=19)
        d = r.route("BTC", "buy", 100000.0, idx=3)
        assert d.paper_only is True

    def test_generate_report_structure(self):
        r = SmartOrderRouter(seed=23)
        decs = [r.route("BTC", "buy", 100000.0, idx=i) for i in range(3)]
        rep = r.generate_report(decs)
        assert rep["report"] == "PHASE22_SMART_ROUTING_REPORT"
        assert rep["decision_count"] == 3
        assert rep["routed_count"] == 3
        assert rep["paper_only"] is True
        assert len(rep["decisions"]) == 3
        json.dumps(rep)

    def test_generate_report_no_nan(self):
        r = SmartOrderRouter(seed=29)
        decs = [r.route("BTC", "buy", 100000.0, idx=i) for i in range(5)]
        rep = r.generate_report(decs)
        assert math.isfinite(rep["config"]["cost_weight"])
        assert math.isfinite(rep["config"]["latency_weight"])
        assert math.isfinite(rep["config"]["liquidity_weight"])


class TestPhase22FillPredictorPaperOnly:
    def test_paper_only_enforced(self):
        f = FillPredictor(seed=1)
        assert f.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            FillPredictor(config=FillConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_make_signal_deterministic(self):
        f1 = FillPredictor(seed=42)
        f2 = FillPredictor(seed=42)
        s1 = f1.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 1.0, 1000000.0, 10.0, True, 0)
        s2 = f2.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 1.0, 1000000.0, 10.0, True, 0)
        assert s1.signal_id == s2.signal_id
        assert s1.spread_bps == s2.spread_bps
        assert s1.depth_usd == s2.depth_usd
        assert s1.paper_only is True

    def test_make_signal_finite(self):
        f = FillPredictor(seed=7)
        for i in range(5):
            s = f.make_signal("ETH", "okx", "sell", 10.0, 50000.0, 2.0, 500000.0, 20.0, False, i)
            assert math.isfinite(s.notional_usd)
            assert math.isfinite(s.spread_bps)
            assert math.isfinite(s.depth_usd)
            assert math.isfinite(s.latency_ms)
            assert isinstance(s.orderflow_confirmed, bool)

    def test_predict_deterministic(self):
        f1 = FillPredictor(seed=42)
        f2 = FillPredictor(seed=42)
        sig = f1.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 1.0, 1000000.0, 10.0, True, 0)
        p1 = f1.predict(sig, 0)
        p2 = f2.predict(sig, 0)
        assert p1.prediction_id == p2.prediction_id
        assert p1.fill_probability == p2.fill_probability
        assert p1.expected_fill_price == p2.expected_fill_price

    def test_fill_probability_range(self):
        f = FillPredictor(seed=11)
        for i in range(10):
            s = f.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, float(i), 1000000.0, float(i * 5), bool(i % 2), i)
            p = f.predict(s, i)
            assert 0.0 <= p.fill_probability <= 1.0
            assert math.isfinite(p.fill_probability)
            assert math.isfinite(p.expected_fill_price)
            assert math.isfinite(p.expected_fill_qty)
            assert math.isfinite(p.expected_time_ms)
            assert math.isfinite(p.confidence)
            assert 0.0 <= p.confidence <= 1.0

    def test_orderflow_confirmed_boosts_prob(self):
        f = FillPredictor(seed=13)
        s_on = f.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 1.0, 1000000.0, 10.0, True, 0)
        s_off = f.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 1.0, 1000000.0, 10.0, False, 1)
        p_on = f.predict(s_on, 0)
        p_off = f.predict(s_off, 1)
        assert p_on.fill_probability >= p_off.fill_probability

    def test_generate_report_structure(self):
        f = FillPredictor(seed=17)
        sigs = [f.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 1.0, 1000000.0, 10.0, True, i) for i in range(3)]
        preds = [f.predict(s, i) for i, s in enumerate(sigs)]
        rep = f.generate_report(sigs, preds)
        assert rep["report"] == "PHASE22_FILL_PREDICTION_REPORT"
        assert rep["signal_count"] == 3
        assert rep["prediction_count"] == 3
        assert rep["paper_only"] is True
        assert "avg_fill_probability" in rep["summary"]
        assert math.isfinite(rep["summary"]["avg_fill_probability"])
        json.dumps(rep)


class TestPhase22SlippageModelPaperOnly:
    def test_paper_only_enforced(self):
        s = SlippageModel(seed=1)
        assert s.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            SlippageModel(config=SlippageConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_make_input_deterministic(self):
        s1 = SlippageModel(seed=42)
        s2 = SlippageModel(seed=42)
        i1 = s1.make_input("BTC", "deribit", "buy", 100000.0, 1.0, 90000.0, 1.0, 1000000.0, 0.2, 0)
        i2 = s2.make_input("BTC", "deribit", "buy", 100000.0, 1.0, 90000.0, 1.0, 1000000.0, 0.2, 0)
        assert i1.input_id == i2.input_id
        assert i1.notional_usd == i2.notional_usd
        assert i1.mid_price == i2.mid_price
        assert i1.paper_only is True

    def test_make_input_finite(self):
        s = SlippageModel(seed=7)
        for i in range(5):
            inp = s.make_input("ETH", "okx", "sell", 50000.0, 10.0, 3000.0, 2.0, 500000.0, 0.5, i)
            assert math.isfinite(inp.notional_usd)
            assert math.isfinite(inp.qty)
            assert math.isfinite(inp.mid_price)
            assert math.isfinite(inp.spread_bps)
            assert math.isfinite(inp.depth_usd)
            assert math.isfinite(inp.volatility)

    def test_estimate_deterministic(self):
        s1 = SlippageModel(seed=42)
        s2 = SlippageModel(seed=42)
        inp = s1.make_input("BTC", "deribit", "buy", 100000.0, 1.0, 90000.0, 1.0, 1000000.0, 0.2, 0)
        r1 = s1.estimate(inp, 0)
        r2 = s2.estimate(inp, 0)
        assert r1.result_id == r2.result_id
        assert r1.total_slippage_bps == r2.total_slippage_bps
        assert r1.slippage_cost_usd == r2.slippage_cost_usd

    def test_estimate_ranges(self):
        s = SlippageModel(seed=11)
        for i in range(10):
            inp = s.make_input("BTC", "deribit", "buy", 100000.0, 1.0, 90000.0, float(i), 1000000.0, float(i) / 10.0, i)
            res = s.estimate(inp, i)
            assert 0.0 <= res.total_slippage_bps <= s.config.max_slippage_bps
            assert math.isfinite(res.temporary_impact_bps)
            assert math.isfinite(res.permanent_impact_bps)
            assert math.isfinite(res.spread_cost_bps)
            assert math.isfinite(res.total_slippage_bps)
            assert math.isfinite(res.slippage_cost_usd)
            assert math.isfinite(res.expected_fill_price)
            assert isinstance(res.within_limit, bool)

    def test_buy_fill_price_above_mid(self):
        s = SlippageModel(seed=13)
        inp = s.make_input("BTC", "deribit", "buy", 100000.0, 1.0, 90000.0, 1.0, 1000000.0, 0.2, 0)
        res = s.estimate(inp, 0)
        assert res.expected_fill_price >= inp.mid_price

    def test_sell_fill_price_below_mid(self):
        s = SlippageModel(seed=13)
        inp = s.make_input("BTC", "deribit", "sell", 100000.0, 1.0, 90000.0, 1.0, 1000000.0, 0.2, 1)
        res = s.estimate(inp, 1)
        assert res.expected_fill_price <= inp.mid_price

    def test_generate_report_structure(self):
        s = SlippageModel(seed=17)
        inputs = [s.make_input("BTC", "deribit", "buy", 100000.0, 1.0, 90000.0, 1.0, 1000000.0, 0.2, i) for i in range(3)]
        results = [s.estimate(inp, i) for i, inp in enumerate(inputs)]
        rep = s.generate_report(inputs, results)
        assert rep["report"] == "PHASE22_SLIPPAGE_REPORT"
        assert rep["input_count"] == 3
        assert rep["result_count"] == 3
        assert rep["paper_only"] is True
        assert "avg_total_slippage_bps" in rep["summary"]
        assert "within_limit_rate" in rep["summary"]
        assert math.isfinite(rep["summary"]["avg_total_slippage_bps"])
        assert 0.0 <= rep["summary"]["within_limit_rate"] <= 1.0
        json.dumps(rep)


class TestPhase22OrderSlicerPaperOnly:
    def test_paper_only_enforced(self):
        sl = OrderSlicer(seed=1)
        assert sl.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            OrderSlicer(config=SlicerConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_slice_order_deterministic(self):
        sl1 = OrderSlicer(seed=42)
        sl2 = OrderSlicer(seed=42)
        p1 = sl1.slice_order("BTC", "buy", 1000000.0, 10.0, "deribit", schedule="twap", n_slices=5, idx=0)
        p2 = sl2.slice_order("BTC", "buy", 1000000.0, 10.0, "deribit", schedule="twap", n_slices=5, idx=0)
        assert p1.plan_id == p2.plan_id
        assert p1.slice_count == p2.slice_count
        assert p1.schedule == p2.schedule
        assert p1.paper_only is True

    def test_slice_order_structure(self):
        sl = OrderSlicer(seed=11)
        p = sl.slice_order("ETH", "sell", 500000.0, 200.0, "okx", schedule="vwap", n_slices=4, idx=1)
        assert p.symbol == "ETH"
        assert p.side == "sell"
        assert p.total_notional_usd == 500000.0
        assert p.total_qty == 200.0
        assert p.schedule == "vwap"
        assert p.slice_count == 4
        assert len(p.slices) == 4
        assert p.venue == "okx"
        assert p.paper_only is True
        total_notional = sum(slc.notional_usd for slc in p.slices)
        assert abs(total_notional - p.total_notional_usd) < 1e-6

    def test_slice_schedules(self):
        sl = OrderSlicer(seed=17)
        for sched in ["twap", "vwap", "adaptive", "invalid_schedule"]:
            p = sl.slice_order("SOL", "buy", 300000.0, 50.0, "binance", schedule=sched, n_slices=3, idx=0)
            assert p.schedule in ("twap", "vwap", "adaptive")
            assert p.slice_count >= 1
            for slc in p.slices:
                assert math.isfinite(slc.notional_usd)
                assert math.isfinite(slc.qty)
                assert math.isfinite(slc.scheduled_offset_ms)
                assert slc.paper_only is True
                assert slc.symbol == "SOL"
                assert slc.venue == "binance"

    def test_slice_count_clamped(self):
        sl = OrderSlicer(seed=19)
        p_big = sl.slice_order("BTC", "buy", 10000000.0, 100.0, "deribit", schedule="twap", n_slices=100, idx=0)
        assert p_big.slice_count <= sl.config.max_slices
        p_small = sl.slice_order("BTC", "buy", 1000.0, 0.01, "deribit", schedule="twap", n_slices=0, idx=1)
        assert p_small.slice_count >= sl.config.min_slices

    def test_generate_report_structure(self):
        sl = OrderSlicer(seed=23)
        plans = [sl.slice_order("BTC", "buy", 500000.0, 5.0, "deribit", schedule="twap", n_slices=3, idx=i) for i in range(2)]
        rep = sl.generate_report(plans)
        assert rep["report"] == "PHASE22_ORDER_SLICING_REPORT"
        assert rep["plan_count"] == 2
        assert rep["total_slice_count"] == 6
        assert rep["paper_only"] is True
        assert math.isfinite(rep["summary"]["avg_slice_notional_usd"])
        json.dumps(rep)


class TestPhase22TCAPaperOnly:
    def test_paper_only_enforced(self):
        t = TCA(seed=1)
        assert t.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            TCA(config=TCAConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_make_trade_deterministic(self):
        t1 = TCA(seed=42)
        t2 = TCA(seed=42)
        tr1 = t1.make_trade("BTC", "deribit", "vol_arb", "buy", 100000.0, 1.0, 90000.0, 90010.0, 1.0, 0)
        tr2 = t2.make_trade("BTC", "deribit", "vol_arb", "buy", 100000.0, 1.0, 90000.0, 90010.0, 1.0, 0)
        assert tr1.trade_id == tr2.trade_id
        assert tr1.arrival_price == tr2.arrival_price
        assert tr1.fill_price == tr2.fill_price
        assert tr1.paper_only is True

    def test_make_trade_finite(self):
        t = TCA(seed=7)
        for i in range(5):
            tr = t.make_trade("ETH", "okx", "cross_asset_vol", "sell", 50000.0, 10.0, 3000.0, 2999.0, 2.0, i)
            assert math.isfinite(tr.notional_usd)
            assert math.isfinite(tr.qty)
            assert math.isfinite(tr.arrival_price)
            assert math.isfinite(tr.fill_price)
            assert math.isfinite(tr.spread_bps)

    def test_analyze_deterministic(self):
        t1 = TCA(seed=42)
        t2 = TCA(seed=42)
        tr = t1.make_trade("BTC", "deribit", "vol_arb", "buy", 100000.0, 1.0, 90000.0, 90010.0, 1.0, 0)
        r1 = t1.analyze(tr, 0)
        r2 = t2.analyze(tr, 0)
        assert r1.result_id == r2.result_id
        assert r1.total_cost_bps == r2.total_cost_bps
        assert r1.total_cost_usd == r2.total_cost_usd

    def test_analyze_ranges(self):
        t = TCA(seed=11)
        for i in range(10):
            tr = t.make_trade("BTC", "deribit", "vol_arb", "buy", 100000.0, 1.0, 90000.0, 90000.0 + i, float(i), i)
            res = t.analyze(tr, i)
            assert 0.0 <= res.total_cost_bps <= t.config.max_tca_bps
            assert math.isfinite(res.implementation_shortfall_bps)
            assert math.isfinite(res.slippage_bps)
            assert math.isfinite(res.spread_cost_bps)
            assert math.isfinite(res.timing_cost_bps)
            assert math.isfinite(res.total_cost_bps)
            assert math.isfinite(res.total_cost_usd)
            assert isinstance(res.within_budget, bool)

    def test_cost_usd_consistent(self):
        t = TCA(seed=13)
        tr = t.make_trade("BTC", "deribit", "vol_arb", "buy", 100000.0, 1.0, 90000.0, 90010.0, 1.0, 0)
        res = t.analyze(tr, 0)
        expected = tr.notional_usd * res.total_cost_bps / 10000.0
        assert abs(res.total_cost_usd - expected) < 1e-6

    def test_by_strategy_attribution(self):
        t = TCA(seed=17)
        trades = [t.make_trade("BTC", "deribit", "vol_arb", "buy", 100000.0, 1.0, 90000.0, 90005.0, 1.0, i) for i in range(3)]
        trades += [t.make_trade("ETH", "okx", "mm", "sell", 50000.0, 10.0, 3000.0, 2998.0, 2.0, i + 10) for i in range(3)]
        results = [t.analyze(tr, i) for i, tr in enumerate(trades)]
        rep = t.generate_report(trades, results)
        assert "vol_arb" in rep["summary"]["by_strategy"]
        assert "mm" in rep["summary"]["by_strategy"]
        assert "deribit" in rep["summary"]["by_venue"]
        assert "okx" in rep["summary"]["by_venue"]

    def test_generate_report_structure(self):
        t = TCA(seed=19)
        trades = [t.make_trade("BTC", "deribit", "vol_arb", "buy", 100000.0, 1.0, 90000.0, 90005.0, 1.0, i) for i in range(3)]
        results = [t.analyze(tr, i) for i, tr in enumerate(trades)]
        rep = t.generate_report(trades, results)
        assert rep["report"] == "PHASE22_TCA_REPORT"
        assert rep["trade_count"] == 3
        assert rep["result_count"] == 3
        assert rep["paper_only"] is True
        assert math.isfinite(rep["summary"]["avg_total_cost_bps"])
        assert math.isfinite(rep["summary"]["avg_total_cost_usd"])
        assert 0.0 <= rep["summary"]["within_budget_rate"] <= 1.0
        json.dumps(rep)


class TestPhase22CrossModuleIntegration:
    def test_router_to_slippage_chain(self):
        router = SmartOrderRouter(seed=42)
        slip = SlippageModel(seed=42)
        d = router.route("BTC", "buy", 200000.0, venues=["deribit", "okx"], idx=0)
        inp = slip.make_input("BTC", d.selected_venue, d.side, d.notional_usd, d.notional_usd / 50000.0, 90000.0, 1.0, 1000000.0, 0.3, 0)
        res = slip.estimate(inp, 0)
        assert math.isfinite(res.total_slippage_bps)
        assert res.symbol == "BTC"

    def test_filler_to_tca_chain(self):
        filler = FillPredictor(seed=42)
        tca = TCA(seed=42)
        sig = filler.make_signal("ETH", "binance", "sell", 10.0, 50000.0, 2.0, 500000.0, 15.0, True, 0)
        pred = filler.predict(sig, 0)
        tr = tca.make_trade("ETH", "binance", "orderflow_momentum", "sell", 50000.0, 10.0, 3000.0, pred.expected_fill_price, 2.0, 0)
        res = tca.analyze(tr, 0)
        assert math.isfinite(pred.expected_fill_price)
        assert math.isfinite(res.total_cost_bps)

    def test_slicer_plan_qty_matches(self):
        sl = OrderSlicer(seed=42)
        p = sl.slice_order("SOL", "buy", 600000.0, 120.0, "bybit", schedule="adaptive", n_slices=6, idx=0)
        total_qty = sum(slce.qty for slce in p.slices)
        assert abs(total_qty - p.total_qty) < 1e-6

    def test_all_modules_paper_only(self):
        assert SmartOrderRouter(seed=1).config.paper_only is True
        assert FillPredictor(seed=1).config.paper_only is True
        assert SlippageModel(seed=1).config.paper_only is True
        assert OrderSlicer(seed=1).config.paper_only is True
        assert TCA(seed=1).config.paper_only is True

    def test_all_reports_serializable(self):
        router = SmartOrderRouter(seed=42)
        filler = FillPredictor(seed=42)
        slip = SlippageModel(seed=42)
        slicer = OrderSlicer(seed=42)
        tca = TCA(seed=42)

        decs = [router.route("BTC", "buy", 100000.0, idx=i) for i in range(2)]
        sigs = [filler.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 1.0, 1000000.0, 10.0, True, i) for i in range(2)]
        preds = [filler.predict(s, i) for i, s in enumerate(sigs)]
        inputs = [slip.make_input("BTC", "deribit", "buy", 100000.0, 1.0, 90000.0, 1.0, 1000000.0, 0.2, i) for i in range(2)]
        sres = [slip.estimate(inp, i) for i, inp in enumerate(inputs)]
        plans = [slicer.slice_order("BTC", "buy", 100000.0, 1.0, "deribit", schedule="twap", n_slices=2, idx=i) for i in range(2)]
        trades = [tca.make_trade("BTC", "deribit", "vol_arb", "buy", 100000.0, 1.0, 90000.0, 90005.0, 1.0, i) for i in range(2)]
        tres = [tca.analyze(tr, i) for i, tr in enumerate(trades)]

        router.generate_report(decs)
        filler.generate_report(sigs, preds)
        slip.generate_report(inputs, sres)
        slicer.generate_report(plans)
        tca.generate_report(trades, tres)

    def test_router_slippage_fill_chain_full(self):
        router = SmartOrderRouter(seed=99)
        filler = FillPredictor(seed=99)
        slip = SlippageModel(seed=99)
        d = router.route("BTC", "buy", 300000.0, venues=["deribit", "okx", "binance"], idx=5)
        sig = filler.make_signal("BTC", d.selected_venue, d.side, d.notional_usd / 50000.0, d.notional_usd, 1.0, 2000000.0, d.expected_latency_ms, True, 5)
        pred = filler.predict(sig, 5)
        inp = slip.make_input("BTC", d.selected_venue, d.side, d.notional_usd, d.notional_usd / 50000.0, 90000.0, 1.0, 2000000.0, 0.4, 5)
        sres = slip.estimate(inp, 5)
        assert d.selected_venue == sig.venue
        assert math.isfinite(pred.fill_probability)
        assert math.isfinite(sres.total_slippage_bps)
        assert pred.expected_fill_price > 0
        assert sres.expected_fill_price > 0

    def test_slice_then_tca_cost(self):
        slicer = OrderSlicer(seed=77)
        tca = TCA(seed=77)
        p = slicer.slice_order("ETH", "buy", 400000.0, 150.0, "okx", schedule="twap", n_slices=4, idx=3)
        trades = [tca.make_trade("ETH", "okx", "vol_arb", "buy", slc.notional_usd, slc.qty, 3000.0, 3001.0, 1.5, i + 20) for i, slc in enumerate(p.slices)]
        results = [tca.analyze(tr, i + 20) for i, tr in enumerate(trades)]
        assert len(results) == p.slice_count
        total_cost_usd = sum(r.total_cost_usd for r in results)
        assert math.isfinite(total_cost_usd)
        assert total_cost_usd >= 0

    def test_different_seeds_produce_different_outputs(self):
        r_a = SmartOrderRouter(seed=1)
        r_b = SmartOrderRouter(seed=2)
        d_a = r_a.route("BTC", "buy", 100000.0, idx=0)
        d_b = r_b.route("BTC", "buy", 100000.0, idx=0)
        assert d_a.decision_id != d_b.decision_id or d_a.score != d_b.score

    def test_spread_impacts_fill_prob(self):
        filler = FillPredictor(seed=55)
        s_low = filler.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 0.5, 1000000.0, 10.0, True, 0)
        s_high = filler.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 4.0, 1000000.0, 10.0, True, 1)
        p_low = filler.predict(s_low, 0)
        p_high = filler.predict(s_high, 1)
        assert p_low.fill_probability >= p_high.fill_probability

    def test_latency_impacts_fill_time(self):
        filler = FillPredictor(seed=55)
        s_fast = filler.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 1.0, 1000000.0, 5.0, True, 0)
        s_slow = filler.make_signal("BTC", "deribit", "buy", 1.0, 100000.0, 1.0, 1000000.0, 40.0, True, 1)
        p_fast = filler.predict(s_fast, 0)
        p_slow = filler.predict(s_slow, 1)
        assert p_slow.expected_time_ms >= p_fast.expected_time_ms

    def test_notional_impacts_slippage(self):
        slip = SlippageModel(seed=66)
        i_small = slip.make_input("BTC", "deribit", "buy", 10000.0, 0.1, 90000.0, 1.0, 1000000.0, 0.2, 0)
        i_big = slip.make_input("BTC", "deribit", "buy", 1000000.0, 10.0, 90000.0, 1.0, 1000000.0, 0.2, 1)
        r_small = slip.estimate(i_small, 0)
        r_big = slip.estimate(i_big, 1)
        assert r_big.total_slippage_bps >= r_small.total_slippage_bps

    def test_tca_cost_scales_with_notional(self):
        tca = TCA(seed=88)
        tr_small = tca.make_trade("BTC", "deribit", "vol_arb", "buy", 10000.0, 0.1, 90000.0, 90001.0, 1.0, 0)
        tr_big = tca.make_trade("BTC", "deribit", "vol_arb", "buy", 1000000.0, 10.0, 90000.0, 90010.0, 1.0, 1)
        r_small = tca.analyze(tr_small, 0)
        r_big = tca.analyze(tr_big, 1)
        assert r_big.total_cost_usd >= r_small.total_cost_usd

    def test_router_selected_venue_in_venues(self):
        router = SmartOrderRouter(seed=3)
        d = router.route("BTC", "buy", 100000.0, venues=["deribit", "okx", "binance"], idx=0)
        assert d.selected_venue in {"deribit", "okx", "binance"}

    def test_fill_expected_qty_le_qty(self):
        filler = FillPredictor(seed=33)
        sig = filler.make_signal("BTC", "deribit", "buy", 10.0, 100000.0, 1.0, 1000000.0, 10.0, True, 0)
        pred = filler.predict(sig, 0)
        assert 0.0 <= pred.expected_fill_qty <= sig.qty

    def test_slippage_within_limit_flag_consistent(self):
        slip = SlippageModel(seed=44)
        tight = slip.make_input("BTC", "deribit", "buy", 100000.0, 1.0, 90000.0, 0.5, 5000000.0, 0.1, 0)
        loose = slip.make_input("BTC", "deribit", "buy", 5000000.0, 50.0, 90000.0, 4.0, 50000.0, 0.9, 1)
        rt = slip.estimate(tight, 0)
        rl = slip.estimate(loose, 1)
        assert (rt.within_limit and rt.total_slippage_bps <= slip.config.max_slippage_bps) or not rt.within_limit
        assert (rl.within_limit and rl.total_slippage_bps <= slip.config.max_slippage_bps) or not rl.within_limit
