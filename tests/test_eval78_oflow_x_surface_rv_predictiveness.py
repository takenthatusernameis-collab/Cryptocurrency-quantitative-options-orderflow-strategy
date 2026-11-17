"""Unit tests for EVAL-78: the **options order-flow imbalance x implied-vol
surface interaction** -> subsequent realized volatility predictiveness.

EVAL-78 is the on-charter, runnable-now *conditional-flow* complement to EVAL-65
(unconditional options order-flow) and EVAL-71/77 (unconditional surface): the same
Spearman rank-IC statistic and both sealed signal reconstructions reused verbatim,
but a distinct signal family (the product of the order-flow z and the surface z). It
needs no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin eight things the next session must not break:
1. the artifact ids are EVAL-78;
2. the sealed machinery (EVAL-61/62/65/71 helpers) is reused verbatim, not forked;
3. ``build_aligned`` intersects the order-flow state grid with the surface bar grid
   and carries spot / oflow z / surface bar;
4. ``evaluate_config`` multiplies the causal surface z by the causal order-flow z
   against forward RV;
5. the composed floor ANDs the EVAL-71 surface floor with the order-flow state floor
   (neither weakened);
6. ``run_eval78(write=False)`` reports BLOCKED below the composed floor and a verdict
   above it;
7. the Spearman IC is bounded and deterministic;
8. the protocol/floor constants are the pre-registered ones.
"""

from __future__ import annotations

import json
import random
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval78_oflow_x_surface_rv_predictiveness as e78

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


def _craft_capture(inst="BTC", n_bars=200, seed=0, base_iv=0.8,
                   base_ms=_BASE_MS, bar_ms=_BAR_MS):
    """Deterministic three-way capture with 1m/5m-shaped perp candles and a
    near-ATM option trade tape. ``surface.snapshots`` is intentionally empty so the
    EVAL-62 order-flow state builder yields no priceable states (used for the
    below-floor BLOCKED path)."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    for i in range(n_bars):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        iv_level = max(0.05, base_iv + 0.1 * rng.uniform(-1, 1))
        for opt in ("C", "P"):
            iv = max(0.05, iv_level + (0.03 if opt == "P" else -0.03))
            trades.append({
                "ts": ts + 1,
                "instrument": f"{inst}-OPT-{int(round(px))}-{opt}",
                "direction": "buy",
                "amount": rng.uniform(0.5, 2.0),
                "price": 0.01,
                "index_price": px,
                "iv": iv,
                "option_type": "call" if opt == "C" else "put",
                "strike": round(px, 2),
                "expiry": "2026-12-30T08:00:00Z",
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
        "source": {"authenticated": False, "public_read_only": True,
                   "venue": "deribit+okx"},
    }


def _captures(n_bars=200, seed_btc=1, seed_eth=2):
    return {
        "BTC": _craft_capture("BTC", n_bars=n_bars, seed=seed_btc, base_iv=0.8),
        "ETH": _craft_capture("ETH", n_bars=n_bars, seed=seed_eth, base_iv=0.9),
    }


def _synthetic_aligned(n=220, seed=0):
    """Deterministic (bar_open_ms, spot, oflow_z, surface_bar) rows."""
    rng = random.Random(seed)
    px = 60000.0
    rows = []
    for i in range(n):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        bo = _BASE_MS + i * _BAR_MS
        rows.append((bo, px, rng.uniform(-2, 2),
                     {"atm_iv": 0.8 + 0.05 * rng.uniform(-1, 1),
                      "skew": 0.03 * rng.uniform(-1, 1)}))
    return rows


def test_ids_are_eval78():
    assert e78.REPORT_ID.startswith("EVAL_78_")
    assert e78.PREREG_ID.startswith("EVAL_78_")
    assert e78.BLOCKED_ID.startswith("EVAL_78_")
    assert "OFLOW_X_SURFACE" in e78.REPORT_ID


def test_reuses_sealed_machinery_verbatim():
    """EVAL-78 must reuse the sealed EVAL-61/62/65/71 helpers, not fork them."""
    assert e78.e61 is e61
    assert e78.e62 is e62
    assert e78.e65 is e65
    assert e78.e71 is e71
    # EVAL-71 surface reconstruction + EVAL-62 order-flow states, verbatim
    assert e78.e71.build_surface_bars is e71.build_surface_bars
    assert e78.e62.build_states is e62.build_states
    # EVAL-65 directional permutation / block-bootstrap IC, verbatim
    assert e78.e65._perm_p_ic is e65._perm_p_ic
    assert e78.e65._boot_ci_ic is e65._boot_ci_ic
    # stats / cost constants match the sealed sources exactly
    assert e78.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e78.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e78.BOOTSTRAP_BLOCK == e65.BOOTSTRAP_BLOCK
    assert e78.SEED == e62.SEED
    assert e78.ZWINDOW == e62.ZWINDOW
    assert e78.FDR_ALPHA == e62.FDR_ALPHA


def test_build_aligned_intersects_common_bar_grid(monkeypatch):
    states = [
        {"bar_ms": _BASE_MS, "spot": 1.0, "signal_z": 0.1},
        {"bar_ms": _BASE_MS + _BAR_MS, "spot": 2.0, "signal_z": 0.2},
        {"bar_ms": _BASE_MS + 2 * _BAR_MS, "spot": 3.0, "signal_z": 0.3},
    ]
    bars = [
        {"bar_open_ms": _BASE_MS + _BAR_MS, "close": 2.0, "atm_iv": 0.8, "skew": 0.01},
        {"bar_open_ms": _BASE_MS + 2 * _BAR_MS, "close": 3.0, "atm_iv": 0.9, "skew": 0.02},
        {"bar_open_ms": _BASE_MS + 3 * _BAR_MS, "close": 4.0, "atm_iv": 1.0, "skew": 0.03},
    ]
    monkeypatch.setattr(e78.e62, "build_states", lambda cap, tox_signal, bar_seconds: states)
    monkeypatch.setattr(e78.e71, "build_surface_bars", lambda cap, bar_seconds: bars)

    aligned = e78.build_aligned({"underlying": "BTC"}, oflow_signal="imbalance",
                                bar_seconds=300.0)
    assert aligned["n_oflow_states"] == 3
    assert aligned["n_surface_bars"] == 3
    rows = aligned["rows"]
    # intersection of {0,1,2} and {1,2,3} bar indices -> two rows, ascending
    assert [r[0] for r in rows] == [_BASE_MS + _BAR_MS, _BASE_MS + 2 * _BAR_MS]
    assert rows[0][1] == 2.0 and abs(rows[0][2] - 0.2) < 1e-12
    assert rows[0][3]["atm_iv"] == 0.8


def test_evaluate_config_runs_and_is_bounded(monkeypatch):
    monkeypatch.setattr(e78, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e78, "BOOTSTRAP_RESAMPLES", 50)
    rows = _synthetic_aligned(n=220, seed=0)
    monkeypatch.setattr(
        e78, "build_aligned",
        lambda cap, oflow_signal, bar_seconds: {"rows": rows, "n_oflow_states": len(rows),
                                                "n_surface_bars": len(rows)},
    )
    res = e78.evaluate_config(
        {"underlying": "BTC"}, surface_signal="atm_iv", oflow_signal="imbalance",
        bar_seconds=300.0, horizon_bars=6,
    )
    assert res["n_pairs"] >= e78.MIN_USABLE_PAIRS_PER_CONFIG
    assert -1.0 <= res["spearman_ic"] <= 1.0
    assert 0.0 <= res["permutation_p"] <= 1.0
    ci = res["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    assert res["pass"] == (
        res["spearman_ic"] > 0.0
        and res["permutation_p"] < 0.05
        and ci[1] > 0.0
    )


def test_evaluate_config_is_deterministic(monkeypatch):
    monkeypatch.setattr(e78, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e78, "BOOTSTRAP_RESAMPLES", 50)
    rows = _synthetic_aligned(n=220, seed=1)
    monkeypatch.setattr(
        e78, "build_aligned",
        lambda cap, oflow_signal, bar_seconds: {"rows": rows, "n_oflow_states": len(rows),
                                                "n_surface_bars": len(rows)},
    )
    a = e78.evaluate_config({"underlying": "BTC"}, surface_signal="skew",
                            oflow_signal="imbalance", bar_seconds=300.0, horizon_bars=6)
    b = e78.evaluate_config({"underlying": "BTC"}, surface_signal="skew",
                            oflow_signal="imbalance", bar_seconds=300.0, horizon_bars=6)
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_campaign_floor_composes_eval71_and_oflow(monkeypatch):
    ok_floor = {"ok": True, "n_option_trades": 100}
    monkeypatch.setattr(e78.e71, "_underlying_surface_floor", lambda cap: ok_floor)
    monkeypatch.setattr(
        e78, "build_aligned",
        lambda cap, oflow_signal, bar_seconds: {"rows": [], "n_oflow_states": 250,
                                                "n_surface_bars": 250},
    )
    caps = {"BTC": {"underlying": "BTC"}, "ETH": {"underlying": "ETH"}}
    fl = e78.campaign_floor(caps, oflow_signal="imbalance")
    assert fl["ok"] is True
    assert fl["checks"]["all_underlyings_ok"] is True
    assert fl["per_underlying"]["BTC"]["oflow_ok"] is True

    # one underlying below the EVAL-71 surface floor -> not ok
    monkeypatch.setattr(
        e78.e71, "_underlying_surface_floor",
        lambda cap: {"ok": cap.get("underlying") == "BTC", "n_option_trades": 100},
    )
    fl2 = e78.campaign_floor(caps, oflow_signal="imbalance")
    assert fl2["ok"] is False

    # surface floor restored but too few order-flow states -> not ok
    monkeypatch.setattr(e78.e71, "_underlying_surface_floor", lambda cap: ok_floor)
    monkeypatch.setattr(
        e78, "build_aligned",
        lambda cap, oflow_signal, bar_seconds: {"rows": [], "n_oflow_states": 5,
                                                "n_surface_bars": 5},
    )
    fl3 = e78.campaign_floor(caps, oflow_signal="imbalance")
    assert fl3["ok"] is False
    assert fl3["per_underlying"]["BTC"]["oflow_ok"] is False


def test_campaign_floor_blocks_short_capture():
    caps = _captures(n_bars=10, seed_btc=9, seed_eth=10)
    fl = e78.campaign_floor(caps, oflow_signal="imbalance")
    assert fl["ok"] is False


def test_run_eval78_no_write_blocks_below_floor():
    caps = _captures(n_bars=20, seed_btc=15, seed_eth=16)
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e78.run_eval78(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e78.REPORT_ID


def test_run_eval78_no_write_meets_floor_and_summarizes(monkeypatch):
    """Orchestration above the composed floor (forced green here to keep the test
    fast; the real floor is exercised on the real captures by the driver)."""
    monkeypatch.setattr(e78, "SURFACE_SIGNALS", ("atm_iv",))
    monkeypatch.setattr(e78, "OFLOW_SIGNALS", ("imbalance",))
    monkeypatch.setattr(e78, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e78, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e78, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e78, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e78, "_underlying_floor",
        lambda cap, oflow_signal: {"underlying": cap.get("underlying"), "ok": True,
                                   "surface_floor_ok": True, "oflow_ok": True,
                                   "n_oflow_states": 250, "surface_floor": {},
                                   "checks": {}},
    )
    rows = _synthetic_aligned(n=220, seed=2)
    monkeypatch.setattr(
        e78, "build_aligned",
        lambda cap, oflow_signal, bar_seconds: {"rows": rows, "n_oflow_states": len(rows),
                                                "n_surface_bars": len(rows)},
    )
    caps = _captures(n_bars=200, seed_btc=17, seed_eth=18)
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e78.run_eval78(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert report["summary"]["n_configs"] == 2
    assert len(report["per_config"]) == 2


def test_protocol_and_floor_constants():
    p = e78.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_oflow_states_per_underlying"] == 200
    assert p["floor"]["min_usable_pairs_per_config"] == e78.MIN_USABLE_PAIRS_PER_CONFIG
    assert set(p["surface_signals"]) == {"atm_iv", "skew"}
    assert p["oflow_signals"] == ["imbalance"]
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert "EVAL-65" in p["extends"]
    assert "EVAL-71" in p["extends"]
    assert "interaction" in p["title"].lower()
    assert "EVAL-71" in p["floor"]["note"]