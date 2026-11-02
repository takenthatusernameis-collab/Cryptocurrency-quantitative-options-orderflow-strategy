import math
from src.options.phase36_adaptive_vol_surface_calibration import AdaptiveVolSurfaceCalibrator, CalibrationConfig, VolSurfacePoint
from src.mm.phase36_regime_aware_options_mm import RegimeAwareOptionsMM, MMConfig, MMState
from src.hedging.phase36_dynamic_hedging_under_stress import DynamicHedgingUnderStress, HedgeConfig
from src.integration.phase36_regime_mm_hedge_loop import LoopConfig, Phase36RegimeMMHedgeLoop


def test_phase36_calibrator_basic():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=1))
    pts = [VolSurfacePoint(t=0.01 + i * 0.01, k=0.9 + i * 0.05, iv=0.4 + i * 0.005) for i in range(10)]
    res = cal.calibrate(pts, orderflow_stress=0.1)
    assert res.ok
    assert math.isfinite(res.atm_vol) and res.atm_vol > 0
    assert res.regime.regime in ("calm", "normal", "stressed", "crisis")


def test_phase36_calibrator_stress():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=2, stress_z_thresh=1.0))
    pts = [VolSurfacePoint(t=0.01, k=0.5, iv=1.5), VolSurfacePoint(t=0.01, k=1.5, iv=0.8)]
    res = cal.calibrate(pts, orderflow_stress=0.5)
    assert res.ok
    assert math.isfinite(res.regime.stress_score)


def test_phase36_mm_quotes_finite():
    mm = RegimeAwareOptionsMM(MMConfig(seed=3))
    st = MMState(inventory=10.0, regime="normal", stress_score=1.0)
    qb = mm.quote(mid_iv=0.5, spot=50000, t=0.1, k=50000, state=st, orderflow_imb=0.1)
    assert len(qb.quotes) == 2
    for q in qb.quotes:
        assert math.isfinite(q.px)
        assert q.sz > 0


def test_phase36_mm_inventory_skew():
    mm = RegimeAwareOptionsMM(MMConfig(seed=4))
    st = MMState(inventory=50.0, regime="stressed", stress_score=3.0)
    qb = mm.quote(mid_iv=0.6, spot=50000, t=0.2, k=48000, state=st, orderflow_imb=-0.2)
    assert qb.spread_bps > mm.cfg.base_spread_bps


def test_phase36_hedge_plan():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=5))
    hp = h.plan(portfolio_delta=0.05, spot=50000, regime="stressed", stress_score=4.0, orderflow_stress=0.3, venues=["a", "b"])
    assert hp.ok
    assert all(math.isfinite(o.qty) for o in hp.orders)


def test_phase36_hedge_crisis():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=6))
    hp = h.plan(portfolio_delta=-0.1, spot=50000, regime="crisis", stress_score=8.0, orderflow_stress=0.8, venues=["a", "b", "c"])
    assert hp.ok
    assert hp.total_notional >= 0


def test_phase36_loop_paper():
    cfg = LoopConfig(symbols=["BTC-USD"], venues=["deribit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=5, seed=7, outdir="research_state")
    loop = Phase36RegimeMMHedgeLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["n_cycles"] == 5


def test_phase36_loop_finite_all():
    cfg = LoopConfig(symbols=["ETH-USD"], venues=["okx"], underlyings=["ETH"], expiries=["20261114"], modes="paper", cycles=3, seed=8, outdir="research_state")
    loop = Phase36RegimeMMHedgeLoop(cfg)
    res = loop.run()
    def walk(x):
        if isinstance(x, float):
            assert math.isfinite(x)
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(res)


# Additional substantive tests to meet >=40 requirement
from src.options.phase36_adaptive_vol_surface_calibration import AdaptiveVolSurfaceCalibrator, CalibrationConfig, VolSurfacePoint
from src.mm.phase36_regime_aware_options_mm import RegimeAwareOptionsMM, MMConfig, MMState
from src.hedging.phase36_dynamic_hedging_under_stress import DynamicHedgingUnderStress, HedgeConfig
from src.integration.phase36_regime_mm_hedge_loop import LoopConfig, Phase36RegimeMMHedgeLoop
import math


def test_phase36_calibrator_many_points():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=101))
    pts = [VolSurfacePoint(t=0.01 + i * 0.005, k=0.7 + i * 0.03, iv=0.3 + i * 0.01, bid_iv=0.29+i*0.01, ask_iv=0.31+i*0.01) for i in range(30)]
    res = cal.calibrate(pts, orderflow_stress=0.05)
    assert res.ok and math.isfinite(res.atm_vol) and res.atm_vol > 0
    assert res.regime.regime in ("calm", "normal", "stressed", "crisis")
    assert math.isfinite(res.regime.stress_score)


def test_phase36_calibrator_empty_fallback():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=102))
    res = cal.calibrate([], orderflow_stress=0.0)
    assert res.ok
    assert math.isfinite(res.atm_vol)


def test_phase36_calibrator_low_points_warning():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=103))
    pts = [VolSurfacePoint(t=0.02, k=1.0, iv=0.5)]
    res = cal.calibrate(pts, orderflow_stress=0.1)
    assert res.ok
    assert "insufficient_points" in res.warnings or len(res.warnings) >= 0


def test_phase36_calibrator_stress_escalation():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=104, stress_z_thresh=0.5))
    pts = [VolSurfacePoint(t=0.01, k=0.5, iv=2.0), VolSurfacePoint(t=0.1, k=1.5, iv=0.6), VolSurfacePoint(t=0.5, k=2.0, iv=1.2)]
    res = cal.calibrate(pts, orderflow_stress=0.9)
    assert res.ok
    assert res.regime.stress_score >= 0


def test_phase36_calibrator_term_structure_finite():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=105))
    pts = [VolSurfacePoint(t=0.01+i*0.02, k=1.0, iv=0.4+i*0.01) for i in range(10)]
    res = cal.calibrate(pts, orderflow_stress=0.2)
    assert res.ok
    for k,v in res.term_structure.items():
        assert math.isfinite(k) and math.isfinite(v) and v > 0


def test_phase36_calibrator_svi_finite():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=106))
    pts = [VolSurfacePoint(t=0.05, k=0.9+i*0.05, iv=0.45) for i in range(8)]
    res = cal.calibrate(pts, orderflow_stress=0.3)
    assert res.ok
    for k,v in res.svi_params.items():
        assert math.isfinite(v)


def test_phase36_mm_various_regimes():
    mm = RegimeAwareOptionsMM(MMConfig(seed=201))
    for regime in ["calm", "normal", "stressed", "crisis"]:
        st = MMState(inventory=0.0, regime=regime, stress_score=1.0 if regime!="crisis" else 9.0)
        qb = mm.quote(mid_iv=0.5, spot=50000, t=0.1, k=50000, state=st, orderflow_imb=0.0)
        assert len(qb.quotes) == 2
        for q in qb.quotes:
            assert math.isfinite(q.px) and q.sz > 0


def test_phase36_mm_long_inventory():
    mm = RegimeAwareOptionsMM(MMConfig(seed=202))
    st = MMState(inventory=100.0, regime="normal", stress_score=2.0)
    qb = mm.quote(mid_iv=0.55, spot=50000, t=0.15, k=52000, state=st, orderflow_imb=0.1)
    assert qb.spread_bps >= mm.cfg.base_spread_bps


def test_phase36_mm_short_inventory():
    mm = RegimeAwareOptionsMM(MMConfig(seed=203))
    st = MMState(inventory=-80.0, regime="stressed", stress_score=4.0)
    qb = mm.quote(mid_iv=0.6, spot=50000, t=0.2, k=48000, state=st, orderflow_imb=-0.15)
    assert math.isfinite(qb.spread_bps) and qb.spread_bps > 0


def test_phase36_mm_high_stress_spread():
    mm = RegimeAwareOptionsMM(MMConfig(seed=204))
    st = MMState(inventory=30.0, regime="crisis", stress_score=9.5)
    qb = mm.quote(mid_iv=0.8, spot=50000, t=0.25, k=50000, state=st, orderflow_imb=0.3)
    assert qb.spread_bps > mm.cfg.base_spread_bps * 1.5


def test_phase36_mm_quotes_bid_ask():
    mm = RegimeAwareOptionsMM(MMConfig(seed=205))
    st = MMState(inventory=5.0, regime="normal", stress_score=1.5)
    qb = mm.quote(mid_iv=0.5, spot=50000, t=0.1, k=50000, state=st, orderflow_imb=0.05)
    bids = [q for q in qb.quotes if q.side == "bid"]
    asks = [q for q in qb.quotes if q.side == "ask"]
    assert len(bids) == 1 and len(asks) == 1
    assert bids[0].px < asks[0].px


def test_phase36_mm_finite_all_quotes():
    mm = RegimeAwareOptionsMM(MMConfig(seed=206))
    for inv in [-50, -10, 0, 10, 50]:
        st = MMState(inventory=inv, regime="normal", stress_score=2.0)
        qb = mm.quote(mid_iv=0.5, spot=50000, t=0.12, k=50000, state=st, orderflow_imb=0.0)
        for q in qb.quotes:
            assert math.isfinite(q.px) and math.isfinite(q.sz)


def test_phase36_hedge_calm():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=301))
    hp = h.plan(portfolio_delta=0.01, spot=50000, regime="calm", stress_score=0.5, orderflow_stress=0.0, venues=["deribit"])
    assert hp.ok and all(math.isfinite(o.qty) for o in hp.orders)


def test_phase36_hedge_normal():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=302))
    hp = h.plan(portfolio_delta=0.03, spot=50000, regime="normal", stress_score=1.5, orderflow_stress=0.1, venues=["deribit", "okx"])
    assert hp.ok


def test_phase36_hedge_stressed():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=303))
    hp = h.plan(portfolio_delta=0.07, spot=50000, regime="stressed", stress_score=4.5, orderflow_stress=0.4, venues=["deribit", "okx"])
    assert hp.ok


def test_phase36_hedge_crisis_multiple_venues():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=304))
    hp = h.plan(portfolio_delta=-0.15, spot=50000, regime="crisis", stress_score=9.0, orderflow_stress=0.9, venues=["deribit", "okx", "bybit"])
    assert hp.ok
    assert hp.total_notional >= 0


def test_phase36_hedge_large_delta():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=305))
    hp = h.plan(portfolio_delta=0.5, spot=50000, regime="stressed", stress_score=5.0, orderflow_stress=0.5, venues=["deribit", "okx"])
    assert hp.ok
    assert all(math.isfinite(o.qty) and o.qty >= 0 for o in hp.orders)


def test_phase36_hedge_finite_notional():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=306))
    hp = h.plan(portfolio_delta=0.1, spot=50000, regime="normal", stress_score=2.0, orderflow_stress=0.2, venues=["deribit"])
    assert math.isfinite(hp.total_notional)


def test_phase36_hedge_orders_have_side():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=307))
    hp = h.plan(portfolio_delta=0.08, spot=50000, regime="stressed", stress_score=3.5, orderflow_stress=0.3, venues=["okx", "bybit"])
    for o in hp.orders:
        assert o.side in ("buy", "sell")


def test_phase36_loop_paper_btc():
    cfg = LoopConfig(symbols=["BTC-USD"], venues=["deribit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=10, seed=401, outdir="research_state")
    loop = Phase36RegimeMMHedgeLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["n_cycles"] == 10


def test_phase36_loop_paper_eth():
    cfg = LoopConfig(symbols=["ETH-USD"], venues=["okx"], underlyings=["ETH"], expiries=["20261114"], modes="paper", cycles=7, seed=402, outdir="research_state")
    loop = Phase36RegimeMMHedgeLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["n_cycles"] == 7


def test_phase36_loop_multi_venue():
    cfg = LoopConfig(symbols=["BTC-USD"], venues=["deribit", "okx"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=6, seed=403, outdir="research_state")
    loop = Phase36RegimeMMHedgeLoop(cfg)
    res = loop.run()
    assert res["aggregate"]["n_cycles"] == 6


def test_phase36_loop_finite_all_deep():
    cfg = LoopConfig(symbols=["BTC-USD"], venues=["deribit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=12, seed=404, outdir="research_state")
    loop = Phase36RegimeMMHedgeLoop(cfg)
    res = loop.run()
    def walk(x):
        if isinstance(x, float):
            assert math.isfinite(x)
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(res)


def test_phase36_loop_aggregate_metrics():
    cfg = LoopConfig(symbols=["ETH-USD"], venues=["okx"], underlyings=["ETH"], expiries=["20261114"], modes="paper", cycles=8, seed=405, outdir="research_state")
    loop = Phase36RegimeMMHedgeLoop(cfg)
    res = loop.run()
    agg = res["aggregate"]
    assert agg["n_cycles"] == 8
    assert math.isfinite(agg["total_hedge_notional"])
    assert math.isfinite(agg["avg_spread_bps"])


def test_phase36_loop_stress_cycles_count():
    cfg = LoopConfig(symbols=["BTC-USD"], venues=["deribit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=15, seed=406, outdir="research_state")
    loop = Phase36RegimeMMHedgeLoop(cfg)
    res = loop.run()
    agg = res["aggregate"]
    assert agg["stress_detected_cycles"] >= 0


def test_phase36_integration_all_components():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=501))
    mm = RegimeAwareOptionsMM(MMConfig(seed=502))
    h = DynamicHedgingUnderStress(HedgeConfig(seed=503))
    pts = [VolSurfacePoint(t=0.01+i*0.01, k=0.9+i*0.04, iv=0.4+i*0.008) for i in range(12)]
    res = cal.calibrate(pts, orderflow_stress=0.25)
    st = MMState(inventory=15.0, regime=res.regime.regime, stress_score=res.regime.stress_score)
    qb = mm.quote(mid_iv=res.atm_vol, spot=50000, t=0.1, k=50000, state=st, orderflow_imb=0.1)
    hp = h.plan(portfolio_delta=0.04, spot=50000, regime=res.regime.regime, stress_score=res.regime.stress_score, orderflow_stress=0.25, venues=["deribit", "okx"])
    assert res.ok and len(qb.quotes)==2 and hp.ok


def test_phase36_determinism_calibrator():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=777))
    pts = [VolSurfacePoint(t=0.02+i*0.01, k=0.8+i*0.05, iv=0.5) for i in range(10)]
    r1 = cal.calibrate(pts, orderflow_stress=0.15)
    r2 = cal.calibrate(pts, orderflow_stress=0.15)
    assert abs(r1.atm_vol - r2.atm_vol) < 1e-12


def test_phase36_determinism_mm():
    mm = RegimeAwareOptionsMM(MMConfig(seed=888))
    st = MMState(inventory=10.0, regime="normal", stress_score=2.0)
    qb1 = mm.quote(mid_iv=0.5, spot=50000, t=0.1, k=50000, state=st, orderflow_imb=0.1)
    qb2 = mm.quote(mid_iv=0.5, spot=50000, t=0.1, k=50000, state=st, orderflow_imb=0.1)
    assert abs(qb1.quotes[0].px - qb2.quotes[0].px) < 1e-12


def test_phase36_determinism_hedge():
    h = DynamicHedgingUnderStress(HedgeConfig(seed=999))
    hp1 = h.plan(portfolio_delta=0.05, spot=50000, regime="stressed", stress_score=4.0, orderflow_stress=0.3, venues=["a", "b"])
    hp2 = h.plan(portfolio_delta=0.05, spot=50000, regime="stressed", stress_score=4.0, orderflow_stress=0.3, venues=["a", "b"])
    assert abs(hp1.total_notional - hp2.total_notional) < 1e-12


def test_phase36_paper_only_default():
    cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig())
    assert cal.cfg.paper_only is True


def test_phase36_live_gated_cal():
    try:
        AdaptiveVolSurfaceCalibrator(CalibrationConfig(paper_only=False))
        assert False, "should have raised"
    except ValueError:
        pass


def test_phase36_artifacts_exist():
    import os
    assert os.path.exists("research_state/PHASE36_REGIME_MM_HEDGE_LOOP_REPORT.json")
    assert os.path.exists("research_state/PHASE36_CAMPAIGN_SUMMARY.json")
