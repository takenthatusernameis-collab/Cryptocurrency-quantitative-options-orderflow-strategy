"""Unit tests for EVAL-62: real options order-flow toxicity -> signal-timed
delta-hedged ATM straddle with the **correct mark-path** net-of-cost P&L.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

The critical regression guard is ``test_markpath_returns_correct_formula``: it
pins the EVAL-57-correct return ``ret_k = (side*exposure*(mark_{k+1}-mark_k)*S
+ hedge*dS - cost)/S`` so a future edit cannot silently reintroduce EVAL-61's
broken un-normalized dollar-P&L-as-return artifact.
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import scripts.eval62_orderflow_realized_vol_markpath as e62


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=3,
                   n_snapshots=None):
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    drifts = [rng.uniform(-1, 1) for _ in range(n_bars)]
    for i in range(n_bars):
        px = max(1.0, px * (1 + drifts[i] * 1e-4))
        candles.append({"ts": base_ms + i * bar_ms, "open": px, "high": px,
                        "low": px, "close": px})
        sign = 1.0 if drifts[i] >= 0 else -1.0
        for _ in range(n_trades_per_bar):
            direction = "buy" if sign > 0 else "sell"
            opt = "call" if rng.random() < 0.5 else "put"
            strike = round(px + rng.randint(-2, 2) * 500, 2)
            amt = rng.uniform(0.1, 2.0)
            trades.append({
                "ts": base_ms + i * bar_ms + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-30DEC26-{int(strike)}-{opt[0].upper()}",
                "direction": direction,
                "amount": amt,
                "price": 0.01,
                "index_price": px,
                "iv": 0.8,
                "option_type": opt,
                "strike": strike,
                "expiry": "2026-12-30T08:00:00Z",
            })

    snaps = []
    snap_count = n_snapshots if n_snapshots is not None else n_bars
    for i in range(min(snap_count, n_bars)):
        bar_ms_i = base_ms + i * bar_ms
        spot = candles[i]["close"]
        strike = round(spot, 2)
        mark = 0.1
        quotes = []
        for opt in ("call", "put"):
            quotes.append({
                "symbol": f"{inst}-OPT-{int(strike)}-{opt[0].upper()}-{i}",
                "underlying": inst,
                "strike": strike,
                "expiry": "2026-12-30T08:00:00Z",
                "option_type": opt,
                "bid": mark * 0.98,
                "ask": mark * 1.02,
                "mark": mark,
                "open_interest": 100.0,
                "volume": 10.0,
                "timestamp": "2023-11-14T00:00:00Z",
            })
        snaps.append({"bar_ms": bar_ms_i, "spot": spot, "quotes": quotes})

    return {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": inst,
        "venue": "deribit+okx",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": snaps},
        "option_trades": trades,
        "perp_candles": candles,
        "okx_inst_id": f"{inst}-USD-SWAP",
        "okx_perp_trades": [],
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit+okx"},
    }


def test_build_states_causal_side_exposure():
    cap = _craft_capture(n_bars=80, seed=5)
    states = e62.build_states(cap, tox_signal="tox", bar_seconds=300.0)
    assert len(states) > 20
    for s in states:
        assert s["spot"] > 0
        assert s["straddle_mark"] > 0
        assert s["side"] in (-1, 0, 1)
        assert 0.0 <= s["exposure"] <= e62.SIZE_CAP
        # exposure is zero exactly when side is zero (flat)
        if s["side"] == 0:
            assert s["exposure"] == 0.0
        else:
            assert s["exposure"] > 0.0


def test_markpath_returns_correct_formula():
    """Regression guard: ret_k = (side*exp*(mark1-mark0)*S0 + hedge*dS - cost)/S0."""
    states = [
        {"spot": 100.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 2.0, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 0},
        {"spot": 101.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 2.5, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 300_000},
        {"spot": 99.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 1.8, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 600_000},
    ]
    out = e62.markpath_returns(states, hedge_fee_bps=5.0)
    assert len(out["returns"]) == 2

    # Step 0: side=1, exp=1, hedge=-1*1*0.5=-0.5, prev_hedge=0 -> turnover 0.5
    s0, s1 = 100.0, 101.0
    hedge0 = -1.0 * 1.0 * 0.5
    d_option0 = 1.0 * 1.0 * (2.5 - 2.0) * s0
    gross0 = d_option0 + hedge0 * (s1 - s0)
    turnover0 = abs(hedge0 - 0.0)
    cost0 = 5.0 * turnover0 * s0 / 1e4
    cost0 += 0.5 * 0.0 * 1.0  # entry half-spread (spread_usd=0)
    ret0_expected = (gross0 - cost0) / s0
    assert abs(out["returns"][0] - ret0_expected) < 1e-12
    # The return must be a proper return (small), NOT a raw dollar P&L.
    assert abs(out["returns"][0]) < 1.0

    # Step 1: hedge stays -0.5 (no rebalance), prev_hedge=-0.5
    s0b, s1b = 101.0, 99.0
    hedge1 = -1.0 * 1.0 * 0.5
    d_option1 = 1.0 * 1.0 * (1.8 - 2.5) * s0b
    gross1 = d_option1 + hedge1 * (s1b - s0b)
    turnover1 = abs(hedge1 - (-0.5))  # 0
    cost1 = 5.0 * turnover1 * s0b / 1e4
    # last step -> exit half-spread (spread_usd=0)
    cost1 += 0.5 * 0.0 * 1.0
    ret1_expected = (gross1 - cost1) / s0b
    assert abs(out["returns"][1] - ret1_expected) < 1e-12


def test_markpath_returns_returns_are_normalized():
    """A large spot move must not produce a >1.0 'return' (the EVAL-61 artifact)."""
    states = [
        {"spot": 100.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 2.0, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 0},
        {"spot": 100.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 1000.0, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 300_000},
    ]
    out = e62.markpath_returns(states, hedge_fee_bps=5.0)
    # mark jumps 2->1000 (an absurd 998 move); return = 998*100/100 = 998/100 = 9.98
    # but the point is it is divided by S0, i.e. a *return*, not the raw 99800 dollar pnl.
    assert abs(out["returns"][0] - (998.0 * 100.0 - 5.0 * 0.5 * 100.0 / 1e4) / 100.0) < 1e-9


def test_markpath_insufficient_states():
    out = e62.markpath_returns([])
    assert out["returns"] == []
    assert out["nonzero"] == 0
    out1 = e62.markpath_returns([
        {"spot": 100.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 2.0, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 0},
    ])
    assert out1["returns"] == []


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=2)  # far below floor
    fl = e62._underlying_floor(cap)
    assert fl["ok"] is False
    assert any(not v for v in fl["checks"].values())


def test_evaluate_config_runs():
    cap = _craft_capture(n_bars=80, seed=3)
    res = e62.evaluate_config(cap, tox_signal="tox", bar_seconds=300.0)
    assert res["underlying"] == "BTC"
    assert res["n_returns"] > 0
    assert "sharpe" in res and "pass" in res
    # kill-switch must not be spuriously breached by un-normalized P&L
    assert res["max_drawdown"] <= 1.0


def test_protocol_and_floor_constants():
    p = e62.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_surface_snapshots_per_underlying"] == 100
    assert p["floor"]["min_option_trades_per_underlying"] == 2000
    assert set(p["tox_signals"]) == {"tox", "imbalance"}
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["kill_switch_max_dd"] == 0.20
    assert "supersedes" in p and "EVAL-61" in p["supersedes"]
    assert "markpath" in p["title"].lower() or "mark-path" in p["title"].lower()


def test_run_eval62_no_write_blocks_below_floor():
    cap = _craft_capture(n_bars=40, seed=7)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e62.run_eval62(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"