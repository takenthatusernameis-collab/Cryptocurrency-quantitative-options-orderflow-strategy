"""Phase 11 tests."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.execution.live_execution import LiveExecutionEngine
from src.alpha.continuous_optimizer import ContinuousAlphaOptimizer, OptConfig
from src.analytics.performance_attribution import PerformanceAttributor
from src.risk.live_risk_gate import LiveRiskGatekeeper
from src.execution.walkforward_live_replay import WalkForwardLiveReplay
from src.execution.phase11_campaign import Phase11Campaign
from src.alpha.phase10_campaign import Phase10Campaign
from src.telemetry.serialization import assert_json_valid


def test_live_execution_invariants():
    eng = LiveExecutionEngine(seed=42)
    class Dummy:
        symbol = "BTC"
        side = "buy"
        qty = 0.02
    d = Dummy()
    orders = eng.route(d, {"BTC": 65000.0})
    assert len(orders) >= 1
    fills = eng.execute(orders, {"BTC": 65000.0})
    assert len(fills) == len(orders)
    rep = eng.reconcile(orders, fills)
    assert_json_valid(rep)
    rep2 = eng.generate_report(orders, fills)
    assert_json_valid(rep2)


def test_continuous_optimizer_determinism():
    opt = ContinuousAlphaOptimizer(OptConfig(seed=123))
    rng = np.random.default_rng(123)
    rets = rng.normal(0.0001, 0.01, 100)
    reg = rng.integers(0, 3, 100)
    r1 = opt.optimize(rets, reg)
    r2 = opt.optimize(rets, reg)
    assert r1["best_sharpe_like"] == r2["best_sharpe_like"]
    rep = opt.generate_report(rets, reg)
    assert_json_valid(rep)


def test_performance_attribution():
    attr = PerformanceAttributor(seed=5)
    rng = np.random.default_rng(5)
    pnl = rng.normal(0.001, 0.01, 50)
    by = {"vol_rv": rng.normal(0.0005, 0.005, 50), "orderflow": rng.normal(0.0003, 0.004, 50)}
    rep = attr.generate_report(pnl, by, rng.integers(0,2,50), rng.uniform(1,3,50))
    assert_json_valid(rep)
    assert "by_alpha_source" in rep


def test_live_risk_gate():
    gate = LiveRiskGatekeeper()
    class Dummy:
        delta_est = 0.05
        vega_est = 0.03
        gamma_est = 0.01
        liquidity_score = 0.5
        dte = 30
    rep = gate.generate_report()
    assert_json_valid(rep)
    res = gate.check(Dummy(), {"drawdown_pct": 0.01, "max_concentration": 0.1})
    assert res["approved"] is True


def test_walkforward_live_replay():
    w = WalkForwardLiveReplay(seed=42)
    rng = np.random.default_rng(42)
    rep = w.generate_report(rng.normal(0.0001, 0.01, 120), rng.integers(0,3,120))
    assert_json_valid(rep)
    assert rep["aggregate"]["n_folds"] >= 1


def test_phase11_campaign_end_to_end():
    camp = Phase11Campaign(symbols=("BTC", "ETH"), seed=42)
    res = camp.run()
    assert len(res["artifacts"]) >= 12
    for p in res["artifacts"]:
        assert Path(p).exists()
    master = res["master"]
    assert_json_valid(master)
    assert master["counts"]["orders"] >= 0


def test_phase11_determinism_byte_identical():
    c1 = Phase11Campaign(symbols=("BTC", "ETH"), seed=42)
    r1 = c1.run()
    c2 = Phase11Campaign(symbols=("BTC", "ETH"), seed=42)
    r2 = c2.run()
    m1 = json.loads(Path(r1["artifacts"][-2]).read_text())
    m2 = json.loads(Path(r2["artifacts"][-2]).read_text())
    assert m1["seed"] == m2["seed"]
    assert m1["counts"] == m2["counts"]
