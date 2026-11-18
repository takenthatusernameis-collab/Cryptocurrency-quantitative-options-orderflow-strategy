"""Unit tests for EVAL-88: the **cross-sectional** options implied-volatility
surface basis (BTC-vs-ETH relative near-ATM IV / skew) -> subsequent relative
*direction* (BTC-minus-ETH forward *signed return spread*) predictiveness.

EVAL-88 is the on-charter, runnable-now *directional* complement to EVAL-77
(relative-vol *magnitude* spread) and EVAL-81 (own-asset order-flow -> own signed
return). It reuses the sealed EVAL-61/62/65/71/77 machinery verbatim, needs no new
acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-88;
2. the sealed machinery (EVAL-61/62/65/71/77 helpers) is reused verbatim, not forked;
3. ``_forward_rel_return_spread`` is causal (target strictly after bar k), is the
   BTC-minus-ETH forward *signed return spread*, and has the right length;
4. ``evaluate_config`` targets the forward relative *direction*, is causal and
   cross-sectional, and its Spearman / permutation / bootstrap inference is bounded
   and deterministic;
5. the composed floor ANDs the EVAL-71 surface floor (both underlyings) with the
   cross-sectional alignment floor (neither weakened);
6. ``run_eval88(write=False)`` reports BLOCKED below the composed floor and a
   verdict above it;
7. the protocol/floor constants are the pre-registered ones.
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
import scripts.eval88_cross_sectional_surface_basis_directional_spread as e88

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


# ---------------------------------------------------------------------------
# Fixtures (mirror the EVAL-77 cross-sectional captures)
# ---------------------------------------------------------------------------
def _craft_capture(inst="BTC", n_bars=200, seed=0, base_iv=0.8,
                   base_ms=_BASE_MS, bar_ms=_BAR_MS):
    """Deterministic three-way capture with perp candles and a near-ATM option
    trade tape (real ``iv`` per trade)."""
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


def _craft_cs(closes_btc, closes_eth, *, base_ms=_BASE_MS, bar_ms=_BAR_MS):
    """A minimal aligned cross-section maps object (no surface needed) for testing
    the pure forward-return-spread math."""
    common = [base_ms + i * bar_ms for i in range(len(closes_btc))]
    maps = {
        "BTC": {common[i]: {"close": closes_btc[i]} for i in range(len(closes_btc))},
        "ETH": {common[i]: {"close": closes_eth[i]} for i in range(len(closes_eth))},
    }
    return {"maps": maps, "common": common, "bar_seconds": 300.0,
            "underlyings": ["BTC", "ETH"]}


def _write_captures(caps):
    td = tempfile.mkdtemp()
    for inst, cap in caps.items():
        p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
    return td


# ---------------------------------------------------------------------------
# 1) artifact ids
# ---------------------------------------------------------------------------
def test_ids_are_eval88():
    assert e88.REPORT_ID.startswith("EVAL_88_")
    assert e88.PREREG_ID.startswith("EVAL_88_")
    assert e88.BLOCKED_ID.startswith("EVAL_88_")
    assert "CROSS_SECTIONAL" in e88.REPORT_ID
    assert "DIRECTIONAL_SPREAD" in e88.REPORT_ID


# ---------------------------------------------------------------------------
# 2) sealed machinery reused verbatim
# ---------------------------------------------------------------------------
def test_reuses_sealed_machinery_verbatim():
    assert e88.e61 is e61
    assert e88.e62 is e62
    assert e88.e65 is e65
    assert e88.e71 is e71
    assert e88.e77 is e77
    # EVAL-77 cross-section + relative-signal reconstruction, verbatim
    assert e88.e77.build_cross_section is e77.build_cross_section
    assert e88.e77._relative_signal_series is e77._relative_signal_series
    assert e88.e77._closes_on_common is e77._closes_on_common
    # EVAL-71 surface floor, verbatim
    assert e88.e71._underlying_surface_floor is e71._underlying_surface_floor
    # EVAL-65 IC stats, verbatim
    assert e88.e65._perm_p_ic is e65._perm_p_ic
    assert e88.e65._boot_ci_ic is e65._boot_ci_ic
    # stats / grid constants match the sealed sources exactly
    assert e88.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e88.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e88.BOOTSTRAP_BLOCK == e65.BOOTSTRAP_BLOCK
    assert e88.SEED == e62.SEED
    assert e88.ZWINDOW == e62.ZWINDOW
    assert e88.FDR_ALPHA == e62.FDR_ALPHA
    assert e88.BASELINE == "BTC" and e88.RELATIVE == "ETH"


# ---------------------------------------------------------------------------
# 3) forward relative signed return spread (causal, BTC-minus-ETH, right length)
# ---------------------------------------------------------------------------
def test_forward_rel_return_spread_is_btc_minus_eth_and_causal():
    # BTC rises, ETH falls -> relative spread strictly positive at every k.
    n = 12
    h = 3
    closes_btc = [100.0 * (1.01 ** i) for i in range(n)]
    closes_eth = [100.0 * (0.99 ** i) for i in range(n)]
    cs = _craft_cs(closes_btc, closes_eth)
    out = e88._forward_rel_return_spread(cs, h)
    assert len(out) == len(cs["common"]) - h
    assert all(v > 0.0 for v in out)

    # exact formula check at k=0
    lr_b0 = math.log(closes_btc[1] / closes_btc[0])
    lr_e0 = math.log(closes_eth[1] / closes_eth[0])
    lr_b1 = math.log(closes_btc[2] / closes_btc[1])
    lr_e1 = math.log(closes_eth[2] / closes_eth[1])
    lr_b2 = math.log(closes_btc[3] / closes_btc[2])
    lr_e2 = math.log(closes_eth[3] / closes_eth[2])
    expected0 = (lr_b0 + lr_b1 + lr_b2) / h - (lr_e0 + lr_e1 + lr_e2) / h
    assert abs(out[0] - expected0) < 1e-12


def test_forward_rel_return_spread_sign_flips_when_eth_outperforms():
    n = 10
    h = 3
    closes_btc = [100.0 * (0.99 ** i) for i in range(n)]
    closes_eth = [100.0 * (1.01 ** i) for i in range(n)]
    cs = _craft_cs(closes_btc, closes_eth)
    out = e88._forward_rel_return_spread(cs, h)
    assert all(v < 0.0 for v in out)


def test_forward_rel_return_spread_short_window_is_empty():
    n = 4
    h = 6  # horizon longer than the available returns
    cs = _craft_cs([100.0 + i for i in range(n)], [100.0 + i for i in range(n)])
    out = e88._forward_rel_return_spread(cs, h)
    assert out == []


# ---------------------------------------------------------------------------
# 4) evaluate_config targets the forward relative direction
# ---------------------------------------------------------------------------
def test_evaluate_config_runs_and_is_bounded(monkeypatch):
    monkeypatch.setattr(e88, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e88, "BOOTSTRAP_RESAMPLES", 50)
    caps = _captures(n_bars=200, seed_btc=11, seed_eth=12)
    res = e88.evaluate_config(
        caps, surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6
    )
    assert res["target"] == "forward_relative_signed_return_spread"
    assert res["n_pairs"] >= e88.MIN_USABLE_PAIRS_PER_CONFIG
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
    monkeypatch.setattr(e88, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e88, "BOOTSTRAP_RESAMPLES", 50)
    caps = _captures(n_bars=200, seed_btc=13, seed_eth=14)
    a = e88.evaluate_config(caps, surface_signal="skew", bar_seconds=300.0, horizon_bars=6)
    b = e88.evaluate_config(caps, surface_signal="skew", bar_seconds=300.0, horizon_bars=6)
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_evaluate_config_insufficient_common_bars(monkeypatch):
    monkeypatch.setattr(
        e88.e77, "build_cross_section",
        lambda captures, bar_seconds: {"common": [1, 2, 3], "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    res = e88.evaluate_config(
        {"BTC": {}, "ETH": {}}, surface_signal="atm_iv", bar_seconds=300.0,
        horizon_bars=6,
    )
    assert res["n_pairs"] == 0
    assert res["pass"] is False
    assert res["reason"] == "insufficient_common_bars"


def test_evaluate_config_insufficient_pairs(monkeypatch):
    monkeypatch.setattr(e88, "MIN_USABLE_PAIRS_PER_CONFIG", 8)
    monkeypatch.setattr(
        e88.e77, "build_cross_section",
        lambda captures, bar_seconds: {"common": list(range(12)), "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    monkeypatch.setattr(
        e88.e77, "_relative_signal_series",
        lambda cs, surface_signal: [0.0] * len(cs["common"]),
    )
    monkeypatch.setattr(
        e88, "_forward_rel_return_spread",
        lambda cs, horizon_bars: [0.0] * (len(cs["common"]) - horizon_bars),
    )
    res = e88.evaluate_config(
        {"BTC": {}, "ETH": {}}, surface_signal="atm_iv", bar_seconds=300.0,
        horizon_bars=6,
    )
    assert res["n_pairs"] < 8
    assert res["pass"] is False
    assert res["reason"] == "insufficient_pairs"


# ---------------------------------------------------------------------------
# 5) composed floor (EVAL-71 both underlyings AND alignment)
# ---------------------------------------------------------------------------
def test_campaign_floor_composes_eval71_and_alignment(monkeypatch):
    ok_floor = {"ok": True, "checks": {"option_trades_ok": True}}
    monkeypatch.setattr(e88.e71, "_underlying_surface_floor", lambda cap: ok_floor)
    monkeypatch.setattr(
        e88.e77, "build_cross_section",
        lambda captures, bar_seconds: {"common": list(range(300)), "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    caps = {"BTC": {"underlying": "BTC"}, "ETH": {"underlying": "ETH"}}
    fl = e88.campaign_floor(caps)
    assert fl["ok"] is True
    assert fl["underlyings_ok"] is True and fl["aligned_ok"] is True
    assert fl["aligned_common_bars_binding"] == 300

    # one underlying below the EVAL-71 floor -> underlyings_ok False
    monkeypatch.setattr(
        e88.e71, "_underlying_surface_floor",
        lambda cap: {"ok": cap.get("underlying") == "BTC", "checks": {}},
    )
    fl2 = e88.campaign_floor(caps)
    assert fl2["ok"] is False and fl2["underlyings_ok"] is False

    # alignment floor restored but too few common bars -> aligned_ok False
    monkeypatch.setattr(e88.e71, "_underlying_surface_floor", lambda cap: ok_floor)
    monkeypatch.setattr(
        e88.e77, "build_cross_section",
        lambda captures, bar_seconds: {"common": list(range(10)), "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    fl3 = e88.campaign_floor(caps)
    assert fl3["ok"] is False and fl3["aligned_ok"] is False


def test_campaign_floor_blocks_short_capture():
    caps = _captures(n_bars=10, seed_btc=9, seed_eth=10)
    fl = e88.campaign_floor(caps)
    assert fl["ok"] is False
    assert fl["underlyings_ok"] is False or fl["aligned_ok"] is False


def test_campaign_floor_blocks_empty():
    assert e88.campaign_floor({})["ok"] is False


# ---------------------------------------------------------------------------
# 6) orchestration (write=False; no research_state writes)
# ---------------------------------------------------------------------------
def test_run_eval88_no_write_blocks_below_floor():
    caps = _captures(n_bars=20, seed_btc=15, seed_eth=16)
    td = _write_captures(caps)
    report = e88.run_eval88(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e88.REPORT_ID


def test_run_eval88_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e88, "SURFACE_SIGNALS", ("atm_iv",))
    monkeypatch.setattr(e88, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e88, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e88, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e88, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e88, "campaign_floor",
        lambda captures: {"underlyings": sorted(captures), "per_underlying": {},
                          "underlyings_ok": True, "aligned_ok": True,
                          "aligned_common_bars_by_grid": {"300.0": 200},
                          "aligned_common_bars_binding": 200, "ok": True,
                          "checks": {}},
    )
    caps = _captures(n_bars=200, seed_btc=17, seed_eth=18)
    td = _write_captures(caps)
    report = e88.run_eval88(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert report["summary"]["n_configs"] == 1
    assert len(report["per_config"]) == 1
    assert report["protocol"]["cross_section"]["baseline"] == "BTC"
    assert report["protocol"]["cross_section"]["relative"] == "ETH"
    assert report["protocol"]["target"] == "forward_relative_signed_return_spread"


# ---------------------------------------------------------------------------
# 7) protocol / floor constants
# ---------------------------------------------------------------------------
def test_protocol_and_floor_constants():
    p = e88.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_aligned_common_bars"] == 200
    assert p["floor"]["min_usable_pairs_per_config"] == e88.MIN_USABLE_PAIRS_PER_CONFIG
    assert set(p["surface_signals"]) == {"atm_iv", "skew"}
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert p["target"] == "forward_relative_signed_return_spread"
    assert p["cross_section"]["baseline"] == "BTC"
    assert p["cross_section"]["relative"] == "ETH"
    assert "EVAL-77" in p["extends"]
    assert "direction" in p["title"].lower()
    assert "EVAL-71" in p["floor"]["note"]