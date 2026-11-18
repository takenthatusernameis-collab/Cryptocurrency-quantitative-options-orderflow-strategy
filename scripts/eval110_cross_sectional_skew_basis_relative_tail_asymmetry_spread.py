#!/usr/bin/env python3
"""EVAL-110: does the causal cross-sectional options **put-call skew basis**
(BTC-vs-ETH relative near-ATM skew) predict the subsequent **relative return
tail-asymmetry spread** between the two underlyings? A distinct, on-charter,
runnable-**now** predictiveness cell on the real on-disk three-way captures.

Why this rung exists (the next runnable-now heavy work after EVAL-109)
----------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The physics-independent
runnable-now line EVAL-70..109 is sealed. EVAL-77 tested the cross-sectional
``atm_iv``/``skew`` basis against the *relative RV* spread; EVAL-89 tested the
``skew`` basis against the *relative VRP*; EVAL-91 tested the ``skew`` basis
against the *relative vol-of-vol* spread; EVAL-105/106 tested the cross-sectional
``term_ratio``/``term_slope`` basis against the *relative tail-asymmetry*
spread. The cross-sectional ``skew`` basis has **never** been paired with the
relative **tail-asymmetry** spread.

The genuinely distinct, on-charter, runnable-**now** cell tested here is: does
the causal cross-sectional near-ATM put-call skew basis at bar ``k`` carry
monotone information about the BTC-minus-ETH **forward return-tail-asymmetry**
spread over bars ``k+1..k+H``? It is **predictiveness only** — no traded-form or
monetization claim.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
-------------------------------------------------------------------------------
For each bar grid ``{60s, 300s}`` and each forward horizon ``H`` bars:

* the causal relative signal is ``rel_z_k = expanding_z( skew_ETH(k) -
  skew_BTC(k) )`` on the common aligned bar grid, where ``skew = mean(put iv) -
  mean(call iv)`` over near-ATM trades is built exactly as EVAL-77
  (``e77.build_cross_section`` + ``e77._relative_signal_series`` verbatim,
  forward-fill then expanding z-score end-of-bar ``k``); and
* the target is the forward **relative tail-asymmetry spread**
  ``y_k = tail_asym_BTC(k) - tail_asym_ETH(k)`` with per-asset
  ``tail_asym = (q95 - median) - (median - q05)`` over the next ``H`` perp log
  returns strictly after ``k`` (EVAL-85 ``_forward_return_tail_asym`` verbatim,
  EVAL-89/93/105/106 spread convention). A config needs at least
  ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

Compute Spearman rank ``IC = rho(rel_z_k, y_k)`` with the sealed EVAL-65
directional permutation and block bootstrap (H1: ``IC > 0`` — a relatively
skew-richer ETH basis precedes a relatively larger BTC-minus-ETH forward
tail-asymmetry spread). A config **passes** only if ``IC > 0``, directional
permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH floors satisfied and at least one config:**
``IC > 0``, directional permutation ``p < 0.05``, block-bootstrap 95% CI lower
``> 0``, and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-110 consumes the same surface data as EVAL-77, so it reuses the sealed
**EVAL-71 surface floor verbatim** for EACH underlying AND the sealed **EVAL-77
cross-sectional alignment floor** (>= ``min_aligned_common_bars``=200 aligned
common bar-ends on the coarsest grid), applied to BOTH BTC and ETH. Below the
floor it seals ``EVAL_110_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64
ladder floor is untouched.

This does **not** re-litigate any sealed result: EVAL-77 measured the
``atm_iv``/``skew`` basis -> *relative RV*; EVAL-89 measured the ``skew``
basis -> *relative VRP*; EVAL-91 measured the ``skew`` basis -> *relative
vol-of-vol*; EVAL-85 measured single-asset ``skew`` -> *own tail asymmetry*;
EVAL-105/106 measured the term basis -> *relative tail asymmetry*. EVAL-110
measures the cross-sectional ``skew`` **basis** -> **relative tail-asymmetry
spread**, reusing all sealed signal/target reconstructions and the EVAL-65
inference verbatim.

Seals ``EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/65/71/77/85 primitives verbatim (no forks, no src).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
import scripts.eval85_surface_skew_forward_return_tail as e85  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_COMBINED"
PREREG_ID = "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION"
BLOCKED_ID = "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_BLOCKED"

BASELINE = "BTC"
RELATIVE = "ETH"

# Pre-registered grid (skew basis x bar grid x forward horizons -> 6 configs).
SURFACE_SIGNALS: Tuple[str, ...] = ("skew",)
TARGET = "forward_relative_tail_asymmetry_spread"

GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

SIGNAL_WINDOW_SECONDS: float = e71.SIGNAL_WINDOW_SECONDS
ATM_BAND: float = e71.ATM_BAND

PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 120

# Composed floor: sealed EVAL-71 surface floor for BOTH underlyings AND the
# sealed EVAL-77 cross-sectional alignment floor. Not the EVAL-64 ladder floor.
FLOOR: Dict[str, Any] = {
    "min_underlyings": int(e71.FLOOR["min_underlyings"]),
    "min_option_trades_per_underlying": int(e71.FLOOR["min_option_trades_per_underlying"]),
    "min_near_atm_option_trades_per_underlying": int(
        e71.FLOOR["min_near_atm_option_trades_per_underlying"]
    ),
    "min_perp_candles_per_underlying": int(e71.FLOOR["min_perp_candles_per_underlying"]),
    "min_perp_span_seconds_per_underlying": float(
        e71.FLOOR["min_perp_span_seconds_per_underlying"]
    ),
    "min_aligned_common_bars": int(e77.FLOOR["min_aligned_common_bars"]),
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "Reuses the sealed EVAL-71 surface floor verbatim "
        "(min_option_trades_per_underlying=1000, "
        "min_near_atm_option_trades_per_underlying=400, "
        "min_perp_candles_per_underlying=1000, "
        "min_perp_span_seconds_per_underlying=82000s) PLUS the sealed EVAL-77 "
        "cross-sectional alignment floor (>= min_aligned_common_bars=200 aligned "
        "common bar-ends on the coarsest grid), applied to BOTH BTC and ETH. Below "
        "the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 "
        "ladder floor."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "scripts/eval85_surface_skew_forward_return_tail.py",
    "scripts/eval110_cross_sectional_skew_basis_relative_tail_asymmetry_spread.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval110_cross_sectional_skew_basis_relative_tail_asymmetry_spread.py "
    "tests/test_eval110_cross_sectional_skew_basis_relative_tail_asymmetry_spread.py",
    "python3 -m pytest -q tests/test_eval110_cross_sectional_skew_basis_relative_tail_asymmetry_spread.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval110_cross_sectional_skew_basis_relative_tail_asymmetry_spread.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval110_cross_sectional_skew_basis_relative_tail_asymmetry_spread.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL110-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD",
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
# Forward relative tail-asymmetry spread target
# ---------------------------------------------------------------------------
def _forward_tail_asym_by_bar(
    capture: Dict[str, Any], *, bar_seconds: float, horizon_bars: int
) -> Dict[int, float]:
    """Per-asset forward return-tail asymmetry indexed by bar_open_ms.

    Reuses EVAL-85's ``_forward_return_tail_asym`` verbatim on EVAL-71's own
    causal surface bars (which carry perp close prices and the skew signal).
    """
    bars = e71.build_surface_bars(
        capture,
        bar_seconds=bar_seconds,
        signal_window_seconds=SIGNAL_WINDOW_SECONDS,
        atm_band=ATM_BAND,
    )
    fwd = e85._forward_return_tail_asym(bars, horizon_bars)
    out: Dict[int, float] = {}
    n_fwd = len(fwd)
    for k, b in enumerate(bars):
        if k < n_fwd and fwd[k] is not None:
            out[int(b["bar_open_ms"])] = float(fwd[k])
    return out


def _relative_tail_asym_spread(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float, horizon_bars: int
) -> Tuple[List[int], List[float]]:
    """Forward relative tail-asymmetry spread on the common aligned grid.

    ``y_k = tail_asym_BTC(k) - tail_asym_ETH(k)`` (EVAL-89/93/105/106 convention)
    aligned on the EVAL-77 common bar grid so both underlyings carry a value.
    Returns the aligned bar-ends and their spreads in the same order.
    """
    ta_b = _forward_tail_asym_by_bar(
        captures[BASELINE], bar_seconds=bar_seconds, horizon_bars=horizon_bars
    )
    ta_r = _forward_tail_asym_by_bar(
        captures[RELATIVE], bar_seconds=bar_seconds, horizon_bars=horizon_bars
    )
    common = e77.build_cross_section(
        {BASELINE: captures[BASELINE], RELATIVE: captures[RELATIVE]},
        bar_seconds=bar_seconds,
    )["common"]
    bars: List[int] = []
    ys: List[float] = []
    for m in common:
        if m in ta_b and m in ta_r:
            bars.append(int(m))
            ys.append(float(ta_b[m]) - float(ta_r[m]))
    return bars, ys


# ---------------------------------------------------------------------------
# Per-(signal, grid, horizon) cross-sectional skew-basis -> relative-tail-asymmetry
# ---------------------------------------------------------------------------
def evaluate_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Cross-sectional skew basis -> relative tail-asymmetry spread for one config.

    ``rel_z_k`` = expanding-z-scored ``skew[ETH] - skew[BTC]`` on the common
    aligned bar grid (EVAL-77 ``build_cross_section`` /
    ``_relative_signal_series`` verbatim); ``y_k`` = forward BTC-minus-ETH
    tail-asymmetry spread over bars ``k+1..k+H`` (EVAL-85 verbatim).
    """
    cs = e77.build_cross_section(captures, bar_seconds=bar_seconds)
    n_common = len(cs["common"])
    if n_common < int(horizon_bars) + 5:
        return {
            "signal": surface_signal,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "target": TARGET,
            "error": "insufficient common surface bars",
            "n_common_bars": n_common,
            "n_pairs": 0,
            "pass": False,
            "reason": "insufficient_common_bars",
        }

    rel_z = e77._relative_signal_series(cs, surface_signal=surface_signal)
    z_by_bar = {
        int(m): float(rel_z[i]) for i, m in enumerate(cs["common"]) if i < len(rel_z)
    }
    y_bars, y = _relative_tail_asym_spread(
        captures, bar_seconds=bar_seconds, horizon_bars=horizon_bars
    )

    xs: List[float] = []
    ys: List[float] = []
    for m, val in zip(y_bars, y):
        if m in z_by_bar:
            xs.append(float(z_by_bar[m]))
            ys.append(float(val))

    if len(xs) < int(MIN_USABLE_PAIRS_PER_CONFIG):
        return {
            "signal": surface_signal,
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
        "signal": surface_signal,
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
# Composed heavy-work floor (EVAL-71 surface floor both underlyings AND EVAL-77
# cross-sectional alignment)
# ---------------------------------------------------------------------------
def _underlying_surface_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    """The sealed EVAL-71 surface floor for one underlying (reused verbatim)."""
    return e71._underlying_surface_floor(capture)


def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Composed floor: both underlyings pass EVAL-71 AND aligned common bars."""
    insts = sorted(captures)
    per_underlying = {i: _underlying_surface_floor(captures[i]) for i in insts}
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
        "eval": "EVAL-110",
        "title": "Cross-sectional options implied-vol SKEW basis (BTC-vs-ETH relative "
                 "near-ATM put-call skew) -> subsequent relative return-tail-asymmetry "
                 "spread (BTC-minus-ETH forward tail asymmetry): wrapper-free Spearman "
                 "rank information coefficient (predictiveness) falsification on the "
                 "real on-disk three-way captures",
        "extends": "EVAL-77 (same cross-sectional BTC-vs-ETH alignment and "
                   "``_relative_signal_series``, reused verbatim) and EVAL-85 (same "
                   "forward return-tail-asymmetry target, reused verbatim) but a "
                   "DISTINCT cell: the *cross-sectional skew basis* (not the "
                   "single-underlying skew of EVAL-85, not the skew basis -> relative "
                   "VRP of EVAL-89, not the skew basis -> relative vol-of-vol of "
                   "EVAL-91, not the term basis -> relative tail asymmetry of "
                   "EVAL-105/106) with the forward relative *tail-asymmetry* spread; "
                   "no new acquisition",
        "supersedes": "nothing — this is the skew-basis partner to EVAL-85 (own-asset "
                      "skew -> own tail asymmetry), EVAL-89/91 (skew basis -> relative "
                      "VRP / vol-of-vol) and EVAL-105/106 (term basis -> relative tail "
                      "asymmetry). It makes a predictiveness claim only, no "
                      "traded-form / monetization claim",
        "capture_dir": str(capture_dir),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_z_k = expanding_z( skew[ETH](k) - skew[BTC](k) )",
            "target": "y_k = tail_asym_BTC(k) - tail_asym_ETH(k) with "
                      "tail_asym_i(k) = (q95 - median) - (median - q05) over the "
                      "next H perp log returns strictly after k (relative tail-"
                      "asymmetry spread)",
        },
        "surface_signals": list(SURFACE_SIGNALS),
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar near-ATM put-call skew (EVAL-71 "
                  "``build_surface_bars``: skew = mean(put iv) - mean(call iv) over "
                  "near-ATM trades); the relative series (ETH - BTC) is forward-filled "
                  "then expanding-zscored end-of-bar k on the EVAL-77 common aligned "
                  "bar grid (reused e77._relative_signal_series / "
                  "e61.expanding_zscore).",
        "target_detail": "forward relative tail-asymmetry spread: per underlying "
                         "tail_asym = (q95 - median) - (median - q05) over the next H "
                         "perp log returns (strictly after the decision at bar k, "
                         "EVAL-85 ``_forward_return_tail_asym`` verbatim), then BTC "
                         "minus ETH on the common aligned bar grid",
        "statistic": "Spearman rank correlation IC = rho(rel_z_k, y_k) over the common "
                     "aligned bar-ends (H1: IC > 0, relatively positive ETH-minus-BTC "
                     "skew basis predicts BTC subsequently carries a relatively richer "
                     "forward tail-asymmetry spread)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the relative tail-asymmetry spread",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": (
            "GO only if, on BOTH BTC and ETH floors satisfied, at least one config "
            "(skew basis x bar grid x horizon) has Spearman IC > 0, directional "
            "permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least "
            "min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that "
            "config; else NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures (option "
                    "trades with real iv/strike/expiry + perp candles for BTC and ETH); "
                    "no new acquisition, no network; composes the EVAL-71 surface floor "
                    "for both underlyings with the EVAL-77 cross-sectional alignment floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval110(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL110-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD",
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
    for sig in SURFACE_SIGNALS:
        for bar_s in GRID_BAR_SECONDS:
            for horizon in FORWARD_HORIZONS_BARS:
                try:
                    res = evaluate_config(
                        captures, surface_signal=sig, bar_seconds=bar_s,
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
        "EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD"
        if floor_ok
        else "EVAL_110_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal cross-sectional options skew basis (ETH - BTC near-ATM put-call "
            "skew) and the subsequent BTC-minus-ETH forward relative tail-asymmetry "
            "spread on the real on-disk captures"
            if floor_ok else "capture below the composed EVAL-71 surface + EVAL-77 "
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
            "The causal cross-sectional options implied-vol put-call skew basis "
            "(BTC-vs-ETH relative near-ATM skew, reconstructed from the real Deribit "
            "option trade tapes) has a positive monotone (Spearman rank) relationship "
            "with the subsequent relative return-tail-asymmetry spread (BTC-minus-ETH "
            "forward tail-asymmetry spread): relative skew richness predicts relative "
            "tail asymmetry. Tested on the already-acquired real on-disk captures at "
            "the composed EVAL-71 surface + EVAL-77 alignment floor."
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
        f"# {PREREG_ID} — cross-sectional skew basis -> relative tail-asymmetry "
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
        f"- Surface signals: {p['surface_signals']}",
        f"- Signal window (s): {p['signal_window_seconds']}",
        f"- Near-ATM band: {p['atm_band']}",
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
        "## Pre-registered composed floor (EVAL-71 surface both underlyings + EVAL-77 alignment)",
        "",
        f"- {fl['note']}",
        f"- Min underlyings: {fl['min_underlyings']}",
        f"- Min aligned common bars (coarsest grid): {fl['min_aligned_common_bars']}",
        f"- Min usable pairs per config: {fl['min_usable_pairs_per_config']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {r['report_id']} — cross-sectional skew basis -> relative "
        f"tail-asymmetry spread predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Verdict detail: {r['verdict_detail']}",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        f"- Aligned common bars by grid: {fl.get('aligned_common_bars_by_grid')}",
        "",
        "## Per-underlying floor (EVAL-71 surface floor)",
        "",
        "| underlying | floor ok | option trades | near-ATM trades | perp candles | span (s) |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        lines.append(
            f"| {inst} | {u.get('ok')} | {u.get('n_option_trades')} | "
            f"{u.get('n_near_atm_option_trades')} | {u.get('n_perp_candles')} | "
            f"{u.get('perp_span_seconds')} |"
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
        "task": r.get("task", "EVAL110-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD"),
        "verdict": "BLOCKED",
        "verdict_detail": "capture below the composed EVAL-71 surface + EVAL-77 alignment "
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
        f"# {BLOCKED_ID} — cross-sectional skew basis -> relative "
        f"tail-asymmetry spread predictiveness: BELOW FLOOR",
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
        "The capture does not meet the composed EVAL-71 surface + EVAL-77 cross-sectional "
        "alignment floor, so no GO/NO-GO verdict is emitted. Do NOT weaken either "
        "floor, do NOT use synthetic data, and do NOT emit NO-GO on under-floor data.",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        lines.append(
            f"- {inst}: ok={u.get('ok')} checks={json.dumps({k: v for k, v in u.items() if k != 'note'})}"
        )
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-110: cross-sectional options skew basis -> relative "
                    "tail-asymmetry spread (BTC-minus-ETH forward tail-asymmetry "
                    "spread) predictiveness (Spearman rank IC) on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label",
        default="EVAL110-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD",
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval110(
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
