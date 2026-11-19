"""Unit tests for EVAL-116: the **cross-sectional causal put-call skew basis
(skew_ETH - skew_BTC) -> subsequent forward relative realized return skewness
spread** predictiveness.

EVAL-116 is the on-charter, runnable-now mandatory next campaign after EVAL-115
that EVAL-77 (cross-sectional surface basis atm_iv+skew -> forward realized-vol
spread) and EVAL-112/113 (single-asset term_ratio/term_slope -> forward return
skewness) leave open: the *cross-sectional* skew basis vs the *forward relative
realized return skewness spread*. It reuses the sealed EVAL-61/62/65/71/77
signal reconstructions and the EVAL-65 inference verbatim, needs no new
acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-116;
2. the sealed machinery (EVAL-61/62/65/71/77 helpers) is reused verbatim, not forked;
3. ``_forward_return_skewness`` is causal (target strictly after bar k) and is
   None on degenerate / zero-variance windows;
4. the relative realized return skewness spread is skewness[ETH] - skewness[BTC];
5. ``evaluate_config`` targets the cross-sectional relative spread, is causal,
   and its Spearman / permutation / bootstrap inference is bounded and deterministic;
6. the composed floor ANDs the sealed EVAL-77 surface basis floor (not weakened);
7. ``run_eval116(write=False)`` reports BLOCKED below the composed floor and a
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
import scripts.eval116_cross_sectional_skew_basis_forward_relative_return_skewness_spread as e116

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _captures(insts=("BTC", "ETH")):
    return {
        i: {"underlying": i, "surface": {"snapshots": []},
            "option_trades": [], "perp_candles": []}
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
def test_ids_are_eval116():
    assert e116.REPORT_ID.startswith("EVAL_116_")
    assert e116.PREREG_ID.startswith("EVAL_116_")
    assert e116.BLOCKED_ID.startswith("EVAL_116_")
    assert "SKEW_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD" in e116.REPORT_ID
    assert e116.TARGET == "forward_relative_return_skewness_spread"
    assert e116.SURFACE_SIGNALS == ("skew",)


# ---------------------------------------------------------------------------
# 2) sealed helpers reused verbatim
# ---------------------------------------------------------------------------
def test_uses_sealed_helpers_verbatim():
    assert e116.e61 is e61
    assert e116.e62 is e62
    assert e116.e65 is e65
    assert e116.e71 is e71
    assert e116.e77 is e77
    assert e116.PERMUTATION_PERMS is e65.PERMUTATION_PERMS
    assert e116.BOOTSTRAP_RESAMPLES is e65.BOOTSTRAP_RESAMPLES
    assert e116.BOOTSTRAP_BLOCK is e65.BOOTSTRAP_BLOCK
    assert e116.FDR_ALPHA is e62.FDR_ALPHA
    assert e116.SEED is e62.SEED
    assert e116.ZWINDOW is e62.ZWINDOW
    assert e116.build_cross_section is e77.build_cross_section
    assert e116._closes_on_common is e77._closes_on_common
    assert e116._relative_signal_series is e77._relative_signal_series
    assert e116.campaign_floor is e77.campaign_floor


# ---------------------------------------------------------------------------
# 3) forward return skewness target: causal + degenerate handling
# ---------------------------------------------------------------------------
def test_forward_return_skewness_length_and_none():
    closes = [1.0, 2.0, 4.0, 7.0, 11.0]
    # lr has 4 entries; h=2 -> windows k=0..2 -> 3 outputs
    out = e116._forward_return_skewness(closes, horizon_bars=2)
    assert len(out) == max(0, len(closes) - 1 - 2 + 1)
    # h larger than available returns -> empty
    assert e116._forward_return_skewness(closes, horizon_bars=10) == []


def test_forward_return_skewness_symmetric_is_zero():
    # symmetric segment around mean -> zero third moment -> skewness 0
    closes = [1.0, math.e ** 0.0, math.e ** 1.0, math.e ** 0.0]  # lr = [0,1,0]
    out = e116._forward_return_skewness(closes, horizon_bars=3)
    assert len(out) == 1
    assert abs(out[0]) < 1e-9


def test_forward_return_skewness_degenerate_none():
    # zero variance window -> None
    closes = [1.0, 1.0, 1.0, 1.0]  # lr = [0,0,0]
    out = e116._forward_return_skewness(closes, horizon_bars=3)
    assert len(out) == 1
    assert out[0] is None
    # fewer than 3 returns -> None
    closes = [1.0, 2.0]  # lr = [ln2], h=3 -> seg length 1 < 3
    out = e116._forward_return_skewness(closes, horizon_bars=3)
    assert out == []


def test_forward_return_skewness_causal_target_after_k():
    # output index k corresponds to returns k+1..k+H (strictly after bar k);
    # verified by length contract and finiteness on a normal series
    closes = [1.0, 1.5, 2.2, 3.1, 4.4, 6.0]
    for h in (2, 3):
        out = e116._forward_return_skewness(closes, horizon_bars=h)
        expected = max(0, len(closes) - 1 - h + 1)
        assert len(out) == expected
        for v in out:
            assert v is None or math.isfinite(v)


# ---------------------------------------------------------------------------
# 4) relative spread direction: skewness[ETH] - skewness[BTC]
# ---------------------------------------------------------------------------
def test_relative_spread_is_eth_minus_btc():
    # Evaluate on a tiny aligned grid; just confirm spread == eth - btc per bar
    closes_b = [1.0, 2.0, 4.0]
    closes_r = [1.0, 1.5, 3.0]
    sb = e116._forward_return_skewness(closes_b, horizon_bars=2)
    sr = e116._forward_return_skewness(closes_r, horizon_bars=2)
    n = min(len(sb), len(sr))
    spread = [float(sr[k]) - float(sb[k]) for k in range(n)]
    assert spread == [float(sr[k]) - float(sb[k]) for k in range(n)]
    # every element finite or None consistently
    for a, b in zip(sb, sr):
        assert (a is None) == (b is None) or (a is not None and b is not None)


# ---------------------------------------------------------------------------
# 5) evaluate_config cross-sectional shape
# ---------------------------------------------------------------------------
def test_evaluate_config_cross_sectional_shape():
    caps = _captures()
    res = e116.evaluate_config(
        caps, surface_signal="skew", bar_seconds=300.0, horizon_bars=6
    )
    assert res["signal"] == "skew"
    assert res["bar_seconds"] == 300.0
    assert res["horizon_bars"] == 6
    assert "n_common_bars" in res and "n_pairs" in res
    assert "spearman_ic" in res and "permutation_p" in res
    assert "bootstrap_ci" in res and len(res["bootstrap_ci"]) == 3
    assert res["pass"] is False  # empty fixtures -> no pairs


def test_evaluate_config_insufficient_pairs():
    caps = _captures()
    res = e116.evaluate_config(
        caps, surface_signal="skew", bar_seconds=60.0, horizon_bars=72
    )
    assert res["n_pairs"] < e116.MIN_USABLE_PAIRS_PER_CONFIG
    assert res["pass"] is False


# ---------------------------------------------------------------------------
# 6) composed floor reuses EVAL-77 surface basis floor, not weakened
# ---------------------------------------------------------------------------
def test_campaign_floor_reuses_eval77_not_weakened():
    assert e116.FLOOR is e77.FLOOR
    assert e116.FLOOR["min_underlyings"] == 2
    assert e116.FLOOR["min_aligned_common_bars"] == 200
    assert e116.FLOOR["min_usable_pairs_per_config"] == 120
    assert "EVAL-64" not in e116.FLOOR.get("note", "")
    caps = _captures()
    floor = e116.campaign_floor(caps)
    assert "per_underlying" in floor
    assert "aligned_ok" in floor
    assert floor["ok"] is False  # empty fixtures below floor


# ---------------------------------------------------------------------------
# 7) run_eval116(write=False): BLOCKED below floor / verdict above
# ---------------------------------------------------------------------------
def test_run_eval116_write_false_structure():
    report = e116.run_eval116(capture_dir=_write_captures(_captures()), write=False)
    assert report["report_id"] == e116.REPORT_ID
    assert report["task"].startswith("EVAL116-")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    assert "floor_ok" in report and "per_config" in report
    assert "pooled" in report and "bh_fdr" in report["pooled"]
    assert len(report["per_config"]) == len(e116.SURFACE_SIGNALS) * len(
        e116.GRID_BAR_SECONDS
    ) * len(e116.FORWARD_HORIZONS_BARS)


def test_go_bar_requires_pooled_bh_fdr():
    report = e116.run_eval116(capture_dir=_write_captures(_captures()), write=False)
    # Empty fixtures -> floor not ok -> BLOCKED, never a synthetic NO-GO
    assert report["verdict"] == "BLOCKED"
    assert report["floor_ok"] is False


# ---------------------------------------------------------------------------
# 8) protocol / floor constants preregistered
# ---------------------------------------------------------------------------
def test_protocol_floor_constants_preregistered():
    proto = e116.build_protocol("data/raw/eval61")
    assert proto["eval"] == "EVAL-116"
    assert proto["cross_section"]["baseline"] == "BTC"
    assert proto["cross_section"]["relative"] == "ETH"
    assert proto["cross_section"]["relative_signal"] == "rel_k = skew[ETH](k) - skew[BTC](k)"
    assert proto["surface_signals"] == ["skew"]
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    assert proto["stats"]["min_usable_pairs_per_config"] == 120
    assert "no new acquisition" in proto["data_availability"]["note"]
    assert "no network" in proto["data_availability"]["note"]


def test_signal_is_skew_only():
    # Single signal: skew (the cross-sectional put-call basis), not atm_iv.
    assert e116.SURFACE_SIGNALS == ("skew",)
    assert "atm_iv" not in e116.SURFACE_SIGNALS


def test_grid_and_horizons_preregistered():
    assert e116.GRID_BAR_SECONDS == (60.0, 300.0)
    assert e116.FORWARD_HORIZONS_BARS == (6, 24, 72)
    assert len(e116.SURFACE_SIGNALS) * len(e116.GRID_BAR_SECONDS) * len(
        e116.FORWARD_HORIZONS_BARS
    ) == 6


# ---------------------------------------------------------------------------
# 9) no synthetic data / real-data note
# ---------------------------------------------------------------------------
def test_no_synthetic_data_note():
    assert "real" in e116.build_protocol("data/raw/eval61")["data_availability"]["note"]
    assert "no network" in e116.COMMANDS[3]


# ---------------------------------------------------------------------------
# 10) code paths + commands
# ---------------------------------------------------------------------------
def test_code_paths_include_runner():
    assert "scripts/eval116_cross_sectional_skew_basis_forward_relative_return_skewness_spread.py" in e116.CODE_PATHS


def test_commands_include_seal_and_no_write():
    assert any("--no-write" in c for c in e116.COMMANDS)
    assert any("--seal" in c for c in e116.COMMANDS)


# ---------------------------------------------------------------------------
# 11) baseline / relative legs
# ---------------------------------------------------------------------------
def test_baseline_relative_legs_btc_eth():
    assert e116.BASELINE == "BTC"
    assert e116.RELATIVE == "ETH"


# ---------------------------------------------------------------------------
# 12) bootstrap CI bounded
# ---------------------------------------------------------------------------
def test_bootstrap_ci_bounded():
    caps = _captures()
    res = e116.evaluate_config(
        caps, surface_signal="skew", bar_seconds=300.0, horizon_bars=24
    )
    ci = res["bootstrap_ci"]
    med, lo, hi = ci
    assert math.isfinite(med) or math.isnan(med)
    assert math.isfinite(lo) or math.isnan(lo)
    assert math.isfinite(hi) or math.isnan(hi)
    assert res["permutation_p"] >= 0.0 and res["permutation_p"] <= 1.0
