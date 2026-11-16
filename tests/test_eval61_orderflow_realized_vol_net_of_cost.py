"""Unit tests for EVAL-61: real options order-flow toxicity -> subsequent realized
volatility, signal-timed delta-hedged ATM straddle net-of-cost falsification.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61


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
        # ATM strike at spot, both call and put with a priceable mark.
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


def test_toxicity_per_bar_signs():
    cap = _craft_capture(n_bars=10, seed=1, n_trades_per_bar=4)
    bar_ends, closes, tox, imb = e61.toxicity_per_bar(cap, bar_seconds=300.0)
    assert len(bar_ends) == len(tox) == len(imb) == 10
    assert all(-1.0 <= t <= 1.0 for t in tox)
    assert all(-1.0 <= t <= 1.0 for t in imb)
    assert all(math.isfinite(c) and c > 0 for c in closes.values())


def test_expanding_zscore_causal():
    xs = [1.0, 2.0, 3.0, 10.0, 1.0]
    zs = e61.expanding_zscore(xs, window=5)
    assert len(zs) == 5
    # First value has n<min_periods(5) -> z=0
    assert zs[0] == 0.0
    # All finite
    assert all(math.isfinite(z) for z in zs)


def test_atm_straddle_prices():
    cap = _craft_capture(n_bars=3, seed=2)
    snap = cap["surface"]["snapshots"][0]
    spot = snap["spot"]
    state_time = __import__("datetime").datetime.fromtimestamp(
        (snap["bar_ms"] + 300_000) / 1000.0, tz=__import__("datetime").timezone.utc,
    )
    st = e61._atm_straddle(snap["quotes"], spot, state_time)
    assert st is not None
    assert math.isfinite(st["iv"]) and st["iv"] > 0
    assert math.isfinite(st["delta"]) and math.isfinite(st["gamma"])
    assert math.isfinite(st["theta"]) and math.isfinite(st["vega"])
    assert st["price_usd"] > 0


def test_straddle_series_and_align():
    cap = _craft_capture(n_bars=10, seed=3)
    av = e61.straddle_series_from_surface(cap)
    assert len(av) == 10
    bar_ends = [b[0] + 300_000 for b in av]  # bar_end after each bar
    aligned = e61.align_straddle(av, bar_ends)
    assert len(aligned) == 10
    assert all(s is not None for s in aligned)


def test_build_bars_attaches_tox_and_straddle():
    cap = _craft_capture(n_bars=40, seed=4)
    av = e61.straddle_series_from_surface(cap)
    bars = e61.build_bars(cap, av, bar_seconds=300.0)
    assert len(bars) >= 30
    assert all("q_tox" in b and "q_imb" in b for b in bars)
    assert all(-1.0 <= b["q_tox"] <= 1.0 for b in bars)
    assert all(-1.0 <= b["q_imb"] <= 1.0 for b in bars)
    assert all("straddle" in b for b in bars)
    assert bars[-1]["close"] > 0


def test_strategy_returns_apply_cost():
    bars = [
        {"close": 100.0, "dt": 300.0 / (365.0 * 86400.0),
         "straddle": {"iv": 0.8, "delta": 0.5, "gamma": 0.001, "theta": -10.0, "vega": 5000.0}},
        {"close": 101.0, "dt": 300.0 / (365.0 * 86400.0),
         "straddle": {"iv": 0.82, "delta": 0.55, "gamma": 0.001, "theta": -10.0, "vega": 5000.0}},
        {"close": 99.0, "dt": 300.0 / (365.0 * 86400.0),
         "straddle": {"iv": 0.79, "delta": 0.45, "gamma": 0.001, "theta": -10.0, "vega": 5000.0}},
    ]
    out = e61.strategy_returns(bars, [1.0, -1.0, 0.0], cost_bps=5.0)
    assert len(out["returns"]) == 2
    # Bar 0: q=1, gross = vega*dIV + 0.5*gamma*dS^2 - theta*dt
    d_iv = 0.82 - 0.8
    d_s = 101.0 - 100.0
    dt = 300.0 / (365.0 * 86400.0)
    gross0 = 1.0 * (5000.0 * d_iv + 0.5 * 0.001 * d_s * d_s - (-10.0) * dt)
    cost0 = 5.0 * (abs(1.0 * 0.5 - 0.0 * 0.0) + abs(1.0 - 0.0)) / 1e4
    assert abs(out["returns"][0] - (gross0 - cost0)) < 1e-9
    assert out["nonzero"] == 2


def test_straddle_unpriceable_contributes_zero():
    bars = [
        {"close": 100.0, "dt": 1.0, "straddle": None},
        {"close": 101.0, "dt": 1.0, "straddle": {"iv": 0.8, "delta": 0.5, "gamma": 0.0,
                                                 "theta": 0.0, "vega": 100.0}},
        {"close": 99.0, "dt": 1.0, "straddle": {"iv": 0.79, "delta": 0.5, "gamma": 0.0,
                                                "theta": 0.0, "vega": 100.0}},
    ]
    out = e61.strategy_returns(bars, [1.0, 1.0, 0.0], cost_bps=5.0)
    # Bar 0 has straddle_k=None -> 0.0 return
    assert out["returns"][0] == 0.0


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=2)  # far below floor
    fl = e61._underlying_floor(cap)
    assert fl["ok"] is False
    assert any(not v for v in fl["checks"].values())


def test_evaluate_config_runs():
    cap = _craft_capture(n_bars=80, seed=3)
    av = e61.straddle_series_from_surface(cap)
    res = e61.evaluate_config(
        cap, av, tox_signal="tox", bar_seconds=300.0,
    )
    assert res["underlying"] == "BTC"
    assert res["n_returns"] > 0
    assert "sharpe" in res and "pass" in res


def test_protocol_and_floor_constants():
    p = e61.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_surface_snapshots_per_underlying"] == 100
    assert p["floor"]["min_option_trades_per_underlying"] == 2000
    assert set(p["tox_signals"]) == {"tox", "imbalance"}
    assert p["cost_bps"] == 5.0
    assert p["bar_seconds_grid"] == [60.0, 300.0]


def test_run_eval61_no_write_blocks_below_floor():
    cap = _craft_capture(n_bars=40, seed=7)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e61.run_eval61(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
