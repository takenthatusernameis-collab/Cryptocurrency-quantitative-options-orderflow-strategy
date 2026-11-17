"""Unit tests for EVAL-73: temporal out-of-sample **stability** of EVAL-71's
predictive-surface GO across a disjoint early/late split of the real on-disk
captures.

EVAL-73 is the on-charter, runnable-now *stability* check that follows EVAL-71
(GO: surface predicts forward RV) and EVAL-72 (NO-GO: surface does not monetize
net-of-cost). It reuses EVAL-71's surface machinery and EVAL-65's Spearman rank-IC
statistics verbatim; the only new logic is the disjoint temporal split and the
sign-consistency stability rule. It needs no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin seven things the next session must not break:
1. the artifact ids are EVAL-73;
2. the statistic (Spearman rank IC) and the surface machinery are reused verbatim
   from EVAL-65 / EVAL-71, not forked;
3. ``_split_capture`` is genuinely DISJOINT (no shared bar or trade) and the
   midpoint partitions the perp candles;
4. ``_half_ic`` matches EVAL-71's full-sample IC exactly (same primitive);
5. the stability rule requires BOTH halves positive AND each half adequately
   populated (a thin / one-sided half is NOT stable);
6. the composed floor blocks (never NO-GO) below floor;
7. ``run_eval73(write=False)`` reports BLOCKED below floor and summarizes above it.
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval73_surface_iv_rv_stability_split as e73


def _craft_surface_capture(
    inst="BTC",
    *,
    n_bars=300,
    seed=0,
    signal_to_vol=0.0,
    n_trades_per_bar=40,
    ar=0.8,
):
    """In-memory three-way capture fixture whose real option-trade IV (near-ATM
    level + put-call skew) is driven by a latent AR(1) factor that also drives the
    forward perp return / volatility. ``signal_to_vol`` > 0 plants a positive
    surface -> forward-vol relationship; ``== 0`` plants none."""
    rng = random.Random(seed)
    bar_ms = 300_000
    base_ms = 1_700_000_000_000
    base_ms -= base_ms % bar_ms
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    latent = 0.5
    for i in range(n_bars):
        latent = ar * latent + rng.uniform(0, 1) * (1.0 - ar)
        latent = max(0.0, min(1.0, latent))
        drift = latent * signal_to_vol + rng.uniform(-1, 1) * 1e-6
        px = max(1.0, px * (1.0 + drift))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        base_iv = 50.0 + latent * 20.0
        for j in range(n_trades_per_bar):
            strike = px * (1.0 + rng.uniform(-0.04, 0.04))
            typ = "P" if j % 2 == 0 else "C"
            if typ == "P":
                iv = base_iv + 5.0 + latent * 10.0
            else:
                iv = base_iv - latent * 5.0
            iv = max(1.0, iv + rng.uniform(-1.0, 1.0))
            trades.append({
                "ts": ts + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-27NOV26-{int(round(strike))}-{typ}",
                "iv": iv,
                "amount": 1.0,
                "index_price": px,
                "option_type": typ.lower(),
            })
    return {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": inst,
        "venue": "deribit+okx",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": []},
        "option_trades": trades,
        "perp_candles": candles,
        "okx_inst_id": f"{inst}-USD-SWAP",
        "okx_perp_trades": [],
        "source": {"authenticated": False, "public_read_only": True, "venue": "deribit+okx"},
    }


def test_ids_are_eval73():
    assert e73.REPORT_ID.startswith("EVAL_73_")
    assert e73.PREREG_ID.startswith("EVAL_73_")
    assert e73.BLOCKED_ID.startswith("EVAL_73_")
    assert "STABILITY_SPLIT" in e73.REPORT_ID


def test_statistic_and_surface_machinery_reused_verbatim():
    """EVAL-73 must reuse the sealed EVAL-65 statistics + EVAL-71 surface
    machinery, not fork them."""
    assert e73.e71 is e71
    assert e73.e65 is e65
    assert e73.e62 is e62
    assert e73.e61 is e61
    # half IC uses the exact EVAL-65 Spearman primitive
    assert e73.e65._spearman is e65._spearman
    # constants match the sealed modules
    assert e73.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e73.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e73.SEED == e62.SEED
    assert e73.ZWINDOW == e62.ZWINDOW
    # full sample goes through EVAL-71 verbatim
    assert e73.e71.evaluate_predictiveness is e71.evaluate_predictiveness


def test_midpoint_and_split_are_disjoint():
    cap = _craft_surface_capture("BTC", n_bars=200, seed=1, n_trades_per_bar=20)
    mid = e73._midpoint_ms(cap)
    ts = [int(c["ts"]) for c in cap["perp_candles"]]
    assert mid == (min(ts) + max(ts)) // 2
    early, late = e73._split_capture(cap, mid)
    e_ts = {int(c["ts"]) for c in early["perp_candles"]}
    l_ts = {int(c["ts"]) for c in late["perp_candles"]}
    # genuinely disjoint: no shared candle ts
    assert e_ts.isdisjoint(l_ts)
    # union reconstructs the original candle count
    assert len(early["perp_candles"]) + len(late["perp_candles"]) == len(cap["perp_candles"])
    # every early candle < mid <= every late candle
    assert all(t < mid for t in e_ts)
    assert all(t >= mid for t in l_ts)
    # trades are partitioned the same way (disjoint)
    e_tr = [int(t["ts"]) for t in early["option_trades"]]
    l_tr = [int(t["ts"]) for t in late["option_trades"]]
    assert len(e_tr) + len(l_tr) == len(cap["option_trades"])


def test_half_adequacy_blocks_thin_half():
    cap = _craft_surface_capture("BTC", n_bars=40, seed=2, n_trades_per_bar=3)
    mid = e73._midpoint_ms(cap)
    early, late = e73._split_capture(cap, mid)
    fl = e73._half_adequacy(late)
    # a 20-bar half is far below the 300-candle adequacy floor
    assert fl["candles_ok"] is False
    assert fl["n_perp_candles"] < e73.MIN_HALF_PERP_CANDLES


def test_half_ic_matches_eval71_full_sample_ic():
    """On a single (unsplit) capture, ``_half_ic`` must reproduce EVAL-71's exact
    full-sample Spearman IC (same primitive, same alignment)."""
    cap = _craft_surface_capture("BTC", n_bars=400, seed=3, signal_to_vol=0.02,
                                 n_trades_per_bar=40)
    full = e71.evaluate_predictiveness(
        cap, surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6,
    )
    half = e73._half_ic(cap, surface_signal="atm_iv", bar_seconds=300.0,
                        horizon_bars=6)
    assert half["ok"] is True
    assert half["n_pairs"] == full["n_pairs"]
    assert abs(half["ic"] - float(full["spearman_ic"])) < 1e-12


def test_evaluate_stability_true_on_planted_persistent_relationship():
    """A planted, persistent surface -> forward-vol relationship that holds across
    the whole capture must be STABLE in both disjoint halves."""
    cap = _craft_surface_capture("BTC", n_bars=1010, seed=5, signal_to_vol=0.02,
                                 n_trades_per_bar=50)
    mid = e73._midpoint_ms(cap)
    res = e73.evaluate_stability(
        cap, surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6,
        midpoint_ms=mid,
    )
    assert res["n_pairs_early"] >= e73.MIN_HALF_PAIRS
    assert res["n_pairs_late"] >= e73.MIN_HALF_PAIRS
    assert res["ic_early"] > 0.0
    assert res["ic_late"] > 0.0
    assert res["stable"] is True


def test_evaluate_stability_false_when_a_half_is_thin():
    """If one disjoint half is too thin to carry MIN_HALF_PAIRS, the config is NOT
    stable (halves_ok is False), regardless of the full-sample IC.

    The late cluster is placed far in the future so the *temporal* midpoint
    isolates a rich early half and a thin late half."""
    early = _craft_surface_capture("BTC", n_bars=600, seed=6, signal_to_vol=0.02,
                                   n_trades_per_bar=50)
    late = _craft_surface_capture("BTC", n_bars=10, seed=7, signal_to_vol=0.0,
                                  n_trades_per_bar=5)
    bar_ms = 300_000
    early_max = max(int(c["ts"]) for c in early["perp_candles"])
    # shift late so its first candle is > 2x the early span past the base -> the
    # temporal midpoint falls in the empty gap, leaving late as its own thin half.
    off = 6_000_000 * bar_ms
    late_c = [dict(c, ts=int(c["ts"]) + off) for c in late["perp_candles"]]
    late_t = [dict(t, ts=int(t["ts"]) + off) for t in late["option_trades"]]
    assert min(int(c["ts"]) for c in late_c) > 2 * early_max
    cap = {
        **early,
        "perp_candles": list(early["perp_candles"]) + late_c,
        "option_trades": list(early["option_trades"]) + late_t,
    }
    mid = e73._midpoint_ms(cap)
    res = e73.evaluate_stability(
        cap, surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6,
        midpoint_ms=mid,
    )
    assert res["n_pairs_early"] >= e73.MIN_HALF_PAIRS
    assert res["halves_ok"] is False
    assert res["n_pairs_late"] < e73.MIN_HALF_PAIRS
    assert res["stable"] is False


def test_floor_blocks_below_floor():
    cap = _craft_surface_capture("BTC", n_bars=40, seed=7, n_trades_per_bar=3)
    fl = e73._underlying_floor(cap)
    assert fl["ok"] is False
    assert fl["eval71_floor_ok"] is False or fl["checks"]["late_near_atm_ok"] is False


def test_floor_passes_on_heavy_capture():
    cap = _craft_surface_capture("BTC", n_bars=1010, seed=3, n_trades_per_bar=50)
    fl = e73._underlying_floor(cap)
    assert fl["eval71_floor_ok"] is True
    assert fl["early_half"]["candles_ok"] is True
    assert fl["late_half"]["candles_ok"] is True
    assert fl["early_half"]["near_atm_ok"] is True
    assert fl["late_half"]["near_atm_ok"] is True
    assert fl["ok"] is True


def test_run_eval73_no_write_blocks_below_floor():
    cap = _craft_surface_capture("BTC", n_bars=40, seed=7, n_trades_per_bar=3)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "three_way_BTC_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
        report = e73.run_eval73(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e73.REPORT_ID


def test_run_eval73_no_write_meets_floor_and_summarizes(monkeypatch):
    """Orchestration above the floor: one signal, one bar grid, one horizon, few
    permutations (the floor is forced green here to keep the test fast; the real
    floor is exercised on the real captures by the driver)."""
    monkeypatch.setattr(e73, "SURFACE_SIGNALS", ("atm_iv",))
    monkeypatch.setattr(e73, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e73, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e73, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e73, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e73, "_underlying_floor",
        lambda cap: {"underlying": cap.get("underlying", "?"), "ok": True,
                     "checks": {}},
    )
    caps = {
        "BTC": _craft_surface_capture("BTC", n_bars=1010, seed=3, signal_to_vol=0.02,
                                      n_trades_per_bar=50),
        "ETH": _craft_surface_capture("ETH", n_bars=1010, seed=4, signal_to_vol=0.02,
                                      n_trades_per_bar=50),
    }
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e73.run_eval73(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert len(report["per_underlying"]) == 2
    assert len(report["per_config"]) == 2  # 2 underlyings * 1 config


def test_protocol_and_floor_constants():
    p = e73.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert set(p["surface_signals"]) == {"atm_iv", "skew"}
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert "EVAL-71" in p["extends"]
    assert "disjoint" in p["split"].lower()
    assert p["floor"]["min_half_pairs"] == e73.MIN_HALF_PAIRS
    assert "stability" in p["title"].lower()