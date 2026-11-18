#!/usr/bin/env python3
"""EVAL-107: does the cross-sectional near-to-far ATM implied-vol **term ratio
basis** (ETH minus BTC) predict the subsequent **relative *vol-of-vol* spread**
(BTC minus ETH forward vol-of-vol)? A distinct, on-charter, runnable-**now**
predictiveness falsification on the real on-disk three-way captures.

Why this rung exists (the mandatory next build after EVAL-106)
-----------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now line
EVAL-70..106 is sealed:

* EVAL-105 sealed ``term_ratio basis`` -> relative **tail-asymmetry** spread (cross-sectional, GO/NO-GO).
* EVAL-90 sealed ``atm_iv basis`` -> relative **vol-of-vol** spread (cross-sectional, NO-GO).
* EVAL-106 sealed ``term_slope basis`` -> relative **tail-asymmetry** spread (cross-sectional, GO/NO-GO).
* EVAL-84 sealed ``term_slope`` -> own forward **vol-of-vol** (single-asset, GO/NO-GO).
* EVAL-97 sealed ``skew`` -> own forward **vol-of-vol** (single-asset, GO).

None of them covers the **cross-sectional term-ratio basis -> forward relative
*vol-of-vol* spread** cell: does the causal ETH-minus-BTC near-to-far ATM IV
term ratio basis predict the subsequent BTC-minus-ETH forward vol-of-vol spread?
This is distinct from:

* EVAL-105 (term-ratio basis -> relative *tail-asymmetry* spread),
* EVAL-90 (atm_iv basis -> relative *vol-of-vol* spread),
* EVAL-84 (single-asset term_slope -> own vol-of-vol),
* EVAL-94 (term-ratio basis -> relative *RV* spread),
* EVAL-97 (single-asset skew -> own vol-of-vol),
* EVAL-102 (single-asset term_ratio -> forward signed return),

and every traded-form / monetization cell. It makes a **predictiveness claim
only** — no traded-form or monetization claim.

EVAL-107 asks the genuinely distinct, on-charter, runnable-**now** question:

    When ETH's near-to-far ATM IV term ratio is rich relative to BTC's, does BTC
    subsequently carry the richer forward vol-of-vol relative to ETH —
    i.e. is the causal cross-sectional ``term_ratio`` basis informative about
    the subsequent relative vol-of-vol spread?

It reuses the sealed EVAL-61/62/65/71/74 machinery, EVAL-77's cross-sectional
alignment helpers and ``_relative_signal_series``, and EVAL-84's vol-of-vol
definition (via EVAL-90's ``_forward_rel_vov_spread``) verbatim, and the
EVAL-65 inference verbatim. It runs on the already-acquired real on-disk
captures with **no new acquisition** and **no network**, so it is heavy work
that is runnable **today**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For the causal term-ratio basis signal
``rel_z_k = expanding_z( term_ratio_ETH(k) - term_ratio_BTC(k) )`` (EVAL-74
``_term_bars`` ``term_ratio = IV(near expiry) / IV(far expiry) - 1``, overlaid
onto EVAL-77's common aligned bar grid; ``rel`` forward-filled causally then
expanding-z-scored end-of-bar ``k`` via EVAL-77 ``_relative_signal_series``),
each bar grid ``{60s, 300s}`` and each forward horizon ``H`` bars, on the
**common aligned** bar grid:

    x_k = rel_z_k                                          (relative term-ratio basis)
    y_k = Vov_BTC(k) - Vov_ETH(k)                          (relative vol-of-vol spread)
          where Vov_i(k) = sqrt(mean((v_j - mean(v))^2))
          and v_j = r_j^2, r_j = log(close_j/close_{j-1})
          over the next H perp bars for underlying i (EVAL-84/90 verbatim)

Compute Spearman rank ``IC = rho(x_k, y_k)``. H1 is ``IC > 0`` (ETH term-ratio
richness -> BTC carries the richer forward vol-of-vol; relative term richness
predicts relative turbulence). A config **passes** only if ``IC > 0``, directional
permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH floors satisfied, at least one config** has
``IC > 0``, directional permutation ``p < 0.05``, block-bootstrap 95% CI lower
``> 0``, at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs, and pooled
BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)`` (the cross-sectional
term-ratio basis does not portably predict the relative vol-of-vol spread).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-107 consumes BOTH underlyings' trade-tape IV surfaces and both perp series,
so it composes the sealed **EVAL-74 term floor verbatim** (EVAL-71 surface floor
+ term adequacy: >= ``MIN_DISTINCT_EXPIRIES`` distinct near-ATM expiries with
``MIN_EXPIRY_TRADES`` trades each, and >= ``MIN_BARS_WITH_TERM`` bars carrying a
term signal; applied to BOTH BTC and ETH, reused verbatim, neither weakened)
with the EVAL-77 cross-sectional alignment floor (>=
``MIN_ALIGNED_COMMON_BARS`` bar-ends where both underlyings carry a causal
surface bar on the coarsest grid). Below the composed floor it seals
``EVAL_107_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/65/71/74 primitives, the EVAL-77 cross-sectional
# alignment helpers, and the EVAL-84/90 vol-of-vol definition verbatim
# (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
import scripts.eval84_term_structure_vol_of_vol_predictiveness as e84  # noqa: E402
import scripts.eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread as e90  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED"
PREREG_ID = "EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION"
BLOCKED_ID = "EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_BLOCKED"

# Pre-registered grid (term_ratio basis x bar grid x forward horizons -> 6 configs).
TERM_SIGNALS: Tuple[str, ...] = ("term_ratio",)
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)
TARGET = "forward_relative_vol_of_vol_spread"

# The cross-section is BTC-vs-ETH, matching the sealed EVAL-77 convention:
# rel = signal[ETH] - signal[BTC]; target = Vov[BTC] - Vov[ETH];
# H1: IC > 0 (ETH term-ratio richness -> BTC richer forward vol-of-vol).
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

# Cross-sectional alignment floor (coarsest grid binding), mirroring EVAL-94/105.
MIN_ALIGNED_COMMON_BARS = 200

# Composed heavy-work floor (EVAL-74 term floor for both underlyings AND the
# EVAL-77 cross-sectional alignment floor).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_distinct_expiries": int(MIN_DISTINCT_EXPIRIES),
    "min_expiry_trades": int(MIN_EXPIRY_TRADES),
    "min_bars_with_term": int(MIN_BARS_WITH_TERM),
    "min_aligned_common_bars": int(MIN_ALIGNED_COMMON_BARS),
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-107 consumes both underlyings' trade-tape IV surfaces and both perp "
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
    "scripts/eval84_term_structure_vol_of_vol_predictiveness.py",
    "scripts/eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread.py",
    "scripts/eval107_cross_sectional_term_ratio_basis_relative_vol_of_vol_spread.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile "
    "scripts/eval107_cross_sectional_term_ratio_basis_relative_vol_of_vol_spread.py "
    "tests/test_eval107_cross_sectional_term_ratio_basis_relative_vol_of_vol_spread.py",
    "python3 -m pytest -q "
    "tests/test_eval107_cross_sectional_term_ratio_basis_relative_vol_of_vol_spread.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval107_cross_sectional_term_ratio_basis_relative_vol_of_vol_spread.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval107_cross_sectional_term_ratio_basis_relative_vol_of_vol_spread.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL107-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
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
# Cross-sectional term-ratio overlay + forward relative vol-of-vol spread target
# ---------------------------------------------------------------------------
def build_cross_section_with_term(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """EVAL-77 cross-section maps with EVAL-74 ``term_ratio`` overlaid by bar.

    Builds the sealed EVAL-77 cross-section (``build_cross_section``) so ``common``,
    ``maps`` and the per-bar ``close`` series are byte-identical to EVAL-77, then
    overlays EVAL-74's causal ``term_ratio`` (recomputed on the same ``bar_seconds``
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
            bar["term_ratio"] = tb.get("term_ratio") if tb is not None else None
    return cs


def _relative_term_ratio_series(
    cs: Dict[str, Any], *, term_signal: str = "term_ratio"
) -> List[float]:
    """Causal expanding-z-scored relative term-ratio basis ``signal[ETH] -
    signal[BTC]`` on the common aligned bar grid.

    Delegates verbatim to EVAL-77 ``_relative_signal_series`` (forward-fill then
    expanding-zscore via the sealed ``e61.expanding_zscore``), reading the
    overlaid ``term_ratio`` field.
    """
    return e77._relative_signal_series(cs, surface_signal=term_signal)


# ---------------------------------------------------------------------------
# Per-(signal, grid, horizon) cross-sectional term-ratio -> relative-vol-of-vol predictiveness
# ---------------------------------------------------------------------------
def evaluate_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    term_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Cross-sectional term-ratio -> relative-vol-of-vol predictiveness for one config.

    ``rel_z_k`` = expanding-z-scored ``term_ratio[ETH] - term_ratio[BTC]`` on the
    common aligned bar grid (EVAL-74 ``_term_bars`` overlaid onto EVAL-77
    ``build_cross_section``; EVAL-77 ``_relative_signal_series`` verbatim);
    ``y_k`` = forward BTC-minus-ETH vol-of-vol spread over bars k+1..k+H (strictly
    after k, EVAL-84/90 ``_forward_rel_vov_spread`` verbatim).
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

    rel_z = _relative_term_ratio_series(cs, term_signal=term_signal)
    y = e90._forward_rel_vov_spread(cs, horizon_bars)

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
        "eval": "EVAL-107",
        "title": "Cross-sectional options implied-vol TERM-RATIO basis (BTC-vs-ETH "
                 "relative near-to-far ATM IV term ratio) -> subsequent relative "
                 "*vol-of-vol* spread (BTC-minus-ETH forward std(squared log returns)): "
                 "wrapper-free Spearman rank information coefficient "
                 "(predictiveness) falsification on the real on-disk three-way captures",
        "extends": "EVAL-74 (same causal term_ratio reconstruction "
                   "``term_ratio = IV(near) / IV(far) - 1`` from the real Deribit "
                   "option trade tape, reused verbatim) and EVAL-77 (same cross-sectional "
                   "BTC-vs-ETH alignment and ``_relative_signal_series``, reused "
                   "verbatim) and EVAL-84/90 (same forward vol-of-vol definition, "
                   "reused verbatim) but a DISTINCT cell: the *cross-sectional "
                   "term-ratio basis* (not the single-underlying term_ratio of "
                   "EVAL-102, not the cross-sectional atm_iv basis of EVAL-90, "
                   "not the cross-sectional tail-asymmetry basis of EVAL-105) "
                   "with the forward relative *vol-of-vol* spread (not the "
                   "relative tail-asymmetry spread of EVAL-105, not the relative RV "
                   "spread of EVAL-94); no new acquisition",
        "supersedes": "nothing — this is the cross-sectional term-ratio partner to "
                       "EVAL-90 (atm_iv basis -> relative vol-of-vol) and "
                       "EVAL-105 (term-ratio basis -> relative tail-asymmetry); "
                       "both use the same sealed signal/target reconstructions. "
                       "It makes a predictiveness claim only, no traded-form / monetization claim",
        "capture_dir": str(capture_dir),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_z_k = expanding_z( term_ratio[ETH](k) - "
                               "term_ratio[BTC](k) )",
            "target": "y_k = Vov_BTC(k) - Vov_ETH(k) with "
                      "Vov_i(k) = sqrt(mean((v_j - mean(v))^2)), "
                      "v_j = r_j^2, r_j = log(close_j/close_{j-1}) over "
                      "next H perp bars (forward relative vol-of-vol spread)",
        },
        "term_signals": list(TERM_SIGNALS),
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "min_expiry_trades": int(MIN_EXPIRY_TRADES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar implied-vol term ratio from the real Deribit "
                  "option trade tape (EVAL-74 ``_term_bars``): near-ATM trades "
                  "grouped by expiry; term_ratio = IV(near expiry) / IV(far expiry) - "
                  "1; the term_ratio field is overlaid by bar_open_ms onto EVAL-77's "
                  "common aligned cross-section; the relative series (ETH - BTC) is "
                  "forward-filled then expanding-zscored end-of-bar k (reused "
                  "e77._relative_signal_series / e61.expanding_zscore).",
        "target_detail": "forward relative vol-of-vol = per underlying vol-of-vol "
                         "sqrt(mean((v_j - mean(v))^2)) with v_j = r_j^2 (squared log "
                         "returns) over the next H perp bars (strictly after the "
                         "decision at bar k, EVAL-84/90 verbatim), then "
                         "BTC minus ETH on the common aligned bar grid",
        "statistic": "Spearman rank correlation IC = rho(rel_z_k, y_k) over the common "
                     "aligned bar-ends (H1: IC > 0, ETH term-ratio-richness predicts "
                     "BTC subsequently carries the richer forward vol-of-vol — "
                     "relative turbulence)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the relative vol-of-vol spread",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": (
            "GO only if, on BOTH BTC and ETH floors satisfied, at least one config "
            "(term_ratio basis x bar grid x horizon) has Spearman IC > 0, "
            "directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, "
            "at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR "
            "rejects that config; else NO-GO CONFIRMED (PASS)."
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


def run_eval107(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL107-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
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
        "EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD"
        if floor_ok
        else "EVAL_107_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal cross-sectional options term-ratio basis (ETH - BTC near-to-far "
            "ATM IV term ratio) and the subsequent BTC-minus-ETH forward relative "
            "*vol-of-vol* spread on the real on-disk captures"
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
            "The causal cross-sectional options implied-vol term-ratio basis "
            "(BTC-vs-ETH relative near-to-far ATM IV term ratio, reconstructed from "
            "the real Deribit option trade tapes) has a positive monotone (Spearman "
            "rank) relationship with the subsequent relative *vol-of-vol* spread "
            "(BTC-minus-ETH forward std of squared log returns): relative term-ratio "
            "richness predicts relative turbulence. Tested on the already-acquired "
            "real on-disk captures at the composed EVAL-74 term + EVAL-77 alignment "
            "floor."
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
        f"# {PREREG_ID} — cross-sectional term-ratio basis -> relative *vol-of-vol* "
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
        f"# {r['report_id']} — cross-sectional term-ratio basis -> relative "
        f"vol-of-vol spread predictiveness (wrapper-free rank IC) falsification",
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
        "task": r.get("task", "EVAL107-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VOL-OF-VOL-SPREAD"),
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
        f"# {BLOCKED_ID} — cross-sectional term-ratio basis -> relative "
        f"vol-of-vol spread predictiveness: BELOW FLOOR",
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
        description="EVAL-107: cross-sectional options term-ratio basis -> relative "
                    "vol-of-vol spread (BTC-minus-ETH forward std(squared log returns)) "
                    "predictiveness (Spearman rank IC) on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label",
        default="EVAL107-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval107(
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