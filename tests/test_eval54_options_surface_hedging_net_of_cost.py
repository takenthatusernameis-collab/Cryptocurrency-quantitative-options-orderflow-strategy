"""Unit tests for EVAL-54 real Deribit options vol-surface/greeks delta-hedged net-of-cost falsification.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network. Marks are generated from Black-Scholes at a
known IV so the IV solve and greeks are exercised end-to-end.
"""

from __future__ import annotations

import math
import random

from src.features.options_pricing import PricingInputs, black_scholes_price

import scripts.eval54_options_surface_hedging_net_of_cost as e54

EXPIRY_A = "2026-12-30T08:00:00Z"
EXPIRY_B = "2026-11-27T08:00:00Z"
_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
_DAY = 365.25 * 86400.0


def _t_years(expiry_iso, state_time_s):
    from datetime import datetime, timezone

    exp = datetime.fromisoformat(expiry_iso.replace("Z", "+00:00"))
    now = datetime.fromtimestamp(state_time_s, tz=timezone.utc)
    return (exp - now).total_seconds() / _DAY


def _mark_btc(spot, strike, t_years, iv, opt):
    price_usd = black_scholes_price(PricingInputs(
        spot=float(spot), strike=float(strike), rate=0.0, volatility=float(iv),
        time_to_expiry=max(float(t_years), 1e-6), option_type=opt, seed=42,
    ))
    return price_usd / float(spot)


def _craft_capture(n_bars=160, seed=0, inst="BTC"):
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    iv = 0.55
    strikes = [-1000, -500, 0, 500, 1000]
    candles = []
    trades = []
    snaps = []
    tid = 0
    for i in range(n_bars):
        drift = rng.uniform(-1, 1) * 1e-4
        px = max(1.0, px * (1.0 + drift))
        bar_ms = _BASE_MS + i * _BAR_MS
        state_time_s = (bar_ms + _BAR_MS) // 1000
        candles.append({"ts": bar_ms, "open": px, "high": px, "low": px, "close": px})
        quotes = []
        # expiry A: 5 strikes x call/put
        for k in strikes:
            strike = round(px + k, 2)
            ta = _t_years(EXPIRY_A, state_time_s)
            for opt in ("call", "put"):
                mark = _mark_btc(px, strike, ta, iv, opt)
                quotes.append({
                    "symbol": f"{inst}-A-{int(strike)}-{opt[0].upper()}-{i}",
                    "underlying": inst, "strike": strike, "expiry": EXPIRY_A,
                    "option_type": opt, "bid": mark * 0.98, "ask": mark * 1.02,
                    "mark": mark, "open_interest": 10.0, "volume": 1.0,
                    "timestamp": "2023-11-14T00:00:00Z",
                })
        # expiry B: 3 strikes x call/put
        for k in (-500, 0, 500):
            strike = round(px + k, 2)
            tb = _t_years(EXPIRY_B, state_time_s)
            for opt in ("call", "put"):
                mark = _mark_btc(px, strike, tb, iv, opt)
                quotes.append({
                    "symbol": f"{inst}-B-{int(strike)}-{opt[0].upper()}-{i}",
                    "underlying": inst, "strike": strike, "expiry": EXPIRY_B,
                    "option_type": opt, "bid": mark * 0.98, "ask": mark * 1.02,
                    "mark": mark, "open_interest": 10.0, "volume": 1.0,
                    "timestamp": "2023-11-14T00:00:00Z",
                })
        snaps.append({"bar_ms": bar_ms, "spot": px, "quotes": quotes})
        # a few signed trades per bar (for the floor parity)
        for _ in range(4):
            tid += 1
            trades.append({
                "ts": bar_ms + rng.randint(1, _BAR_MS - 1),
                "instrument": f"{inst}-A-{int(round(px))}-C-{i}",
                "direction": "buy" if rng.random() < 0.5 else "sell",
                "amount": rng.uniform(0.1, 1.0), "price": 0.02,
                "index_price": px, "iv": 55.0, "option_type": "call",
                "strike": round(px, 2), "expiry": EXPIRY_A,
            })

    return {
        "schema": "deribit_options_surface_capture_v1",
        "underlying": inst,
        "venue": "deribit",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "perp_resolution": "1",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": snaps},
        "option_trades": trades,
        "perp_candles": candles,
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit"},
    }


def test_iv_and_delta_ranges():
    from datetime import datetime, timezone

    cap = _craft_capture(n_bars=6, seed=0)
    snap = cap["surface"]["snapshots"][0]
    spot = snap["spot"]
    state_time = datetime.fromtimestamp((snap["bar_ms"] + _BAR_MS) // 1000, tz=timezone.utc)
    call_q = next(q for q in snap["quotes"]
                  if q["option_type"] == "call" and abs(q["strike"] - spot) < 1)
    g = e54._iv_and_delta(call_q["mark"], call_q["bid"], call_q["ask"], spot,
                          call_q["strike"], call_q["expiry"], state_time, "call")
    assert g is not None
    assert 0.0 <= g["delta"] <= 1.0
    assert math.isfinite(g["price_usd"]) and g["price_usd"] > 0.0
    # IV should be recovered close to the true 0.55 (ATM, well above intrinsic)
    assert abs(g["iv"] - 0.55) < 0.05


def test_delta_hedge_series_shape_and_costs():
    cap = _craft_capture(n_bars=120, seed=1)
    s = e54._delta_hedge_series(cap, structure="atm_straddle", expiry_iso=EXPIRY_A, rebalance=1)
    assert s["n_states"] >= 100
    assert s["n_returns"] == s["n_states"] - 1
    assert len(s["returns"]) == s["n_returns"]
    assert all(math.isfinite(r) for r in s["returns"])
    assert all(c >= -1e-12 for c in s["cost_returns"])
    assert s["entry_spread_usd"] >= 0.0 and s["exit_spread_usd"] >= 0.0


def test_rebalance_reduces_turnover():
    cap = _craft_capture(n_bars=120, seed=2)
    s1 = e54._delta_hedge_series(cap, structure="atm_call", expiry_iso=EXPIRY_A, rebalance=1)
    s2 = e54._delta_hedge_series(cap, structure="atm_call", expiry_iso=EXPIRY_A, rebalance=2)
    assert s2["n_hedge_rebalances"] <= s1["n_hedge_rebalances"]
    assert s1["n_hedge_rebalances"] >= s2["n_hedge_rebalances"]


def test_config_grid_covers_expiries_and_rebalance():
    cap = _craft_capture(n_bars=30, seed=3)
    expiries = e54._distinct_expiries(cap)
    assert expiries == sorted(expiries) and len(expiries) >= 2
    grid = e54._config_grid(cap)
    structures = {g["structure"] for g in grid}
    assert structures == set(e54.STRUCTURES)
    assert {g["rebalance"] for g in grid} == set(e54.REBALANCE_CHOICES)
    assert {g["expiry"] for g in grid} == set(expiries[:2])


def test_evaluate_config_runs():
    cap = _craft_capture(n_bars=100, seed=4)
    res = e54.evaluate_config(cap, structure="atm_call", expiry_iso=EXPIRY_A, rebalance=1)
    assert res["underlying"] == "BTC"
    assert res["n_returns"] >= e54.MIN_RETURNS_PER_CONFIG
    assert "sharpe" in res and "pass" in res
    assert 0.0 <= res["median_iv"] <= 5.0
    assert "bootstrap_ci" in res and "permutation_p" in res


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=5)  # far below floor
    fl = e54._underlying_floor(cap)
    assert fl["ok"] is False
    assert any(not v for v in fl["checks"].values())


def test_protocol_and_floor_constants():
    p = e54.build_protocol("data/raw/eval54")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_surface_snapshots_per_underlying"] == 100
    assert p["floor"]["min_option_trades_per_underlying"] == 2000
    assert set(p["structures"]) == set(e54.STRUCTURES)
    assert p["hedge_fee_bps"] == e54.HEDGE_FEE_BPS
    assert p["kill_switch_max_dd"] == e54.KILL_SWITCH_MAX_DD


def test_prereg_payload_from_constants_only():
    p = e54._prereg_payload("2026-11-15T18:00:00Z", "data/raw/eval54", "TASK")
    assert p["prereg_id"] == e54.PREREG_ID
    assert p["generated_at"] == "2026-11-15T18:00:00Z"
    assert p["protocol"]["eval"] == "EVAL-54"
    # prereg is built purely from protocol constants (no measurement leakage)
    assert "surface_to_greeks" in p["protocol"] and "go_bar" in p["protocol"]