#!/usr/bin/env python3
"""EVAL-89: does the **cross-sectional put-call SKEW basis** (BTC-vs-ETH relative
put-call skew) predict the subsequent **relative *variance risk premium* (VRP)
spread** — i.e. when ETH's skew is rich relative to BTC's, does BTC subsequently
carry the richer forward VRP? A distinct, runnable-**now** relative-value *VRP*
predictiveness falsification on the real on-disk three-way captures.

Why this rung exists (anti-avoidance priority cell)
---------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + **options order-flow** + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now line
EVAL-70..88 is sealed (EVAL-89 is this campaign):

* EVAL-71/73 sealed ``GO CONFIRMED`` — the *single-underlying* options implied-vol
  surface (near-ATM IV level + put-call skew) predicts the same underlying's
  forward *RV level* (and is stable OOS).
* EVAL-77 sealed ``GO CONFIRMED`` — the *cross-sectional* BTC-vs-ETH surface basis
  predicts the subsequent BTC-minus-ETH *realized-vol spread* (relative **vol**).
* EVAL-80 sealed ``NO-GO CONFIRMED (PASS)`` — that cross-sectional basis does not
  monetize net-of-cost through a delta-hedged two-leg ATM straddle **spread**.
* EVAL-85/86/87 sealed ``GO CONFIRMED`` — *single-underlying* skew / atm_iv ->
  forward return tail asymmetry / VRP.
* EVAL-88 sealed ``GO CONFIRMED`` — the *cross-sectional* basis predicts the
  subsequent relative *direction* (BTC-minus-ETH signed return spread).

None of them covers a **cross-sectional skew basis -> forward relative *VRP*
spread** cell: does the *relative put-call skew* (BTC vs ETH) predict the
subsequent BTC-minus-ETH *relative VRP* (how much richer implied vol is versus
subsequently realized vol)? This is the relative-value *VRP* complement to EVAL-86
(own-asset skew -> own VRP) and is distinct from EVAL-77 (basis -> RV *spread*),
EVAL-88 (basis -> *return* spread) and every traded-form cell.

EVAL-89 asks the genuinely distinct, on-charter, runnable-**now** question:

    When ETH's put-call skew is rich relative to BTC's, does BTC subsequently
    carry the richer forward VRP (atm_iv - forward_RV) — i.e. is the causal
    BTC-vs-ETH skew **basis** informative about the subsequent BTC-minus-ETH
    relative *variance risk premium* spread (relative-value VRP)?

This is **not** EVAL-77 (relative RV *spread*, a realized-vol magnitude),
**not** EVAL-86 (own-asset skew -> own VRP; here it is cross-sectional and the
target is a BTC-minus-ETH *spread*), **not** EVAL-88 (relative *return* direction),
and **not** any single-underlying surface cell. It reuses the sealed EVAL-77
cross-sectional alignment, the EVAL-71 surface reconstruction + forward-RV, the
EVAL-86 VRP definition and the EVAL-65 inference verbatim; it runs on the
already-acquired real on-disk captures with **no new acquisition** and **no
network**, so it is heavy work that is runnable **today**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For the causal skew basis signal ``rel_z_k = expanding_z( skew_ETH(k) -
skew_BTC(k) )`` (EVAL-77 ``_relative_signal_series(surface_signal="skew")``),
each bar grid ``{60s, 300s}`` and each forward horizon ``H`` bars, on the
**common aligned** bar grid:

    x_k = rel_z_k                                             (relative skew richness)
    y_k = VRP_BTC(k) - VRP_ETH(k)                             (relative VRP spread)
          where VRP_i(k) = atm_iv_i(k) - forward_RV_i(k+1..k+H)
          and forward_RV_i = sqrt(mean(log-return^2)) over the next H perp bars

``rel_z`` is forward-filled causally then expanding-z-scored end-of-bar ``k``;
``y`` uses the near-ATM IV at bar ``k`` (known) minus the forward realized vol
strictly after ``k`` (EVAL-71 ``_forward_rv`` / EVAL-77 ``_rv_series``, identical
definition). Compute Spearman rank ``IC = rho(x_k, y_k)``. H1 is ``IC > 0``
(ETH skew-rich -> BTC forward VRP richer; fear/skew mean-reverts so the feared
asset's VRP compresses). A config **passes** only if ``IC > 0``, directional
permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if at least one config** passes AND pooled BH-FDR rejects that config;
else ``NO-GO CONFIRMED (PASS)`` (the cross-sectional skew basis does not portably
predict relative VRP).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-89 consumes BOTH underlyings' trade-tape IV surfaces and both perp series, so
it composes the sealed EVAL-71 surface floor (applied to BOTH BTC and ETH, reused
verbatim) with a cross-sectional alignment floor (>= ``MIN_ALIGNED_COMMON_BARS``
bar-ends where both underlyings carry a causal near-ATM IV on the coarsest grid).
Neither is weakened. Below the composed floor it seals
``EVAL_89_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD_PREREGISTRATION_<UTC>``
then ``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the sealed EVAL-61/62/65/71/77 primitives and the EVAL-86 VRP
# definition verbatim (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD_COMBINED"
PREREG_ID = "EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD_PREREGISTRATION"
BLOCKED_ID = "EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD_BLOCKED"

# Pre-registered grid (skew basis x bar grid x forward horizons). The target is a
# DISTINCT cell: the forward relative *VRP* spread (BTC minus ETH), not the RV
# spread (EVAL-77), not the return spread (EVAL-88), not own-asset VRP (EVAL-86).
# Use the SKEW basis (not atm_iv) so the signal does not mechanically appear inside
# the target (the target subtracts atm_iv from forward RV).
SURFACE_SIGNALS: Tuple[str, ...] = ("skew",)
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)
TARGET = "forward_relative_vrp_spread"

# The cross-section is BTC-vs-ETH, matching the sealed EVAL-77 convention:
# rel = signal[ETH] - signal[BTC]; target = VRP[BTC] - VRP[ETH]; H1: IC > 0
# (ETH skew richness predicts BTC carries the richer forward VRP).
BASELINE = e77.BASELINE  # "BTC"
RELATIVE = e77.RELATIVE  # "ETH"

# Statistics reused verbatim from EVAL-65 (identical permutation / bootstrap / seed).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 120

# Composed heavy-work floor (EVAL-71 floor for both underlyings AND alignment).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_aligned_common_bars": 200,
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-89 consumes both underlyings' trade-tape IV surfaces and both perp "
        "series. It composes the sealed EVAL-71 surface floor (applied to BOTH BTC "
        "and ETH, reused verbatim, neither weakened) with a cross-sectional "
        "alignment floor (>= min_aligned_common_bars bar-ends where both underlyings "
        "carry a causal near-ATM IV on the coarsest grid). This is NOT the EVAL-64 "
        "options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and "
        "is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "scripts/eval86_surface_skew_forward_vrp_predictiveness.py",
    "scripts/eval89_cross_sectional_skew_basis_relative_vrp_spread.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile "
    "scripts/eval89_cross_sectional_skew_basis_relative_vrp_spread.py "
    "tests/test_eval89_cross_sectional_skew_basis_relative_vrp_spread.py",
    "python3 -m pytest -q "
    "tests/test_eval89_cross_sectional_skew_basis_relative_vrp_spread.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval89_cross_sectional_skew_basis_relative_vrp_spread.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval89_cross_sectional_skew_basis_relative_vrp_spread.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL89-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VRP-SPREAD",
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
# Forward relative *VRP* spread target (distinct from EVAL-77 forward RV spread
# and EVAL-88 forward return spread): BTC-minus-ETH forward VRP.
# ---------------------------------------------------------------------------
def _atm_iv_on_common(cs: Dict[str, Any], inst: str) -> List[float]:
    """Causal forward-filled near-ATM implied vol for ``inst`` on the common bar
    grid (EVAL-71 ``_forward_fill``, reused verbatim)."""
    maps = cs["maps"][inst]
    raw = [maps[int(m)].get("atm_iv") for m in cs["common"]]
    return e71._forward_fill(raw)


def _forward_vrp_on_common(
    cs: Dict[str, Any], inst: str, horizon_bars: int
) -> List[float]:
    """Forward VRP for ``inst`` on the common aligned grid.

    ``VRP_i(k) = atm_iv_i(k) - forward_RV_i(k+1..k+H)`` where the forward realized
    vol is ``sqrt(mean(log-return^2))`` over the next ``H`` perp bars (identical
    definition to EVAL-71 ``_forward_rv`` via EVAL-77 ``_rv_series``). The near-ATM
    IV at bar ``k`` is known at the decision, and the forward RV is strictly after
    ``k`` — so the target is causal. Length is ``len(common) - H``.
    """
    closes = e77._closes_on_common(cs, inst)
    rv = e77._rv_series(closes, horizon_bars)
    atm_iv = _atm_iv_on_common(cs, inst)
    out: List[float] = []
    for k in range(len(rv)):
        out.append(float(atm_iv[k]) - float(rv[k]))
    return out


def _forward_rel_vrp_spread(
    cs: Dict[str, Any], horizon_bars: int
) -> List[float]:
    """Forward BTC-minus-ETH relative VRP spread on the common aligned grid.

    ``y_k = VRP_BTC(k) - VRP_ETH(k)`` with ``VRP_i(k) = atm_iv_i(k) -
    forward_RV_i(k+1..k+H)``. Strictly distinct from EVAL-77's forward RV *spread*
    (realized-vol magnitude) and EVAL-88's forward *signed return spread* (relative
    direction). Returns a list indexed by bar ``k`` of length ``len(common) - H``.
    """
    vrp_b = _forward_vrp_on_common(cs, BASELINE, horizon_bars)
    vrp_r = _forward_vrp_on_common(cs, RELATIVE, horizon_bars)
    n = min(len(vrp_b), len(vrp_r))
    return [vrp_b[k] - vrp_r[k] for k in range(n)]


# ---------------------------------------------------------------------------
# Per-(signal, grid, horizon) cross-sectional relative-VRP predictiveness
# ---------------------------------------------------------------------------
def evaluate_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Cross-sectional relative-VRP predictiveness for one (signal, grid, horizon).

    ``rel_z_k`` = expanding-z-scored ``signal[ETH] - signal[BTC]`` on the common
    aligned bar grid (EVAL-77 reconstruction verbatim, ``surface_signal="skew"``);
    ``y_k`` = forward BTC-minus-ETH VRP spread over bars k+1..k+H (strictly after k).
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
    y = _forward_rel_vrp_spread(cs, horizon_bars)

    xs: List[float] = []
    ys: List[float] = []
    for k in range(min(len(y), len(rel_z))):
        xs.append(float(rel_z[k]))
        ys.append(float(y[k]))

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
# Composed heavy-work floor (EVAL-71 floor for both underlyings AND alignment)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    """The sealed EVAL-71 surface floor for one underlying (reused verbatim)."""
    fl = e71._underlying_surface_floor(capture)
    return {
        "underlying": capture.get("underlying", "?"),
        "surface_floor_ok": bool(fl.get("ok")),
        "surface_floor": fl,
        "checks": {"surface_floor_ok": bool(fl.get("ok"))},
        "ok": bool(fl.get("ok")),
    }


def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Composed floor: both underlyings pass EVAL-71 AND aligned common bars."""
    insts = sorted(captures)
    per_underlying = {i: _underlying_floor(captures[i]) for i in insts}
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
        "eval": "EVAL-89",
        "title": "Cross-sectional put-call skew basis (BTC-vs-ETH relative skew) -> "
                 "subsequent relative *variance risk premium* (VRP) spread "
                 "(BTC-minus-ETH forward atm_iv - forward_RV): wrapper-free Spearman "
                 "rank information coefficient (predictiveness) falsification on the "
                 "real on-disk three-way captures",
        "extends": "EVAL-77 (same cross-sectional BTC-vs-ETH surface basis and "
                    "aligned common-bar reconstruction, reused verbatim; skew basis) "
                    "and EVAL-86 (forward VRP definition atm_iv - forward_RV, reused "
                    "verbatim) but a DISTINCT target: the forward relative VRP *spread* "
                    "(BTC minus ETH), not the relative RV spread (EVAL-77), not the "
                    "relative return direction (EVAL-88), not own-asset VRP (EVAL-86); "
                    "no new acquisition",
        "supersedes": "nothing — this is the relative-value *VRP* complement to "
                       "EVAL-86 (own-asset skew -> own VRP) and a distinct cell from "
                       "EVAL-77 (relative-vol spread) and EVAL-88 (relative direction). "
                       "It makes a predictiveness claim only, no traded-form / "
                       "monetization claim",
        "capture_dir": str(capture_dir),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_z_k = expanding_z( skew[ETH](k) - skew[BTC](k) )",
            "target": "y_k = VRP_BTC(k) - VRP_ETH(k) with "
                      "VRP_i(k) = atm_iv_i(k) - forward_RV_i(k+1..k+H) "
                      "(forward relative variance risk premium spread)",
        },
        "surface_signals": list(SURFACE_SIGNALS),
        "target": TARGET,
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar put-call skew surface (EVAL-71 build_surface_bars) "
                  "for BTC and ETH: skew = mean(put iv) - mean(call iv) over near-ATM "
                  "trades; the relative series (ETH - BTC) is forward-filled then "
                  "expanding-zscored end-of-bar k (reused e61.expanding_zscore via "
                  "EVAL-77). The skew basis is used (not atm_iv) so the signal does "
                  "not mechanically appear inside the target.",
        "target_detail": "forward relative VRP = per underlying VRP = atm_iv at bar k "
                         "minus forward realized vol sqrt(mean(log-return^2)) over the "
                         "next H perp bars (strictly after the decision at bar k, "
                         "EVAL-71 _forward_rv via EVAL-77 _rv_series), then BTC minus "
                         "ETH on the common aligned bar grid",
        "statistic": "Spearman rank correlation IC = rho(rel_z_k, y_k) over the common "
                     "aligned bar-ends (H1: IC > 0, ETH skew-richness predicts BTC "
                     "carries the richer forward VRP — relative-value VRP mean "
                     "reversion)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the relative-VRP spread",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": (
            "GO only if at least one config (skew basis x bar grid x horizon) has "
            "Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI "
            "lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled "
            "BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures (option "
                    "trades with real iv + perp candles for BTC and ETH); no new "
                    "acquisition, no network; composes the EVAL-71 floor for both "
                    "underlyings with a cross-sectional alignment floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval89(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL89-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VRP-SPREAD",
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
        "EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD" if floor_ok
        else "EVAL_89_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal cross-sectional put-call skew basis (ETH - BTC) and the "
            "subsequent BTC-minus-ETH forward relative *VRP* spread "
            "(atm_iv - forward_RV) on the real on-disk captures"
            if floor_ok else "capture below the composed EVAL-71 + alignment floor; "
                              "no verdict"
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
            "The causal cross-sectional put-call skew basis (BTC-vs-ETH relative "
            "skew, reconstructed from the real Deribit option trade tapes) has a "
            "positive monotone (Spearman rank) relationship with the subsequent "
            "relative *variance risk premium* spread (BTC-minus-ETH forward "
            "atm_iv - forward_RV): relative skew richness mean-reverts in VRP. Tested "
            "on the already-acquired real on-disk captures at the composed EVAL-71 + "
            "alignment floor."
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
        f"# {PREREG_ID} — cross-sectional put-call skew basis -> relative *VRP* "
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
        "## Pre-registered composed floor (EVAL-71 both underlyings + alignment)",
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
        f"# {r['report_id']} — cross-sectional put-call skew basis -> relative *VRP* "
        f"spread predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Verdict detail: {r['verdict_detail']}",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        f"- Aligned common bars by grid: {fl.get('aligned_common_bars_by_grid')}",
        "",
        "## Per-underlying EVAL-71 floor",
        "",
        "| underlying | surface floor ok | option trades | near-ATM | perp candles | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        s = u.get("surface_floor", {})
        lines.append(
            f"| {inst} | {u.get('surface_floor_ok')} | {s.get('n_option_trades')} | "
            f"{s.get('n_near_atm_option_trades')} | {s.get('n_perp_candles')} | "
            f"{u.get('ok')} |"
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
        "task": r.get("task", "EVAL89-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VRP-SPREAD"),
        "verdict": "BLOCKED",
        "verdict_detail": "capture below the composed EVAL-71 + alignment floor; no verdict (never a NO-GO)",
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
        f"# {BLOCKED_ID} — cross-sectional put-call skew basis -> relative *VRP* "
        f"spread predictiveness: BELOW FLOOR",
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
        "The capture does not meet the composed EVAL-71 + cross-sectional alignment "
        "floor, so no GO/NO-GO verdict is emitted. Do NOT weaken either floor, do NOT "
        "use synthetic data, and do NOT emit NO-GO on under-floor data.",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        lines.append(
            f"- {inst}: surface_floor_ok={u.get('surface_floor_ok')} "
            f"checks={json.dumps(u.get('checks'))}"
        )
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-89: cross-sectional put-call skew basis -> relative *VRP* "
                    "spread (BTC-minus-ETH forward atm_iv - forward_RV) predictiveness "
                    "(Spearman rank IC) on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label",
        default="EVAL89-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VRP-SPREAD",
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval89(
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