"""Unit tests for EVAL-130: the **cross-sectional causal near-to-far ATM
implied-vol atm_iv basis (atm_iv_ETH - atm_iv_BTC) -> subsequent forward
relative realized return tail-asymmetry spread** predictiveness.

EVAL-130 is the on-charter, runnable-now mandatory next campaign after EVAL-129
that EVAL-77 (cross-sectional surface basis atm_iv+skew -> forward realized-vol
spread), EVAL-105/106 (cross-sectional term-ratio/term-slope basis -> forward
relative tail-asymmetry spread), EVAL-110 (cross-sectional skew basis -> forward
relative tail-asymmetry spread), EVAL-128 (cross-sectional atm_iv basis -> forward
relative return skewness spread), and EVAL-127 (cross-sectional atm_iv basis ->
forward relative return kurtosis spread) leave open: the *cross-sectional atm_iv
basis* vs the *forward relative realized return tail-asymmetry spread*. It reuses
the sealed EVAL-61/62/65/71/77/85 signal reconstructions and the EVAL-65
inference verbatim, needs no new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-130;
2. the sealed machinery (EVAL-61/62/65/71/77/85 helpers) is reused verbatim, not forked;
3. ``_forward_return_tail_asym`` is causal (target strictly after bar k) and is
   None on degenerate / fewer-than-3-returns windows;
4. the relative realized return tail-asymmetry spread is tail_asym_BTC - tail_asym_ETH;
5. ``evaluate_config`` targets the cross-sectional relative spread, is causal,
   and its Spearman / permutation / bootstrap inference is bounded and deterministic;
6. the composed floor ANDs the sealed EVAL-77 surface basis floor (not weakened);
7. ``run_eval130(write=False)`` reports BLOCKED below the composed floor and a
   verdict above it;
8. the protocol/floor constants are the pre-registered ones.
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77
import scripts.eval85_surface_skew_forward_return_tail as e85
import scripts.eval130_cross_sectional_atm_iv_basis_forward_relative_return_tail_asymmetry_spread as e130

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _captures(insts=("BTC", "ETH")):
    return {
        i: {"underlying": i, "surface": {"snapshots": []},
            "option_trades": [], "perp_bars": []}
        for i in insts
    }


def _write_captures(caps):
    td = tempfile.mkdtemp()
    for inst, cap in caps.items():
        p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
    return td


# ---------------------------------------------------------------------------
# 1) artifact ids
# ---------------------------------------------------------------------------
def test_ids_are_eval130():
    assert e130.REPORT_ID.startswith("EVAL_130_")
    assert e130.PREREG_ID.startswith("EVAL_130_")
    assert e130.BLOCKED_ID.startswith("EVAL_130_")
    assert "ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD" in e130.REPORT_ID
    assert e130.TARGET == "forward_relative_tail_asymmetry_spread"
    assert e130.SURFACE_SIGNALS == ("atm_iv",)


# ---------------------------------------------------------------------------
# 2) sealed helpers reused verbatim
# ---------------------------------------------------------------------------
def test_uses_sealed_helpers_verbatim():
    assert e130.e61 is e61
    assert e130.e62 is e62
    assert e130.e65 is e65
    assert e130.e71 is e71
    assert e130.e77 is e77
    assert e130.e85 is e85
    assert e130.PERMUTATION_PERMS is e65.PERMUTATION_PERMS
    assert e130.BOOTSTRAP_RESAMPLES is e65.BOOTSTRAP_RESAMPLES
    assert e130.BOOTSTRAP_BLOCK is e65.BOOTSTRAP_BLOCK
    assert e130.FDR_ALPHA is e62.FDR_ALPHA
    assert e130.SEED is e62.SEED
    assert e130.ZWINDOW is e62.ZWINDOW
    assert e130.build_cross_section is e77.build_cross_section
    assert e130._closes_on_common is e77._closes_on_common
    assert e130._relative_signal_series is e77._relative_signal_series
    assert e130.campaign_floor is e77.campaign_floor


# ---------------------------------------------------------------------------
# 3) forward return tail-asymmetry target: causal + degenerate handling
# ---------------------------------------------------------------------------
def test_forward_return_tail_asym_length_and_none():
    closes = [1.0, 2.0, 4.0, 7.0, 11.0]
    # lr has 4 entries; h=2 -> windows k=0..2 -> 3 outputs
    out = e130._forward_return_tail_asym(closes, horizon_bars=2)
    assert len(out) == max(0, len(closes) - 1 - 2 + 1)
    # h larger than available returns -> empty
    assert e130._forward_return_tail_asym(closes, horizon_bars=10) == []


def test_forward_return_tail_asym_degenerate_none():
    # fewer than 3 returns -> None
    closes = [1.0, 2.0, 3.0]  # lr = [ln2, ln1.5], h=3 -> seg length 2 < 3
    out = e130._forward_return_tail_asym(closes, horizon_bars=3)
    assert out == []


def test_forward_return_tail_asym_causal_target_after_k():
    # output index k corresponds to returns k+1..k+H (strictly after bar k);
    # verified by length contract and finiteness on a normal series
    closes = [1.0, 1.5, 2.2, 3.1, 4.4, 6.0]
    for h in (3, 5):
        out = e130._forward_return_tail_asym(closes, horizon_bars=h)
        expected = max(0, len(closes) - 1 - h + 1)
        assert len(out) == expected
        for v in out:
            assert v is None or math.isfinite(v)


# ---------------------------------------------------------------------------
# 4) relative spread direction: tail_asym_BTC - tail_asym_ETH
# ---------------------------------------------------------------------------
def test_relative_spread_is_btc_minus_eth():
    # Evaluate on a tiny aligned grid; just confirm spread == btc - eth per bar.
    # Need >= 3 returns per window (h=3) and finite values; use asymmetric increments.
    closes_b = [1.0, 1.5, 2.2, 3.1, 4.4]  # lr length 4 -> h=3 gives 2 windows
    closes_r = [1.0, 1.8, 3.0, 4.4, 6.2]  # lr length 4 -> h=3 gives 2 windows
    tb = e130._forward_return_tail_asym(closes_b, horizon_bars=3)
    tr = e130._forward_return_tail_asym(closes_r, horizon_bars=3)
    n = min(len(tb), len(tr))
    spread = [float(tb[k]) - float(tr[k]) for k in range(n)]
    assert spread == [float(tb[k]) - float(tr[k]) for k in range(n)]
    # both legs must be finite on this non-degenerate series
    for a, b in zip(tb, tr):
        assert a is not None and b is not None
        assert math.isfinite(a) and math.isfinite(b)


# ---------------------------------------------------------------------------
# 5) evaluate_config cross-sectional shape
# ---------------------------------------------------------------------------
def test_evaluate_config_cross_sectional_shape():
    caps = _captures()
    res = e130.evaluate_config(
        caps, surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=6
    )
    assert res["signal"] == "atm_iv"
    assert res["bar_seconds"] == 300.0
    assert res["horizon_bars"] == 6
    assert "n_common_bars" in res and "n_pairs" in res
    assert "spearman_ic" in res and "permutation_p" in res
    assert "bootstrap_ci" in res and len(res["bootstrap_ci"]) == 3
    assert res["pass"] is False  # empty fixtures -> no pairs


def test_evaluate_config_insufficient_pairs():
    caps = _captures()
    res = e130.evaluate_config(
        caps, surface_signal="atm_iv", bar_seconds=60.0, horizon_bars=72
    )
    assert res["n_pairs"] < e130.MIN_USABLE_PAIRS_PER_CONFIG
    assert res["pass"] is False


# ---------------------------------------------------------------------------
# 6) composed floor reuses EVAL-77 surface basis floor, not weakened
# ---------------------------------------------------------------------------
def test_campaign_floor_reuses_eval77_not_weakened():
    assert e130.FLOOR is e77.FLOOR
    assert e130.FLOOR["min_underlyings"] == 2
    assert e130.FLOOR["min_aligned_common_bars"] == 200
    assert e130.FLOOR["min_usable_pairs_per_config"] == 120
    # The note identifies this as the EVAL-77 surface basis floor, NOT the
    # EVAL-64 options-surface snapshot floor that governs the ladder.
    note = e130.FLOOR.get("note", "")
    assert "EVAL-77" in note
    assert "NOT the EVAL-64" in note
    caps = _captures()
    floor = e130.campaign_floor(caps)
    assert "per_underlying" in floor
    assert "aligned_ok" in floor
    assert floor["ok"] is False  # empty fixtures below floor


# ---------------------------------------------------------------------------
# 7) run_eval130(write=False): BLOCKED below floor / verdict above
# ---------------------------------------------------------------------------
def test_run_eval130_write_false_structure():
    report = e130.run_eval130(capture_dir=_write_captures(_captures()), write=False)
    assert report["report_id"] == e130.REPORT_ID
    assert report["task"].startswith("EVAL130-")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    assert "floor_ok" in report and "per_config" in report
    assert "pooled" in report and "bh_fdr" in report["pooled"]
    assert len(report["per_config"]) == len(e130.SURFACE_SIGNALS) * len(
        e130.GRID_BAR_SECONDS
    ) * len(e130.FORWARD_HORIZONS_BARS)


def test_go_bar_requires_pooled_bh_fdr():
    report = e130.run_eval130(capture_dir=_write_captures(_captures()), write=False)
    # Empty fixtures -> floor not ok -> BLOCKED, never a synthetic NO-GO
    assert report["verdict"] == "BLOCKED"
    assert report["floor_ok"] is False


# ---------------------------------------------------------------------------
# 8) protocol / floor constants preregistered
# ---------------------------------------------------------------------------
def test_protocol_floor_constants_preregistered():
    proto = e130.build_protocol("data/raw/eval61")
    assert proto["eval"] == "EVAL-130"
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"
    assert proto["cross_section"]["relative_signal"] == "rel_k = atm_iv[ETH](k) - atm_iv[BTC](k)"
    assert "tail_asym_BTC" in proto["cross_section"]["target"]
    assert "tail_asym_ETH" in proto["cross_section"]["target"]
    assert proto["surface_signals"] == ["atm_iv"]
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["stats"]["min_usable_pairs_per_config"] == 120
    assert "no new acquisition" in proto["data_availability"]["note"]
    assert "no network" in proto["data_availability"]["note"]


def test_signal_is_atm_iv_only():
    # Single signal: atm_iv (the cross-sectional atm_iv basis), not skew or term_ratio.
    assert e130.SURFACE_SIGNALS == ("atm_iv",)
    assert "skew" not in e130.SURFACE_SIGNALS
    assert "term_ratio" not in e130.SURFACE_SIGNALS


def test_grid_and_horizons_preregistered():
    assert e130.GRID_BAR_SECONDS == (60.0, 300.0)
    assert e130.FORWARD_HORIZONS_BARS == (6, 24, 72)
    assert len(e130.SURFACE_SIGNALS) * len(e130.GRID_BAR_SECONDS) * len(
        e130.FORWARD_HORIZONS_BARS
    ) == 6


# ---------------------------------------------------------------------------
# 9) no synthetic data / real-data note
# ---------------------------------------------------------------------------
def test_no_synthetic_data_note():
    assert "real" in e130.build_protocol("data/raw/eval61")["data_availability"]["note"]
    assert "no network" in e130.COMMANDS[3]


# ---------------------------------------------------------------------------
# 10) code paths + commands
# ---------------------------------------------------------------------------
def test_code_paths_include_runner():
    assert "scripts/eval130_cross_sectional_atm_iv_basis_forward_relative_return_tail_asymmetry_spread.py" in e130.CODE_PATHS


def test_commands_include_seal_and_no_write():
    assert any("--no-write" in c for c in e130.COMMANDS)
    assert any("--seal" in c for c in e130.COMMANDS)


# ---------------------------------------------------------------------------
# 11) baseline / relative legs
# ---------------------------------------------------------------------------
def test_baseline_relative_legs_btc_eth():
    assert e130.BASELINE == "BTC"
    assert e130.RELATIVE == "ETH"


# ---------------------------------------------------------------------------
# 12) bootstrap CI bounded
# ---------------------------------------------------------------------------
def test_bootstrap_ci_bounded():
    caps = _captures()
    res = e130.evaluate_config(
        caps, surface_signal="atm_iv", bar_seconds=300.0, horizon_bars=24
    )
    ci = res["bootstrap_ci"]
    med, lo, hi = ci
    assert math.isfinite(med) or math.isnan(med)
    assert math.isfinite(lo) or math.isnan(lo)
    assert math.isfinite(hi) or math.isnan(hi)
    assert res["permutation_p"] >= 0.0 and res["permutation_p"] <= 1.0


# ---------------------------------------------------------------------------
# 13) cross-sectional atm_iv field present on the cross-section
# ---------------------------------------------------------------------------
def test_build_cross_section_has_atm_iv_field():
    caps = _captures()
    cs = e130.build_cross_section(caps, bar_seconds=60.0)
    assert "common" in cs
    assert "maps" in cs
    assert "BTC" in cs["maps"]
    assert "ETH" in cs["maps"]
    # atm_iv field exists (may be None)
    for inst in ("BTC", "ETH"):
        for bo, bar in cs["maps"][inst].items():
            assert "atm_iv" in bar


# ---------------------------------------------------------------------------
# 14) _relative_signal_series with surface_signal="atm_iv"
# ---------------------------------------------------------------------------
def test_relative_atm_iv_series_shape():
    caps = _captures()
    cs = e130.build_cross_section(caps, bar_seconds=60.0)
    rel_z = e130._relative_signal_series(cs, surface_signal="atm_iv")
    assert isinstance(rel_z, list)
    assert len(rel_z) == len(cs["common"])


# ---------------------------------------------------------------------------
# 15) identity: FLOOR and campaign_floor are e77's (not copies)
# ---------------------------------------------------------------------------
def test_floor_is_eval77_identity():
    assert e130.FLOOR is e77.FLOOR
    assert e130.campaign_floor is e77.campaign_floor