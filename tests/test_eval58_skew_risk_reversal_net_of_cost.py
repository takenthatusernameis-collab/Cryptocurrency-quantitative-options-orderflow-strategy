"""Unit tests for EVAL-58 real Deribit options vol-surface/greeks skew /
risk-reversal (25Δ) net-of-cost falsification.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network. Marks are generated from Black-Scholes at a
known IV (per wing: call IV / put IV, optionally ramped so the put-call skew
moves); the perpetual carries a small random walk so the delta-hedge sees a real
``dS``. EVAL-58 is the *skew / risk-reversal (25Δ)* book (long one 25Δ wing /
short the other, sized by the skew mean-reversion deviation, delta-hedged in the
perpetual), distinct from EVAL-54's short-vol delta-hedging, EVAL-55's long-gamma
gamma-scalping, EVAL-56's term-structure calendar spread and EVAL-57's VRP
straddle.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timezone

from src.features.options_pricing import PricingInputs, black_scholes_price

import scripts.eval58_skew_risk_reversal_net_of_cost as e58

EXPIRY = "2026-12-30T08:00:00Z"  # front expiry (~29d after the fixture window)
_BAR_MS = 300_000
_DAY = 365.25 * 86400.0
_BASE_MS = int(
    datetime(2026, 12, 1, 0, 0, 0, tzinfo=timezone.utc).timestamp() * 1000
)
_BASE_MS = (_BASE_MS // _BAR_MS) * _BAR_MS  # 5m-aligned
STRIKES_PCT = (-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15)


def _t_years(expiry_iso, state_time_s):
    exp = datetime.fromisoformat(expiry_iso.replace("Z", "+00:00"))
    now = datetime.fromtimestamp(state_time_s, tz=timezone.utc)
    return (exp - now).total_seconds() / _DAY


def _mark_btc(spot, strike, t_years, iv, opt):
    price_usd = black_scholes_price(PricingInputs(
        spot=float(spot), strike=float(strike), rate=0.0, volatility=float(iv),
        time_to_expiry=max(float(t_years), 1e-6), option_type=opt, seed=42,
    ))
    return price_usd / float(spot)


def _craft_capture(n_bars=160, seed=0, inst="BTC", iv_call=0.5, iv_put=0.5,
                   iv_put_end=None, spot_px=60000.0, drop_puts=False,
                   drop_calls=False):
    """Deterministic capture. Puts are marked at ``iv_put`` (optionally ramping
    linearly to ``iv_put_end`` across bars) and calls at ``iv_call`` so the
    put-call skew = IV_put - IV_call moves. Perp has a small random walk so the
    hedge sees a real ``dS``."""
    rng = random.Random(seed)
    px = spot_px
    n = max(1, n_bars)
    candles = []
    trades = []
    snaps = []
    tid = 0
    for i in range(n):
        bar_ms = _BASE_MS + i * _BAR_MS
        state_time_s = (bar_ms + _BAR_MS) // 1000
        bar_closes = []
        for m in range(5):
            drift = rng.gauss(0.0, 1.0) * 0.02 / math.sqrt(_DAY / 60.0)
            px = max(1.0, px * (1.0 + drift))
            ts = bar_ms + m * 60_000
            candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
            bar_closes.append(px)
        spot = bar_closes[-1]
        if iv_put_end is None:
            iv_p = float(iv_put)
        else:
            frac = i / max(1, n - 1)
            iv_p = float(iv_put) + (float(iv_put_end) - float(iv_put)) * frac
        ta = _t_years(EXPIRY, state_time_s)
        quotes = []
        for kp in STRIKES_PCT:
            strike = round(spot * (1.0 + kp), 2)
            for opt in ("call", "put"):
                if drop_calls and opt == "call":
                    continue
                if drop_puts and opt == "put":
                    continue
                iv = iv_call if opt == "call" else iv_p
                mark = _mark_btc(spot, strike, ta, iv, opt)
                quotes.append({
                    "symbol": f"{inst}-F-{int(strike)}-{opt[0].upper()}-{i}",
                    "underlying": inst, "strike": strike, "expiry": EXPIRY,
                    "option_type": opt, "bid": mark * 0.98, "ask": mark * 1.02,
                    "mark": mark, "open_interest": 10.0, "volume": 1.0,
                    "timestamp": "2026-11-14T00:00:00Z",
                })
        snaps.append({"bar_ms": bar_ms, "spot": spot, "quotes": quotes})
        for _ in range(4):
            tid += 1
            trades.append({
                "ts": bar_ms + rng.randint(1, _BAR_MS - 1),
                "instrument": f"{inst}-F-{int(round(spot))}-C-{i}",
                "direction": "buy" if rng.random() < 0.5 else "sell",
                "amount": rng.uniform(0.1, 1.0), "price": 0.02,
                "index_price": spot, "iv": 50.0, "option_type": "call",
                "strike": round(spot, 2), "expiry": EXPIRY,
            })

    return {
        "schema": "deribit_options_surface_capture_v1",
        "underlying": inst,
        "venue": "deribit",
        "window_start": "2026-12-01T00:00:00Z",
        "window_end": "2026-12-02T00:00:00Z",
        "perp_resolution": "1",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": snaps},
        "option_trades": trades,
        "perp_candles": candles,
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit"},
    }


# ---------------------------------------------------------------------------
# IV / greeks + 25Δ wing selection
# ---------------------------------------------------------------------------
def test_iv_and_greeks_ranges():
    cap = _craft_capture(n_bars=6, seed=0, iv_call=0.55, iv_put=0.55)
    snap = cap["surface"]["snapshots"][0]
    spot = snap["spot"]
    state_time = datetime.fromtimestamp((snap["bar_ms"] + _BAR_MS) // 1000, tz=timezone.utc)
    call_q = next(q for q in snap["quotes"]
                  if q["option_type"] == "call" and q["expiry"] == EXPIRY)
    g = e58._iv_and_greeks(call_q["mark"], call_q["bid"], call_q["ask"], spot,
                           call_q["strike"], call_q["expiry"], state_time, "call")
    assert g is not None
    assert 0.0 <= g["delta"] <= 1.0
    assert g["gamma"] >= 0.0
    assert math.isfinite(g["price_usd"]) and g["price_usd"] > 0.0
    assert abs(g["iv"] - 0.55) < 0.05


def test_select_rr_wings_picks_25d():
    cap = _craft_capture(n_bars=10, seed=1, iv_call=0.5, iv_put=0.5)
    enriched = e58._enrich_snapshots(cap)
    pick = e58._select_rr_wings(enriched[0]["by_expiry"], EXPIRY)
    assert pick is not None
    call, put = pick["call"], pick["put"]
    # ~25Δ: |delta| near 0.25 on both wings.
    assert abs(abs(call["delta"]) - 0.25) < 0.15
    assert abs(abs(put["delta"]) - 0.25) < 0.15
    # Call is OTM above, put OTM below.
    assert call["delta"] > 0.0 and put["delta"] < 0.0
    assert call["strike"] > put["strike"]
    # Both wings carry a finite positive IV.
    assert math.isfinite(call["iv"]) and call["iv"] > 0.0
    assert math.isfinite(put["iv"]) and put["iv"] > 0.0


def test_select_rr_wings_invalid_when_one_side_missing():
    cap = _craft_capture(n_bars=10, seed=1, drop_puts=True)
    enriched = e58._enrich_snapshots(cap)
    assert e58._select_rr_wings(enriched[0]["by_expiry"], EXPIRY) is None


# ---------------------------------------------------------------------------
# Risk-reversal series (shape, costs, validity)
# ---------------------------------------------------------------------------
def test_rr_series_shape_and_costs():
    cap = _craft_capture(n_bars=120, seed=2, iv_call=0.5, iv_put=0.5, iv_put_end=0.9)
    s = e58._rr_series(cap, expiry=EXPIRY, skew_lookback=12,
                       skew_target=0.5, size_cap=1.0, rebalance=1)
    assert s["valid"] is True
    assert s["n_states"] >= 50
    assert s["n_returns"] == s["n_states"] - 1
    assert len(s["returns"]) == s["n_returns"]
    assert all(math.isfinite(r) for r in s["returns"])
    assert all(c >= -1e-12 for c in s["cost_returns"])
    assert s["entry_spread_usd"] >= 0.0 and s["exit_spread_usd"] >= 0.0
    assert math.isfinite(s["median_call_iv"]) and s["median_call_iv"] > 0
    assert math.isfinite(s["median_put_iv"]) and s["median_put_iv"] > 0
    assert math.isfinite(s["median_skew"])
    # Nonzero P&L exists (skew is ramping so positions are taken).
    assert any(abs(r) > 1e-12 for r in s["returns"])
    # ~25Δ wings sit roughly around spot.
    assert s["strike_call"] > 0.0 and s["strike_put"] > 0.0


def test_rr_series_invalid_no_put_wing():
    cap = _craft_capture(n_bars=120, seed=2, drop_puts=True)
    s = e58._rr_series(cap, expiry=EXPIRY, skew_lookback=12,
                       skew_target=0.5, size_cap=1.0, rebalance=1)
    assert s["valid"] is False
    assert s["returns"] == []
    assert "error" in s


def test_rr_side_long_when_skew_rising():
    """iv_put ramps up (skew rises) => later states are LONG risk reversal."""
    cap = _craft_capture(n_bars=140, seed=3, iv_call=0.4, iv_put=0.4, iv_put_end=1.1)
    states = e58._rr_states(cap, expiry=EXPIRY, skew_lookback=12,
                            skew_target=0.5, size_cap=1.0)
    active = [s for s in states if s.get("active")]
    half = len(active) // 2
    tail = active[half:]
    long_steps = sum(1 for s in tail if s["side"] > 0)
    short_steps = sum(1 for s in tail if s["side"] < 0)
    assert long_steps > short_steps, f"expected long-RR bias: long={long_steps} short={short_steps}"


def test_rr_side_short_when_skew_falling():
    """iv_put ramps down (skew falls) => later states are SHORT risk reversal."""
    cap = _craft_capture(n_bars=140, seed=3, iv_call=0.4, iv_put=1.1, iv_put_end=0.4)
    states = e58._rr_states(cap, expiry=EXPIRY, skew_lookback=12,
                            skew_target=0.5, size_cap=1.0)
    active = [s for s in states if s.get("active")]
    half = len(active) // 2
    tail = active[half:]
    long_steps = sum(1 for s in tail if s["side"] > 0)
    short_steps = sum(1 for s in tail if s["side"] < 0)
    assert short_steps > long_steps, f"expected short-RR bias: long={long_steps} short={short_steps}"


def test_rebalance_reduces_turnover():
    cap = _craft_capture(n_bars=120, seed=4, iv_call=0.4, iv_put=0.4, iv_put_end=1.0)
    s1 = e58._rr_series(cap, expiry=EXPIRY, skew_lookback=12,
                        skew_target=0.5, size_cap=1.0, rebalance=1)
    s2 = e58._rr_series(cap, expiry=EXPIRY, skew_lookback=12,
                        skew_target=0.5, size_cap=1.0, rebalance=2)
    assert s2["n_hedge_rebalances"] <= s1["n_hedge_rebalances"]


# ---------------------------------------------------------------------------
# Config grid + evaluation
# ---------------------------------------------------------------------------
def test_config_grid_covers_params():
    cap = _craft_capture(n_bars=30, seed=5, iv_call=0.5, iv_put=0.5, iv_put_end=0.8)
    expiries = e58._distinct_expiries(cap)
    assert expiries == sorted(expiries) and len(expiries) >= 1
    grid = e58._config_grid(cap)
    structures = {g["structure"] for g in grid}
    assert structures == set(e58.STRUCTURES)
    assert all(g["expiry"] == expiries[0] for g in grid)
    assert {g["skew_lookback"] for g in grid} == set(e58.SKEW_LOOKBACK_BARS)
    assert {g["skew_target"] for g in grid} == set(e58.SKEW_TARGET_CHOICES)
    assert {g["size_cap"] for g in grid} == set(e58.SIZE_CAP_CHOICES)
    assert {g["rebalance"] for g in grid} == set(e58.REBALANCE_CHOICES)
    expected = (len(e58.STRUCTURES) * len(e58.SKEW_LOOKBACK_BARS)
                * len(e58.SKEW_TARGET_CHOICES) * len(e58.SIZE_CAP_CHOICES)
                * len(e58.REBALANCE_CHOICES))
    assert len(grid) == expected


def test_evaluate_config_runs():
    cap = _craft_capture(n_bars=100, seed=6, iv_call=0.4, iv_put=0.4, iv_put_end=1.0)
    res = e58.evaluate_config(cap, structure="risk_reversal_25d_delta_hedged",
                              expiry=EXPIRY, skew_lookback=12,
                              skew_target=0.5, size_cap=1.0, rebalance=1)
    assert res["underlying"] == "BTC"
    assert res["valid"] is True
    assert res["n_returns"] >= e58.MIN_RETURNS_PER_CONFIG
    assert "sharpe" in res and "pass" in res
    assert 0.0 <= res["median_call_iv"] <= 5.0
    assert 0.0 <= res["median_put_iv"] <= 5.0
    assert "bootstrap_ci" in res and "permutation_p" in res
    assert math.isfinite(res["median_skew"])


def test_evaluate_config_invalid_when_no_wing():
    cap = _craft_capture(n_bars=100, seed=6, drop_puts=True)
    res = e58.evaluate_config(cap, structure="risk_reversal_25d_delta_hedged",
                              expiry=EXPIRY, skew_lookback=12,
                              skew_target=0.5, size_cap=1.0, rebalance=1)
    assert res["valid"] is False
    assert res["pass"] is False
    assert res["n_returns"] == 0


# ---------------------------------------------------------------------------
# Floor / term structure / protocol
# ---------------------------------------------------------------------------
def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=7, iv_call=0.5, iv_put=0.5)  # far below floor
    fl = e58._underlying_floor(cap)
    assert fl["ok"] is False
    assert any(not v for v in fl["checks"].values())


def test_term_structure_viability_needs_two_expiries():
    cap = _craft_capture(n_bars=150, seed=8, iv_call=0.5, iv_put=0.5)
    ts = e58._term_structure_viability(cap)
    # single-expiry fixture: only one expiry => not viable
    assert ts["n_viable_expiries"] == 1
    assert ts["viable"] is False


def test_protocol_and_floor_constants():
    p = e58.build_protocol("data/raw/eval58")
    assert p["eval"] == "EVAL-58"
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_surface_snapshots_per_underlying"] == 100
    assert p["floor"]["min_option_trades_per_underlying"] == 2000
    assert p["floor"]["term_structure_min_expiries"] == 2
    assert p["floor"]["term_structure_min_snapshots_per_expiry"] == 100
    assert set(p["structures"]) == set(e58.STRUCTURES)
    assert p["hedge_fee_bps"] == e58.HEDGE_FEE_BPS
    assert p["kill_switch_max_dd"] == e58.KILL_SWITCH_MAX_DD
    assert p["delta_target"] == e58.DELTA_TARGET


def test_prereg_payload_from_constants_only():
    p = e58._prereg_payload("2026-11-15T20:10:00Z", "data/raw/eval58", "TASK")
    assert p["prereg_id"] == e58.PREREG_ID
    assert p["generated_at"] == "2026-11-15T20:10:00Z"
    assert p["protocol"]["eval"] == "EVAL-58"
    assert "surface_to_iv" in p["protocol"] and "go_bar" in p["protocol"]
    assert "risk-reversal" in p["hypothesis"].lower()


def test_rr_structure_distinct_from_straddle_and_calendar():
    """EVAL-58 must be the 25Δ risk reversal, not EVAL-57's VRP straddle or
    EVAL-56's calendar spread."""
    assert e58.STRUCTURES == ("risk_reversal_25d_delta_hedged",)
    assert not any(s.startswith("vrp_straddle") for s in e58.STRUCTURES)
    assert not any(s.startswith("long_near_short_far") for s in e58.STRUCTURES)