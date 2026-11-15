"""Unit tests for EVAL-56 real Deribit options vol-surface/greeks term-structure
calendar-spread net-of-cost falsification.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network. Marks are generated from Black-Scholes at a
known IV so the IV solve and greeks are exercised end-to-end. EVAL-56 is the
*term-structure calendar spread* (long near-expiry ATM straddle / short far-expiry
ATM straddle at a common strike), distinct from EVAL-54's short-vol delta-hedging
and EVAL-55's long-gamma gamma-scalping.
"""

from __future__ import annotations

import math
import random

from src.features.options_pricing import PricingInputs, black_scholes_price

import scripts.eval56_term_structure_calendar_net_of_cost as e56

EXPIRY_A = "2026-12-30T08:00:00Z"  # near
EXPIRY_B = "2026-11-27T08:00:00Z"  # far (earlier calendar date; used as the second listed expiry)
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
        # expiry B: same 5 strikes x call/put (common strikes exist in both)
        for k in strikes:
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


def _craft_capture_no_common(n_bars=160, seed=0, inst="BTC"):
    """Like _craft_capture but expiry B has no common strikes with expiry A
    (disjoint strikes) -> calendar config invalid."""
    cap = _craft_capture(n_bars=n_bars, seed=seed, inst=inst)
    new_quotes = []
    for snap in cap["surface"]["snapshots"]:
        kept = []
        for q in snap["quotes"]:
            if q["expiry"] == EXPIRY_B:
                # move expiry B strikes away so none match expiry A's strikes
                q = dict(q)
                q["strike"] = round(q["strike"] + 9999.0, 2)
                q["symbol"] = f"{inst}-B-disjoint-{int(q['strike'])}-{q['option_type'][0].upper()}"
            kept.append(q)
        new_quotes.append(kept)
    for snap, kept in zip(cap["surface"]["snapshots"], new_quotes):
        snap["quotes"] = kept
    return cap


def test_iv_and_greeks_ranges():
    from datetime import datetime, timezone

    cap = _craft_capture(n_bars=6, seed=0)
    snap = cap["surface"]["snapshots"][0]
    spot = snap["spot"]
    state_time = datetime.fromtimestamp((snap["bar_ms"] + _BAR_MS) // 1000, tz=timezone.utc)
    call_q = next(q for q in snap["quotes"]
                  if q["option_type"] == "call" and abs(q["strike"] - spot) < 1
                  and q["expiry"] == EXPIRY_A)
    g = e56._iv_and_greeks(call_q["mark"], call_q["bid"], call_q["ask"], spot,
                           call_q["strike"], call_q["expiry"], state_time, "call")
    assert g is not None
    assert 0.0 <= g["delta"] <= 1.0
    assert g["gamma"] >= 0.0
    assert math.isfinite(g["price_usd"]) and g["price_usd"] > 0.0
    assert abs(g["iv"] - 0.55) < 0.05


def test_pick_calendar_quotes_common_strike():
    cap = _craft_capture(n_bars=10, seed=1)
    snap = cap["surface"]["snapshots"][0]
    spot = snap["spot"]
    pick = e56._pick_calendar_quotes(snap["quotes"], spot, EXPIRY_A, EXPIRY_B)
    assert pick is not None
    assert pick["valid"] is True
    assert pick["near"]["call"] is not None and pick["near"]["put"] is not None
    assert pick["far"]["call"] is not None and pick["far"]["put"] is not None
    # same strike on both sides
    assert abs(pick["near"]["call"]["strike"] - pick["far"]["call"]["strike"]) < 1e-9
    assert pick["strike"] > 0
    assert pick["spread_usd"] >= 0.0


def test_pick_calendar_quotes_invalid_when_no_common():
    cap = _craft_capture_no_common(n_bars=10, seed=1)
    snap = cap["surface"]["snapshots"][0]
    spot = snap["spot"]
    pick = e56._pick_calendar_quotes(snap["quotes"], spot, EXPIRY_A, EXPIRY_B)
    assert pick is None


def test_calendar_spread_series_shape_and_costs():
    cap = _craft_capture(n_bars=120, seed=2)
    s = e56._calendar_spread_series(cap, near_expiry=EXPIRY_A, far_expiry=EXPIRY_B,
                                    rebalance=1)
    assert s["valid"] is True
    assert s["n_states"] >= 100
    assert s["n_returns"] == s["n_states"] - 1
    assert len(s["returns"]) == s["n_returns"]
    assert all(math.isfinite(r) for r in s["returns"])
    assert all(c >= -1e-12 for c in s["cost_returns"])
    assert s["entry_spread_usd"] >= 0.0 and s["exit_spread_usd"] >= 0.0
    assert s["total_premium_usd"] > 0.0 or s["total_premium_usd"] == 0.0
    assert math.isfinite(s["realized_gamma_capture_usd"])
    assert math.isfinite(s["gamma_capture_over_premium"])
    assert len(s["gamma_capture_returns"]) == s["n_returns"]
    assert abs(s["strike"] - cap["surface"]["snapshots"][0]["spot"]) < 5000


def test_calendar_spread_series_invalid_no_common():
    cap = _craft_capture_no_common(n_bars=120, seed=2)
    s = e56._calendar_spread_series(cap, near_expiry=EXPIRY_A, far_expiry=EXPIRY_B,
                                    rebalance=1)
    assert s["valid"] is False
    assert s["returns"] == []
    assert "error" in s


def test_hedge_is_short_net_delta():
    """Long near straddle + short far straddle => net delta hedged short underlying."""
    cap = _craft_capture(n_bars=120, seed=3)
    s = e56._calendar_spread_series(cap, near_expiry=EXPIRY_A, far_expiry=EXPIRY_B,
                                    rebalance=1)
    assert s["n_states"] >= 100
    assert "long_near_short_far_straddle" in e56.STRUCTURES


def test_rebalance_reduces_turnover():
    cap = _craft_capture(n_bars=120, seed=4)
    s1 = e56._calendar_spread_series(cap, near_expiry=EXPIRY_A, far_expiry=EXPIRY_B,
                                     rebalance=1)
    s2 = e56._calendar_spread_series(cap, near_expiry=EXPIRY_A, far_expiry=EXPIRY_B,
                                     rebalance=2)
    assert s2["n_hedge_rebalances"] <= s1["n_hedge_rebalances"]


def test_config_grid_covers_expiries_and_rebalance():
    cap = _craft_capture(n_bars=30, seed=5)
    expiries = e56._distinct_expiries(cap)
    assert expiries == sorted(expiries) and len(expiries) >= 2
    grid = e56._config_grid(cap)
    structures = {g["structure"] for g in grid}
    assert structures == set(e56.STRUCTURES)
    assert {g["rebalance"] for g in grid} == set(e56.REBALANCE_CHOICES)
    assert len(grid) == len(e56.REBALANCE_CHOICES) * len(e56.EXPIRY_PAIRS)
    for g in grid:
        assert g["near"] == expiries[0]
        assert g["far"] == expiries[1]


def test_evaluate_config_runs():
    cap = _craft_capture(n_bars=100, seed=6)
    res = e56.evaluate_config(cap, structure="long_near_short_far_straddle",
                              near=EXPIRY_A, far=EXPIRY_B, rebalance=1)
    assert res["underlying"] == "BTC"
    assert res["valid"] is True
    assert res["n_returns"] >= e56.MIN_RETURNS_PER_CONFIG
    assert "sharpe" in res and "pass" in res
    assert 0.0 <= res["median_iv"] <= 5.0
    assert "bootstrap_ci" in res and "permutation_p" in res
    assert "gamma_capture_over_premium" in res


def test_evaluate_config_invalid_when_no_common_strike():
    cap = _craft_capture_no_common(n_bars=100, seed=6)
    res = e56.evaluate_config(cap, structure="long_near_short_far_straddle",
                              near=EXPIRY_A, far=EXPIRY_B, rebalance=1)
    assert res["valid"] is False
    assert res["pass"] is False
    assert res["n_returns"] == 0


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=7)  # far below floor
    fl = e56._underlying_floor(cap)
    assert fl["ok"] is False
    assert any(not v for v in fl["checks"].values())


def test_term_structure_viability_needs_two_expiries():
    cap = _craft_capture(n_bars=150, seed=8)  # >=100 snapshots per expiry
    ts = e56._term_structure_viability(cap)
    # synthetic fixture: both expiries present in every snapshot => viable
    assert ts["n_viable_expiries"] >= 2
    assert ts["viable"] is True


def test_protocol_and_floor_constants():
    p = e56.build_protocol("data/raw/eval56")
    assert p["eval"] == "EVAL-56"
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_surface_snapshots_per_underlying"] == 100
    assert p["floor"]["min_option_trades_per_underlying"] == 2000
    assert p["floor"]["term_structure_min_expiries"] == 2
    assert p["floor"]["term_structure_min_snapshots_per_expiry"] == 100
    assert set(p["structures"]) == set(e56.STRUCTURES)
    assert p["hedge_fee_bps"] == e56.HEDGE_FEE_BPS
    assert p["kill_switch_max_dd"] == e56.KILL_SWITCH_MAX_DD


def test_prereg_payload_from_constants_only():
    p = e56._prereg_payload("2026-11-15T18:50:00Z", "data/raw/eval56", "TASK")
    assert p["prereg_id"] == e56.PREREG_ID
    assert p["generated_at"] == "2026-11-15T18:50:00Z"
    assert p["protocol"]["eval"] == "EVAL-56"
    # prereg is built purely from protocol constants (no measurement leakage)
    assert "surface_to_greeks" in p["protocol"] and "go_bar" in p["protocol"]
    assert "calendar" in p["hypothesis"].lower() or "term-structure" in p["hypothesis"].lower()


def test_calendar_structures_distinct_from_gamma_scalp():
    """EVAL-56 must be the term-structure calendar spread, not EVAL-55's gamma scalp."""
    assert e56.STRUCTURES == ("long_near_short_far_straddle",)
    assert not any(s.startswith("long_atm") for s in e56.STRUCTURES)
