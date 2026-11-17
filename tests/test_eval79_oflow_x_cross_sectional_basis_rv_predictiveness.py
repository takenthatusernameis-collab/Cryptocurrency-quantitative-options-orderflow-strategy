"""Unit tests for EVAL-79: the **options order-flow imbalance x cross-sectional
implied-volatility basis** -> subsequent realized volatility predictiveness.

EVAL-79 is the on-charter, runnable-now *conditional-flow* complement to EVAL-65
(unconditional options order-flow), EVAL-77 (unconditional cross-sectional basis)
and EVAL-78 (order-flow x single-underlying surface): the same Spearman rank-IC
statistic and all sealed signal reconstructions reused verbatim, but a distinct
signal family — flow conditioned on the cross-sectional BTC-vs-ETH near-ATM IV
basis. It needs no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin eight things the next session must not break:
1. the artifact ids are EVAL-79;
2. the sealed machinery (EVAL-61/62/65/71/77 helpers) is reused verbatim, not forked;
3. ``_aligned_rows`` intersects the order-flow state grid with the common
   cross-sectional bar grid and carries spot / oflow z / basis z;
4. ``evaluate_config`` multiplies the causal basis z by the causal order-flow z
   against forward RV, per underlying;
5. the composed floor ANDs the EVAL-71 surface floor, the order-flow state floor
   and the cross-sectional alignment floor (none weakened);
6. ``run_eval79(write=False)`` reports BLOCKED below the composed floor and a
   verdict above it;
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
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77
import scripts.eval79_oflow_x_cross_sectional_basis_rv_predictiveness as e79

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


def _craft_capture(inst="BTC", n_bars=200, seed=0, base_iv=0.8,
                   base_ms=_BASE_MS, bar_ms=_BAR_MS):
    """Deterministic three-way capture with perp candles and a near-ATM option
    trade tape. ``surface.snapshots`` is intentionally empty so the EVAL-62
    order-flow state builder yields no priceable states (used for the
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


def _cs_fixture(n=220, seed=0):
    """Deterministic cross-section fixture: common bar grid, per-underlying bar
    maps with close/atm_iv/skew."""
    rng = random.Random(seed)
    px = 60000.0
    maps = {"BTC": {}, "ETH": {}}
    common = []
    for i in range(n):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        bo = _BASE_MS + i * _BAR_MS
        common.append(bo)
        for inst in ("BTC", "ETH"):
            maps[inst][bo] = {
                "bar_open_ms": bo,
                "close": px,
                "atm_iv": 0.8 + 0.05 * rng.uniform(-1, 1),
                "skew": 0.03 * rng.uniform(-1, 1),
            }
    return {"maps": maps, "common": common, "bar_seconds": 300.0,
            "underlyings": ["BTC", "ETH"]}


def _synthetic_rows(n=220, seed=0):
    """Deterministic (bar_open_ms, spot, oflow_z, basis_z) rows on the common
    grid."""
    rng = random.Random(seed)
    px = 60000.0
    rows = []
    for i in range(n):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        bo = _BASE_MS + i * _BAR_MS
        rows.append((bo, px, rng.uniform(-2, 2), rng.uniform(-1, 1)))
    return rows


def test_ids_are_eval79():
    assert e79.REPORT_ID.startswith("EVAL_79_")
    assert e79.PREREG_ID.startswith("EVAL_79_")
    assert e79.BLOCKED_ID.startswith("EVAL_79_")
    assert "OFLOW_X_CROSS_SECTIONAL" in e79.REPORT_ID


def test_reuses_sealed_machinery_verbatim():
    """EVAL-79 must reuse the sealed EVAL-61/62/65/71/77 helpers, not fork them."""
    assert e79.e61 is e61
    assert e79.e62 is e62
    assert e79.e65 is e65
    assert e79.e71 is e71
    assert e79.e77 is e77
    # EVAL-77 cross-section + basis, EVAL-71 surface, EVAL-62 states, verbatim
    assert e79.e77.build_cross_section is e77.build_cross_section
    assert e79.e77._relative_signal_series is e77._relative_signal_series
    assert e79.e71.build_surface_bars is e71.build_surface_bars
    assert e79.e71._underlying_surface_floor is e71._underlying_surface_floor
    assert e79.e62.build_states is e62.build_states
    # EVAL-65 directional permutation / block-bootstrap IC, verbatim
    assert e79.e65._perm_p_ic is e65._perm_p_ic
    assert e79.e65._boot_ci_ic is e65._boot_ci_ic
    # stats / cost constants match the sealed sources exactly
    assert e79.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e79.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e79.BOOTSTRAP_BLOCK == e65.BOOTSTRAP_BLOCK
    assert e79.SEED == e62.SEED
    assert e79.ZWINDOW == e62.ZWINDOW
    assert e79.FDR_ALPHA == e62.FDR_ALPHA


def test_aligned_rows_intersects_common_grid(monkeypatch):
    states = [
        {"bar_ms": _BASE_MS, "spot": 1.0, "signal_z": 0.1},
        {"bar_ms": _BASE_MS + _BAR_MS, "spot": 2.0, "signal_z": 0.2},
        {"bar_ms": _BASE_MS + 2 * _BAR_MS, "spot": 3.0, "signal_z": 0.3},
    ]
    maps = {
        _BASE_MS: {"bar_open_ms": _BASE_MS, "close": 1.0},
        _BASE_MS + _BAR_MS: {"bar_open_ms": _BASE_MS + _BAR_MS, "close": 2.0},
        _BASE_MS + 2 * _BAR_MS: {"bar_open_ms": _BASE_MS + 2 * _BAR_MS, "close": 3.0},
        _BASE_MS + 3 * _BAR_MS: {"bar_open_ms": _BASE_MS + 3 * _BAR_MS, "close": 4.0},
    }
    cs = {"maps": {"BTC": maps}, "common": [_BASE_MS, _BASE_MS + _BAR_MS,
                                            _BASE_MS + 2 * _BAR_MS,
                                            _BASE_MS + 3 * _BAR_MS]}
    basis_z = [0.5, 0.6, 0.7, 0.8]
    monkeypatch.setattr(e79.e62, "build_states", lambda cap, tox_signal, bar_seconds: states)
    monkeypatch.setattr(e77, "build_cross_section", lambda caps, bar_seconds: cs)
    monkeypatch.setattr(e77, "_relative_signal_series",
                        lambda cs, surface_signal: basis_z)

    rows = e79._aligned_rows({"underlying": "BTC"}, "BTC", cs, basis_z,
                             bar_seconds=300.0)
    # intersection of state bars {0,1,2} and common {0,1,2,3} -> three rows
    assert [r[0] for r in rows] == [_BASE_MS, _BASE_MS + _BAR_MS, _BASE_MS + 2 * _BAR_MS]
    assert rows[0][1] == 1.0 and abs(rows[0][2] - 0.1) < 1e-12 and abs(rows[0][3] - 0.5) < 1e-12


def test_evaluate_config_runs_and_is_bounded(monkeypatch):
    monkeypatch.setattr(e79, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e79, "BOOTSTRAP_RESAMPLES", 50)
    cs = _cs_fixture(n=220, seed=0)
    rows = _synthetic_rows(n=220, seed=0)
    basis_z = [r[3] for r in rows]
    monkeypatch.setattr(e77, "build_cross_section", lambda caps, bar_seconds: cs)
    monkeypatch.setattr(e79, "_aligned_rows",
                        lambda cap, inst, cs2, basis_z2, bar_seconds: rows)
    monkeypatch.setattr(e77, "_relative_signal_series",
                        lambda cs2, surface_signal: basis_z)

    res = e79.evaluate_config(
        _captures(), basis_signal="atm_iv", bar_seconds=300.0, horizon_bars=6,
    )
    assert res["n_pairs"] >= e79.MIN_USABLE_PAIRS_PER_CONFIG
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
    monkeypatch.setattr(e79, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e79, "BOOTSTRAP_RESAMPLES", 50)
    cs = _cs_fixture(n=220, seed=1)
    rows = _synthetic_rows(n=220, seed=1)
    basis_z = [r[3] for r in rows]
    monkeypatch.setattr(e77, "build_cross_section", lambda caps, bar_seconds: cs)
    monkeypatch.setattr(e79, "_aligned_rows",
                        lambda cap, inst, cs2, basis_z2, bar_seconds: rows)
    monkeypatch.setattr(e77, "_relative_signal_series",
                        lambda cs2, surface_signal: basis_z)

    a = e79.evaluate_config(_captures(), basis_signal="skew",
                            bar_seconds=300.0, horizon_bars=6)
    b = e79.evaluate_config(_captures(), basis_signal="skew",
                            bar_seconds=300.0, horizon_bars=6)
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_campaign_floor_composes_all_three_floors(monkeypatch):
    ok_floor = {"ok": True, "n_option_trades": 100}
    monkeypatch.setattr(e71, "_underlying_surface_floor", lambda cap: ok_floor)
    states_250 = [{"bar_ms": _BASE_MS + i * _BAR_MS, "spot": 1.0, "signal_z": 0.1}
                  for i in range(250)]
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states_250)
    cs_250 = _cs_fixture(n=250, seed=0)
    monkeypatch.setattr(e77, "build_cross_section",
                        lambda caps, bar_seconds: cs_250)

    caps = _captures()
    fl = e79.campaign_floor(caps)
    assert fl["ok"] is True
    assert fl["checks"]["all_underlyings_ok"] is True
    assert fl["checks"]["aligned_ok"] is True
    assert fl["aligned_common_bars_coarsest"] == 250

    # one underlying below the EVAL-71 surface floor -> not ok
    monkeypatch.setattr(
        e71, "_underlying_surface_floor",
        lambda cap: {"ok": cap.get("underlying") == "BTC", "n_option_trades": 100},
    )
    fl2 = e79.campaign_floor(caps)
    assert fl2["ok"] is False

    # surface floor restored, alignment floor not met -> not ok
    monkeypatch.setattr(e71, "_underlying_surface_floor", lambda cap: ok_floor)
    cs_5 = _cs_fixture(n=5, seed=0)
    monkeypatch.setattr(e77, "build_cross_section",
                        lambda caps, bar_seconds: cs_5)
    fl3 = e79.campaign_floor(caps)
    assert fl3["ok"] is False
    assert fl3["checks"]["aligned_ok"] is False


def test_campaign_floor_blocks_short_capture():
    caps = _captures(n_bars=10, seed_btc=9, seed_eth=10)
    fl = e79.campaign_floor(caps)
    assert fl["ok"] is False


def test_run_eval79_no_write_blocks_below_floor():
    caps = _captures(n_bars=20, seed_btc=15, seed_eth=16)
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e79.run_eval79(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e79.REPORT_ID


def test_run_eval79_no_write_meets_floor_and_summarizes(monkeypatch):
    """Orchestration above the composed floor (forced green here to keep the
    test fast; the real floor is exercised on the real captures by the driver)."""
    monkeypatch.setattr(e79, "BASIS_SIGNALS", ("atm_iv",))
    monkeypatch.setattr(e79, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e79, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e79, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e79, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e79, "campaign_floor",
        lambda captures: {"underlyings": sorted(captures), "ok": True,
                          "aligned_common_bars_coarsest": 250, "aligned_ok": True,
                          "per_underlying": {i: {"ok": True} for i in captures},
                          "checks": {"all_underlyings_ok": True, "aligned_ok": True}},
    )
    cs = _cs_fixture(n=220, seed=2)
    rows = _synthetic_rows(n=220, seed=2)
    basis_z = [r[3] for r in rows]
    monkeypatch.setattr(e77, "build_cross_section", lambda caps, bar_seconds: cs)
    monkeypatch.setattr(e79, "_aligned_rows",
                        lambda cap, inst, cs2, basis_z2, bar_seconds: rows)
    monkeypatch.setattr(e77, "_relative_signal_series",
                        lambda cs2, surface_signal: basis_z)
    caps = _captures(n_bars=200, seed_btc=17, seed_eth=18)
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e79.run_eval79(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one monkeypatched config (basis x grid x horizon), pooled across underlyings
    assert report["summary"]["n_configs"] == 1
    assert len(report["per_config"]) == 1


def test_protocol_and_floor_constants():
    p = e79.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_oflow_states_per_underlying"] == 200
    assert p["floor"]["min_aligned_common_bars"] == 200
    assert p["floor"]["min_usable_pairs_per_config"] == e79.MIN_USABLE_PAIRS_PER_CONFIG
    assert set(p["basis_signals"]) == {"atm_iv", "skew"}
    assert p["oflow_signals"] == ["imbalance"]
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert "EVAL-65" in p["extends"]
    assert "EVAL-77" in p["extends"]
    assert "EVAL-78" in p["extends"]
    assert "cross-sectional" in p["title"].lower()
    assert "EVAL-71" in p["floor"]["note"]
