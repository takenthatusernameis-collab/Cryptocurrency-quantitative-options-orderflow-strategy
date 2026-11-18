"""Unit tests for EVAL-93: the **cross-sectional** options **term-slope basis**
(BTC-vs-ETH relative near-minus-far near-ATM IV term slope) -> subsequent
relative *realized-vol* (RV) spread (BTC-minus-ETH forward RV) predictiveness.

EVAL-93 is the on-charter, runnable-now *cross-sectional term-slope* partner to
EVAL-74 (own-asset term slope -> own RV, sealed NO-GO) and EVAL-77 (cross-sectional
level/skew basis -> relative RV spread, sealed GO), and a distinct cell from
EVAL-84 (own-asset term slope -> own vol-of-vol), EVAL-88 (relative direction),
EVAL-89/92 (relative VRP spread), and EVAL-90/91 (relative vol-of-vol). It reuses
the sealed EVAL-61/62/65/71/74/77 machinery verbatim, needs no new acquisition and
no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-93;
2. the sealed machinery (EVAL-61/62/65/71/74/77 helpers) is reused verbatim, not
   forked;
3. ``build_cross_section_with_term`` overlays EVAL-74 ``term_slope`` onto EVAL-77's
   common aligned cross-section by ``bar_open_ms`` without changing the bar grid,
   ``close`` series, or ``common`` set;
4. ``_relative_term_slope_series`` delegates to the EVAL-77 relative series with
   the ``term_slope`` signal (not atm_iv/skew);
5. ``_forward_rel_rv_spread`` is the BTC-minus-ETH forward *realized-vol* spread, is
   causal, and has the right length;
6. ``evaluate_config`` targets the forward relative *RV* spread with the
   ``term_slope`` signal, is causal and cross-sectional, and its Spearman /
   permutation / bootstrap inference is bounded and deterministic;
7. the composed floor ANDs the EVAL-74 term floor (both underlyings) with the
   EVAL-77 cross-sectional alignment floor (neither weakened);
8. ``run_eval93(write=False)`` reports BLOCKED below the composed floor and a
   verdict above it;
9. the protocol/floor constants are the pre-registered ones, and the signal is
   pinned to ``term_slope`` (not atm_iv/skew).
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
import scripts.eval74_surface_term_structure_predictiveness as e74
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77
import scripts.eval93_cross_sectional_term_slope_basis_relative_rv_spread as e93

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000
DEFAULT_EXPIRIES = ("18NOV26", "20NOV26", "27NOV26", "4DEC26")


# ---------------------------------------------------------------------------
# Fixtures (mirror EVAL-74's multi-expiry term-structure captures)
# ---------------------------------------------------------------------------
def _craft_term_capture(
    inst="BTC",
    *,
    n_bars=200,
    seed=0,
    n_trades_per_bar=40,
    base_ms=_BASE_MS,
    bar_ms=_BAR_MS,
    expiries=DEFAULT_EXPIRIES,
):
    """Deterministic three-way capture whose real option-trade IV term structure
    (near-minus-far near-ATM IV slope) is populated across several expiries."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    n_exp = len(expiries)
    candles = []
    trades = []
    latent = 0.5
    for i in range(n_bars):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        for j in range(n_trades_per_bar):
            e_idx = j % n_exp
            frac = (e_idx / (n_exp - 1)) if n_exp > 1 else 0.0
            base_iv = 60.0 - frac * 20.0
            sens = 20.0 * (1.0 - frac)
            strike = px * (1.0 + rng.uniform(-0.04, 0.04))
            typ = "P" if j % 2 == 0 else "C"
            iv = max(1.0, base_iv + latent * sens + rng.uniform(-0.5, 0.5))
            trades.append({
                "ts": ts + rng.randint(1, bar_ms - 1),
                "instrument": f"{inst}-{expiries[e_idx]}-{int(round(strike))}-{typ}",
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
        "source": {"authenticated": False, "public_read_only": True,
                   "venue": "deribit+okx"},
    }


def _captures(n_bars=200, seed_btc=1, seed_eth=2):
    return {
        "BTC": _craft_term_capture("BTC", n_bars=n_bars, seed=seed_btc),
        "ETH": _craft_term_capture("ETH", n_bars=n_bars, seed=seed_eth),
    }


def _craft_cs(closes_btc, closes_eth, *, base_ms=_BASE_MS, bar_ms=_BAR_MS):
    """A minimal aligned cross-section maps object (close per bar) for testing the
    pure forward-RV-spread math (EVAL-77 ``_closes_on_common`` + ``_rv_series``)."""
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
def test_ids_are_eval93():
    assert e93.REPORT_ID.startswith("EVAL_93_")
    assert e93.PREREG_ID.startswith("EVAL_93_")
    assert e93.BLOCKED_ID.startswith("EVAL_93_")
    assert "CROSS_SECTIONAL" in e93.REPORT_ID
    assert "TERM_SLOPE_BASIS" in e93.REPORT_ID
    assert "RELATIVE_RV_SPREAD" in e93.REPORT_ID


# ---------------------------------------------------------------------------
# 2) sealed machinery reused verbatim
# ---------------------------------------------------------------------------
def test_reuses_sealed_machinery_verbatim():
    assert e93.e61 is e61
    assert e93.e62 is e62
    assert e93.e65 is e65
    assert e93.e71 is e71
    assert e93.e74 is e74
    assert e93.e77 is e77
    # EVAL-77 cross-section + relative-signal + forward-RV helpers, verbatim
    assert e93.e77.build_cross_section is e77.build_cross_section
    assert e93.e77._relative_signal_series is e77._relative_signal_series
    assert e93.e77._closes_on_common is e77._closes_on_common
    assert e93.e77._rv_series is e77._rv_series
    # EVAL-74 term-structure helpers, verbatim
    assert e93.e74._term_bars is e74._term_bars
    assert e93.e74._underlying_term_floor is e74._underlying_term_floor
    assert e93.e74._term_adequacy is e74._term_adequacy
    # EVAL-65 IC stats, verbatim
    assert e93.e65._perm_p_ic is e65._perm_p_ic
    assert e93.e65._boot_ci_ic is e65._boot_ci_ic
    # stats / grid / term constants match the sealed sources exactly
    assert e93.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e93.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e93.BOOTSTRAP_BLOCK == e65.BOOTSTRAP_BLOCK
    assert e93.SEED == e62.SEED
    assert e93.ZWINDOW == e62.ZWINDOW
    assert e93.FDR_ALPHA == e62.FDR_ALPHA
    assert e93.SIGNAL_WINDOW_SECONDS == e74.SIGNAL_WINDOW_SECONDS
    assert e93.ATM_BAND == e74.ATM_BAND
    assert e93.MIN_EXPIRY_TRADES == e74.MIN_EXPIRY_TRADES
    assert e93.MIN_DISTINCT_EXPIRIES == e74.MIN_DISTINCT_EXPIRIES
    assert e93.MIN_BARS_WITH_TERM == e74.MIN_BARS_WITH_TERM
    assert e93.BASELINE == "BTC" and e93.RELATIVE == "ETH"


def test_underlying_term_floor_delegates_to_eval74_verbatim():
    cap = _craft_term_capture("BTC", n_bars=1010, seed=3, n_trades_per_bar=40)
    assert e93._underlying_term_floor(cap) == e74._underlying_term_floor(cap)


# ---------------------------------------------------------------------------
# 3) build_cross_section_with_term overlays term_slope onto the EVAL-77 grid
# ---------------------------------------------------------------------------
def test_build_cross_section_with_term_preserves_eval77_grid_and_close():
    caps = _captures(n_bars=60, seed_btc=21, seed_eth=22)
    cs = e93.build_cross_section_with_term(caps, bar_seconds=300.0)
    base = e77.build_cross_section(caps, bar_seconds=300.0)
    # identical common bar grid and close series (the overlay must not disturb them)
    assert cs["common"] == base["common"]
    for inst in ("BTC", "ETH"):
        for bo in base["common"]:
            assert cs["maps"][inst][int(bo)]["close"] == base["maps"][inst][int(bo)]["close"]
            # every bar carries a term_slope field (None or float)
            assert "term_slope" in cs["maps"][inst][int(bo)]


def test_build_cross_section_with_term_matches_eval74_term_slope():
    caps = _captures(n_bars=60, seed_btc=23, seed_eth=24)
    cs = e93.build_cross_section_with_term(caps, bar_seconds=300.0)
    for inst in ("BTC", "ETH"):
        term = {int(b["bar_open_ms"]): b for b in
                e74._term_bars(caps[inst], bar_seconds=300.0)}
        for bo in cs["common"]:
            want = term[int(bo)]["term_slope"]
            got = cs["maps"][inst][int(bo)]["term_slope"]
            assert got == want


# ---------------------------------------------------------------------------
# 4) relative term-slope basis (delegates to EVAL-77 relative series, term_slope)
# ---------------------------------------------------------------------------
def test_relative_term_slope_series_delegates_with_term_slope_signal(monkeypatch):
    seen = {}

    def _spy(cs, surface_signal):
        seen["surface_signal"] = surface_signal
        return [0.0] * len(cs["common"])

    monkeypatch.setattr(e93.e77, "_relative_signal_series", _spy)
    cs = {"common": list(range(12)), "maps": {}, "bar_seconds": 300.0,
          "underlyings": ["BTC", "ETH"]}
    e93._relative_term_slope_series(cs, term_signal="term_slope")
    assert seen["surface_signal"] == "term_slope"


def test_relative_term_slope_series_equals_eval77_relative_series():
    caps = _captures(n_bars=60, seed_btc=25, seed_eth=26)
    cs = e93.build_cross_section_with_term(caps, bar_seconds=300.0)
    got = e93._relative_term_slope_series(cs, term_signal="term_slope")
    want = e77._relative_signal_series(cs, surface_signal="term_slope")
    assert got == want


# ---------------------------------------------------------------------------
# 5) forward relative RV spread (causal, BTC-minus-ETH, right length)
# ---------------------------------------------------------------------------
def test_forward_rel_rv_spread_flat_is_zero():
    n = 12
    cs = _craft_cs([100.0] * n, [100.0] * n)
    out = e93._forward_rel_rv_spread(cs, 3)
    assert len(out) == n - 3
    assert all(abs(v) < 1e-12 for v in out)


def test_forward_rel_rv_spread_reflects_relative_vol():
    # ETH more volatile than BTC -> rv_BTC - rv_ETH < 0
    n = 12
    btc = [100.0 * (1.0001 ** i) for i in range(n)]
    eth = [100.0 * (1.01 ** (i % 2)) * (1.0001 ** i) for i in range(n)]
    cs = _craft_cs(btc, eth)
    out = e93._forward_rel_rv_spread(cs, 3)
    assert len(out) == n - 3
    assert sum(out) < 0.0


def test_forward_rel_rv_spread_short_window_is_empty():
    n = 4
    cs = _craft_cs([100.0 + i for i in range(n)], [100.0 + i for i in range(n)])
    out = e93._forward_rel_rv_spread(cs, 6)
    assert out == []


# ---------------------------------------------------------------------------
# 6) evaluate_config targets the forward relative RV spread with term_slope
# ---------------------------------------------------------------------------
def test_evaluate_config_runs_and_is_bounded(monkeypatch):
    monkeypatch.setattr(e93, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e93, "BOOTSTRAP_RESAMPLES", 50)
    caps = _captures(n_bars=200, seed_btc=11, seed_eth=12)
    res = e93.evaluate_config(
        caps, term_signal="term_slope", bar_seconds=300.0, horizon_bars=6
    )
    assert res["target"] == "forward_relative_rv_spread"
    assert res["signal"] == "term_slope"
    assert res["n_pairs"] >= e93.MIN_USABLE_PAIRS_PER_CONFIG
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
    monkeypatch.setattr(e93, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e93, "BOOTSTRAP_RESAMPLES", 50)
    caps = _captures(n_bars=200, seed_btc=13, seed_eth=14)
    a = e93.evaluate_config(caps, term_signal="term_slope", bar_seconds=300.0, horizon_bars=6)
    b = e93.evaluate_config(caps, term_signal="term_slope", bar_seconds=300.0, horizon_bars=6)
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_evaluate_config_uses_term_slope_not_atm_iv(monkeypatch):
    seen = {}

    def _spy(cs, surface_signal):
        seen["surface_signal"] = surface_signal
        return [0.0] * len(cs["common"])

    monkeypatch.setattr(e93.e77, "_relative_signal_series", _spy)
    monkeypatch.setattr(
        e93, "build_cross_section_with_term",
        lambda captures, bar_seconds: {"common": list(range(12)), "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    monkeypatch.setattr(
        e93, "_forward_rel_rv_spread",
        lambda cs, horizon_bars: [0.0] * (len(cs["common"]) - horizon_bars),
    )
    e93.evaluate_config(
        {"BTC": {}, "ETH": {}}, term_signal="term_slope", bar_seconds=300.0,
        horizon_bars=6,
    )
    assert seen["surface_signal"] == "term_slope"


def test_evaluate_config_insufficient_common_bars(monkeypatch):
    monkeypatch.setattr(
        e93, "build_cross_section_with_term",
        lambda captures, bar_seconds: {"common": [1, 2, 3], "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    res = e93.evaluate_config(
        {"BTC": {}, "ETH": {}}, term_signal="term_slope", bar_seconds=300.0,
        horizon_bars=6,
    )
    assert res["n_pairs"] == 0
    assert res["pass"] is False
    assert res["reason"] == "insufficient_common_bars"


def test_evaluate_config_insufficient_pairs(monkeypatch):
    monkeypatch.setattr(e93, "MIN_USABLE_PAIRS_PER_CONFIG", 8)
    monkeypatch.setattr(
        e93, "build_cross_section_with_term",
        lambda captures, bar_seconds: {"common": list(range(12)), "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    monkeypatch.setattr(
        e93, "_relative_term_slope_series",
        lambda cs, term_signal="term_slope": [0.0] * len(cs["common"]),
    )
    monkeypatch.setattr(
        e93, "_forward_rel_rv_spread",
        lambda cs, horizon_bars: [0.0] * (len(cs["common"]) - horizon_bars),
    )
    res = e93.evaluate_config(
        {"BTC": {}, "ETH": {}}, term_signal="term_slope", bar_seconds=300.0,
        horizon_bars=6,
    )
    assert res["n_pairs"] < 8
    assert res["pass"] is False
    assert res["reason"] == "insufficient_pairs"


# ---------------------------------------------------------------------------
# 7) composed floor (EVAL-74 term both underlyings AND EVAL-77 alignment)
# ---------------------------------------------------------------------------
def test_campaign_floor_composes_eval74_and_alignment(monkeypatch):
    ok_floor = {"ok": True, "checks": {"eval71_floor_ok": True}}

    monkeypatch.setattr(e93, "_underlying_term_floor", lambda cap: ok_floor)
    monkeypatch.setattr(
        e93.e77, "build_cross_section",
        lambda captures, bar_seconds: {"common": list(range(300)), "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    caps = {"BTC": {"underlying": "BTC"}, "ETH": {"underlying": "ETH"}}
    fl = e93.campaign_floor(caps)
    assert fl["ok"] is True
    assert fl["underlyings_ok"] is True and fl["aligned_ok"] is True
    assert fl["aligned_common_bars_binding"] == 300

    # one underlying below the EVAL-74 term floor -> underlyings_ok False
    monkeypatch.setattr(
        e93, "_underlying_term_floor",
        lambda cap: {"ok": cap.get("underlying") == "BTC", "checks": {}},
    )
    fl2 = e93.campaign_floor(caps)
    assert fl2["ok"] is False and fl2["underlyings_ok"] is False

    # term floor restored but too few common bars -> aligned_ok False
    monkeypatch.setattr(e93, "_underlying_term_floor", lambda cap: ok_floor)
    monkeypatch.setattr(
        e93.e77, "build_cross_section",
        lambda captures, bar_seconds: {"common": list(range(10)), "maps": {},
                                       "bar_seconds": bar_seconds,
                                       "underlyings": sorted(captures)},
    )
    fl3 = e93.campaign_floor(caps)
    assert fl3["ok"] is False and fl3["aligned_ok"] is False


def test_campaign_floor_blocks_empty():
    assert e93.campaign_floor({})["ok"] is False


def test_campaign_floor_blocks_sparse_capture():
    # few bars, few trades per bar -> EVAL-74 term adequacy fails
    caps = _captures(n_bars=30, seed_btc=9, seed_eth=10)
    caps = {k: _craft_term_capture(k, n_bars=30, seed=9, n_trades_per_bar=3)
            for k in ("BTC", "ETH")}
    fl = e93.campaign_floor(caps)
    assert fl["ok"] is False
    assert fl["underlyings_ok"] is False or fl["aligned_ok"] is False


# ---------------------------------------------------------------------------
# 8) orchestration (write=False; no research_state writes)
# ---------------------------------------------------------------------------
def test_run_eval93_no_write_blocks_below_floor():
    caps = {
        "BTC": _craft_term_capture("BTC", n_bars=20, seed=15, n_trades_per_bar=3),
        "ETH": _craft_term_capture("ETH", n_bars=20, seed=16, n_trades_per_bar=3),
    }
    td = _write_captures(caps)
    report = e93.run_eval93(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e93.REPORT_ID


def test_run_eval93_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e93, "TERM_SIGNALS", ("term_slope",))
    monkeypatch.setattr(e93, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e93, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e93, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e93, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e93, "campaign_floor",
        lambda captures: {"underlyings": sorted(captures), "per_underlying": {},
                          "underlyings_ok": True, "aligned_ok": True,
                          "aligned_common_bars_by_grid": {"300.0": 200},
                          "aligned_common_bars_binding": 200, "ok": True,
                          "checks": {}},
    )
    caps = _captures(n_bars=200, seed_btc=17, seed_eth=18)
    td = _write_captures(caps)
    report = e93.run_eval93(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert report["summary"]["n_configs"] == 1
    assert len(report["per_config"]) == 1
    assert report["protocol"]["cross_section"]["baseline"] == "BTC"
    assert report["protocol"]["cross_section"]["relative"] == "ETH"
    assert report["protocol"]["target"] == "forward_relative_rv_spread"


# ---------------------------------------------------------------------------
# 9) protocol / floor constants (signal pinned to term_slope)
# ---------------------------------------------------------------------------
def test_protocol_and_floor_constants():
    p = e93.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_aligned_common_bars"] == 200
    assert p["floor"]["min_distinct_expiries"] == e93.MIN_DISTINCT_EXPIRIES
    assert p["floor"]["min_expiry_trades"] == e93.MIN_EXPIRY_TRADES
    assert p["floor"]["min_bars_with_term"] == e93.MIN_BARS_WITH_TERM
    assert p["floor"]["min_usable_pairs_per_config"] == e93.MIN_USABLE_PAIRS_PER_CONFIG
    assert tuple(p["term_signals"]) == ("term_slope",)
    assert e93.TERM_SIGNALS == ("term_slope",)
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert p["target"] == "forward_relative_rv_spread"
    assert p["cross_section"]["baseline"] == "BTC"
    assert p["cross_section"]["relative"] == "ETH"
    assert "EVAL-74" in p["extends"]
    assert "EVAL-77" in p["extends"]
    assert "EVAL-71" in p["floor"]["note"] or "EVAL-74" in p["floor"]["note"]
    assert "term" in p["title"].lower()


def test_signal_is_term_slope_basis_in_protocol_text():
    p = e93.build_protocol("data/raw/eval61")
    # the relative signal must be the near-minus-far term slope basis, not atm_iv/skew
    assert "term_slope" in p["cross_section"]["relative_signal"]
    assert "atm_iv" not in p["cross_section"]["relative_signal"]
    assert "skew" not in p["cross_section"]["relative_signal"]
    assert "term_slope" in p["signal"].lower() or "term structure" in p["signal"].lower()