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
