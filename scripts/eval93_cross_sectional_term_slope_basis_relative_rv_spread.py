#!/usr/bin/env python3
"""EVAL-93: does the **cross-sectional term-structure SLOPE basis** (BTC-vs-ETH
relative near-minus-far ATM IV term slope) predict the subsequent **relative
*realized-vol* (RV) spread** — i.e. when ETH's near-minus-far ATM IV term slope is
steep relative to BTC's, does BTC subsequently realize a richer forward RV
relative to ETH? A distinct, runnable-**now** cross-sectional *term-structure*
predictiveness falsification on the real on-disk three-way captures.

Why this rung exists (anti-avoidance mandatory next build)
----------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + **options order-flow** + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now surface line
EVAL-70..92 is sealed:

* EVAL-71/73 sealed ``GO CONFIRMED`` — the *single-underlying* near-ATM IV surface
  (level + put-call skew) predicts that underlying's forward *RV level* (stable
  OOS).
* EVAL-74 sealed ``NO-GO CONFIRMED (PASS)`` — the *single-underlying* term-structure
  slope (``term_slope``) predicts ETH forward RV but is null on BTC.
* EVAL-77 sealed ``GO CONFIRMED`` — the *cross-sectional* BTC-vs-ETH surface basis
  (``atm_iv``/``skew``) predicts the subsequent BTC-minus-ETH *RV spread*.
* EVAL-84 sealed ``NO-GO CONFIRMED (PASS)`` — the *single-underlying* term slope
  predicts own vol-of-vol but null on BTC.
* EVAL-88 sealed ``GO CONFIRMED`` — the *cross-sectional* basis predicts the
  subsequent relative *direction* (BTC-minus-ETH signed return spread).
* EVAL-89/92 sealed ``NO-GO CONFIRMED (PASS)`` — the *cross-sectional* skew / atm_iv
  bases predict relative *VRP* spread.
* EVAL-90/91 sealed ``GO CONFIRMED`` — the *cross-sectional* atm_iv / skew bases
  predict the subsequent relative *vol-of-vol* spread.

None of them covers the **cross-sectional term-structure SLOPE basis -> forward
relative *realized-vol* spread** cell: does the *relative near-minus-far term
slope* (BTC vs ETH) predict the subsequent BTC-minus-ETH *realized-vol spread*?
This is distinct from:

* EVAL-74 (own-asset term slope -> own RV level),
* EVAL-77 (cross-sectional *level/skew* basis -> relative RV spread),
* EVAL-84 (own-asset term slope -> own vol-of-vol),
* EVAL-88 (cross-sectional basis -> relative *direction*),
* EVAL-89/92 (cross-sectional basis -> relative *VRP* spread),
* EVAL-90/91 (cross-sectional basis -> relative *vol-of-vol* spread),

and every traded-form / monetization cell. It makes a **predictiveness claim only**
— no traded-form or monetization claim.

EVAL-93 asks the genuinely distinct, on-charter, runnable-**now** question:

    When ETH's near-minus-far near-ATM IV term slope is steep relative to BTC's,
    does BTC subsequently realize a richer forward RV relative to ETH — i.e. is the
    causal BTC-vs-ETH term-structure **slope basis** informative about the
    subsequent BTC-minus-ETH relative *realized-vol* spread?

It reuses the sealed EVAL-61/62/65/71 machinery and the EVAL-65 inference
verbatim, reuses EVAL-77's cross-sectional alignment / forward-RV helpers, and
overlays EVAL-74's causal ``term_slope`` onto EVAL-77's common bar grid by
``bar_open_ms`` (no fork of sealed code, no src edits). It runs on the
already-acquired real on-disk captures with **no new acquisition** and **no
network**, so it is heavy work that is runnable **today**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For the causal term-slope basis signal
``rel_z_k = expanding_z( term_slope_ETH(k) - term_slope_BTC(k) )`` (EVAL-74
``_term_bars`` ``term_slope = IV(near expiry) - IV(far expiry)`` in vol points,
overlaid onto EVAL-77's common aligned bar grid; ``rel`` forward-filled causally
then expanding-z-scored end-of-bar ``k`` via EVAL-77
``_relative_signal_series``), each bar grid ``{60s, 300s}`` and each forward
horizon ``H`` bars, on the **common aligned** bar grid:

    x_k = rel_z_k                                    (relative term-slope richness)
    y_k = RV_BTC(k) - RV_ETH(k)                      (relative realized-vol spread)
          where RV_i(k) = sqrt(mean(log-return^2)) over the next H perp bars
          strictly after the decision at bar k (EVAL-77 ``_rv_series``)

Compute Spearman rank ``IC = rho(x_k, y_k)``. H1 is ``IC > 0`` (ETH term-slope-rich
-> BTC subsequently realizes a richer forward RV; relative term richness
mean-reverts). A config **passes** only if ``IC > 0``, directional permutation
``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if at least one config** passes AND pooled BH-FDR rejects that config;
else ``NO-GO CONFIRMED (PASS)`` (the cross-sectional term-slope basis does not
portably predict the relative RV spread).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-93 consumes BOTH underlyings' trade-tape IV surfaces and both perp series, so
it composes the sealed EVAL-74 term-structure floor (EVAL-71 surface floor + term
adequacy: >= ``MIN_DISTINCT_EXPIRIES`` distinct near-ATM expiries with
``MIN_EXPIRY_TRADES`` trades each, and >= ``MIN_BARS_WITH_TERM`` bars carrying a
term signal; applied to BOTH BTC and ETH, reused verbatim, neither weakened) with
the EVAL-77 cross-sectional alignment floor (>= ``MIN_ALIGNED_COMMON_BARS``
bar-ends where both underlyings carry a causal surface bar on the coarsest grid).
Below the composed floor it seals ``EVAL_93_..._BLOCKED_<UTC>`` (never a NO-GO).
The EVAL-64 feasible floor that governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD_PREREGISTRATION_<UTC>``
then ``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the sealed EVAL-61/62/65/71 primitives, the EVAL-77 cross-sectional
# alignment / forward-RV helpers, and the EVAL-74 causal term-structure helpers
# verbatim (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD_COMBINED"
PREREG_ID = "EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD_PREREGISTRATION"
BLOCKED_ID = "EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD_BLOCKED"

# Pre-registered grid (term_slope basis x bar grid x forward horizons). The signal
# is EVAL-74's ``term_slope`` (near-minus-far near-ATM IV, vol points); the target
# is the forward relative *realized-vol* spread (BTC minus ETH) — the EVAL-77
# target, but on the *term-slope basis* rather than the EVAL-77 level/skew basis.
TERM_SIGNALS: Tuple[str, ...] = ("term_slope",)
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)
TARGET = "forward_relative_rv_spread"

# The cross-section is BTC-vs-ETH, matching the sealed EVAL-77 convention:
# rel = signal[ETH] - signal[BTC]; target = RV[BTC] - RV[ETH]; H1: IC > 0
# (ETH term-slope richness predicts BTC subsequently carries a richer forward RV).
BASELINE = e77.BASELINE  # "BTC"
RELATIVE = e77.RELATIVE  # "ETH"

# Term-structure / near-ATM constants reused verbatim from EVAL-74 (which reuses
# the sealed EVAL-71 constants): trailing aggregation window, near-ATM band, and
# per-expiry adequacy.
SIGNAL_WINDOW_SECONDS = e74.SIGNAL_WINDOW_SECONDS
ATM_BAND = e74.ATM_BAND
MIN_EXPIRY_TRADES = e74.MIN_EXPIRY_TRADES
MIN_DISTINCT_EXPIRIES = e74.MIN_DISTINCT_EXPIRIES
MIN_BARS_WITH_TERM = e74.MIN_BARS_WITH_TERM

# Statistics reused verbatim from EVAL-65 / EVAL-62 (identical permutation /
# bootstrap / seed).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 120

# Composed heavy-work floor (EVAL-74 term floor for both underlyings AND the
# EVAL-77 cross-sectional alignment floor).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_distinct_expiries": int(MIN_DISTINCT_EXPIRIES),
    "min_expiry_trades": int(MIN_EXPIRY_TRADES),
    "min_bars_with_term": int(MIN_BARS_WITH_TERM),
    "min_aligned_common_bars": 200,
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-93 consumes both underlyings' trade-tape IV surfaces and both perp "
        "series. It composes the sealed EVAL-74 term-structure floor (EVAL-71 surface "
        "floor + term adequacy: >= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries "
        "with >= MIN_EXPIRY_TRADES trades each, and >= MIN_BARS_WITH_TERM bars "
        "carrying a term signal; applied to BOTH BTC and ETH, reused verbatim, "
        "neither weakened) with the sealed EVAL-77 cross-sectional alignment floor "
        "(>= min_aligned_common_bars bar-ends where both underlyings carry a causal "
        "surface bar on the coarsest grid). This is NOT the EVAL-64 options-surface "
        "snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
    "scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "scripts/eval93_cross_sectional_term_slope_basis_relative_rv_spread.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile "
    "scripts/eval93_cross_sectional_term_slope_basis_relative_rv_spread.py "
    "tests/test_eval93_cross_sectional_term_slope_basis_relative_rv_spread.py",
    "python3 -m pytest -q "
    "tests/test_eval93_cross_sectional_term_slope_basis_relative_rv_spread.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval93_cross_sectional_term_slope_basis_relative_rv_spread.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval93_cross_sectional_term_slope_basis_relative_rv_spread.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL93-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-RV-SPREAD",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


def _select_one_capture_per_underlying(
    captures: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Richest (most real option trades) real capture per underlying; deterministic.

    Reuses the sealed EVAL-77 selector verbatim.
    """
    return e77._select_one_capture_per_underlying(captures)


# ---------------------------------------------------------------------------
# Cross-sectional term-slope overlay + forward relative realized-vol spread target
# ---------------------------------------------------------------------------
def build_cross_section_with_term(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """EVAL-77 cross-section maps with EVAL-74 ``term_slope`` overlaid by bar.

    Builds the sealed EVAL-77 cross-section (``build_cross_section``) so ``common``,
    ``maps`` and the per-bar ``close`` series are byte-identical to EVAL-77, then
    overlays EVAL-74's causal ``term_slope`` (recomputed on the same ``bar_seconds``
    grid from the same real trade tape) onto each map bar by ``bar_open_ms``. The
    sealed code and artifacts are not mutated — the overlay is in-memory only.
    """
    cs = e77.build_cross_section(captures, bar_seconds=bar_seconds)
    for inst, cap in captures.items():
        m = cs["maps"].get(inst, {})
        if not m:
            continue
        term_bars = e74._term_bars(cap, bar_seconds=bar_seconds)
        term_by_bar = {int(b["bar_open_ms"]): b for b in term_bars}
        for bo, bar in m.items():
            tb = term_by_bar.get(int(bo))
            bar["term_slope"] = tb.get("term_slope") if tb is not None else None
    return cs


def _relative_term_slope_series(
    cs: Dict[str, Any], *, term_signal: str = "term_slope"
) -> List[float]:
    """Causal expanding-z-scored relative term-slope basis ``signal[ETH] -
    signal[BTC]`` on the common aligned bar grid.

    Delegates verbatim to EVAL-77 ``_relative_signal_series`` (forward-fill then
    expanding-zscore via the sealed ``e61.expanding_zscore``), reading the
    overlaid ``term_slope`` field.
    """
    return e77._relative_signal_series(cs, surface_signal=term_signal)


def _forward_rel_rv_spread(
    cs: Dict[str, Any], horizon_bars: int
) -> List[float]:
    """Forward BTC-minus-ETH relative realized-vol spread on the common aligned grid.

    ``y_k = RV_BTC(k) - RV_ETH(k)`` where ``RV_i(k) = sqrt(mean(log-return^2))``
    over the next ``H`` perp bars strictly after the decision at bar ``k``
    (EVAL-77 ``_closes_on_common`` + ``_rv_series`` verbatim). Length is
    ``len(common) - H`` per underlying; the spread is over ``min(len) `` pairs.
    """
    closes_b = e77._closes_on_common(cs, BASELINE)
    closes_r = e77._closes_on_common(cs, RELATIVE)
    rv_b = e77._rv_series(closes_b, horizon_bars)
    rv_r = e77._rv_series(closes_r, horizon_bars)
    n = min(len(rv_b), len(rv_r))
    return [float(rv_b[k]) - float(rv_r[k]) for k in range(n)]


# ---------------------------------------------------------------------------
# Per-(signal, grid, horizon) cross-sectional term-slope -> relative-RV predictiveness
# ---------------------------------------------------------------------------
def evaluate_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    term_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Cross-sectional term-slope -> relative-RV predictiveness for one config.

    ``rel_z_k`` = expanding-z-scored ``term_slope[ETH] - term_slope[BTC]`` on the
    common aligned bar grid (EVAL-74 ``_term_bars`` overlaid onto EVAL-77
    ``build_cross_section``; EVAL-77 ``_relative_signal_series`` verbatim);
    ``y_k`` = forward BTC-minus-ETH RV spread over bars k+1..k+H (strictly after k,
    EVAL-77 ``_rv_series``).
    """
    cs = build_cross_section_with_term(captures, bar_seconds=bar_seconds)
    n_common = len(cs["common"])
    if n_common < int(horizon_bars) + 5:
        return {
            "signal": term_signal,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "target": TARGET,
            "error": "insufficient common surface bars",
            "n_common_bars": n_common,
            "n_pairs": 0,
            "pass": False,
            "reason": "insufficient_common_bars",
        }

    rel_z = _relative_term_slope_series(cs, term_signal=term_signal)
    y = _forward_rel_rv_spread(cs, horizon_bars)

    xs: List[float] = []
    ys: List[float] = []
    for k in range(min(len(y), len(rel_z))):
        xs.append(float(rel_z[k]))
        ys.append(float(y[k]))

    if len(xs) < int(MIN_USABLE_PAIRS_PER_CONFIG):
        return {
            "signal": term_signal,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "target": TARGET,
            "error": "insufficient aligned pairs",
            "n_common_bars": n_common,
            "n_pairs": len(xs),
            "pass": False,
            "reason": "insufficient_pairs",
        }

    ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(
        xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED
    )
    passed = bool(
        ic > 0.0
        and perm_p < 0.05
        and ci_lo > 0.0
        and len(xs) >= int(MIN_USABLE_PAIRS_PER_CONFIG)
    )
    return {
        "signal": term_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "target": TARGET,
        "n_common_bars": n_common,
        "n_pairs": len(xs),
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "pass": passed,
        "reason": "ok" if passed else "gate_fail",
    }


# ---------------------------------------------------------------------------
# Composed heavy-work floor (EVAL-74 term floor for both underlyings AND EVAL-77
# cross-sectional alignment)
# ---------------------------------------------------------------------------
def _underlying_term_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    """The sealed EVAL-74 term-structure floor for one underlying (reused verbatim)."""
    return e74._underlying_term_floor(capture)


def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Composed floor: both underlyings pass EVAL-74 AND aligned common bars."""
    insts = sorted(captures)
    per_underlying = {i: _underlying_term_floor(captures[i]) for i in insts}
    both_present = BASELINE in captures and RELATIVE in captures
    underlyings_ok = bool(
        both_present
        and all(per_underlying[i]["ok"] for i in (BASELINE, RELATIVE))
    )

    aligned_by_grid: Dict[str, int] = {}
    if both_present:
        for bar_s in GRID_BAR_SECONDS:
            cs = e77.build_cross_section(
                {BASELINE: captures[BASELINE], RELATIVE: captures[RELATIVE]},
                bar_seconds=bar_s,
            )
            aligned_by_grid[str(bar_s)] = len(cs["common"])

    coarsest = max(GRID_BAR_SECONDS)
    aligned_binding = int(aligned_by_grid.get(str(coarsest), 0))
    aligned_ok = aligned_binding >= int(FLOOR["min_aligned_common_bars"])
    return {
        "underlyings": insts,
        "per_underlying": per_underlying,
        "underlyings_ok": underlyings_ok,
        "aligned_common_bars_by_grid": aligned_by_grid,
        "aligned_common_bars_binding": aligned_binding,
        "aligned_ok": aligned_ok,
        "checks": {
            "underlyings_ok": underlyings_ok,
            "aligned_ok": aligned_ok,
        },
        "ok": bool(underlyings_ok and aligned_ok),
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-93",
        "title": "Cross-sectional options implied-vol TERM-SLOPE basis (BTC-vs-ETH "
                 "relative near-minus-far ATM IV term slope) -> subsequent relative "
                 "*realized-vol* (RV) spread (BTC-minus-ETH forward RV): wrapper-free "
                 "Spearman rank information coefficient (predictiveness) falsification "
                 "on the real on-disk three-way captures",
        "extends": "EVAL-74 (same causal term-slope reconstruction "
                    "``term_slope = IV(near) - IV(far)`` from the real Deribit option "
                    "trade tape, reused verbatim) and EVAL-77 (same cross-sectional "
                    "BTC-vs-ETH alignment and forward-RV spread target, reused "
                    "verbatim) but a DISTINCT cell: the *cross-sectional term-slope "
                    "basis* (not the single-underlying term slope of EVAL-74, not the "
                    "cross-sectional level/skew basis of EVAL-77) with the forward "
                    "relative *realized-vol* spread (not the RV level of EVAL-74, not "
                    "the relative direction of EVAL-88, not the relative VRP spread of "
                    "EVAL-89/92, not the relative vol-of-vol spread of EVAL-90/91); no "
                    "new acquisition",
        "supersedes": "nothing — this is the cross-sectional term-slope partner to "
                       "EVAL-74 (own-asset term slope) and EVAL-77 (cross-sectional "
                       "level/skew basis); both used the same forward-RV target "
                       "machinery. It makes a predictiveness claim only, no traded-form "
                       "/ monetization claim",
        "capture_dir": str(capture_dir),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_z_k = expanding_z( term_slope[ETH](k) - "
                              "term_slope[BTC](k) )",
            "target": "y_k = RV_BTC(k) - RV_ETH(k) with "
                      "RV_i(k) = sqrt(mean(log-return^2)) over the next H perp bars "
                      "strictly after k (relative realized-vol spread)",
        },
        "term_signals": list(TERM_SIGNALS),
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "min_expiry_trades": int(MIN_EXPIRY_TRADES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar implied-vol term structure from the real Deribit "
                  "option trade tape (EVAL-74 ``_term_bars``): near-ATM trades grouped "
                  "by expiry; term_slope = IV(near expiry) - IV(far expiry) in vol "
                  "points; near = earliest and far = latest expiry each with >= "
                  "min_expiry_trades near-ATM trades in the trailing window. The "
                  "term_slope field is overlaid by bar_open_ms onto EVAL-77's common "
                  "aligned cross-section; the relative series (ETH - BTC) is forward-"
                  "filled then expanding-zscored end-of-bar k (reused "
                  "e77._relative_signal_series / e61.expanding_zscore).",
        "target_detail": "forward relative realized-vol spread: per underlying RV = "
                         "sqrt(mean(log-return^2)) over the next H perp bars (strictly "
                         "after the decision at bar k, EVAL-77 ``_rv_series`` "
                         "verbatim), then BTC minus ETH on the common aligned bar grid",
        "statistic": "Spearman rank correlation IC = rho(rel_z_k, y_k) over the common "
                     "aligned bar-ends (H1: IC > 0, ETH term-slope-richness predicts "
                     "BTC subsequently carries a richer forward RV — relative-value RV "
                     "mean reversion)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the relative-RV spread",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": (
            "GO only if at least one config (term_slope basis x bar grid x horizon) has "
            "Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI "
            "lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled "
            "BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures (option "
                    "trades with real iv/strike/expiry + perp candles for BTC and ETH); "
                    "no new acquisition, no network; composes the EVAL-74 term floor "
                    "for both underlyings with the EVAL-77 cross-sectional alignment "
                    "floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval93(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL93-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-RV-SPREAD",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    selected = _select_one_capture_per_underlying(
        e61._capture_inventory(str(capture_dir_abs))
    )
    captures = {str(c.get("underlying")): c for c in selected}

    floor = campaign_floor(captures)
    floor_ok = bool(len(captures) >= int(FLOOR["min_underlyings"]) and floor["ok"])

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for sig in TERM_SIGNALS:
        for bar_s in GRID_BAR_SECONDS:
            for horizon in FORWARD_HORIZONS_BARS:
                try:
                    res = evaluate_config(
                        captures, term_signal=sig, bar_seconds=bar_s,
                        horizon_bars=horizon,
                    )
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{sig}::bar{bar_s}::h{horizon}: {exc!r}")
                    continue
                per_config.append(res)

    p_values = {
        f"{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}":
            _finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    pass_configs: List[str] = []
    for r in per_config:
        key = f"{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}"
        if r.get("pass") and key in rejected:
            pass_configs.append(key)

    valid = [r for r in per_config if r.get("n_pairs", 0) > 0]
    best = (
        max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9))
        if valid else None
    )

    any_pass = bool(pass_configs)
    go = bool(floor_ok and any_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD" if floor_ok
        else "EVAL_93_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal cross-sectional options term-slope basis (ETH - BTC near-minus-far "
            "ATM IV term slope) and the subsequent BTC-minus-ETH forward relative "
            "*realized-vol* spread on the real on-disk captures"
            if floor_ok else "capture below the composed EVAL-74 term + EVAL-77 "
                              "alignment floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "summary": {
            "n_configs": len(per_config),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::bar{best['bar_seconds']}::h{best['horizon_bars']}"
                if best else "n/a"
            ),
        },
        "pooled": {
            "bh_fdr": bh,
            "any_config_pass": any_pass,
            "campaign_state": campaign_state,
        },
        "errors": errors,
    }

    if not write:
        return report

    prereg = _build_prereg(report)
    e62._seal(PREREG_ID, prereg, _build_prereg_md)

    if not floor_ok:
        e62._seal(BLOCKED_ID, _build_blocked_report(report), _build_blocked_md)
        return report

    e62._seal(REPORT_ID, report, _build_md)
    return report


# ---------------------------------------------------------------------------
# Seal artifact builders
# ---------------------------------------------------------------------------
def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "The causal cross-sectional options implied-vol TERM-SLOPE basis "
            "(BTC-vs-ETH relative near-minus-far near-ATM IV term slope, reconstructed "
            "from the real Deribit option trade tapes) has a positive monotone "
            "(Spearman rank) relationship with the subsequent relative realized "
            "volatility (BTC-minus-ETH forward RV spread): relative term-slope "
            "richness mean-reverts. Tested on the already-acquired real on-disk "
            "captures at the composed EVAL-74 term + EVAL-77 alignment floor."
        ),
        "extends": p["extends"],
        "data_availability": p["data_availability"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    fl = p["floor"]
    cs = p["cross_section"]
    lines = [
        f"# {PREREG_ID} — cross-sectional term-slope basis -> relative *realized-vol* "
        f"spread predictiveness (wrapper-free Spearman rank IC)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Cross-section: baseline `{cs['baseline']}`, relative `{cs['relative']}`",
        f"- Relative signal: {cs['relative_signal']}",
        f"- Target: {cs['target']}",
        f"- Term signals: {p['term_signals']}",
        f"- Signal window (s): {p['signal_window_seconds']}",
        f"- Near-ATM band: {p['atm_band']}",
        f"- Min trades per expiry bucket: {p['min_expiry_trades']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Signal: {p['signal']}",
        f"- Target detail: {p['target_detail']}",
        f"- Statistic: {p['statistic']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']} / "
        f"zwindow {p['stats']['zwindow']} / "
        f"min usable pairs {p['stats']['min_usable_pairs_per_config']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered composed floor (EVAL-74 term both underlyings + EVAL-77 alignment)",
        "",
        f"- {fl['note']}",
        f"- Min underlyings: {fl['min_underlyings']}",
        f"- Min distinct near-ATM expiries: {fl['min_distinct_expiries']}",
        f"- Min trades per expiry bucket: {fl['min_expiry_trades']}",
        f"- Min bars with a term signal: {fl['min_bars_with_term']}",
        f"- Min aligned common bars (coarsest grid): {fl['min_aligned_common_bars']}",
        f"- Min usable pairs per config: {fl['min_usable_pairs_per_config']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {r['report_id']} — cross-sectional term-slope basis -> relative "
        f"*realized-vol* spread predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Verdict detail: {r['verdict_detail']}",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        f"- Aligned common bars by grid: {fl.get('aligned_common_bars_by_grid')}",
        "",
        "## Per-underlying floor (EVAL-71 surface floor + term-structure adequacy)",
        "",
        "| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |",
        "|---|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        el = u.get("eval71_floor", {})
        ta = u.get("term_adequacy", {})
        lines.append(
            f"| {inst} | {u.get('eval71_floor_ok')} | {ta.get('n_distinct_expiries')} | "
            f"{ta.get('bars_with_term_max')} | {u.get('ok')} |"
        )
    lines += ["", "## Configs (best first by Spearman IC)", ""]
    lines += ["| signal | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |",
              "|---|---|---|---|---|---|---|---|"]
    rows = sorted(
        [c for c in r["per_config"] if c.get("n_pairs", 0) > 0],
        key=lambda c: _finite(c.get("spearman_ic"), -1e9),
        reverse=True,
    )
    for c in rows:
        ci = c.get("bootstrap_ci") or [0.0, 0.0, 0.0]
        lines.append(
            f"| {c['signal']} | {c['bar_seconds']:.0f} | {c['horizon_bars']} | "
            f"{c['n_pairs']} | {c['spearman_ic']:.4f} | {c['permutation_p']:.4f} | "
            f"[{ci[0]:.4f}, {ci[1]:.4f}, {ci[2]:.4f}] | {c['pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- Any config pass: {r['pooled']['any_config_pass']}",
              f"- Campaign state: {r['pooled']['campaign_state']}"]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r.get("generated_at", _utc_now_iso()),
        "task": r.get("task", "EVAL93-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-RV-SPREAD"),
        "verdict": "BLOCKED",
        "verdict_detail": "capture below the composed EVAL-74 term + EVAL-77 alignment "
                          "floor; no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "campaign_floor": r.get("campaign_floor", {}),
        "floor": r.get("floor", dict(FLOOR)),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    fl = r.get("campaign_floor", {}) or {}
    lines = [
        f"# {BLOCKED_ID} — cross-sectional term-slope basis -> relative "
        f"*realized-vol* spread predictiveness: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Underlyings: {', '.join(r.get('underlyings', []))}",
        f"- Underlyings floor met: {fl.get('underlyings_ok')}",
        f"- Aligned common bars by grid: {fl.get('aligned_common_bars_by_grid')}",
        f"- Aligned floor met: {fl.get('aligned_ok')}",
        "",
        "The capture does not meet the composed EVAL-74 term + EVAL-77 cross-sectional "
        "alignment floor, so no GO/NO-GO verdict is emitted. Do NOT weaken either "
        "floor, do NOT use synthetic data, and do NOT emit NO-GO on under-floor data.",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        lines.append(
            f"- {inst}: eval71_floor_ok={u.get('eval71_floor_ok')} "
            f"checks={json.dumps(u.get('checks'))}"
        )
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-93: cross-sectional options term-slope basis -> relative "
                    "*realized-vol* spread (BTC-minus-ETH forward RV) predictiveness "
                    "(Spearman rank IC) on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label",
        default="EVAL93-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-RV-SPREAD",
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval93(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(),
                "task": args.task_label,
                "capture_dir": args.capture_dir,
                "underlyings": [],
                "campaign_floor": {},
                "floor": dict(FLOOR),
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "summary": report.get("summary"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())