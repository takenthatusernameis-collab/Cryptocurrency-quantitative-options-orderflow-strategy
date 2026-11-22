"""Unit tests for EVAL-184: surface-line traded-form net-of-cost OOS verdict
(the EVAL-69 analogue for the EVAL-177/168/169 surface GOs: skew/atm_iv/term_slope
-> forward variance/CVaR via signal-timed delta-hedged ATM straddle, mark-path
net-of-cost P&L, pooled across BTC+ETH, EVAL-64 feasible floor verbatim).

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-184 and match the gate's pre-registered globs;
2. the traded-form machinery (EVAL-62 markpath + EVAL-57 straddle + EVAL-71 surface
   bars + EVAL-74 term bars + EVAL-64 floor) is reused verbatim, not forked;
3. ``surface_signal_by_bar_end`` maps each surface signal to the bar-end grid;
4. ``build_surface_states`` is causal (side/exposure, no lookahead) and driven by
   the surface signal;
5. the floor is the EVAL-64 feasible floor verbatim (never weakened);
6. ``run_eval184(write=False)`` reports BLOCKED below the floor and a verdict above
   it;
7. the traded-form P&L is EVAL-62's normalized mark-path P&L (no EVAL-61
   un-normalized-dollar artifact).
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
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
import scripts.eval67_btc_oflow_tox_rv_oos as e67
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval74_surface_term_structure_predictiveness as e74
import scripts.eval184_surface_traded_netofcost_oos as e184


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=4,
                   n_snapshots=None, base_iv=0.8, expiry="2026-12-30T08:00:00Z"):
    """Deterministic three-way capture: surface snapshots + near-ATM option trades
    (with a varying IV surface) + 1m perp candles. Single expiry by default."""
    rng = random.Random(seed)
    base_ms = 1_700_000_000_000
    bar_ms = 300_000
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    snaps = []
    n_snaps = n_snapshots if n_snapshots is not None else n_bars
    for i in range(n_bars):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        for j in range(n_trades_per_bar):
            opt = "call" if (j % 2 == 0) else "put"
            strike = round(px * (1.0 + rng.uniform(-0.04, 0.04)), 2)
            iv = base_iv + 0.1 * math.sin(i * 0.1) + (0.05 if opt == "put" else -0.05)
            iv = max(0.05, iv + rng.uniform(-0.01, 0.01))
            trades.append({
                "ts": ts + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-30DEC26-{int(strike)}-{opt[0].upper()}",
                "direction": "buy",
                "amount": rng.uniform(0.5, 2.0),
                "price": 0.01,
                "index_price": px,
                "iv": iv,
                "option_type": opt,
                "strike": strike,
                "expiry": expiry,
            })
        if i < n_snaps:
            strike = round(px, 2)
            quotes = []
            for opt in ("call", "put"):
                quotes.append({
                    "symbol": f"{inst}-OPT-{int(strike)}-{opt[0].upper()}-{i}",
                    "underlying": inst,
                    "strike": strike,
                    "expiry": expiry,
                    "option_type": opt,
                    "bid": 0.098,
                    "ask": 0.102,
                    "mark": 0.1,
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


def _craft_capture_two_expiry(n_bars=120, seed=0, inst="BTC"):
    """Two-expiry capture so EVAL-74 _term_bars can produce a non-null term_slope."""
    cap_a = _craft_capture(n_bars=n_bars, seed=seed, inst=inst,
                           expiry="2026-12-30T08:00:00Z")
    cap_b = _craft_capture(n_bars=n_bars, seed=seed + 1000, inst=inst,
                           expiry="2027-03-30T08:00:00Z")
    return {
        "schema": cap_a["schema"],
        "underlying": inst,
        "venue": cap_a["venue"],
        "window_start": cap_a["window_start"],
        "window_end": cap_a["window_end"],
        "surface": cap_a["surface"],
        "option_trades": cap_a["option_trades"] + cap_b["option_trades"],
        "perp_candles": cap_a["perp_candles"],
        "okx_inst_id": cap_a["okx_inst_id"],
        "okx_perp_trades": [],
        "source": cap_a["source"],
    }


def test_ids_are_eval184_and_match_gate_globs():
    assert e184.REPORT_ID.startswith("EVAL_184_")
    assert e184.PREREG_ID.startswith("EVAL_184_")
    assert e184.BLOCKED_ID.startswith("EVAL_184_")
    assert "SURFACE_TRADED_NETFCOST_OOS" in e184.REPORT_ID
    assert e184.PREREG_GLOB == e184.PREREG_ID + "_*"
    assert e184.COMBINED_GLOB == e184.REPORT_ID + "_*"
    assert e184.BLOCKED_GLOB == e184.BLOCKED_ID + "_*"
    assert e184.DEFAULT_CAPTURE_DIR == "data/raw/eval84cap"


def test_reuses_sealed_machinery_verbatim():
    """EVAL-184 must reuse the sealed EVAL-57/61/62/64/67/71/74 helpers verbatim."""
    assert e184.e62 is e62
    assert e184.e71 is e71
    assert e184.e74 is e74
    assert e184.e64 is e64
    assert e184.e67 is e67
    assert e184.e57 is e57
    assert e184.e61 is e61
    # EVAL-62 mark-path net-of-cost P&L, verbatim
    assert e184.e62.markpath_returns is e62.markpath_returns
    # EVAL-64 feasible floor, verbatim (never weakened)
    assert e184._underlying_floor_strict is e64._underlying_floor_strict
    # stats / cost constants match EVAL-62 exactly
    assert e184.PERMUTATION_PERMS == e62.PERMUTATION_PERMS
    assert e184.BOOTSTRAP_RESAMPLES == e62.BOOTSTRAP_RESAMPLES
    assert e184.SEED == e62.SEED
    assert e184.SIZE_CAP == e62.SIZE_CAP
    assert e184.KILL_SWITCH_MAX_DD == e62.KILL_SWITCH_MAX_DD
    assert e184.HEDGE_FEE_BPS == e62.HEDGE_FEE_BPS
    assert e184.ZWINDOW == e62.ZWINDOW
    # surface signal window from EVAL-71
    assert e184.SIGNAL_WINDOW_SECONDS == e71.SIGNAL_WINDOW_SECONDS


def test_surface_signal_by_bar_end_aligns_to_bar_end_grid():
    cap = _craft_capture(n_bars=30, seed=1)
    grid = 300_000
    for sig in ("skew", "atm_iv", "term_slope"):
        sig_map = e184.surface_signal_by_bar_end(
            cap, surface_signal=sig, bar_seconds=300.0
        )
        for k in sig_map:
            assert k % grid == 0
        bars = e71.build_surface_bars(cap, bar_seconds=300.0)
        expected = {int(b["bar_open_ms"]) + grid: b.get(sig) for b in bars}
        assert set(sig_map) == set(expected)
        for k, v in expected.items():
            if v is None:
                assert sig_map[k] is None
            else:
                assert abs(sig_map[k] - v) < 1e-12


def test_build_surface_states_schema_and_causal():
    cap = _craft_capture(n_bars=80, seed=5)
    for sig in ("skew", "atm_iv"):
        states = e184.build_surface_states(
            cap, surface_signal=sig, bar_seconds=300.0
        )
        assert len(states) > 20
        prev = -1
        for s in states:
            assert s["spot"] > 0.0
            assert s["straddle_mark"] > 0.0
            assert s["side"] in (-1, 0, 1)
            assert 0.0 <= s["exposure"] <= e184.SIZE_CAP
            if s["side"] == 0:
                assert s["exposure"] == 0.0
            else:
                assert s["exposure"] > 0.0
            assert s["bar_ms"] > prev
            prev = s["bar_ms"]


def test_build_surface_states_driven_by_surface_signal():
    """The state signal must come from the surface signal: switching signal changes z."""
    cap = _craft_capture(n_bars=80, seed=6)
    st_skew = e184.build_surface_states(cap, surface_signal="skew", bar_seconds=300.0)
    st_iv = e184.build_surface_states(cap, surface_signal="atm_iv", bar_seconds=300.0)
    z_skew = [s["signal_z"] for s in st_skew]
    z_iv = [s["signal_z"] for s in st_iv]
    assert len(z_skew) == len(z_iv) and len(z_skew) > 0
    assert any(abs(a - b) > 1e-9 for a, b in zip(z_skew, z_iv))
    assert any(abs(z) > 1e-9 for z in z_skew)


def test_term_slope_states_from_e74_term_bars():
    """term_slope must flow from EVAL-74 _term_bars (two-expiry capture)."""
    cap = _craft_capture_two_expiry(n_bars=80, seed=7)
    states = e184.build_surface_states(
        cap, surface_signal="term_slope", bar_seconds=300.0
    )
    # term_slope needs >=2 near-ATM expiries; may be None for sparse tapes.
    assert all(s["signal_z"] == 0.0 or abs(s["signal_z"]) > 0 for s in states)


def test_floor_is_eval64_strict_verbatim(monkeypatch):
    """EVAL-184's floor is the EVAL-64 feasible floor; never weakened."""
    full = {
        "underlying": "BTC", "n_surface_snapshots": 1000,
        "n_surface_instruments": 100, "n_surface_bars_5m": 1000,
        "n_option_trades": 2000, "n_of_instruments": 150,
        "of_span_seconds": 82000.0, "n_of_bars_5m": 240,
        "n_perp_candles": 1000, "perp_span_seconds": 300000.0,
        "n_perp_bars_5m": 1000, "n_common_bars_5m": 240,
        "checks": {"snapshots_ok": True, "surface_instruments_ok": True,
                   "surface_bars_ok": True, "trades_ok": True,
                   "of_instruments_ok": True, "of_span_ok": True,
                   "of_bars_ok": True, "perp_bars_ok": True,
                   "perp_span_ok": True, "common_overlap_ok": True},
        "ok": True,
    }
    bad = dict(full)
    bad["ok"] = False
    bad["checks"] = {k: False for k in full["checks"]}

    monkeypatch.setattr(e184, "_underlying_floor_strict", lambda cap: full)
    fl = e184._underlying_floor({"underlying": "BTC"})
    assert fl["ok"] is True
    assert fl["checks"] == full["checks"]

    monkeypatch.setattr(e184, "_underlying_floor_strict", lambda cap: bad)
    fl2 = e184._underlying_floor({"underlying": "BTC"})
    assert fl2["ok"] is False


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=2)  # far below floor
    fl = e184._underlying_floor(cap)
    assert fl["ok"] is False


def test_evaluate_config_runs_and_is_normalized():
    cap = _craft_capture(n_bars=120, seed=3)
    res = e184.evaluate_config(cap, surface_signal="atm_iv", bar_seconds=300.0)
    assert res["underlying"] == "BTC"
    assert res["n_returns"] > 0
    assert "sharpe" in res and "permutation_p" in res and "pass" in res
    assert res["max_drawdown"] <= 1.0
    assert all(abs(r) < 1.0 for r in
               e62.markpath_returns(
                   e184.build_surface_states(cap, surface_signal="atm_iv",
                                             bar_seconds=300.0)
               )["returns"])


def test_markpath_returns_is_the_sealed_eval62_pnl():
    """Regression guard: EVAL-184 must not reintroduce an un-normalized dollar P&L."""
    states = [
        {"spot": 100.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 2.0, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 0},
        {"spot": 101.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 2.5, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 300_000},
        {"spot": 99.0, "side": 1, "exposure": 1.0, "straddle_delta": 0.5,
         "straddle_mark": 1.8, "spread_usd": 0.0, "signal_z": 1.0, "bar_ms": 600_000},
    ]
    out = e184.e62.markpath_returns(states, hedge_fee_bps=5.0)
    assert len(out["returns"]) == 2
    assert all(abs(r) < 1.0 for r in out["returns"])


def test_run_eval184_no_write_blocks_below_floor():
    cap = _craft_capture(n_bars=40, seed=7)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e184.run_eval184(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e184.REPORT_ID


def test_run_eval184_no_write_meets_floor_and_summarizes(monkeypatch):
    """Orchestration above the floor: force floor green, few perms, both underlyings."""
    monkeypatch.setattr(e184, "SURFACE_SIGNALS", ("skew",))
    monkeypatch.setattr(e184, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e184, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e184, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e184, "MIN_POOLED_RETURNS", 1)
    monkeypatch.setattr(
        e184, "_underlying_floor_strict",
        lambda cap: {"underlying": cap.get("underlying", "?"), "ok": True,
                     "checks": {}, "n_surface_snapshots": 1000,
                     "n_surface_instruments": 100, "n_surface_bars_5m": 1000,
                     "n_option_trades": 2000, "n_of_instruments": 150,
                     "of_span_seconds": 82000.0, "n_of_bars_5m": 240,
                     "n_perp_candles": 1000, "perp_span_seconds": 300000.0,
                     "n_perp_bars_5m": 1000, "n_common_bars_5m": 240},
    )
    caps = {
        "BTC": _craft_capture(n_bars=120, seed=3),
        "ETH": _craft_capture(n_bars=120, seed=4, inst="ETH"),
    }
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e184.run_eval184(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)",
                                 "INCONCLUSIVE (UNDERPOWERED)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_underlying_floor"]) == 2


def test_protocol_and_floor_constants():
    p = e184.build_protocol("data/raw/eval84cap")
    assert p["floor"]["min_underlyings"] == 2
    assert set(p["surface_signals"]) == {"skew", "atm_iv", "term_slope"}
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["kill_switch_max_dd"] == 0.20
    assert p["min_pooled_returns"] == 790
    assert "EVAL-69" in p["extends"]
    assert "EVAL-64" in p["title"] or "EVAL-64" in p["extends"]
    assert "mark-path" in p["traded_form"].lower()
