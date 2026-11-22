"""Unit tests for EVAL-185: surface-line traded-form ROBUSTNESS GRID (is the
EVAL-184 surface NO-GO a monetization/horizon artifact?).

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-185 and match the gate's pre-registered globs;
2. the traded-form machinery (EVAL-184 + EVAL-62 markpath + EVAL-57 straddle +
   EVAL-71 surface bars + EVAL-74 term bars + EVAL-64 floor) is reused verbatim;
3. the grid is exactly 3 signals x 5 horizons {60,120,240,300,360}s x 3 cost
   haircuts {0.5x,1x,2x} = 45 pooled configs (matches eval185_phaseb_gate.py);
4. ``scale_states_cost`` scales the real spread by the haircut;
5. ``evaluate_config_cost`` applies the haircut to BOTH the hedge fee and the spread
   (higher haircut -> weakly-lower net return);
6. the floor is the EVAL-64 feasible floor verbatim (never weakened);
7. ``run_eval185(write=False)`` reports BLOCKED below the floor and a verdict above it;
8. cost-robustness aggregation: a (signal,horizon) passes at >=2/3 haircuts;
9. no stale signal/target/task-label ids leaked from EVAL-184.
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
import scripts.eval185_surface_traded_robustness_oos as e185


def _craft_capture(n_bars=120, seed=0, inst="BTC", n_trades_per_bar=4,
                   n_snapshots=None, base_iv=0.8, expiry="2026-12-30T08:00:00Z"):
    """Deterministic three-way capture (mirrors the EVAL-184 test fixture)."""
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


def test_ids_are_eval185_and_match_gate_globs():
    assert e185.REPORT_ID.startswith("EVAL_185_")
    assert e185.PREREG_ID.startswith("EVAL_185_")
    assert e185.BLOCKED_ID.startswith("EVAL_185_")
    assert "SURFACE_TRADED_ROBUSTNESS_GRID" in e185.REPORT_ID
    assert e185.PREREG_GLOB == e185.PREREG_ID + "_*"
    assert e185.COMBINED_GLOB == e185.REPORT_ID + "_*"
    assert e185.BLOCKED_GLOB == e185.BLOCKED_ID + "_*"
    assert e185.DEFAULT_CAPTURE_DIR == "data/raw/eval84cap"
    # gate globs (eval185_phaseb_gate.py) must match
    import scripts.eval185_phaseb_gate as gate
    assert gate.PREREG_GLOB == e185.PREREG_GLOB
    assert gate.COMBINED_GLOB == e185.COMBINED_GLOB
    assert gate.BLOCKED_GLOB == e185.BLOCKED_GLOB
    assert gate.TASK_LABEL == e185.DEFAULT_TASK_LABEL


def test_grid_matches_gate_exactly():
    """The 3x5x3 = 45-config grid must equal eval185_phaseb_gate.py's grid."""
    import scripts.eval185_phaseb_gate as gate
    assert tuple(e185.SURFACE_SIGNALS) == tuple(gate.SURFACE_GO_CELLS[i]["signal"]
                                               for i in range(len(gate.SURFACE_GO_CELLS)))
    assert tuple(e185.HORIZON_GRID_SECONDS) == tuple(gate.HORIZON_GRID_SECONDS)
    assert tuple(e185.COST_HAIRCUTS) == tuple(gate.COST_HAIRCUTS)
    assert e185.GRID_CONFIG_COUNT == gate.GRID_CONFIG_COUNT == 45
    assert set(e185.HORIZON_GRID_SECONDS) == {60.0, 120.0, 240.0, 300.0, 360.0}
    assert set(e185.COST_HAIRCUTS) == {0.5, 1.0, 2.0}


def test_reuses_sealed_machinery_verbatim():
    """EVAL-185 must reuse EVAL-184 + EVAL-57/61/62/64/67/71/74 helpers verbatim."""
    assert e185.e184 is e184
    assert e185.e62 is e62
    assert e185.e71 is e71
    assert e185.e74 is e74
    assert e185.e64 is e64
    assert e185.e67 is e67
    assert e185.e57 is e57
    assert e185.e61 is e61
    # surface-state builder reused from EVAL-184 verbatim
    assert e185.e184.build_surface_states is e184.build_surface_states
    # EVAL-62 mark-path net-of-cost P&L, verbatim
    assert e185.e62.markpath_returns is e62.markpath_returns
    # EVAL-64 feasible floor, verbatim (never weakened)
    assert e185._underlying_floor_strict is e64._underlying_floor_strict
    # signals/targets/builders identical to EVAL-184
    assert tuple(e185.SURFACE_SIGNALS) == tuple(e184.SURFACE_SIGNALS)
    assert e185.SIGNAL_TARGET == e184.SIGNAL_TARGET
    assert e185.SIGNAL_BUILDER == e184.SIGNAL_BUILDER
    # stats / cost constants match EVAL-184 exactly
    assert e185.PERMUTATION_PERMS == e184.PERMUTATION_PERMS
    assert e185.BOOTSTRAP_RESAMPLES == e184.BOOTSTRAP_RESAMPLES
    assert e185.SEED == e184.SEED
    assert e185.SIZE_CAP == e184.SIZE_CAP
    assert e185.KILL_SWITCH_MAX_DD == e184.KILL_SWITCH_MAX_DD
    assert e185.HEDGE_FEE_BPS == e184.HEDGE_FEE_BPS
    assert e185.ZWINDOW == e184.ZWINDOW
    assert e185.MIN_POOLED_RETURNS == e184.MIN_POOLED_RETURNS


def test_scale_states_cost_scales_spread_only():
    states = [
        {"spot": 100.0, "spread_usd": 0.4, "side": 1, "exposure": 1.0},
        {"spot": 101.0, "spread_usd": 0.2, "side": 1, "exposure": 1.0},
    ]
    scaled = e185.scale_states_cost(states, cost_haircut=2.0)
    assert abs(scaled[0]["spread_usd"] - 0.8) < 1e-12
    assert abs(scaled[1]["spread_usd"] - 0.4) < 1e-12
    # spot/other fields untouched
    assert scaled[0]["spot"] == 100.0
    # original not mutated
    assert states[0]["spread_usd"] == 0.4
    # 1x is identity
    ident = e185.scale_states_cost(states, cost_haircut=1.0)
    assert abs(ident[0]["spread_usd"] - 0.4) < 1e-12


def test_evaluate_config_cost_higher_haircut_no_better():
    """A larger cost haircut must not improve the net-of-cost mean return."""
    cap = _craft_capture(n_bars=120, seed=11)
    states = e184.build_surface_states(cap, surface_signal="atm_iv", bar_seconds=300.0)
    r_low = e185.evaluate_config_cost(
        states, underlying="BTC", surface_signal="atm_iv",
        bar_seconds=300.0, cost_haircut=0.5,
    )
    r_high = e185.evaluate_config_cost(
        states, underlying="BTC", surface_signal="atm_iv",
        bar_seconds=300.0, cost_haircut=2.0,
    )
    assert r_low["n_returns"] == r_high["n_returns"]
    # higher haircut => weakly-lower mean net return
    assert r_high["mean_return"] <= r_low["mean_return"] + 1e-12


def test_floor_is_eval64_strict_verbatim(monkeypatch):
    """EVAL-185's floor is the EVAL-64 feasible floor; never weakened."""
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

    monkeypatch.setattr(e185, "_underlying_floor_strict", lambda cap: full)
    fl = e185._underlying_floor({"underlying": "BTC"})
    assert fl["ok"] is True
    assert fl["checks"] == full["checks"]

    monkeypatch.setattr(e185, "_underlying_floor_strict", lambda cap: bad)
    fl2 = e185._underlying_floor({"underlying": "BTC"})
    assert fl2["ok"] is False


def test_floor_blocks_short_capture():
    cap = _craft_capture(n_bars=30, seed=2)  # far below floor
    fl = e185._underlying_floor(cap)
    assert fl["ok"] is False


def test_build_states_reused_from_eval184():
    """EVAL-185 reuses EVAL-184's surface-state builder verbatim."""
    cap = _craft_capture(n_bars=80, seed=5)
    st = e185.e184.build_surface_states(
        cap, surface_signal="skew", bar_seconds=300.0
    )
    assert len(st) > 20
    for s in st:
        assert s["spot"] > 0.0
        assert s["straddle_mark"] > 0.0
        assert s["side"] in (-1, 0, 1)


def test_run_eval185_no_write_blocks_below_floor():
    cap = _craft_capture(n_bars=40, seed=7)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e185.run_eval185(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e185.REPORT_ID


def test_run_eval185_no_write_meets_floor_and_summarizes(monkeypatch):
    """Orchestration above the floor: force floor green, few perms, both underlyings."""
    monkeypatch.setattr(e185, "SURFACE_SIGNALS", ("skew",))
    monkeypatch.setattr(e185, "HORIZON_GRID_SECONDS", (300.0,))
    monkeypatch.setattr(e185, "COST_HAIRCUTS", (1.0,))
    monkeypatch.setattr(e185, "GRID_CONFIG_COUNT", 1)
    monkeypatch.setattr(e185, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e185, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(e185, "MIN_POOLED_RETURNS", 1)
    monkeypatch.setattr(
        e185, "_underlying_floor_strict",
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
        report = e185.run_eval185(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)",
                                 "INCONCLUSIVE (UNDERPOWERED)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_underlying_floor"]) == 2
    # one (signal,bar) x one haircut => exactly one pooled config
    assert report["pooled"]["grid_config_count"] == 1
    assert "cost_robust_pairs" in report["pooled"]
    assert "min_cost_scenarios_pass" in report["pooled"]


def test_protocol_constants():
    p = e185.build_protocol("data/raw/eval84cap")
    assert p["floor"]["min_underlyings"] == 2
    assert set(p["surface_signals"]) == {"skew", "atm_iv", "term_slope"}
    assert p["horizon_grid_seconds"] == [60.0, 120.0, 240.0, 300.0, 360.0]
    assert p["cost_haircuts"] == [0.5, 1.0, 2.0]
    assert p["grid_config_count"] == 45
    assert p["min_cost_scenarios_pass"] == 2
    assert p["kill_switch_max_dd"] == 0.20
    assert p["min_pooled_returns"] == 790
    assert "EVAL-184" in p["extends"]


def test_no_stale_eval184_ids_or_task_labels():
    """Regression guard: no stale EVAL-184 ids/labels leaked into EVAL-185."""
    assert "EVAL_184" not in e185.REPORT_ID
    assert "EVAL_184" not in e185.PREREG_ID
    assert "EVAL_184" not in e185.BLOCKED_ID
    assert e185.DEFAULT_TASK_LABEL == "EVAL185-SURFACE-TRADED-ROBUSTNESS-GRID"
    assert "EVAL184" not in e185.DEFAULT_TASK_LABEL
    # builders/targets are the surviving surface GO cells, not order-flow toxicity
    assert set(e185.SIGNAL_TARGET) == {"skew", "atm_iv", "term_slope"}
    for b in e185.SIGNAL_BUILDER.values():
        assert b in ("e71.build_surface_bars", "e74._term_bars")