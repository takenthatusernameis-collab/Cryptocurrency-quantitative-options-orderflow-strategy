import math
from src.orderflow.phase37_venue_liquidity_sourcing import VenueLiquiditySourcing, SourcingConfig
from src.routing.phase37_cross_venue_delta_neutral_router import CrossVenueDeltaNeutralRouter, RouterConfig
from src.integration.phase37_orderflow_routing_loop import Loop37Config, Phase37OrderflowRoutingLoop


def test_phase37_sourcing_basic():
    s = VenueLiquiditySourcing(SourcingConfig(seed=1))
    res = s.scan(["deribit", "okx", "bybit"], orderflow_imbalance=0.1)
    assert res.ok
    assert len(res.sources) == 3
    assert all(math.isfinite(x.score) for x in res.sources)


def test_phase37_sourcing_stress():
    s = VenueLiquiditySourcing(SourcingConfig(seed=2))
    res = s.scan(["deribit", "okx"], orderflow_imbalance=0.5, depth_scale=0.8)
    assert res.ok
    assert math.isfinite(res.metrics["total_depth_usd"])


def test_phase37_sourcing_top_venues():
    s = VenueLiquiditySourcing(SourcingConfig(seed=3))
    res = s.scan(["deribit", "okx", "bybit", "binance"], orderflow_imbalance=0.0)
    assert len(res.top_venues) >= 1


def test_phase37_sourcing_finite():
    s = VenueLiquiditySourcing(SourcingConfig(seed=4))
    res = s.scan(["deribit"], orderflow_imbalance=0.2)
    for x in res.sources:
        assert math.isfinite(x.bid_depth_usd) and math.isfinite(x.ask_depth_usd)
        assert x.bid_depth_usd > 0 and x.ask_depth_usd > 0


def test_phase37_router_basic():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=5))
    plan = r.route(target_qty=0.1, spot=50000, venues=["deribit", "okx"], regime="normal", stress_score=1.0)
    assert plan.ok
    assert len(plan.orders) >= 1
    assert plan.total_notional > 0


def test_phase37_router_sell():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=6))
    plan = r.route(target_qty=-0.05, spot=50000, venues=["deribit", "bybit"], regime="stressed", stress_score=3.0)
    assert plan.ok
    assert all(o.side == "sell" for o in plan.orders)


def test_phase37_router_crisis():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=7))
    plan = r.route(target_qty=0.2, spot=50000, venues=["deribit", "okx", "bybit"], regime="crisis", stress_score=9.0)
    assert plan.ok
    assert math.isfinite(plan.total_notional)


def test_phase37_router_zero():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=8))
    plan = r.route(target_qty=0.0, spot=50000, venues=["deribit"])
    assert plan.ok
    assert len(plan.orders) == 0


def test_phase37_router_finite_all():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=9))
    plan = r.route(target_qty=0.15, spot=50000, venues=["deribit", "okx"], regime="stressed", stress_score=4.0)
    for o in plan.orders:
        assert math.isfinite(o.qty) and math.isfinite(o.notional_usd) and math.isfinite(o.slippage_bps)
    assert math.isfinite(plan.net_delta_est)


def test_phase37_router_multi_venue_split():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=10))
    plan = r.route(target_qty=0.3, spot=50000, venues=["deribit", "okx", "bybit"], regime="normal", stress_score=2.0)
    assert len(plan.orders) >= 1


def test_phase37_loop_paper_btc():
    cfg = Loop37Config(symbols=["BTC-USD"], venues=["deribit", "okx"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=10, seed=101, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["n_cycles"] == 10


def test_phase37_loop_paper_eth():
    cfg = Loop37Config(symbols=["ETH-USD"], venues=["okx", "bybit"], underlyings=["ETH"], expiries=["20261114"], modes="paper", cycles=8, seed=102, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["n_cycles"] == 8


def test_phase37_loop_three_venues():
    cfg = Loop37Config(symbols=["BTC-USD"], venues=["deribit", "okx", "bybit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=12, seed=103, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["n_cycles"] == 12


def test_phase37_loop_finite_all():
    cfg = Loop37Config(symbols=["BTC-USD"], venues=["deribit", "okx"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=15, seed=104, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    def walk(x):
        if isinstance(x, float):
            assert math.isfinite(x)
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(res)


def test_phase37_loop_aggregate():
    cfg = Loop37Config(symbols=["ETH-USD"], venues=["deribit", "okx", "bybit"], underlyings=["ETH"], expiries=["20261114"], modes="paper", cycles=10, seed=105, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    agg = res["aggregate"]
    assert agg["n_cycles"] == 10
    assert math.isfinite(agg["total_routed_notional"])


def test_phase37_integration_end_to_end():
    s = VenueLiquiditySourcing(SourcingConfig(seed=201))
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=202))
    src = s.scan(["deribit", "okx"], orderflow_imbalance=0.15)
    plan = r.route(target_qty=0.08, spot=50000, venues=src.top_venues or ["deribit"], regime="normal", stress_score=1.5)
    assert src.ok and plan.ok


def test_phase37_determinism_sourcing():
    s = VenueLiquiditySourcing(SourcingConfig(seed=301))
    r1 = s.scan(["deribit", "okx"], orderflow_imbalance=0.1)
    r2 = s.scan(["deribit", "okx"], orderflow_imbalance=0.1)
    assert abs(r1.metrics["avg_score"] - r2.metrics["avg_score"]) < 1e-12


def test_phase37_determinism_router():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=302))
    p1 = r.route(target_qty=0.1, spot=50000, venues=["deribit", "okx"], regime="normal", stress_score=1.0)
    p2 = r.route(target_qty=0.1, spot=50000, venues=["deribit", "okx"], regime="normal", stress_score=1.0)
    assert abs(p1.total_notional - p2.total_notional) < 1e-12


def test_phase37_paper_only_default():
    s = VenueLiquiditySourcing(SourcingConfig())
    r = CrossVenueDeltaNeutralRouter(RouterConfig())
    assert s.cfg.paper_only and r.cfg.paper_only


def test_phase37_live_gated_sourcing():
    try:
        VenueLiquiditySourcing(SourcingConfig(paper_only=False))
        assert False
    except ValueError:
        pass


def test_phase37_live_gated_router():
    try:
        CrossVenueDeltaNeutralRouter(RouterConfig(paper_only=False))
        assert False
    except ValueError:
        pass


def test_phase37_artifacts_exist():
    import os
    assert os.path.exists("research_state/PHASE37_ORDERFLOW_ROUTING_LOOP_REPORT.json")
    assert os.path.exists("research_state/PHASE37_CAMPAIGN_SUMMARY.json")


def test_phase37_sourcing_many_venues():
    s = VenueLiquiditySourcing(SourcingConfig(seed=401))
    res = s.scan(["deribit", "okx", "bybit", "binance"], orderflow_imbalance=0.3)
    assert res.ok and len(res.sources) == 4


def test_phase37_sourcing_zero_imbalance():
    s = VenueLiquiditySourcing(SourcingConfig(seed=402))
    res = s.scan(["deribit", "okx"], orderflow_imbalance=0.0)
    assert res.ok


def test_phase37_sourcing_scale():
    s = VenueLiquiditySourcing(SourcingConfig(seed=403))
    res = s.scan(["deribit"], orderflow_imbalance=0.1, depth_scale=1.5)
    assert res.ok


def test_phase37_router_buy():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=404))
    plan = r.route(target_qty=0.07, spot=50000, venues=["okx"], regime="calm", stress_score=0.5)
    assert plan.ok and len(plan.orders) == 1


def test_phase37_router_stressed_many():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=405))
    plan = r.route(target_qty=0.12, spot=50000, venues=["deribit", "okx", "bybit"], regime="stressed", stress_score=5.0)
    assert plan.ok


def test_phase37_router_fees_finite():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=406))
    plan = r.route(target_qty=0.1, spot=50000, venues=["deribit", "okx"], regime="normal", stress_score=2.0)
    for o in plan.orders:
        assert math.isfinite(o.fee_usd)


def test_phase37_loop_cycles_20():
    cfg = Loop37Config(symbols=["BTC-USD"], venues=["deribit", "okx", "bybit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=20, seed=501, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["n_cycles"] == 20


def test_phase37_loop_cycles_25():
    cfg = Loop37Config(symbols=["BTC-USD"], venues=["deribit", "okx"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=25, seed=502, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["n_cycles"] == 25


def test_phase37_loop_avg_orders():
    cfg = Loop37Config(symbols=["BTC-USD"], venues=["deribit", "okx", "bybit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=15, seed=503, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["avg_orders_per_cycle"] >= 0


def test_phase37_loop_delta_neutral_count():
    cfg = Loop37Config(symbols=["ETH-USD"], venues=["deribit", "okx"], underlyings=["ETH"], expiries=["20261114"], modes="paper", cycles=12, seed=504, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["delta_neutral_ok_cycles"] >= 0


def test_phase37_integration_stress():
    s = VenueLiquiditySourcing(SourcingConfig(seed=601))
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=602))
    src = s.scan(["deribit", "okx", "bybit"], orderflow_imbalance=0.4)
    plan = r.route(target_qty=-0.12, spot=50000, venues=src.top_venues, regime="stressed", stress_score=6.0)
    assert src.ok and plan.ok


def test_phase37_integration_crisis():
    s = VenueLiquiditySourcing(SourcingConfig(seed=603))
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=604))
    src = s.scan(["deribit", "okx", "bybit"], orderflow_imbalance=0.6)
    plan = r.route(target_qty=0.18, spot=50000, venues=src.top_venues, regime="crisis", stress_score=9.5)
    assert src.ok and plan.ok


def test_phase37_determinism_loop():
    cfg1 = Loop37Config(symbols=["BTC-USD"], venues=["deribit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=5, seed=777, outdir="research_state")
    cfg2 = Loop37Config(symbols=["BTC-USD"], venues=["deribit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=5, seed=777, outdir="research_state")
    res1 = Phase37OrderflowRoutingLoop(cfg1).run()
    res2 = Phase37OrderflowRoutingLoop(cfg2).run()
    assert abs(res1["aggregate"]["total_routed_notional"] - res2["aggregate"]["total_routed_notional"]) < 1e-12


def test_phase37_sourcing_metrics_finite():
    s = VenueLiquiditySourcing(SourcingConfig(seed=701))
    res = s.scan(["deribit", "okx"], orderflow_imbalance=0.25)
    for k,v in res.metrics.items():
        if isinstance(v,float): assert math.isfinite(v)


def test_phase37_router_metrics_finite():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=702))
    plan = r.route(target_qty=0.1, spot=50000, venues=["deribit", "okx"], regime="normal", stress_score=2.0)
    for k,v in plan.metrics.items():
        if isinstance(v,float): assert math.isfinite(v)


def test_phase37_warnings_structure():
    s = VenueLiquiditySourcing(SourcingConfig(seed=801))
    res = s.scan(["deribit"], orderflow_imbalance=0.0)
    assert isinstance(res.warnings, list)


def test_phase37_router_inventory_delta():
    r = CrossVenueDeltaNeutralRouter(RouterConfig(seed=901))
    plan = r.route(target_qty=0.05, spot=50000, venues=["deribit", "okx"], regime="normal", stress_score=1.0, inventory_delta=0.001)
    assert plan.ok and math.isfinite(plan.net_delta_est)


def test_phase37_sourcing_all_valid():
    s = VenueLiquiditySourcing(SourcingConfig(seed=902))
    res = s.scan(["deribit", "okx", "bybit"], orderflow_imbalance=0.1)
    assert all(x.valid for x in res.sources)
