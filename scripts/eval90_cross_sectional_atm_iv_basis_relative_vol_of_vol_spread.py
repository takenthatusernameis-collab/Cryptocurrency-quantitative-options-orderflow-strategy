#!/usr/bin/env python3
"""EVAL-90: does the **cross-sectional near-ATM IV basis** (BTC-vs-ETH relative
near-ATM implied vol) predict the subsequent **relative *vol-of-vol* spread** —
i.e. when ETH's near-ATM implied vol is rich relative to BTC's, does BTC
subsequently carry the richer forward **vol-of-vol** (turbulence / unevenness of
the realized-variance path, ``Vov_i = std_j(r_j^2)`` over the next H perp bars)
relative to ETH? A distinct, runnable-**now** relative-value *vol-of-vol*
predictiveness falsification on the real on-disk three-way captures.

Why this rung exists (anti-avoidance mandatory next build)
----------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + **options order-flow** + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now line
EVAL-70..89 is sealed:

* EVAL-71/73 sealed ``GO CONFIRMED`` — the *single-underlying* options implied-vol
  surface (near-ATM IV level + put-call skew) predicts the same underlying's
  forward *RV level* (and is stable OOS).
* EVAL-77 sealed ``GO CONFIRMED`` — the *cross-sectional* BTC-vs-ETH surface basis
  (near-ATM IV / skew) predicts the subsequent BTC-minus-ETH *realized-vol spread*
  (relative **vol magnitude**).
* EVAL-80 sealed ``NO-GO CONFIRMED (PASS)`` — that cross-sectional basis does not
  monetize net-of-cost through a delta-hedged two-leg ATM straddle **spread**.
* EVAL-84 sealed ``NO-GO CONFIRMED (PASS)`` — *own-asset* term-structure slope
  predicts forward *vol-of-vol* on ETH but is null on BTC (not portable).
* EVAL-85/86/87 sealed ``GO CONFIRMED`` — *single-underlying* skew / atm_iv ->
  forward tail asymmetry / VRP.
* EVAL-88 sealed ``GO CONFIRMED`` — the *cross-sectional* basis predicts the
  subsequent relative *direction* (BTC-minus-ETH signed return spread).
* EVAL-89 sealed ``NO-GO CONFIRMED (PASS)`` — the *cross-sectional skew basis* does
  not portably predict the subsequent relative *VRP* spread.

None of them covers a **cross-sectional near-ATM IV basis -> forward relative
*vol-of-vol* spread** cell: does the *relative implied-vol level* (BTC vs ETH)
predict the subsequent BTC-minus-ETH *relative vol-of-vol* (how uneven/turbulent
each underlying's forward realized-variance path is)? This is the relative-value
*vol-of-vol* complement to EVAL-84 (own-asset term_slope -> vol-of-vol) and is
distinct from EVAL-77 (basis -> RV *spread*), EVAL-88 (basis -> *return* spread),
EVAL-89 (skew basis -> *VRP* spread), and every traded-form cell. ``atm_iv`` is a
vol *level* and does not appear inside the vol-of-vol target, so there is no
mechanical overlap.

EVAL-90 asks the genuinely distinct, on-charter, runnable-**now** question:

    When ETH's near-ATM implied vol is rich relative to BTC's, does BTC
    subsequently carry the richer forward vol-of-vol — i.e. is the causal
    BTC-vs-ETH near-ATM IV **basis** informative about the subsequent
    BTC-minus-ETH relative *volatility-of-realized-variance* spread?

This is **not** EVAL-77 (relative RV *spread*, a realized-vol magnitude),
**not** EVAL-84 (own-asset term-structure -> own vol-of-vol; here it is
cross-sectional on the atm_iv basis and the target is a BTC-minus-ETH *spread*),
**not** EVAL-88 (relative *return* direction), **not** EVAL-89 (skew basis ->
relative *VRP* spread), and **not** any single-underlying surface or traded-form
cell. It reuses the sealed EVAL-61/62/65/71/77 signal reconstructions, the
EVAL-84 vol-of-vol definition, and the EVAL-65 inference verbatim; it runs on the
already-acquired real on-disk captures with **no new acquisition** and **no
network**, so it is heavy work that is runnable **today**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For the causal atm_iv basis signal ``rel_z_k = expanding_z( atm_iv_ETH(k) -
atm_iv_BTC(k) )`` (EVAL-77 ``_relative_signal_series(surface_signal="atm_iv")``),
each bar grid ``{60s, 300s}`` and each forward horizon ``H`` bars, on the
**common aligned** bar grid:

    x_k = rel_z_k                                             (relative iv richness)
    y_k = Vov_BTC(k) - Vov_ETH(k)                             (relative vol-of-vol spread)
          where Vov_i(k) = sqrt(mean((v_j - mean(v))^2))
          and v_j = r_j^2, r_j = log(close_j/close_{j-1})
          over the next H perp bars for underlying i

``rel_z`` is forward-filled causally then expanding-z-scored end-of-bar ``k``;
``y`` uses log returns strictly after ``k`` (EVAL-84 vol-of-vol definition,
computed per-underlying on the common aligned grid). Compute Spearman rank
``IC = rho(x_k, y_k)``. H1 is ``IC > 0`` (ETH iv-rich -> BTC forward vol-of-vol
richer; relative implied richness precedes relatively more turbulent realized
variance paths). A config **passes** only if ``IC > 0``, directional permutation
``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if at least one config** passes AND pooled BH-FDR rejects that config;
else ``NO-GO CONFIRMED (PASS)`` (the cross-sectional atm_iv basis does not
portably predict relative vol-of-vol).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-90 consumes BOTH underlyings' trade-tape IV surfaces and both perp series, so
it composes the sealed EVAL-71 surface floor (applied to BOTH BTC and ETH, reused
verbatim) with a cross-sectional alignment floor (>= ``MIN_ALIGNED_COMMON_BARS``
bar-ends where both underlyings carry a causal near-ATM IV on the coarsest grid).
Neither is weakened. Below the composed floor it seals
``EVAL_90_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/65/71/77 primitives and the EVAL-84 vol-of-vol
# definition verbatim (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
import scripts.eval84_term_structure_vol_of_vol_predictiveness as e84  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED"
PREREG_ID = "EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION"
BLOCKED_ID = "EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_BLOCKED"

# Pre-registered grid (atm_iv basis x bar grid x forward horizons). The target is
# a DISTINCT cell: the forward relative *vol-of-vol* spread (BTC minus ETH), not
# the RV spread (EVAL-77), not the return spread (EVAL-88), not the VRP spread
# (EVAL-89), not own-asset vol-of-vol (EVAL-84). Use the ATM-IV basis (distinct
# from EVAL-89's skew basis); atm_iv is a vol level and is not inside the
# vol-of-vol target.
SURFACE_SIGNALS: Tuple[str, ...] = ("atm_iv",)
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)
TARGET = "forward_relative_vol_of_vol_spread"

# The cross-section is BTC-vs-ETH, matching the sealed EVAL-77 convention:
# rel = signal[ETH] - signal[BTC]; target = Vov[BTC] - Vov[ETH]; H1: IC > 0
# (ETH iv richness predicts BTC carries the richer forward vol-of-vol).
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
        "EVAL-90 consumes both underlyings' trade-tape IV surfaces and both perp "
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
    "scripts/eval84_term_structure_vol_of_vol_predictiveness.py",
    "scripts/eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile "
    "scripts/eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread.py "
    "tests/test_eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread.py",
    "python3 -m pytest -q "
    "tests/test_eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL90-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
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
# Forward relative *vol-of-vol* spread target (distinct from EVAL-77 forward RV
# spread, EVAL-88 forward return spread, EVAL-89 forward VRP spread): BTC-minus-ETH
# forward vol-of-vol.
# ---------------------------------------------------------------------------
def _forward_vov_on_common(
    cs: Dict[str, Any], inst: str, horizon_bars: int
) -> List[float]:
    """Forward vol-of-vol for ``inst`` on the common aligned grid.

    ``Vov_i(k) = sqrt(mean((v_j - mean(v))^2))`` with ``v_j = r_j^2`` and
    ``r_j = log(close_j/close_{j-1})`` over the next ``H`` perp bars (EVAL-84
    vol-of-vol definition), computed on the common aligned closes for ``inst``
    (EVAL-77 ``_closes_on_common``). The target uses log returns strictly after
    bar ``k``. Returns a list indexed by bar ``k`` of length
    ``len(common) - H`` (one value per decision bar with a full forward window).
    """
    closes = e77._closes_on_common(cs, inst)
    lr = (
        [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)]
        if len(closes) >= 2
        else []
    )
    h = int(horizon_bars)
    out: List[float] = []
    for k in range(0, len(lr) - h + 1):
        seg = lr[k:k + h]
        sq = [r * r for r in seg]
        m = sum(sq) / float(h)
        var = sum((x - m) ** 2 for x in sq) / float(h)
        out.append(math.sqrt(max(0.0, var)))
    return out


def _forward_rel_vov_spread(
    cs: Dict[str, Any], horizon_bars: int
) -> List[float]:
    """Forward BTC-minus-ETH relative vol-of-vol spread on the common aligned grid.

    ``y_k = Vov_BTC(k) - Vov_ETH(k)`` with ``Vov_i(k)`` the forward vol-of-vol
    (std of squared log returns) over the next ``H`` perp bars (strictly after the
    decision at bar ``k``). Strictly distinct from EVAL-77's forward RV *spread*
    (realized-vol magnitude), EVAL-88's forward *signed return spread* (relative
    direction), and EVAL-89's forward relative *VRP* spread. Returns a list indexed
    by bar ``k`` of length ``len(common) - H``.
    """
    vov_b = _forward_vov_on_common(cs, BASELINE, horizon_bars)
    vov_r = _forward_vov_on_common(cs, RELATIVE, horizon_bars)
    n = min(len(vov_b), len(vov_r))
    return [vov_b[k] - vov_r[k] for k in range(n)]


# ---------------------------------------------------------------------------
# Per-(signal, grid, horizon) cross-sectional relative-vol-of-vol predictiveness
# ---------------------------------------------------------------------------
def evaluate_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Cross-sectional relative-vol-of-vol predictiveness for one config.

    ``rel_z_k`` = expanding-z-scored ``signal[ETH] - signal[BTC]`` on the common
    aligned bar grid (EVAL-77 reconstruction verbatim, ``surface_signal="atm_iv"``);
    ``y_k`` = forward BTC-minus-ETH vol-of-vol spread over bars k+1..k+H (strictly
    after k).
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
    y = _forward_rel_vov_spread(cs, horizon_bars)

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
        "eval": "EVAL-90",
        "title": "Cross-sectional near-ATM IV basis (BTC-vs-ETH relative near-ATM IV) -> "
                 "subsequent relative *vol-of-vol* spread "
                 "(BTC-minus-ETH forward std(squared log returns)): wrapper-free "
                 "Spearman rank information coefficient (predictiveness) falsification "
                 "on the real on-disk three-way captures",
        "extends": "EVAL-77 (same cross-sectional BTC-vs-ETH surface basis and "
                   "aligned common-bar reconstruction, reused verbatim; atm_iv basis) "
                   "and EVAL-84 (forward vol-of-vol definition std(squared log returns), "
                   "reused verbatim) but a DISTINCT target: the forward relative "
                   "vol-of-vol *spread* (BTC minus ETH), not the relative RV spread "
                   "(EVAL-77), not the relative return direction (EVAL-88), not the "
                   "relative VRP spread (EVAL-89), not own-asset vol-of-vol (EVAL-84); "
                   "no new acquisition",
        "supersedes": "nothing — this is the relative-value *vol-of-vol* complement to "
                      "EVAL-84 (own-asset term_slope -> vol-of-vol) and a distinct cell "
                      "from EVAL-77 (relative-vol spread), EVAL-88 (relative direction), "
                      "and EVAL-89 (relative VRP spread). It makes a predictiveness claim "
                      "only, no traded-form / monetization claim",
        "capture_dir": str(capture_dir),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_z_k = expanding_z( atm_iv[ETH](k) - atm_iv[BTC](k) )",
            "target": "y_k = Vov_BTC(k) - Vov_ETH(k) with "
                      "Vov_i(k) = sqrt(mean((v_j - mean(v))^2)), v_j = r_j^2, "
                      "r_j = log(close_j/close_{j-1}) over next H perp bars "
                      "(forward relative vol-of-vol spread)",
        },
        "surface_signals": list(SURFACE_SIGNALS),
        "target": TARGET,
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar near-ATM implied vol surface (EVAL-71 build_surface_bars) "
                  "for BTC and ETH; the relative series (ETH - BTC) is forward-filled then "
                  "expanding-zscored end-of-bar k (reused e61.expanding_zscore via "
                  "EVAL-77). The atm_iv basis is used (a vol level, not inside the "
                  "vol-of-vol target), distinct from EVAL-89's skew basis.",
        "target_detail": "forward relative vol-of-vol = per underlying vol-of-vol "
                         "sqrt(mean((v_j - mean(v))^2)) with v_j = r_j^2 (squared log "
                         "returns) over the next H perp bars (strictly after the decision "
                         "at bar k, EVAL-84 definition on EVAL-77 aligned common closes), "
                         "then BTC minus ETH on the common aligned bar grid",
        "statistic": "Spearman rank correlation IC = rho(rel_z_k, y_k) over the common "
                     "aligned bar-ends (H1: IC > 0, ETH iv-richness predicts BTC carries "
                     "the richer forward vol-of-vol — relative turbulence)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the relative-vol-of-vol spread",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": (
            "GO only if at least one config (atm_iv basis x bar grid x horizon) has "
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


def run_eval90(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL90-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
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
        "EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD" if floor_ok
        else "EVAL_90_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal cross-sectional near-ATM IV basis (ETH - BTC) and the subsequent "
            "BTC-minus-ETH forward relative *vol-of-vol* spread "
            "(std of squared log returns) on the real on-disk captures"
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
            "The causal cross-sectional near-ATM IV basis (BTC-vs-ETH relative "
            "near-ATM implied vol, reconstructed from the real Deribit option trade "
            "tapes) has a positive monotone (Spearman rank) relationship with the "
            "subsequent relative *vol-of-vol* spread (BTC-minus-ETH forward "
            "std of squared log returns): relative iv richness precedes relatively "
            "more turbulent realized variance paths. Tested on the already-acquired "
            "real on-disk captures at the composed EVAL-71 + alignment floor."
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
        f"# {PREREG_ID} — cross-sectional near-ATM IV basis -> relative *vol-of-vol* "
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
        f"# {r['report_id']} — cross-sectional near-ATM IV basis -> relative *vol-of-vol* "
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
        "task": r.get("task", "EVAL90-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VOL-OF-VOL-SPREAD"),
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
        f"# {BLOCKED_ID} — cross-sectional near-ATM IV basis -> relative *vol-of-vol* "
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
        description="EVAL-90: cross-sectional near-ATM IV basis -> relative *vol-of-vol* "
                    "spread (BTC-minus-ETH forward std(squared log returns)) predictiveness "
                    "(Spearman rank IC) on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label",
        default="EVAL90-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VOL-OF-VOL-SPREAD",
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval90(
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
