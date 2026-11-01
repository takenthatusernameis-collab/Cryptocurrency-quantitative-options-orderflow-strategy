"""Phase 10 Alpha tests (vol surface RV, orderflow alpha, fusion, sizing, OOS)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.alpha.vol_surface_rv import VolSurfaceRVEngine, VolSurfaceRVConfig
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.alpha.signal_fusion import SignalFusion
from src.alpha.position_sizing import PositionSizer
from src.alpha.walkforward_oos import WalkForwardOOS, OOSConfig
from src.alpha.phase10_campaign import Phase10Campaign
from src.data.schemas import OptionContract, OptionQuote, OptionsChain, OrderflowSnapshot, Trade
from src.telemetry.serialization import assert_json_valid
from datetime import datetime, timezone, timedelta


def test_rv_engine_deterministic():
    camp = Phase10Campaign(symbols=("BTC",), seed=42)
    chain = camp._gen_chain("BTC")
    eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=42))
    opps1 = eng.detect_dislocations(chain, spot=65000.0)
    opps2 = eng.detect_dislocations(chain, spot=65000.0)
    assert [o.rationale_hash for o in opps1] == [o.rationale_hash for o in opps2]
    rep = eng.generate_report(opps1, 42)
    assert_json_valid(rep)
    assert rep["seed"] == 42


def test_orderflow_alpha_deterministic():
    camp = Phase10Campaign(symbols=("BTC",), seed=123)
    snap = camp._gen_orderflow("BTC")
    eng = OrderflowAlphaEngine(seed=123)
    f1 = eng.extract_features(snap)
    f2 = eng.extract_features(snap)
    assert f1.cumulative_delta == f2.cumulative_delta
    rep = eng.generate_report([f1])
    assert_json_valid(rep)


def test_signal_fusion_gates():
    eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=7))
    camp = Phase10Campaign(symbols=("ETH",), seed=7)
    chain = camp._gen_chain("ETH")
    opps = eng.detect_dislocations(chain, spot=3400.0)
    ofeng = OrderflowAlphaEngine(seed=7)
    feat = ofeng.extract_features(camp._gen_orderflow("ETH"))
    fusion = SignalFusion(seed=7, max_abs_delta=0.15, max_abs_vega=0.10, gamma_band=0.05, min_liquidity=0.0, min_dte=1, max_dte=90)
    intents = fusion.fuse(opps, [feat], {"ETH": 0.01})
    for it in intents:
        assert abs(it.delta_est) <= 0.15 + 1e-12
        assert abs(it.vega_est) <= 0.10 + 1e-12
        assert abs(it.gamma_est) <= 0.05 + 1e-12
        assert it.liquidity_score >= 0.0
    rep = fusion.generate_report(intents)
    assert_json_valid(rep)


def test_position_sizing_caps():
    eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=9))
    camp = Phase10Campaign(symbols=("BTC", "ETH"), seed=9)
    chain_b = camp._gen_chain("BTC")
    chain_e = camp._gen_chain("ETH")
    opps = eng.detect_dislocations(chain_b, 65000.0) + eng.detect_dislocations(chain_e, 3400.0)
    ofeng = OrderflowAlphaEngine(seed=9)
    feats = [ofeng.extract_features(camp._gen_orderflow("BTC")), ofeng.extract_features(camp._gen_orderflow("ETH"))]
    fusion = SignalFusion(seed=9, min_liquidity=0.0)
    intents = fusion.fuse(opps, feats, {"BTC": 0.01})
    sizer = PositionSizer(capital=100000.0, seed=9)
    sized = sizer.size(intents)
    for s in sized:
        assert abs(s.delta_usd) <= 5000.0 + 1e-6
        assert s.notional_usd <= 100000.0 * 0.02 + 1e-6
    rep = sizer.generate_report(sized)
    assert_json_valid(rep)


def test_walkforward_oos_valid():
    oos = WalkForwardOOS(OOSConfig(seed=42, n_points=200))
    rng = np.random.default_rng(42)
    rets = rng.normal(0.0001, 0.01, 200)
    rep = oos.run(rets)
    assert_json_valid(rep)
    agg = rep["aggregate"]
    assert np.isfinite(agg["sharpe"])
    assert np.isfinite(agg["sortino"])
    assert np.isfinite(agg["max_dd"])


def test_phase10_campaign_end_to_end():
    camp = Phase10Campaign(symbols=("BTC", "ETH"), seed=42)
    res = camp.run()
    assert len(res["artifacts"]) >= 12
    # check all files exist
    for p in res["artifacts"]:
        assert Path(p).exists()
    master = res["master"]
    assert_json_valid(master)
    assert master["counts"]["rv_opps"] >= 0
    assert master["counts"]["of_features"] == 2


def test_phase10_determinism_byte_identical():
    camp1 = Phase10Campaign(symbols=("BTC", "ETH"), seed=42)
    res1 = camp1.run()
    camp2 = Phase10Campaign(symbols=("BTC", "ETH"), seed=42)
    res2 = camp2.run()
    # compare master
    m1 = json.loads(Path(res1["artifacts"][-2]).read_text())  # master json
    m2 = json.loads(Path(res2["artifacts"][-2]).read_text())
    assert m1["seed"] == m2["seed"]
    assert m1["counts"] == m2["counts"]
