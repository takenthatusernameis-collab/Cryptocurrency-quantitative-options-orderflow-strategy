"""Unit tests for EVAL-52 real Deribit options surface x options order-flow net-of-cost falsification.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.
"""

from __future__ import annotations

import math
import random

import scripts.eval52_options_surface_orderflow_net_of_cost as e52


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=3, n_snapshots=None):
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    tid = 0
    # per-bar drift decided first so we can sign flow and build snapshots coherently
    drifts = [rng.uniform(-1, 1) for _ in range(n_bars)]
    for i in range(n_bars):
        px = max(1.0, px * (1 + drifts[i] * 1e-4))
        candles.append({"ts": base_ms + i * bar_ms, "open": px, "high": px,
                        "low": px, "close": px})
        sign = 1.0 if drifts[i] >= 0 else -1.0
        for _ in range(n_trades_per_bar):
            tid += 1
            direction = "buy" if sign > 0 else "sell"
            opt = "call" if rng.random() < 0.5 else "put"
            strike = round(px + rng.randint(-2, 2) * 500, 2)
            trades.append({
                "ts": base_ms + i * bar_ms + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-30DEC26-{int(strike)}-{'C' if opt=='call' else 'P'}",
                "direction": direction,
                "amount": rng.uniform(0.1, 2.0),
                "price": 0.01,
                "index_price": px,
                "iv": 50.0,
                "option_type": opt,
                "strike": strike,
                "expiry": "2026-12-30T08:00:00Z",
            })

    # simple chain-shaped snapshots: a few strikes/expiries per bar with mark/bid/ask
    snaps = []
    snap_count = n_snapshots if n_snapshots is not None else n_bars
    for i in range(min(snap_count, n_bars)):
        bar_ms_i = base_ms + i * bar_ms
        spot = candles[i]["close"]
        quotes = []
        for k in (-2, -1, 0, 1, 2):
            strike = round(spot + k * 500, 2)
            for opt in ("call", "put"):
                mark = max(0.01, 0.05 * spot + (0.01 if opt == "call" else 0.02))
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
                    "timestamp": f"2023-11-14T00:{i%60:02d}:00Z",
                })
        snaps.append({"bar_ms": bar_ms_i, "spot": spot, "quotes": quotes})

    return {
        "schema": "deribit_options_surface_orderflow_capture_v1",
        "underlying": inst,
        "venue": "deribit",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": snaps},
        "option_trades": trades,
        "perp_candles": candles,
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit"},
    }


def test_build_bars_orders_and_attaches_return():
    cap = _craft_capture(n_bars=40)
    surf = e52.surface_signal_series(cap, cap["perp_candles"])
    bars = e52.build_bars(cap, surf, bar_seconds=300.0)
    assert len(bars) >= 30
    ends = [b["bar_end"] for b in bars]
    assert ends == sorted(ends)
    assert all(math.isfinite(b["imbalance"]) for b in bars)
    assert all("ret" in b for b in bars)
    assert bars[-1]["ret"] == 0.0
    assert all("surface" in b for b in bars)


def test_signed_flow_signs_and_notional():
    cap = {
        "perp_candles": [{"ts": 0, "close": 100.0}, {"ts": 300000, "close": 100.0}],
        "option_trades": [
            {"ts": 1000, "direction": "buy", "amount": 2.0, "index_price": 100.0, "option_type": "call"},
        ],
        "surface": {"snapshots": []},
        "underlying": "BTC", "venue": "deribit",
    }
    b = e52.build_bars(cap, [], bar_seconds=300.0)
    active = [x for x in b if x["n_trades"] > 0]
    assert active and active[0]["imbalance"] > 0

    cap2 = {
        "perp_candles": [{"ts": 0, "close": 100.0}, {"ts": 300000, "close": 100.0}],
        "option_trades": [
            {"ts": 1000, "direction": "buy", "amount": 1.0, "index_price": 200.0, "option_type": "call"},
            {"ts": 2000, "direction": "sell", "amount": 1.0, "index_price": 100.0, "option_type": "call"},
        ],
        "surface": {"snapshots": []},
        "underlying": "BTC", "venue": "deribit",
    }
    b2 = e52.build_bars(cap2, [], bar_seconds=300.0)
    a2 = [x for x in b2 if x["n_trades"] > 0]
    assert abs(a2[0]["imbalance"]) < 1e-12
    assert a2[0]["notional_imbalance"] > 0


def test_fusion_rules():
    s = [1.0, -1.0, 1.0, 0.0]
    f = [1.0, -1.0, -1.0, 1.0]
    assert e52.fuse_sign_agreement(s, f) == [1.0, -1.0, 0.0, 0.0]
    assert e52.fuse_regime_filter(s, f) == [1.0, 1.0, -1.0, 0.0]
    cz = e52.fuse_continuous_zscore(s, f)
    assert len(cz) == 4 and all(-1.0 <= v <= 1.0 for v in cz)


def test_expanding_zscore_and_strategy_returns():
    zs = e52.expanding_zscore([1, 1, 1, 5, 1], window=5)
    assert len(zs) == 5
    bars = [{"ret": 0.01}, {"ret": -0.01}, {"ret": 0.0}]
    out = e52.strategy_returns(bars, [1.0, 1.0, 0.0], cost_bps=5.0)
    assert len(out["returns"]) == 2
    assert out["nonzero"] == 2
    # gross 0.01 then -0.01 minus turnover cost on first step (0->1) and hold
    assert out["returns"][0] < 0.01


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=2)  # far below floor
    fl = e52._underlying_floor(cap)
    assert fl["ok"] is False
    assert any(not v for v in fl["checks"].values())


def test_evaluate_config_runs():
    cap = _craft_capture(n_bars=80, seed=3)
    surf = e52.surface_signal_series(cap, cap["perp_candles"])
    res = e52.evaluate_config(cap, surf, fusion="sign_agreement", of_signal="imbalance", bar_seconds=300.0)
    assert res["underlying"] == "BTC"
    assert res["n_returns"] > 0
    assert "sharpe" in res and "pass" in res


def test_protocol_and_floor_constants():
    p = e52.build_protocol("data/raw/eval52")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_surface_snapshots_per_underlying"] == 100
    assert set(p["fusion_rules"]) == {"sign_agreement", "regime_filter", "continuous_zscore"}
