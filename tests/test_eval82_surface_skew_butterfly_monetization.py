"""Unit tests for EVAL-82: surface (EVAL-71 near-ATM IV level + put-call skew)
-> signal-timed delta-hedged **butterfly** (smile-convexity structure) with the
**correct mark-path** net-of-cost P&L (EVAL-62) — the traded-form monetization
falsification.

EVAL-82 is the on-charter, runnable-now traded-form complement to EVAL-72: the
same EVAL-72 signal set {atm_iv, skew} and the same correct mark-path net-of-cost
P&L, but a **distinct traded form** — a four-leg butterfly (long OTM call wing +
long OTM put wing, short ATM body) that isolates smile convexity, rather than the
already-tested ATM straddle. It needs no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin seven things the next session must not break:
1. the artifact ids are EVAL-82;
2. the traded-form machinery (EVAL-62 markpath + EVAL-57 greeks + EVAL-71 surface
   + EVAL-76 OTM-wing picker) is reused verbatim, not forked;
3. ``build_butterfly_states`` builds a four-leg butterfly (ATM body + two OTM
   wings), is causal, near-delta-neutral, and is driven by the surface signal;
4. the composed floor ANDs the sealed EVAL-61/62 and EVAL-71 floors AND a
   butterfly-constructibility floor (none weakened);
5. ``run_eval82(write=False)`` reports BLOCKED below the composed floor and a
   verdict above it;
6. the butterfly P&L is EVAL-62's normalized mark-path P&L (no un-normalized
   dollar artifact);
7. the signal set and traded-form constants are the pre-registered ones.
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import scripts.eval57_vrp_net_of_cost as e57
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval76_surface_skew_risk_reversal_monetization as e76
import scripts.eval82_surface_skew_butterfly_monetization as e82

_EXPIRY_ISO = "2026-12-30T08:00:00Z"


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=8,
                   n_snapshots=None, base_iv=0.8):
    """Deterministic three-way capture: real-shaped surface snapshots carrying a
    full OTM chain (strikes both sides of spot) + near-ATM option trades + 1m perp
    candles. The strike ladder guarantees an ATM body and two OTM wings."""
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    snaps = []
    n_snaps = n_snapshots if n_snapshots is not None else n_bars
    # Strikes span below and above spot so ATM body + OTM call/put wings exist.
    rel_strikes = (0.95, 0.98, 0.99, 1.0, 1.01, 1.02, 1.05)
    for i in range(n_bars):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        iv_level = max(0.05, base_iv + 0.1 * math.sin(i * 0.1)
                       + rng.uniform(-0.005, 0.005))
        for j in range(n_trades_per_bar):
            opt = "call" if (j % 2 == 0) else "put"
            strike = round(px * (1.0 + rng.uniform(-0.02, 0.02)), 2)
            iv = max(0.05, iv_level + (0.03 if opt == "put" else -0.03)
                     + rng.uniform(-0.003, 0.003))
            trades.append({
                "ts": ts + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-OPT-{int(strike)}-{opt[0].upper()}",
                "direction": "buy",
                "amount": rng.uniform(0.5, 2.0),
                "price": 0.01,
                "index_price": px,
                "iv": iv,
                "option_type": opt,
                "strike": strike,
                "expiry": _EXPIRY_ISO,
            })
        if i < n_snaps:
            quotes = []
            for rel in rel_strikes:
                strike = round(px * rel, 2)
                for opt in ("call", "put"):
                    # OTM-ish wing marks, both positive and priceable.
                    mark = max(0.02, 0.05 + abs(rel - 1.0) * 0.4)
                    quotes.append({
                        "symbol": f"{inst}-OPT-{int(strike)}-{opt[0].upper()}-{i}",
                        "underlying": inst,
                        "strike": strike,
                        "expiry": _EXPIRY_ISO,
                        "option_type": opt,
                        "bid": round(mark * 0.98, 6),
                        "ask": round(mark * 1.02, 6),
                        "mark": mark,
                        "open_interest": 100.0,
                        "volume": 10.0,
                        "timestamp": "2023-11-14T00:00:00Z",
                    })
            snaps.append({"bar_ms": ts, "spot": px, "quotes": quotes})

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
        "source": {"authenticated": False, "public_read_only": True,
                   "venue": "deribit+okx"},
    }


def test_ids_are_eval82():
    assert e82.REPORT_ID.startswith("EVAL_82_")
    assert e82.PREREG_ID.startswith("EVAL_82_")
    assert e82.BLOCKED_ID.startswith("EVAL_82_")
    assert "BUTTERFLY_MONETIZATION" in e82.REPORT_ID


def test_reuses_sealed_machinery_verbatim():
    """EVAL-82 must reuse the sealed EVAL-57/61/62/71/76 helpers, not fork them."""
    assert e82.e62 is e62
    assert e82.e61 is e61
    assert e82.e57 is e57
    assert e82.e71 is e71
    assert e82.e76 is e76
    # EVAL-62 mark-path net-of-cost P&L, verbatim
    assert e82.e62.markpath_returns is e62.markpath_returns
    # quote pickers reused verbatim: EVAL-57 ATM body + EVAL-76 OTM wings
    assert e82.e57._pick_straddle_quotes is e57._pick_straddle_quotes
    assert e82.e76._pick_risk_reversal_quotes is e76._pick_risk_reversal_quotes
    # the traded signal set is IDENTICAL to EVAL-72 (level + skew)
    assert set(e82.SURFACE_SIGNALS) == {"atm_iv", "skew"}
    assert set(e82.SURFACE_SIGNALS).issubset(set(e71.SURFACE_SIGNALS))
    # stats / cost constants match EVAL-62 exactly
    assert e82.PERMUTATION_PERMS == e62.PERMUTATION_PERMS
    assert e82.BOOTSTRAP_RESAMPLES == e62.BOOTSTRAP_RESAMPLES
    assert e82.SEED == e62.SEED
    assert e82.SIZE_CAP == e62.SIZE_CAP
    assert e82.KILL_SWITCH_MAX_DD == e62.KILL_SWITCH_MAX_DD
    assert e82.HEDGE_FEE_BPS == e62.HEDGE_FEE_BPS


def test_build_butterfly_states_schema_and_causal():
    cap = _craft_capture(n_bars=80, seed=5)
    states = e82.build_butterfly_states(
        cap, surface_signal="skew", bar_seconds=300.0
    )
    assert len(states) > 20
    prev = -1
    for s in states:
        assert s["spot"] > 0.0
        # butterfly: the two OTM wings bracket the ATM body strike K
        # (lower wing < K < upper wing); they are picked relative to K so they can
        # never coincide with the body put/call.
        assert s["strike_put"] < s["atm_strike"]
        assert s["strike_call"] > s["atm_strike"]
        # aggregate mark/delta present and non-degenerate (signed, may be negative)
        assert "straddle_mark" in s and "straddle_delta" in s
        assert abs(s["straddle_mark"]) > 0.0
        assert s["structure"] == "butterfly"
        assert s["side"] in (-1, 0, 1)
        assert 0.0 <= s["exposure"] <= e82.SIZE_CAP
        if s["side"] == 0:
            assert s["exposure"] == 0.0
        else:
            assert s["exposure"] > 0.0
        # strictly ascending, non-overlapping bar starts (causal ordering)
        assert s["bar_ms"] > prev
        prev = s["bar_ms"]


def test_butterfly_is_near_delta_neutral():
    """The butterfly must be (near) delta-neutral by construction -- that is what
    distinguishes it from the ATM straddle (EVAL-72) and the risk reversal
    (EVAL-76). Its |delta| must be far below a straddle's ~2x per-leg delta."""
    cap = _craft_capture(n_bars=80, seed=9)
    states = e82.build_butterfly_states(
        cap, surface_signal="atm_iv", bar_seconds=300.0
    )
    assert len(states) > 20
    max_abs_delta = max(abs(s["straddle_delta"]) for s in states)
    # a butterfly's delta is a small residual of four offsetting legs; assert it is
    # bounded well below a full straddle body (~2.0).
    assert max_abs_delta < 1.5


def test_build_butterfly_states_driven_by_signal():
    """The state signal must come from the EVAL-71 surface signal: it must be
    non-degenerate and match the expanding z of the causal signal on the EVAL-62
    bar grid."""
    cap = _craft_capture(n_bars=80, seed=6)
    states = e82.build_butterfly_states(
        cap, surface_signal="atm_iv", bar_seconds=300.0
    )
    z = [s["signal_z"] for s in states]
    assert len(z) > 0
    assert any(abs(v) > 1e-9 for v in z)
    bar_ends, _c, _t, _i = e61.toxicity_per_bar(cap, 300.0)
    raw = [e76.surface_signal_by_bar_end(
        cap, surface_signal="atm_iv", bar_seconds=300.0).get(int(be)) for be in bar_ends]
    filled = e71._forward_fill(raw)
    sig_z = e61.expanding_zscore(filled, e82.ZWINDOW)
    idx = {int(be): i for i, be in enumerate(bar_ends)}
    for s in states:
        i = idx[int(s["bar_ms"]) + 300_000]
        assert abs(s["signal_z"] - float(sig_z[i])) < 1e-9


def test_floor_composes_all_sealed_floors_and_butterfly(monkeypatch):
    """EVAL-82's floor is the AND of the EVAL-61/62 traded floor, the EVAL-71
    surface floor, and a butterfly-constructibility floor; none is weakened."""
    traded_ok = {"ok": True, "checks": {}}
    traded_bad = {"ok": False, "checks": {}}
    signal_ok = {"ok": True, "checks": {}}
    signal_bad = {"ok": False, "checks": {}}

    monkeypatch.setattr(e82.e61, "_underlying_floor", lambda cap: traded_ok)
    monkeypatch.setattr(e82.e71, "_underlying_surface_floor", lambda cap: signal_ok)
    monkeypatch.setattr(
        e82, "build_butterfly_states",
        lambda cap, surface_signal, bar_seconds: [
            {"bar_ms": i, "spot": 1.0, "signal_z": 0.1} for i in range(250)
        ],
    )
    fl = e82._underlying_floor({"underlying": "BTC"}, bar_seconds=300.0)
    assert fl["ok"] is True
    assert fl["traded_floor_ok"] and fl["signal_floor_ok"] and fl["butterfly_floor_ok"]

    monkeypatch.setattr(e82.e61, "_underlying_floor", lambda cap: traded_bad)
    fl2 = e82._underlying_floor({"underlying": "BTC"}, bar_seconds=300.0)
    assert fl2["ok"] is False and fl2["traded_floor_ok"] is False

    monkeypatch.setattr(e82.e61, "_underlying_floor", lambda cap: traded_ok)
    monkeypatch.setattr(e82.e71, "_underlying_surface_floor", lambda cap: signal_bad)
    fl3 = e82._underlying_floor({"underlying": "BTC"}, bar_seconds=300.0)
    assert fl3["ok"] is False and fl3["signal_floor_ok"] is False

    # butterfly-constructibility floor fails when too few butterfly states
    monkeypatch.setattr(e82.e71, "_underlying_surface_floor", lambda cap: signal_ok)
    monkeypatch.setattr(
        e82, "build_butterfly_states",
        lambda cap, surface_signal, bar_seconds: [
            {"bar_ms": i, "spot": 1.0, "signal_z": 0.1} for i in range(5)
        ],
    )
    fl4 = e82._underlying_floor({"underlying": "BTC"}, bar_seconds=300.0)
    assert fl4["ok"] is False and fl4["butterfly_floor_ok"] is False


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=2)  # far below floor
    fl = e82._underlying_floor(cap, bar_seconds=300.0)
    assert fl["ok"] is False
    assert (
        fl["traded_floor_ok"] is False
        or fl["signal_floor_ok"] is False
        or fl["butterfly_floor_ok"] is False
    )


def test_campaign_floor_blocks_single_underlying():
    caps = {"BTC": _craft_capture(n_bars=120, seed=3)}
    fl = e82.campaign_floor(caps)
    assert fl["ok"] is False
    assert fl["checks"]["all_underlyings_ok"] is False


def test_evaluate_config_runs_and_is_normalized(monkeypatch):
    monkeypatch.setattr(e82, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e82, "BOOTSTRAP_RESAMPLES", 50)
    cap = _craft_capture(n_bars=120, seed=3)
    res = e82.evaluate_config(cap, surface_signal="skew", bar_seconds=300.0)
    assert res["underlying"] == "BTC"
    assert res["n_returns"] > 0
    assert "sharpe" in res and "permutation_p" in res and "pass" in res
    # EVAL-62 normalized mark-path P&L: drawdown can never be a >1.0 artifact
    assert res["max_drawdown"] <= 1.0
    # EVAL-62 markpath returns -> returns are proper returns
    assert all(abs(r) < 1.0 for r in
               e62.markpath_returns(
                   e82.build_butterfly_states(
                       cap, surface_signal="skew", bar_seconds=300.0)
               )["returns"])


def test_markpath_returns_is_the_sealed_eval62_pnl():
    """Regression guard: EVAL-82 must not reintroduce an un-normalized dollar P&L."""
    states = [
        {"spot": 100.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.0,
         "straddle_mark": -0.5, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 0},
        {"spot": 101.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.0,
         "straddle_mark": -0.2, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 300_000},
        {"spot": 99.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.0,
         "straddle_mark": -0.7, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 600_000},
    ]
    out = e82.e62.markpath_returns(states, hedge_fee_bps=5.0)
    assert len(out["returns"]) == 2
    # spot-normalized: each return is small, not a raw dollar P&L
    assert all(abs(r) < 1.0 for r in out["returns"])


def test_run_eval82_no_write_blocks_below_floor():
    cap = _craft_capture(n_bars=40, seed=7)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e82.run_eval82(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e82.REPORT_ID


def test_run_eval82_no_write_meets_floor_and_summarizes(monkeypatch):
    """Orchestration above the composed floor: two signals, one bar grid, few
    permutations (the floor itself is forced green here to keep the test fast; the
    real floor is exercised on the real captures by the driver)."""
    monkeypatch.setattr(e82, "SURFACE_SIGNALS", ("atm_iv", "skew"))
    monkeypatch.setattr(e82, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e82, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e82, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e82, "campaign_floor",
        lambda captures: {"underlyings": sorted(captures), "ok": True,
                          "per_underlying": {i: {"ok": True} for i in captures},
                          "checks": {"all_underlyings_ok": True}},
    )
    caps = {
        "BTC": _craft_capture(n_bars=120, seed=3),
        "ETH": _craft_capture(n_bars=120, seed=4, inst="ETH"),
    }
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e82.run_eval82(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_underlying"]) == 2
    # 2 underlyings * 2 signals * 1 grid = 4 configs
    assert len(report["per_config"]) == 4


def test_protocol_and_floor_constants():
    p = e82.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_butterfly_states_per_underlying"] == 200
    assert p["floor"]["min_states_per_config"] == e82.MIN_STATES_PER_CONFIG
    assert set(p["surface_signals"]) == {"atm_iv", "skew"}
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["kill_switch_max_dd"] == 0.20
    assert "EVAL-72" in p["extends"]
    assert "butterfly" in p["traded_form"].lower()
    assert "convexity" in p["traded_form"].lower() or "convexity" in p["title"].lower()
    assert "EVAL-61" in p["floor"]["composed_of"][0]
    assert "EVAL-71" in p["floor"]["composed_of"][1]
    assert "butterfly" in p["floor"]["composed_of"][2].lower()
    assert "mark-path" in p["title"].lower() or "mark path" in p["title"].lower()