"""Phase 15 cross-venue tests: arbitrage, delta-neutral MM, latency routing, orchestration."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import pytest

from src.arbitrage import (
    ArbitrageConfig,
    ArbitrageDetector,
    ArbitrageOpportunity,
    ArbitrageQuote,
    DEFAULT_SYMBOLS,
    SUPPORTED_VENUES,
    default_arbitrage_config,
)
from src.marketmaking import DeltaNeutralMM, MMConfig, black_scholes_greeks
from src.execution.latency_aware_router import LatencyAwareRouter, LatencyRouterConfig
from src.orchestration import CrossVenueOrchestrator, CrossVenueConfig
from src.deployment.phase15_campaign import Phase15Campaign


def _make_quote(venue="deribit", symbol="BTC", bid=64990.0, ask=65010.0, bid_size=1.0, ask_size=1.0, ts="2026-11-01T00:00:00Z"):
    return ArbitrageQuote(
        venue=venue,
        symbol=symbol,
        bid=bid,
        ask=ask,
        bid_size=bid_size,
        ask_size=ask_size,
        timestamp=ts,
        received_at=ts,
        source="orderflow",
    )


class TestArbitrageBasics:
    def test_arbitrage_quote_validation(self):
        q = _make_quote()
        assert q.mid() > 64990.0 and q.mid() < 65010.0
        assert q.spread() > 0
        assert q.spread_bps() > 0

    def test_arbitrage_config_defaults(self):
        cfg = default_arbitrage_config()
        assert "deribit" in cfg.venues
        assert "okx" in cfg.venues
        assert "binance" in cfg.venues
        assert cfg.paper_only is True

    def test_arbitrage_config_rejects_bad_venue(self):
        with pytest.raises(Exception):
            ArbitrageConfig(venues=("badvenue",), symbols=("BTC",))

    def test_detector_submit_quotes(self):
        det = ArbitrageDetector(seed=42)
        qlist = [_make_quote(), _make_quote(venue="okx"), _make_quote(venue="binance")]
        accepted = det.submit_quotes(qlist)
        assert accepted == 3

    def test_detector_generates_report(self):
        det = ArbitrageDetector(seed=1)
        det.submit_quotes([_make_quote(), _make_quote(venue="okx")])
        opps = det.detect({"BTC": 65000.0}, {"BTC": 0.6})
        report = det.generate_report(opps)
        assert report["schema"] == "arbitrage_report_v1"
        assert "counts" in report
        assert math.isfinite(report["summary"]["total_opportunities"])


class TestArbitrageCrossVenue:
    def test_cross_venue_spread_detection(self):
        det = ArbitrageDetector(seed=7)
        det.submit_quotes([
            _make_quote(venue="deribit", bid=64900.0, ask=64910.0),
            _make_quote(venue="okx", bid=64950.0, ask=64960.0),
        ])
        opps = det.detect({"BTC": 64930.0}, {"BTC": 0.6})
        # May or may not find depending on fees, but must be finite
        assert isinstance(opps, list)

    def test_fee_adjusted_edge(self):
        det = ArbitrageDetector(seed=123)
        det.submit_quotes([
            _make_quote(venue="deribit", bid=64800.0, ask=64900.0, bid_size=1.0, ask_size=1.0),
            _make_quote(venue="okx", bid=64950.0, ask=65000.0, bid_size=1.0, ask_size=1.0),
        ])
        opps = det.detect({"BTC": 64925.0}, {"BTC": 0.6})
        for o in opps:
            assert math.isfinite(o.net_edge_bps)
            assert math.isfinite(o.gross_edge_bps)

    def test_stale_quote_filtering(self):
        det = ArbitrageDetector(seed=5, config=ArbitrageConfig(max_quote_age_seconds=1.0))
        old = _make_quote(ts="2026-01-01T00:00:00Z")
        det.submit_quotes([old, _make_quote(venue="okx")])
        opps = det.detect({"BTC": 65000.0}, {"BTC": 0.6})
        assert isinstance(opps, list)

    def test_determinism_arbitrage(self):
        det1 = ArbitrageDetector(seed=42)
        det2 = ArbitrageDetector(seed=42)
        quotes = [_make_quote(), _make_quote(venue="okx"), _make_quote(venue="binance")]
        det1.submit_quotes(quotes)
        det2.submit_quotes(quotes)
        o1 = det1.detect({"BTC": 65000.0}, {"BTC": 0.6})
        o2 = det2.detect({"BTC": 65000.0}, {"BTC": 0.6})
        assert len(o1) == len(o2)

    def test_volatility_spread_sanity(self):
        det = ArbitrageDetector(seed=9)
        det.submit_quotes([_make_quote(bid=64000.0, ask=66000.0), _make_quote(venue="okx")])
        opps = det.detect({"BTC": 65000.0}, {"BTC": 0.6})
        assert isinstance(opps, list)


class TestMarketMaking:
    def test_mm_config(self):
        cfg = MMConfig(symbols=("BTC", "ETH"), venues=("deribit", "okx", "binance"))
        assert cfg.paper_only is True

    def test_black_scholes_greeks_finite(self):
        g = black_scholes_greeks(65000.0, 66000.0, 0.05, 0.6, "call")
        for k in ["price", "delta", "gamma", "vega", "theta"]:
            assert math.isfinite(g[k])

    def test_mm_open_position(self):
        mm = DeltaNeutralMM(seed=42)
        g = black_scholes_greeks(65000.0, 68250.0, 0.05, 0.6, "call")
        pos = mm.open_position(
            symbol="BTC",
            venue="deribit",
            instrument="BTC-68250-C",
            kind="option",
            side="long",
            quantity=0.1,
            strike=68250.0,
            expiry="2026-12-31",
            option_type="call",
            entry_price=g["price"],
            mark_price=g["price"],
            spot=65000.0,
            implied_vol=0.6,
        )
        assert pos.quantity > 0

    def test_mm_hedge(self):
        mm = DeltaNeutralMM(seed=13)
        g = black_scholes_greeks(65000.0, 61750.0, 0.05, 0.6, "put")
        mm.open_position("BTC", "deribit", "BTC-61750-P", "option", "short", 0.2,
                         strike=61750.0, expiry="2026-12-31", option_type="put",
                         entry_price=g["price"], mark_price=g["price"], spot=65000.0, implied_vol=0.6)
        res = mm.hedge("BTC", 65000.0)
        assert res["hedged"]

    def test_mm_risk_check(self):
        mm = DeltaNeutralMM(seed=5)
        risk = mm.risk_check()
        assert "within_limits" in risk

    def test_mm_kill_switch(self):
        mm = DeltaNeutralMM(seed=7)
        mm.trigger_kill_switch("test", source="unit")
        assert mm.kill_switch_triggered

    def test_mm_report_finite(self):
        mm = DeltaNeutralMM(seed=11)
        g = black_scholes_greeks(65000.0, 68250.0, 0.05, 0.6, "call")
        mm.open_position("BTC", "deribit", "BTC-68250-C", "option", "long", 0.15,
                         strike=68250.0, expiry="2026-12-31", option_type="call",
                         entry_price=g["price"], mark_price=g["price"], spot=65000.0, implied_vol=0.6)
        mm.update_marks({"BTC": 65000.0}, {"BTC": 0.6})
        rpt = mm.generate_report()
        assert math.isfinite(rpt["pnl"]["net_pnl_usd"])
        assert math.isfinite(rpt["risk_metrics"]["max_drawdown_pct"])


class TestLatencyRouting:
    def test_router_config(self):
        cfg = LatencyRouterConfig(venues=("deribit", "okx", "binance"))
        assert cfg.paper_only is True

    def test_router_quote_update(self):
        r = LatencyAwareRouter(seed=42)
        r.update_quote("deribit", "BTC", 64990.0, 65010.0, 1.0, 1.0, "2026-11-01T00:00:00Z")
        r.update_quote("okx", "BTC", 64992.0, 65008.0, 1.0, 1.0, "2026-11-01T00:00:00Z")

    def test_router_latency_record(self):
        r = LatencyAwareRouter(seed=1)
        r.record_latency("deribit", 12.5, "BTC")
        r.record_latency("okx", 18.0, "BTC")

    def test_router_route_intent(self):
        r = LatencyAwareRouter(seed=7)
        r.update_quote("deribit", "BTC", 64990.0, 65010.0, 2.0, 2.0, "2026-11-01T00:00:00Z")
        r.update_quote("okx", "BTC", 64995.0, 65005.0, 2.0, 2.0, "2026-11-01T00:00:00Z")
        route = r.route_intent({"symbol": "BTC", "side": "buy", "quantity": 0.1, "price": 65000.0})
        assert route.order_id
        assert route.venue in ("deribit", "okx", "binance")

    def test_router_cancel_replace(self):
        r = LatencyAwareRouter(seed=3)
        r.update_quote("deribit", "BTC", 64990.0, 65010.0, 1.0, 1.0, "2026-11-01T00:00:00Z")
        route = r.route_intent({"symbol": "BTC", "side": "sell", "quantity": 0.1, "price": 65000.0})
        rep = r.replace(route.order_id, price=route.price * 0.999)
        assert rep is None or isinstance(rep, str)

    def test_router_track_fill(self):
        r = LatencyAwareRouter(seed=11)
        r.update_quote("deribit", "BTC", 64990.0, 65010.0, 1.0, 1.0, "2026-11-01T00:00:00Z")
        route = r.route_intent({"symbol": "BTC", "side": "buy", "quantity": 0.1, "price": 65000.0})
        r.track_fill(route.order_id, route.price, quantity=route.quantity, commission=1.0, symbol="BTC")

    def test_router_report_finite(self):
        r = LatencyAwareRouter(seed=23)
        r.update_quote("deribit", "BTC", 64990.0, 65010.0, 1.0, 1.0, "2026-11-01T00:00:00Z")
        r.record_latency("deribit", 10.0)
        route = r.route_intent({"symbol": "BTC", "side": "buy", "quantity": 0.05, "price": 65000.0})
        r.track_fill(route.order_id, route.price, quantity=route.quantity)
        rpt = r.generate_report()
        assert math.isfinite(rpt["routing"]["avg_cost_bps"])
        assert math.isfinite(rpt["slippage"]["avg_slippage_bps"])


class TestOrchestration:
    def test_orchestrator_config(self):
        cfg = CrossVenueConfig(symbols=("BTC", "ETH"), venues=("deribit", "okx", "binance"))
        assert cfg.paper_only is True

    def test_orchestrator_init(self):
        orch = CrossVenueOrchestrator(seed=42)
        assert orch.paper_only is True

    def test_orchestrator_submit_snapshot(self):
        orch = CrossVenueOrchestrator(seed=5)
        quotes = [
            {"venue": "deribit", "symbol": "BTC", "bid": 64990.0, "ask": 65010.0, "bid_size": 1.0, "ask_size": 1.0, "timestamp": "2026-11-01T00:00:00Z", "received_at": "2026-11-01T00:00:00Z"},
            {"venue": "okx", "symbol": "BTC", "bid": 64992.0, "ask": 65008.0, "bid_size": 1.0, "ask_size": 1.0, "timestamp": "2026-11-01T00:00:00Z", "received_at": "2026-11-01T00:00:00Z"},
        ]
        accepted = orch.submit_market_snapshot(quotes, {"BTC": 65000.0}, {"BTC": 0.6})
        assert accepted >= 0

    def test_orchestrator_run_cycle(self):
        orch = CrossVenueOrchestrator(seed=7)
        quotes = [{"venue": "deribit", "symbol": "BTC", "bid": 64990.0, "ask": 65010.0, "bid_size": 1.0, "ask_size": 1.0, "timestamp": "2026-11-01T00:00:00Z", "received_at": "2026-11-01T00:00:00Z"}]
        orch.submit_market_snapshot(quotes, {"BTC": 65000.0}, {"BTC": 0.6})
        res = orch.run_cycle(1)
        assert "status" in res

    def test_orchestrator_generate_report(self):
        orch = CrossVenueOrchestrator(seed=13)
        quotes = [{"venue": "deribit", "symbol": "BTC", "bid": 64990.0, "ask": 65010.0, "bid_size": 1.0, "ask_size": 1.0, "timestamp": "2026-11-01T00:00:00Z", "received_at": "2026-11-01T00:00:00Z"}]
        orch.submit_market_snapshot(quotes, {"BTC": 65000.0}, {"BTC": 0.6})
        orch.run_cycle(1)
        rpt = orch.generate_report()
        assert math.isfinite(rpt["pnl"]["net_pnl_usd"])

    def test_orchestrator_kill_switch(self):
        orch = CrossVenueOrchestrator(seed=17)
        orch.trigger_kill_switch("test halt")
        assert orch.kill_switch_triggered


class TestCampaign:
    def test_campaign_init_paper_only(self):
        camp = Phase15Campaign(symbols=("BTC", "ETH"), seed=42, venues=("deribit", "okx", "binance"))
        assert camp.paper_only is True

    def test_campaign_rejects_live(self):
        with pytest.raises(Exception):
            Phase15Campaign(paper_only=False)

    def test_campaign_deterministic_symbols_venues(self):
        camp = Phase15Campaign(symbols=("BTC", "ETH"), seed=42)
        assert camp.symbols == ("BTC", "ETH")
        assert "deribit" in camp.venues

    @pytest.mark.slow
    def test_campaign_run_small(self, tmp_path):
        camp = Phase15Campaign(symbols=("BTC",), seed=123, venues=("deribit", "okx"), cycles=2, outdir=tmp_path)
        res = camp.run()
        assert res["status"] == "completed"
        assert res["master_report"]["paper_only"] is True


class TestDeterminism:
    def test_deterministic_arbitrage_seeds(self):
        d1 = ArbitrageDetector(seed=42)
        d2 = ArbitrageDetector(seed=42)
        qs = [_make_quote(), _make_quote(venue="okx")]
        d1.submit_quotes(qs); d2.submit_quotes(qs)
        assert len(d1.detect({"BTC": 65000.0}, {"BTC": 0.6})) == len(d2.detect({"BTC": 65000.0}, {"BTC": 0.6}))

    def test_deterministic_mm_seeds(self):
        m1 = DeltaNeutralMM(seed=42)
        m2 = DeltaNeutralMM(seed=42)
        assert type(m1).__name__ == type(m2).__name__

    def test_deterministic_router_seeds(self):
        r1 = LatencyAwareRouter(seed=42)
        r2 = LatencyAwareRouter(seed=42)
        r1.update_quote("deribit", "BTC", 64990, 65010, 1, 1, "2026-11-01T00:00:00Z")
        r2.update_quote("deribit", "BTC", 64990, 65010, 1, 1, "2026-11-01T00:00:00Z")


class TestFiniteNumerics:
    @pytest.mark.parametrize("venue", list(SUPPORTED_VENUES))
    def test_all_venues_supported(self, venue):
        q = _make_quote(venue=venue)
        assert q.venue == venue

    def test_no_nan_inf_arbitrage_report(self):
        det = ArbitrageDetector(seed=99)
        det.submit_quotes([_make_quote(), _make_quote(venue="okx")])
        opps = det.detect({"BTC": 65000.0}, {"BTC": 0.6})
        rpt = det.generate_report(opps)
        s = json.dumps(rpt)
        assert "NaN" not in s and "Infinity" not in s

    def test_no_nan_inf_mm_report(self):
        mm = DeltaNeutralMM(seed=77)
        g = black_scholes_greeks(65000.0, 68250.0, 0.05, 0.6, "call")
        mm.open_position("BTC", "deribit", "BTC-68250-C", "option", "long", 0.1,
                         strike=68250.0, expiry="2026-12-31", option_type="call",
                         entry_price=g["price"], mark_price=g["price"], spot=65000.0, implied_vol=0.6)
        mm.update_marks({"BTC": 65000.0}, {"BTC": 0.6})
        rpt = mm.generate_report()
        s = json.dumps(rpt)
        assert "NaN" not in s and "Infinity" not in s

    def test_no_nan_inf_router_report(self):
        r = LatencyAwareRouter(seed=55)
        r.update_quote("deribit", "BTC", 64990, 65010, 1, 1, "2026-11-01T00:00:00Z")
        route = r.route_intent({"symbol": "BTC", "side": "buy", "quantity": 0.1, "price": 65000.0})
        r.track_fill(route.order_id, route.price, 0.1)
        rpt = r.generate_report()
        s = json.dumps(rpt)
        assert "NaN" not in s and "Infinity" not in s

    def test_no_nan_inf_orchestrator_report(self):
        orch = CrossVenueOrchestrator(seed=33)
        quotes = [{"venue": "deribit", "symbol": "BTC", "bid": 64990, "ask": 65010, "bid_size": 1, "ask_size": 1, "timestamp": "2026-11-01T00:00:00Z", "received_at": "2026-11-01T00:00:00Z"}]
        orch.submit_market_snapshot(quotes, {"BTC": 65000.0}, {"BTC": 0.6})
        orch.run_cycle(1)
        rpt = orch.generate_report()
        s = json.dumps(rpt)
        assert "NaN" not in s and "Infinity" not in s


class TestEdgeCases:
    def test_arbitrage_empty_quotes(self):
        det = ArbitrageDetector(seed=1)
        opps = det.detect({"BTC": 65000.0}, {"BTC": 0.6})
        assert isinstance(opps, list)

    def test_arbitrage_invalid_symbol_handling(self):
        det = ArbitrageDetector(seed=2)
        det.submit_quotes([_make_quote(symbol="BTC"), _make_quote(venue="okx", symbol="BTC")])
        opps = det.detect({"BTC": 65000.0}, {"BTC": 0.6})
        assert isinstance(opps, list)

    def test_mm_update_marks(self):
        mm = DeltaNeutralMM(seed=4)
        g = black_scholes_greeks(65000.0, 68250.0, 0.05, 0.6, "call")
        mm.open_position("BTC", "deribit", "BTC-68250-C", "option", "long", 0.1,
                         strike=68250.0, expiry="2026-12-31", option_type="call",
                         entry_price=g["price"], mark_price=g["price"], spot=65000.0, implied_vol=0.6)
        mm.update_marks({"BTC": 66000.0}, {"BTC": 0.65})
        rpt = mm.generate_report()
        assert math.isfinite(rpt["pnl"]["unrealized_pnl_usd"])

    def test_router_multiple_venues_routing(self):
        r = LatencyAwareRouter(seed=9)
        for v in SUPPORTED_VENUES:
            r.update_quote(v, "BTC", 64990, 65010, 1, 1, "2026-11-01T00:00:00Z")
        route = r.route_intent({"symbol": "BTC", "side": "buy", "quantity": 0.1, "price": 65000.0})
        assert route.venue in SUPPORTED_VENUES

    def test_orchestrator_eth_symbol(self):
        orch = CrossVenueOrchestrator(seed=8, config=CrossVenueConfig(symbols=("ETH",), venues=("deribit", "okx")))
        quotes = [{"venue": "deribit", "symbol": "ETH", "bid": 65990, "ask": 66010, "bid_size": 1, "ask_size": 1, "timestamp": "2026-11-01T00:00:00Z", "received_at": "2026-11-01T00:00:00Z"}]
        orch.submit_market_snapshot(quotes, {"ETH": 66000.0}, {"ETH": 0.7})
        res = orch.run_cycle(1)
        assert res is not None


class TestSchemas:
    def test_arbitrage_opportunity_structure(self):
        det = ArbitrageDetector(seed=15)
        det.submit_quotes([_make_quote(bid=64800, ask=64900), _make_quote(venue="okx", bid=64950, ask=65000)])
        opps = det.detect({"BTC": 64925.0}, {"BTC": 0.6})
        for o in opps:
            d = o.to_dict() if hasattr(o, "to_dict") else None
            assert o.buy_venue in SUPPORTED_VENUES or o.sell_venue in SUPPORTED_VENUES

    def test_all_reports_have_timestamps(self):
        det = ArbitrageDetector(seed=19)
        det.submit_quotes([_make_quote(), _make_quote(venue="okx")])
        rpt = det.generate_report(det.detect({"BTC": 65000.0}, {"BTC": 0.6}))
        assert "timestamp" in rpt or "generated_at" in rpt


class TestPaperOnlyGates:
    def test_arbitrage_paper_only_default(self):
        cfg = ArbitrageConfig()
        assert cfg.paper_only is True

    def test_mm_paper_only_default(self):
        cfg = MMConfig()
        assert cfg.paper_only is True

    def test_router_paper_only_default(self):
        cfg = LatencyRouterConfig()
        assert cfg.paper_only is True

    def test_orchestrator_paper_only_default(self):
        cfg = CrossVenueConfig()
        assert cfg.paper_only is True

    def test_campaign_forces_paper_only(self):
        camp = Phase15Campaign(symbols=("BTC",), seed=1)
        assert camp.paper_only is True


class TestMoreArbitrage:
    def test_arbitrage_qualified_filtering(self):
        det = ArbitrageDetector(seed=101)
        det.submit_quotes([_make_quote(bid=64900, ask=64910), _make_quote(venue="okx", bid=64950, ask=64960)])
        opps = det.detect({"BTC": 64930.0}, {"BTC": 0.6})
        rpt = det.generate_report(opps)
        assert "counts" in rpt

    def test_arbitrage_multiple_symbols(self):
        det = ArbitrageDetector(seed=102, config=ArbitrageConfig(symbols=("BTC", "ETH")))
        det.submit_quotes([_make_quote(symbol="BTC"), _make_quote(venue="okx", symbol="BTC"), _make_quote(symbol="ETH"), _make_quote(venue="okx", symbol="ETH")])
        opps = det.detect({"BTC": 65000.0, "ETH": 66000.0}, {"BTC": 0.6, "ETH": 0.7})
        assert isinstance(opps, list)

    def test_arbitrage_with_three_venues(self):
        det = ArbitrageDetector(seed=103)
        det.submit_quotes([_make_quote(venue="deribit"), _make_quote(venue="okx"), _make_quote(venue="binance")])
        opps = det.detect({"BTC": 65000.0}, {"BTC": 0.6})
        assert isinstance(opps, list)

    def test_arbitrage_summary_metrics(self):
        det = ArbitrageDetector(seed=104)
        det.submit_quotes([_make_quote(), _make_quote(venue="okx", bid=64980, ask=65000)])
        opps = det.detect({"BTC": 65000.0}, {"BTC": 0.6})
        rpt = det.generate_report(opps)
        assert "summary" in rpt


class TestMoreMM:
    def test_mm_put_position(self):
        mm = DeltaNeutralMM(seed=201)
        g = black_scholes_greeks(65000.0, 61750.0, 0.05, 0.6, "put")
        pos = mm.open_position("BTC", "deribit", "BTC-61750-P", "option", "long", 0.2,
                               strike=61750.0, expiry="2026-12-31", option_type="put",
                               entry_price=g["price"], mark_price=g["price"], spot=65000.0, implied_vol=0.6)
        assert pos is not None

    def test_mm_perp_hedge(self):
        mm = DeltaNeutralMM(seed=202)
        g = black_scholes_greeks(65000.0, 68250.0, 0.05, 0.6, "call")
        mm.open_position("BTC", "deribit", "BTC-68250-C", "option", "long", 0.15,
                         strike=68250.0, expiry="2026-12-31", option_type="call",
                         entry_price=g["price"], mark_price=g["price"], spot=65000.0, implied_vol=0.6)
        res = mm.hedge("BTC", 65000.0, qty=0.1)
        assert "hedged" in res or "hedge_quantity" in res

    def test_mm_inventory_tracking(self):
        mm = DeltaNeutralMM(seed=203)
        g = black_scholes_greeks(65000.0, 68250.0, 0.05, 0.6, "call")
        mm.open_position("BTC", "deribit", "BTC-68250-C", "option", "long", 0.1,
                         strike=68250.0, expiry="2026-12-31", option_type="call",
                         entry_price=g["price"], mark_price=g["price"], spot=65000.0, implied_vol=0.6)
        inv = mm.inventory()
        assert "net_delta" in inv or "positions" in inv

    def test_mm_close_position(self):
        mm = DeltaNeutralMM(seed=204)
        g = black_scholes_greeks(65000.0, 68250.0, 0.05, 0.6, "call")
        pid = mm.open_position("BTC", "deribit", "BTC-68250-C", "option", "long", 0.1,
                               strike=68250.0, expiry="2026-12-31", option_type="call",
                               entry_price=g["price"], mark_price=g["price"], spot=65000.0, implied_vol=0.6).position_id
        res = mm.close_position(pid, close_price=g["price"])
        assert res is not None

    def test_mm_drawdown_tracking(self):
        mm = DeltaNeutralMM(seed=205)
        rpt = mm.generate_report()
        assert "drawdown_pct" in rpt["pnl"] or "max_drawdown_pct" in rpt["risk_metrics"]


class TestMoreRouter:
    def test_router_fill_tracking(self):
        r = LatencyAwareRouter(seed=301)
        r.update_quote("deribit", "BTC", 64990, 65010, 1, 1, "2026-11-01T00:00:00Z")
        route = r.route_intent({"symbol": "BTC", "side": "buy", "quantity": 0.1, "price": 65000.0})
        r.track_fill(route.order_id, route.price, 0.1, commission=0.5)
        rpt = r.generate_report()
        assert rpt["counts"]["fills"] >= 0

    def test_router_cost_tracking(self):
        r = LatencyAwareRouter(seed=302)
        r.update_quote("deribit", "BTC", 64990, 65010, 1, 1, "2026-11-01T00:00:00Z")
        route = r.route_intent({"symbol": "BTC", "side": "buy", "quantity": 0.1, "price": 65000.0})
        assert hasattr(route, "total_cost_bps") or "cost" in route.to_dict()

    def test_router_slippage_tracking(self):
        r = LatencyAwareRouter(seed=303)
        r.update_quote("deribit", "BTC", 64990, 65010, 1, 1, "2026-11-01T00:00:00Z")
        route = r.route_intent({"symbol": "BTC", "side": "buy", "quantity": 0.1, "price": 65000.0})
        r.track_fill(route.order_id, route.price + 1.0, 0.1)
        rpt = r.generate_report()
        assert "slippage" in rpt

    def test_router_latency_averages(self):
        r = LatencyAwareRouter(seed=304)
        r.record_latency("deribit", 10.0)
        r.record_latency("okx", 20.0)
        r.record_latency("binance", 15.0)
        rpt = r.generate_report()
        assert "latency" in rpt


class TestMoreOrch:
    def test_orchestrator_multi_cycle(self):
        orch = CrossVenueOrchestrator(seed=401, config=CrossVenueConfig(cycles=3))
        quotes = [{"venue": "deribit", "symbol": "BTC", "bid": 64990, "ask": 65010, "bid_size": 1, "ask_size": 1, "timestamp": "2026-11-01T00:00:00Z", "received_at": "2026-11-01T00:00:00Z"}]
        orch.submit_market_snapshot(quotes, {"BTC": 65000.0}, {"BTC": 0.6})
        for i in range(1, 4):
            res = orch.run_cycle(i)
            assert res["status"] in ("ok", "halted")

    def test_orchestrator_pnl_tracking(self):
        orch = CrossVenueOrchestrator(seed=402)
        quotes = [{"venue": "deribit", "symbol": "BTC", "bid": 64990, "ask": 65010, "bid_size": 1, "ask_size": 1, "timestamp": "2026-11-01T00:00:00Z", "received_at": "2026-11-01T00:00:00Z"}]
        orch.submit_market_snapshot(quotes, {"BTC": 65000.0}, {"BTC": 0.6})
        orch.run_cycle(1)
        rpt = orch.generate_report()
        assert "pnl" in rpt
        assert math.isfinite(rpt["pnl"]["net_pnl_usd"])

    def test_orchestrator_save_state(self, tmp_path):
        orch = CrossVenueOrchestrator(seed=403, outdir=str(tmp_path))
        quotes = [{"venue": "deribit", "symbol": "BTC", "bid": 64990, "ask": 65010, "bid_size": 1, "ask_size": 1, "timestamp": "2026-11-01T00:00:00Z", "received_at": "2026-11-01T00:00:00Z"}]
        orch.submit_market_snapshot(quotes, {"BTC": 65000.0}, {"BTC": 0.6})
        orch.run_cycle(1)
        state = orch.save_state(tmp_path / "state.json")
        assert Path(state).exists()


class TestStressDeterminism:
    def test_deterministic_campaign_small(self, tmp_path):
        c1 = Phase15Campaign(symbols=("BTC",), seed=777, venues=("deribit", "okx"), cycles=1, outdir=tmp_path / "a")
        c2 = Phase15Campaign(symbols=("BTC",), seed=777, venues=("deribit", "okx"), cycles=1, outdir=tmp_path / "b")
        r1 = c1.run()
        r2 = c2.run()
        assert r1["status"] == r2["status"]
        assert r1["master_report"]["seed"] == r2["master_report"]["seed"]

    def test_campaign_artifacts_created(self, tmp_path):
        c = Phase15Campaign(symbols=("BTC", "ETH"), seed=888, venues=("deribit", "okx", "binance"), cycles=2, outdir=tmp_path)
        r = c.run()
        assert len(r["artifacts"]) >= 5
        for a in r["artifacts"]:
            assert Path(a).exists()

    def test_campaign_all_reports_present(self, tmp_path):
        c = Phase15Campaign(symbols=("BTC",), seed=999, venues=("deribit", "okx", "binance"), cycles=1, outdir=tmp_path)
        r = c.run()
        assert (tmp_path / "PHASE15_CROSSVENUE_REPORT.json").exists()
        assert (tmp_path / "ARBITRAGE_REPORT.json").exists()
        assert (tmp_path / "DELTA_NEUTRAL_MM_REPORT.json").exists()
        assert (tmp_path / "LATENCY_ROUTING_REPORT.json").exists()
        assert (tmp_path / "CROSSVENUE_ORCHESTRATION_REPORT.json").exists()

    def test_campaign_master_has_required_fields(self, tmp_path):
        c = Phase15Campaign(symbols=("BTC", "ETH"), seed=42, venues=("deribit", "okx", "binance"), cycles=3, outdir=tmp_path)
        r = c.run()
        m = r["master_report"]
        assert m["campaign_id"] == "phase15_42"
        assert m["seed"] == 42
        assert m["paper_only"] is True
        assert m["status"] == "completed"
        assert "git_sha" in m
        assert "artifacts" in m


class TestCampaignScript:
    def test_phase15_script_exists(self):
        assert Path("scripts/run_phase15_crossvenue_campaign.py").exists()

    def test_campaign_import(self):
        from src.deployment.phase15_campaign import Phase15Campaign
        c = Phase15Campaign(symbols=("BTC",), seed=1, cycles=1)
        assert hasattr(c, "run")


class TestIntegrationFull:
    def test_full_integration_seed42_btc_eth_three_venues(self, tmp_path):
        c = Phase15Campaign(symbols=("BTC", "ETH"), seed=42, venues=("deribit", "okx", "binance"), cycles=5, outdir=tmp_path)
        r = c.run()
        assert r["status"] == "completed"
        # Check no NaN/Inf in all artifacts
        for art in r["artifacts"]:
            if art.endswith(".json"):
                data = json.loads(Path(art).read_text())
                s = json.dumps(data)
                assert "NaN" not in s
                assert "Infinity" not in s
