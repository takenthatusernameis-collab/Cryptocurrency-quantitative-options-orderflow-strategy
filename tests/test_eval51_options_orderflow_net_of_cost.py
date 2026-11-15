"""Unit tests for EVAL-51 real Deribit options order-flow net-of-cost falsification.

These tests verify the pure bar-building / signed-flow aggregation / z-score /
net-of-cost strategy functions, the per-underlying evaluator, and the heavy-work
floor (a short or partial capture must NOT produce a GO/NO-GO verdict). They use
deterministic in-memory capture fixtures (unit-test inputs only) and never touch
``research_state/`` or real data.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import scripts.eval51_acquire_options_orderflow as acq
import scripts.eval51_options_orderflow_net_of_cost as e51


# ---------------------------------------------------------------------------
# Bar building + signed-flow aggregation
# ---------------------------------------------------------------------------
def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=3):
    """Deterministic capture: a random-walk underlying and signed option flow that
    is (by construction) correlated with the next-bar underlying move, so the
    strategy tests can assert a positive-Sharpe path exists."""
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0
    candles = []
    trades = []
    tid = 0
    for i in range(n_bars):
        drift = rng.uniform(-1, 1)
        px = max(1.0, px * (1 + drift * 1e-4))
        candles.append({"ts": base_ms + i * bar_ms, "open": px, "high": px,
                        "low": px, "close": px})
        # sign the flow with the *next* drift so imbalance leads the move
        sign = 1.0 if drift >= 0 else -1.0
        for _ in range(n_trades_per_bar):
            tid += 1
            direction = "buy" if sign > 0 else "sell"
            trades.append({
                "ts": base_ms + i * bar_ms + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-30DEC26-{60000 + rng.randint(-1, 1) * 500}-C",
                "direction": direction,
                "amount": rng.uniform(0.1, 2.0),
                "price": 0.01,
                "index_price": px,
                "iv": 50.0,
                "option_type": "call" if rng.random() < 0.5 else "put",
                "strike": 60000.0,
                "expiry": "2026-12-30T08:00:00Z",
            })
    return {
        "schema": "test_fixture",
        "underlying": inst,
        "venue": "deribit",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "option_trades": trades,
        "perp_candles": candles,
    }


def test_build_bars_orders_and_attaches_return():
    cap = _craft_capture(n_bars=40)
    bars = e51.build_bars(cap, bar_seconds=5.0)
    assert len(bars) >= 30
    ends = [b["bar_end"] for b in bars]
    assert ends == sorted(ends)
    assert all(math.isfinite(b["imbalance"]) for b in bars)
    assert all("ret" in b for b in bars)
    # last bar has no next bar -> ret 0
    assert bars[-1]["ret"] == 0.0


def test_signed_flow_signs():
    cap = _craft_capture(n_bars=20, seed=1)
    bars = e51.build_bars(cap, bar_seconds=5.0)
    # a bar with only buy trades -> positive imbalance
    buy_bar = {
        "perp_candles": [{"ts": 0, "close": 100.0}, {"ts": 300000, "close": 101.0}],
        "option_trades": [
            {"ts": 1000, "direction": "buy", "amount": 2.0, "index_price": 100.0, "option_type": "call"},
        ],
    }
    b = e51.build_bars(buy_bar, bar_seconds=5.0)
    active = [x for x in b if x["n_trades"] > 0]
    assert active and active[0]["imbalance"] > 0


def test_notional_imbalance_uses_index_price():
    cap = {
        "perp_candles": [{"ts": 0, "close": 100.0}, {"ts": 300000, "close": 100.0}],
        "option_trades": [
            {"ts": 1000, "direction": "buy", "amount": 1.0, "index_price": 200.0, "option_type": "call"},
            {"ts": 2000, "direction": "sell", "amount": 1.0, "index_price": 100.0, "option_type": "call"},
        ],
    }
    b = e51.build_bars(cap, bar_seconds=5.0)
    active = [x for x in b if x["n_trades"] > 0]
    # equal amounts -> amount imbalance 0, but notional favors the buy (200 vs 100)
    assert abs(active[0]["imbalance"]) < 1e-12
    assert active[0]["notional_imbalance"] > 0


def test_call_minus_put():
    cap = {
        "perp_candles": [{"ts": 0, "close": 100.0}, {"ts": 300000, "close": 100.0}],
        "option_trades": [
            {"ts": 1000, "direction": "buy", "amount": 2.0, "index_price": 100.0, "option_type": "call"},
            {"ts": 2000, "direction": "sell", "amount": 1.0, "index_price": 100.0, "option_type": "put"},
        ],
    }
    b = e51.build_bars(cap, bar_seconds=5.0)
    active = [x for x in b if x["n_trades"] > 0]
    # call_buy=2, put_sell=1 -> call_minus_put = (2-0) - (0-1) = 3 / total 3 = 1.0
    assert abs(active[0]["call_minus_put"] - 1.0) < 1e-12


# ---------------------------------------------------------------------------
# z-score + net-of-cost strategy
# ---------------------------------------------------------------------------
def test_expanding_zscore_zero_before_min_periods():
    zs = e51.expanding_zscore([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], window=5, min_periods=5)
    assert zs[0] == 0.0 and zs[1] == 0.0 and zs[2] == 0.0 and zs[3] == 0.0
    assert zs[4] != 0.0


def test_strategy_returns_rising_flow_is_long_and_profitable():
    bars = [
        {"bar_end": i * 300000, "imbalance": float(i), "ret": 0.001,
         "close": 100.0, "n_trades": 1}
        for i in range(12)
    ]
    sr = e51.strategy_returns(bars, "imbalance", z_clamp=1.0)
    assert len(sr["returns"]) == len(bars) - 1
    assert sr["nonzero"] > 0
    assert e51._sharpe_of_returns(sr["returns"]) > 0


def test_cost_reduces_return():
    bars = [
        {"bar_end": i * 300000, "imbalance": 1.0 if i % 2 == 0 else -1.0,
         "ret": 0.0, "close": 100.0, "n_trades": 1}
        for i in range(20)
    ]
    gross = e51.strategy_returns(bars, "imbalance", z_clamp=1.0, cost_bps=0.0)
    net = e51.strategy_returns(bars, "imbalance", z_clamp=1.0, cost_bps=5.0)
    assert e51._mean(net["returns"]) <= e51._mean(gross["returns"])


def test_max_drawdown_and_kill_switch():
    assert e51._max_drawdown([0.1, -0.5, 0.1]) > 0.3
    assert e51.kill_switch_breach(0.25) is True
    assert e51.kill_switch_breach(0.1) is False


# ---------------------------------------------------------------------------
# Evaluator + floor
# ---------------------------------------------------------------------------
def test_evaluate_capture_runs_without_error():
    cap = _craft_capture(n_bars=200, seed=2)
    res = e51.evaluate_capture(cap, signal="imbalance", bar_seconds=5.0)
    assert res["underlying"] == "BTC"
    assert res["n_returns"] > 0
    assert math.isfinite(res["sharpe"])
    assert 0.0 <= res["permutation_p"] <= 1.0
    assert len(res["bootstrap_ci"]) == 3
    assert isinstance(res["pass"], bool)


def test_run_eval51_floor_blocks_short_capture(tmp_path):
    cap = _craft_capture(n_bars=100, seed=3, inst="BTC", n_trades_per_bar=2)
    (tmp_path / "options_orderflow_BTC_20260101T000000Z.json").write_text(json.dumps(cap))
    report = e51.run_eval51(
        capture_dir=str(tmp_path),
        write=False,
        min_trades=2000,
        min_bars=288,
        min_instruments=10,
        min_span=86400.0,
        min_underlyings=2,
    )
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"


def test_run_eval51_no_write_seals_nothing(tmp_path):
    cap = _craft_capture(n_bars=200, seed=4, inst="BTC")
    (tmp_path / "options_orderflow_BTC_20260101T000000Z.json").write_text(json.dumps(cap))
    before = set(p.name for p in e51.OUT_DIR.glob("EVAL_51_*"))
    e51.run_eval51(capture_dir=str(tmp_path), write=False)
    after = set(p.name for p in e51.OUT_DIR.glob("EVAL_51_*"))
    assert before == after


def test_capture_inventory_keeps_newest_per_underlying(tmp_path):
    old = _craft_capture(n_bars=100, seed=5, inst="BTC")
    old["window_end"] = "2023-11-14T00:00:00Z"
    new = _craft_capture(n_bars=300, seed=6, inst="BTC")
    new["window_end"] = "2023-11-16T00:00:00Z"
    (tmp_path / "options_orderflow_BTC_20260101T000000Z.json").write_text(json.dumps(old))
    (tmp_path / "options_orderflow_BTC_20260102T000000Z.json").write_text(json.dumps(new))
    inv = e51._capture_inventory(str(tmp_path))
    assert len(inv) == 1
    assert len(inv[0]["perp_candles"]) == 300  # newest kept, not double-counted


# ---------------------------------------------------------------------------
# Acquisition helpers (pure, no network)
# ---------------------------------------------------------------------------
def test_normalize_trade_maps_fields():
    from datetime import datetime, timezone

    row = {"instrument_name": "BTC-30DEC26-60000-C", "option_type": "call", "strike": 60000.0,
           "expiry": datetime(2026, 12, 30, 8, 0, tzinfo=timezone.utc)}
    out = acq.normalize_trade(
        {"timestamp": 123, "instrument_name": "BTC-30DEC26-60000-C", "direction": "BUY",
         "amount": "1.5", "price": "0.02", "index_price": "60000", "iv": "40"},
        row,
    )
    assert out["direction"] == "buy"
    assert out["amount"] == 1.5
    assert out["option_type"] == "call"
    assert out["expiry"] == "2026-12-30T08:00:00Z"


def test_summarize_counts_buys_sells_and_instruments():
    cap = {
        "underlying": "BTC",
        "option_trades": [
            {"ts": 1000, "instrument": "A", "direction": "buy", "amount": 1.0, "index_price": 100.0, "strike": 1.0},
            {"ts": 2000, "instrument": "A", "direction": "sell", "amount": 2.0, "index_price": 100.0, "strike": 1.0},
            {"ts": 3000, "instrument": "B", "direction": "buy", "amount": 3.0, "index_price": 100.0, "strike": 2.0},
        ],
        "perp_candles": [{"ts": 0, "close": 1.0}, {"ts": 1, "close": 2.0}],
    }
    s = acq.summarize(cap)
    assert s["n_option_trades"] == 3
    assert s["n_instruments_with_trades"] == 2
    assert s["n_buy"] == 2 and s["n_sell"] == 1
    assert s["non_degenerate"] is True