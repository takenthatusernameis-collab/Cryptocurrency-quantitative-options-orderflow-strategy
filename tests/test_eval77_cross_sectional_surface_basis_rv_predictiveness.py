"""Unit tests for EVAL-77: the **cross-sectional** options implied-volatility
surface basis (BTC-vs-ETH relative near-ATM IV / skew) -> subsequent relative
realized volatility (BTC-minus-ETH forward RV spread) predictiveness.

EVAL-77 is the on-charter, runnable-now cross-sectional complement to EVAL-71/73/74:
the same Spearman rank-IC statistic and surface reconstruction, but a distinct
signal family (BTC-vs-ETH relative IV rather than a single-underlying level/skew
or term structure). It needs no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin eight things the next session must not break:
1. the artifact ids are EVAL-77;
2. the sealed machinery (EVAL-61/62/65/71 helpers) is reused verbatim, not forked;
3. ``build_cross_section`` aligns the two underlyings on their common bar grid;
4. ``_relative_signal_series`` is causal ETH-minus-BTC relative surface IV/skew;
5. the target is the BTC-minus-ETH forward realized-vol spread;
6. the composed floor ANDs the EVAL-71 floor (both underlyings) with the
   cross-sectional alignment floor (neither weakened);
7. ``run_eval77(write=False)`` reports BLOCKED below the composed floor and a
   verdict above it;
8. the Spearman IC is bounded and deterministic.
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
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


def _craft_capture(inst="BTC", n_bars=200, seed=0, base_iv=0.8,
                   base_ms=_BASE_MS, bar_ms=_BAR_MS):
    """Deterministic three-way capture with 1m/5m-shaped perp candles and a
    near-ATM option trade tape (real ``iv`` per trade)."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    for i in range(n_bars):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        iv_level = max(0.05, base_iv + 0.1 * math.sin(i * 0.1)
                       + rng.uniform(-0.005, 0.005))
        for opt in ("C", "P"):
            iv = max(0.05, iv_level + (0.03 if opt == "P" else -0.03)
                     + rng.uniform(-0.003, 0.003))
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


def test_ids_are_eval77():
    assert e77.REPORT_ID.startswith("EVAL_77_")
    assert e77.PREREG_ID.startswith("EVAL_77_")
    assert e77.BLOCKED_ID.startswith("EVAL_77_")
    assert "CROSS_SECTIONAL" in e77.REPORT_ID


def test_reuses_sealed_machinery_verbatim():
    """EVAL-77 must reuse the sealed EVAL-61/62/65/71 helpers, not fork them."""
    assert e77.e61 is e61
    assert e77.e62 is e62
    assert e77.e65 is e65
    assert e77.e71 is e71
    # EVAL-71 surface reconstruction, verbatim
    assert e77.e71.build_surface_bars is e71.build_surface_bars
    # EVAL-65 directional permutation / block-bootstrap IC, verbatim
    assert e77.e65._perm_p_ic is e65._perm_p_ic
    assert e77.e65._boot_ci_ic is e65._boot_ci_ic
    # stats / cost constants match the sealed sources exactly
    assert e77.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e77.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e77.BOOTSTRAP_BLOCK == e65.BOOTSTRAP_BLOCK
    assert e77.SEED == e62.SEED
    assert e77.ZWINDOW == e62.ZWINDOW
    assert e77.FDR_ALPHA == e62.FDR_ALPHA


def test_build_cross_section_aligns_common_bar_grid():
    caps = _captures(n_bars=30, seed_btc=3, seed_eth=4)
    cs = e77.build_cross_section(caps, bar_seconds=300.0)
    assert cs["underlyings"] == ["BTC", "ETH"]
    # identical grids -> every bar-open is common
    btc = {int(b["bar_open_ms"]) for b in e71.build_surface_bars(caps["BTC"], bar_seconds=300.0)}
    eth = {int(b["bar_open_ms"]) for b in e71.build_surface_bars(caps["ETH"], bar_seconds=300.0)}
    assert set(cs["common"]) == (btc & eth)
    assert len(cs["common"]) == len(btc) == 30
    # non-overlapping grids -> empty intersection
    shifted = _captures(n_bars=30, seed_btc=3, seed_eth=4)
    shifted["ETH"] = _craft_capture("ETH", n_bars=30, seed=4, base_iv=0.9,
                                    base_ms=_BASE_MS + 100 * _BAR_MS)
    cs2 = e77.build_cross_section(shifted, bar_seconds=300.0)
    assert set(cs2["common"]).isdisjoint(set(cs["common"]))


def test_relative_signal_series_is_causal_eth_minus_btc():
    caps = _captures(n_bars=60, seed_btc=5, seed_eth=6)
    cs = e77.build_cross_section(caps, bar_seconds=300.0)
    z = e77._relative_signal_series(cs, surface_signal="atm_iv")
    assert len(z) == len(cs["common"])

    # Recompute the expected series independently from EVAL-71 bars.
    maps = cs["maps"]
    raw = []
    for m in cs["common"]:
        b = maps["BTC"][int(m)].get("atm_iv")
        r = maps["ETH"][int(m)].get("atm_iv")
        raw.append(float(r) - float(b) if (b is not None and r is not None) else None)
    filled = e71._forward_fill(raw)
    expected = e61.expanding_zscore(filled, e77.ZWINDOW)
    for got, exp in zip(z, expected):
        assert abs(got - exp) < 1e-12
    # the relative series must be non-degenerate
    assert any(abs(v) > 1e-9 for v in z)


def test_rv_spread_target_is_btc_minus_eth_forward_rv():
    caps = _captures(n_bars=40, seed_btc=7, seed_eth=8)
    cs = e77.build_cross_section(caps, bar_seconds=300.0)
    horizon = 6
    closes_b = e77._closes_on_common(cs, "BTC")
    closes_r = e77._closes_on_common(cs, "ETH")
    rv_b = e77._rv_series(closes_b, horizon)
    rv_r = e77._rv_series(closes_r, horizon)
    expected = [rv_b[k] - rv_r[k] for k in range(len(rv_b))]
    assert len(expected) == len(cs["common"]) - horizon
    assert all(math.isfinite(v) for v in expected)
    # both legs are genuine realized vols (non-negative)
    assert all(v >= 0.0 for v in rv_b) and all(v >= 0.0 for v in rv_r)


def test_campaign_floor_composes_eval71_and_alignment(monkeypatch):
    ok_floor = {"ok": True, "checks": {"option_trades_ok": True}}
    monkeypatch.setattr(e77.e71, "_underlying_surface_floor", lambda cap: ok_floor)
    monkeypatch.setattr(
        e77, "build_cross_section",
        lambda captures, bar_seconds: {"common": list(range(300)), "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    caps = {"BTC": {"underlying": "BTC"}, "ETH": {"underlying": "ETH"}}
    fl = e77.campaign_floor(caps)
    assert fl["ok"] is True
    assert fl["underlyings_ok"] is True and fl["aligned_ok"] is True
    assert fl["aligned_common_bars_binding"] == 300

    # one underlying below the EVAL-71 floor -> underlyings_ok False
    monkeypatch.setattr(
        e77.e71, "_underlying_surface_floor",
        lambda cap: {"ok": cap.get("underlying") == "BTC", "checks": {}},
    )
    fl2 = e77.campaign_floor(caps)
    assert fl2["ok"] is False and fl2["underlyings_ok"] is False

    # alignment floor restored but too few common bars -> aligned_ok False
    monkeypatch.setattr(e77.e71, "_underlying_surface_floor", lambda cap: ok_floor)
    monkeypatch.setattr(
        e77, "build_cross_section",
        lambda captures, bar_seconds: {"common": list(range(10)), "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    fl3 = e77.campaign_floor(caps)
    assert fl3["ok"] is False and fl3["aligned_ok"] is False


def test_campaign_floor_blocks_short_capture():
    caps = _captures(n_bars=10, seed_btc=9, seed_eth=10)
    fl = e77.campaign_floor(caps)
    assert fl["ok"] is False
    assert fl["underlyings_ok"] is False or fl["aligned_ok"] is False


def test_evaluate_config_runs_and_is_bounded(monkeypatch):
    monkeypatch.setattr(e77, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e77, "BOOTSTRAP_RESAMPLES", 50)
    caps = _captures(n_bars=200, seed_btc=11, seed_eth=12)
    res = e77.evaluate_config(
        caps, surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6
    )
    assert res["n_pairs"] >= e77.MIN_USABLE_PAIRS_PER_CONFIG
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
    monkeypatch.setattr(e77, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e77, "BOOTSTRAP_RESAMPLES", 50)
    caps = _captures(n_bars=200, seed_btc=13, seed_eth=14)
    a = e77.evaluate_config(caps, surface_signal="skew", bar_seconds=300.0, horizon_bars=6)
    b = e77.evaluate_config(caps, surface_signal="skew", bar_seconds=300.0, horizon_bars=6)
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_run_eval77_no_write_blocks_below_floor():
    caps = _captures(n_bars=20, seed_btc=15, seed_eth=16)
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e77.run_eval77(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e77.REPORT_ID


def test_run_eval77_no_write_meets_floor_and_summarizes(monkeypatch):
    """Orchestration above the composed floor: few configs / perms (the floor is
    forced green here to keep the test fast; the real floor is exercised on the
    real captures by the driver)."""
    monkeypatch.setattr(e77, "SURFACE_SIGNALS", ("atm_iv",))
    monkeypatch.setattr(e77, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e77, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e77, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e77, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e77, "campaign_floor",
        lambda captures: {"underlyings": sorted(captures), "per_underlying": {},
                          "underlyings_ok": True, "aligned_ok": True,
                          "aligned_common_bars_by_grid": {"300.0": 200},
                          "aligned_common_bars_binding": 200, "ok": True,
                          "checks": {}},
    )
    caps = _captures(n_bars=200, seed_btc=17, seed_eth=18)
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e77.run_eval77(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert report["summary"]["n_configs"] == 1
    assert len(report["per_config"]) == 1
    assert "baseline" in report["protocol"]["cross_section"]
    assert report["protocol"]["cross_section"]["baseline"] == "BTC"
    assert report["protocol"]["cross_section"]["relative"] == "ETH"


def test_protocol_and_floor_constants():
    p = e77.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_aligned_common_bars"] == 200
    assert p["floor"]["min_usable_pairs_per_config"] == e77.MIN_USABLE_PAIRS_PER_CONFIG
    assert set(p["surface_signals"]) == {"atm_iv", "skew"}
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert p["cross_section"]["baseline"] == "BTC"
    assert p["cross_section"]["relative"] == "ETH"
    assert "EVAL-71" in p["extends"]
    assert "EVAL-74" in p["extends"]
    assert "cross-sectional" in p["title"].lower()
    assert "EVAL-71" in p["floor"]["note"]