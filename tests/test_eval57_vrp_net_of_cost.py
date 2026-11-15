"""Unit tests for EVAL-57 real Deribit options vol-surface/greeks volatility risk
premium (VRP) / realized-vs-implied vol net-of-cost falsification.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network. Marks are generated from Black-Scholes at a
known IV; perp candles carry a separate realized vol so the VRP spread (IV -
realized) is exercised end-to-end. EVAL-57 is the *VRP straddle* (long/short ATM
straddle sized by the IV-realized-vol spread, delta-hedged in the perpetual),
distinct from EVAL-54's short-vol delta-hedging, EVAL-55's long-gamma gamma-scalping
and EVAL-56's term-structure calendar spread.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timezone

from src.features.options_pricing import PricingInputs, black_scholes_price

import scripts.eval57_vrp_net_of_cost as e57

EXPIRY = "2026-12-30T08:00:00Z"  # front expiry
_BASE_MS = 1_700_000_100_000  # 5m-aligned (multiple of 300_000)
_BAR_MS = 300_000
_DAY = 365.25 * 86400.0


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


def _craft_capture(n_bars=160, seed=0, inst="BTC", iv=0.55, realized_vol=0.35,
                   spot_px=60000.0):
    """Build a deterministic capture: options marked at `iv`, perp candles with
    `realized_vol` so IV != realized (nonzero VRP spread)."""
    rng = random.Random(seed)
    px = spot_px
    strikes = [-1000, -500, 0, 500, 1000]
    candles = []
    trades = []
    snaps = []
    tid = 0
    minute = 0
    for i in range(n_bars):
        bar_ms = _BASE_MS + i * _BAR_MS
        state_time_s = (bar_ms + _BAR_MS) // 1000
        # 1m perp candles covering this 5m bar (5 candles), last close at bar end.
        bar_closes = []
        for m in range(5):
            drift = rng.uniform(-1, 1) * realized_vol / math.sqrt(_DAY / 60.0)
            px = max(1.0, px * (1.0 + drift))
            ts = bar_ms + m * 60_000
            candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
            bar_closes.append(px)
            minute += 1
        spot = bar_closes[-1]
        ta = _t_years(EXPIRY, state_time_s)
        quotes = []
        for k in strikes:
            strike = round(spot + k, 2)
            for opt in ("call", "put"):
                mark = _mark_btc(spot, strike, ta, iv, opt)
                quotes.append({
                    "symbol": f"{inst}-F-{int(strike)}-{opt[0].upper()}-{i}",
                    "underlying": inst, "strike": strike, "expiry": EXPIRY,
                    "option_type": opt, "bid": mark * 0.98, "ask": mark * 1.02,
                    "mark": mark, "open_interest": 10.0, "volume": 1.0,
                    "timestamp": "2023-11-14T00:00:00Z",
                })
        snaps.append({"bar_ms": bar_ms, "spot": spot, "quotes": quotes})
        for _ in range(4):
            tid += 1
            trades.append({
                "ts": bar_ms + rng.randint(1, _BAR_MS - 1),
                "instrument": f"{inst}-F-{int(round(spot))}-C-{i}",
                "direction": "buy" if rng.random() < 0.5 else "sell",
                "amount": rng.uniform(0.1, 1.0), "price": 0.02,
                "index_price": spot, "iv": 55.0, "option_type": "call",
                "strike": round(spot, 2), "expiry": EXPIRY,
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
    """Like _craft_capture but call strikes shifted so no call+put common strike."""
    cap = _craft_capture(n_bars=n_bars, seed=seed, inst=inst)
    for snap in cap["surface"]["snapshots"]:
        new_quotes = []
        for q in snap["quotes"]:
            if q["option_type"] == "call":
                q = dict(q)
                q["strike"] = round(q["strike"] + 9999.0, 2)
                q["symbol"] = f"{inst}-F-disjoint-{int(q['strike'])}-{q['option_type'][0].upper()}"
            new_quotes.append(q)
        snap["quotes"] = new_quotes
    return cap


def test_iv_and_greeks_ranges():
    cap = _craft_capture(n_bars=6, seed=0)
    snap = cap["surface"]["snapshots"][0]
    spot = snap["spot"]
    state_time = datetime.fromtimestamp((snap["bar_ms"] + _BAR_MS) // 1000, tz=timezone.utc)
    call_q = next(q for q in snap["quotes"]
                  if q["option_type"] == "call" and abs(q["strike"] - spot) < 1
                  and q["expiry"] == EXPIRY)
    g = e57._iv_and_greeks(call_q["mark"], call_q["bid"], call_q["ask"], spot,
                           call_q["strike"], call_q["expiry"], state_time, "call")
    assert g is not None
    assert 0.0 <= g["delta"] <= 1.0
    assert g["gamma"] >= 0.0
    assert math.isfinite(g["price_usd"]) and g["price_usd"] > 0.0
    assert abs(g["iv"] - 0.55) < 0.05


def test_pick_straddle_quotes_common_strike():
    cap = _craft_capture(n_bars=10, seed=1)
    snap = cap["surface"]["snapshots"][0]
    spot = snap["spot"]
    pick = e57._pick_straddle_quotes(snap["quotes"], spot, EXPIRY)
    assert pick is not None
    assert pick["valid"] is True
    assert pick["call"] is not None and pick["put"] is not None
    assert abs(pick["call"]["strike"] - pick["put"]["strike"]) < 1e-9
    assert pick["strike"] > 0
    assert pick["spread_usd"] >= 0.0


def test_pick_straddle_quotes_invalid_when_no_common():
    cap = _craft_capture_no_common(n_bars=10, seed=1)
    snap = cap["surface"]["snapshots"][0]
    spot = snap["spot"]
    pick = e57._pick_straddle_quotes(snap["quotes"], spot, EXPIRY)
    assert pick is None


def test_vrp_series_shape_and_costs():
    cap = _craft_capture(n_bars=120, seed=2, iv=0.55, realized_vol=0.35)
    s = e57._vrp_series(cap, expiry=EXPIRY, lookback_bars=12,
                        vol_target=0.5, size_cap=1.0, rebalance=1)
    assert s["valid"] is True
    assert s["n_states"] >= 50
    assert s["n_returns"] == s["n_states"] - 1
    assert len(s["returns"]) == s["n_returns"]
    assert all(math.isfinite(r) for r in s["returns"])
    assert all(c >= -1e-12 for c in s["cost_returns"])
    assert s["entry_spread_usd"] >= 0.0 and s["exit_spread_usd"] >= 0.0
    assert s["total_premium_usd"] > 0.0
    assert math.isfinite(s["median_iv"]) and s["median_iv"] > 0
    assert math.isfinite(s["median_realized_vol"]) and s["median_realized_vol"] > 0
    assert abs(s["mean_vrp_spread"]) > 0  # IV != realized => nonzero VRP spread
    assert abs(s["strike"] - cap["surface"]["snapshots"][0]["spot"]) < 5000


def test_vrp_series_invalid_no_common():
    cap = _craft_capture_no_common(n_bars=120, seed=2)
    s = e57._vrp_series(cap, expiry=EXPIRY, lookback_bars=12,
                        vol_target=0.5, size_cap=1.0, rebalance=1)
    assert s["valid"] is False
    assert s["returns"] == []
    assert "error" in s


def test_vrp_side_long_when_iv_below_realized():
    """IV (0.55) < realized (0.80) => long vol (side=+1)."""
    cap = _craft_capture(n_bars=100, seed=3, iv=0.55, realized_vol=0.80)
    s = e57._vrp_series(cap, expiry=EXPIRY, lookback_bars=12,
                        vol_target=0.5, size_cap=1.0, rebalance=1)
    assert s["valid"] is True
    # Rebuild states via internal: check mean side is positive (long vol bias).
    states = _capture_states(cap, EXPIRY, 12, 0.5, 1.0, 1)
    long_steps = sum(1 for st in states if st["side"] > 0)
    short_steps = sum(1 for st in states if st["side"] < 0)
    assert long_steps > short_steps, f"expected long-vol bias: long={long_steps} short={short_steps}"


def test_vrp_side_short_when_iv_above_realized():
    """IV (0.80) > realized (0.55) => short vol (side=-1)."""
    cap = _craft_capture(n_bars=100, seed=3, iv=0.80, realized_vol=0.55)
    states = _capture_states(cap, EXPIRY, 12, 0.5, 1.0, 1)
    long_steps = sum(1 for st in states if st["side"] > 0)
    short_steps = sum(1 for st in states if st["side"] < 0)
    assert short_steps > long_steps, f"expected short-vol bias: long={long_steps} short={short_steps}"


def _capture_states(cap, expiry, lookback, vol_target, size_cap, rebalance):
    """Helper: run _vrp_series internals to inspect per-state side/exposure."""
    import types
    snapshots = sorted(
        cap.get("surface", {}).get("snapshots", []) or [],
        key=lambda s: int(s.get("bar_ms") or 0),
    )
    perp_closes = e57._perp_5m_closes(cap.get("perp_candles", []) or [], e57.BAR_SECONDS)
    close_by_bar = {int(ts): px for ts, px in perp_closes}
    close_ts_sorted = [ts for ts, _ in perp_closes]
    states = []
    for snap in snapshots:
        bar_ms = int(snap.get("bar_ms") or 0)
        if bar_ms <= 0:
            continue
        spot = e57._finite(snap.get("spot"), 0.0)
        if spot <= 0.0:
            continue
        pick = e57._pick_straddle_quotes(snap.get("quotes") or [], spot, expiry)
        if not pick or not pick.get("valid"):
            continue
        state_time = datetime.fromtimestamp(
            (bar_ms + int(e57.BAR_SECONDS) * 1000) // 1000, tz=timezone.utc,
        )
        legs = []
        ok = True
        for key in ("call", "put"):
            q = pick[key]
            g = e57._iv_and_greeks(
                e57._finite(q.get("mark"), 0.0), e57._finite(q.get("bid"), 0.0),
                e57._finite(q.get("ask"), 0.0), spot, e57._finite(q.get("strike"), 0.0),
                q.get("expiry"), state_time,
                str(q.get("option_type") or key).lower(),
            )
            if g is None:
                ok = False
                break
            legs.append(g)
        if not ok or not legs:
            continue
        iv = e57._mean([l["iv"] for l in legs if math.isfinite(l["iv"])])
        if not math.isfinite(iv) or iv <= 0.0:
            continue
        try:
            idx = close_ts_sorted.index(bar_ms)
        except ValueError:
            idx = -1
        realized = e57._realized_vol_at(perp_closes, idx, lookback) if idx >= 0 else None
        if realized is None or not math.isfinite(realized) or realized <= 0.0:
            continue
        spread = iv - realized
        side = 1 if spread < 0.0 else (-1 if spread > 0.0 else 0)
        exposure = min(abs(spread) / vol_target, size_cap) if vol_target > 0 else 0.0
        if side == 0 or exposure <= 0.0:
            side = 0
            exposure = 0.0
        states.append({"side": int(side), "exposure": float(exposure),
                       "iv": float(iv), "realized": float(realized),
                       "spread": float(spread)})
    return states


def test_rebalance_reduces_turnover():
    cap = _craft_capture(n_bars=120, seed=4, iv=0.55, realized_vol=0.35)
    s1 = e57._vrp_series(cap, expiry=EXPIRY, lookback_bars=12,
                         vol_target=0.5, size_cap=1.0, rebalance=1)
    s2 = e57._vrp_series(cap, expiry=EXPIRY, lookback_bars=12,
                         vol_target=0.5, size_cap=1.0, rebalance=2)
    assert s2["n_hedge_rebalances"] <= s1["n_hedge_rebalances"]


def test_config_grid_covers_params():
    cap = _craft_capture(n_bars=30, seed=5, iv=0.55, realized_vol=0.35)
    expiries = e57._distinct_expiries(cap)
    assert expiries == sorted(expiries) and len(expiries) >= 1
    grid = e57._config_grid(cap)
    structures = {g["structure"] for g in grid}
    assert structures == set(e57.STRUCTURES)
    assert all(g["expiry"] == expiries[0] for g in grid)
    assert {g["lookback_bars"] for g in grid} == set(e57.LOOKBACK_BARS)
    assert {g["vol_target"] for g in grid} == {0.5, 1.0}
    assert {g["size_cap"] for g in grid} == {0.5, 1.0}
    assert {g["rebalance"] for g in grid} == set(e57.REBALANCE_CHOICES)
    expected = (len(e57.STRUCTURES) * len(e57.LOOKBACK_BARS) * 2 * 2 *
                len(e57.REBALANCE_CHOICES))
    assert len(grid) == expected


def test_evaluate_config_runs():
    cap = _craft_capture(n_bars=100, seed=6, iv=0.55, realized_vol=0.35)
    res = e57.evaluate_config(cap, structure="vrp_straddle_delta_hedged",
                              expiry=EXPIRY, lookback_bars=12,
                              vol_target=0.5, size_cap=1.0, rebalance=1)
    assert res["underlying"] == "BTC"
    assert res["valid"] is True
    assert res["n_returns"] >= e57.MIN_RETURNS_PER_CONFIG
    assert "sharpe" in res and "pass" in res
    assert 0.0 <= res["median_iv"] <= 5.0
    assert "bootstrap_ci" in res and "permutation_p" in res
    assert math.isfinite(res["median_realized_vol"])


def test_evaluate_config_invalid_when_no_common_strike():
    cap = _craft_capture_no_common(n_bars=100, seed=6)
    res = e57.evaluate_config(cap, structure="vrp_straddle_delta_hedged",
                              expiry=EXPIRY, lookback_bars=12,
                              vol_target=0.5, size_cap=1.0, rebalance=1)
    assert res["valid"] is False
    assert res["pass"] is False
    assert res["n_returns"] == 0


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=7, iv=0.55, realized_vol=0.35)  # far below floor
    fl = e57._underlying_floor(cap)
    assert fl["ok"] is False
    assert any(not v for v in fl["checks"].values())


def test_term_structure_viability_needs_two_expiries():
    cap = _craft_capture(n_bars=150, seed=8, iv=0.55, realized_vol=0.35)
    ts = e57._term_structure_viability(cap)
    # single-expiry fixture: only one expiry => not viable
    assert ts["n_viable_expiries"] == 1
    assert ts["viable"] is False


def test_protocol_and_floor_constants():
    p = e57.build_protocol("data/raw/eval57")
    assert p["eval"] == "EVAL-57"
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_surface_snapshots_per_underlying"] == 100
    assert p["floor"]["min_option_trades_per_underlying"] == 2000
    assert p["floor"]["term_structure_min_expiries"] == 2
    assert p["floor"]["term_structure_min_snapshots_per_expiry"] == 100
    assert set(p["structures"]) == set(e57.STRUCTURES)
    assert p["hedge_fee_bps"] == e57.HEDGE_FEE_BPS
    assert p["kill_switch_max_dd"] == e57.KILL_SWITCH_MAX_DD
    assert p["vol_target"] == e57.VOL_TARGET
    assert p["size_cap"] == e57.SIZE_CAP


def test_prereg_payload_from_constants_only():
    p = e57._prereg_payload("2026-11-15T19:10:00Z", "data/raw/eval57", "TASK")
    assert p["prereg_id"] == e57.PREREG_ID
    assert p["generated_at"] == "2026-11-15T19:10:00Z"
    assert p["protocol"]["eval"] == "EVAL-57"
    assert "surface_to_iv" in p["protocol"] and "go_bar" in p["protocol"]
    assert "volatility risk premium" in p["hypothesis"].lower()


def test_vrp_structure_distinct_from_calendar_spread():
    """EVAL-57 must be the VRP straddle, not EVAL-56's calendar spread."""
    assert e57.STRUCTURES == ("vrp_straddle_delta_hedged",)
    assert not any(s.startswith("long_near_short_far") for s in e57.STRUCTURES)
