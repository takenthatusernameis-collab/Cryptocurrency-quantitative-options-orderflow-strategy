#!/usr/bin/env python3
"""EVAL-182: does the **cross-asset causal options order-flow toxicity x atm_iv
surface interaction spillover** (the OTHER underlying's z-scored options order-flow
toxicity multiplied by its near-ATM implied-vol level) predict the subsequent
**forward realized return variance** of the target underlying?

A distinct, on-charter, runnable-now predictiveness cell on the real on-disk
three-way captures — advancing the repo charter toward tradeable net-of-cost alpha
by testing whether the interaction of options order-flow toxicity and implied-vol
spillover carries directional information beyond either signal alone.

Why this rung exists (build immediately after EVAL-181 seals)
-------------------------------------------------------------
Repository charter (Cryptocurrency-quantitative-options-orderflow-strategy) is
crypto options surface + options order-flow -> tradeable, net-of-cost alpha on REAL
public data. EVAL-176 (cross-asset atm_iv spillover -> forward realized return
variance), EVAL-159/160 (cross-asset order-flow toxicity/imbalance -> forward
variance), EVAL-180 (cross-asset order-flow imbalance x atm_iv interaction -> forward
variance), and EVAL-181 (cross-asset order-flow imbalance x atm_iv interaction ->
forward CVaR) are sealed. EVAL-182 is the missing **toxicity interaction** cell:
does the product of the other asset's order-flow toxicity z and atm_iv z predict
the target's forward realized return variance? No toxicity interaction cell exists
yet (EVAL-151 measured toxicity x atm_iv interaction -> forward signed return mean;
EVAL-182 measures the same interaction against forward realized return variance).

Why interaction and why forward realized return variance
-------------------------------------------------------
EVAL-176 measures cross-asset atm_iv alone -> realized return variance. EVAL-159
measures cross-asset order-flow toxicity alone -> realized return variance. Neither
tests whether the two order-flow/surface channels *combine* to strengthen
predictiveness. The genuinely distinct, on-charter, runnable-now cell tested here
is: does the causal per-bar interaction
``tox_z[OTHER](k) * atm_iv_z[OTHER](k)`` carry monotone (Spearman rank) information
about the target underlying's subsequent forward realized return variance over bars
``k+1..k+H`` (EVAL-172 ``_forward_return_variance``, verbatim)? It is
**predictiveness only** — no traded-form or monetization claim.

Constructibility (verified, do not re-litigate): per-bar options order-flow
toxicity IS constructible for BOTH underlyings —
``e62.build_states(capture, tox_signal="tox", bar_seconds=300)`` returns **289
states** with a ``signal_z`` column on each of the three
``data/raw/eval61/three_way_*.json`` tapes (EVAL-159/EVAL-160 convention,
tox_signal="tox"). Surface atm_iv bars are constructible via EVAL-71
``build_surface_bars`` on the same tapes. Both signals share the ``bar_ms``
alignment key, so the interaction is computable on the common grid.
EVAL-182 is therefore **runnable, not BLOCKED** for data absence.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
-------------------------------------------------------------------------------
For each target underlying (BTC, ETH), each bar grid ``{60s, 300s}`` and each
forward horizon ``H`` bars:

* the causal per-bar options order-flow toxicity ``signal_z`` of the **other**
  underlying is reconstructed exactly as EVAL-159/160/EVAL-151 (EVAL-61/62
  ``build_states(tox_signal="tox")`` with EVAL-62 ``ZWINDOW``); and
* the causal per-bar near-ATM implied-vol level ``atm_iv`` of the **other**
  underlying is reconstructed exactly as EVAL-176 (EVAL-71
  ``build_surface_bars`` with the EVAL-71 signal window / ATM band constants
  verbatim — **surface bar, NOT the term bar**); and
* the interaction signal is ``tox_z * atm_iv_z`` (z-scored end-of-bar ``k``
  via ``e61.expanding_zscore`` after causal forward-fill); and
* the target is the forward **realized return variance** of the *target*
  underlying over bars ``k+1..k+H``:
  ``var_k = mean((r - mean(r))**2)`` for ``r_i = log(close_i / close_{i-1})``
  over ``i in k+1..k+H`` (EVAL-172 ``_forward_return_variance``, verbatim).
  Windows with fewer than ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs are dropped.

Compute Spearman rank ``IC = rho(other_interaction_z_k, own_variance_{k+1..k+H})``
with the sealed EVAL-65 directional permutation and block bootstrap (H1:
``IC > 0`` — the other asset's heavier buy-side options toxicity coinciding with
higher near-ATM IV precedes higher forward realized return variance on the target).
A config **passes** only if ``IC > 0``, directional permutation ``p < 0.05``,
block-bootstrap 95% CI lower ``> 0``, and at least ``MIN_USABLE_PAIRS_PER_CONFIG``
usable pairs.

**GO only if, on BOTH BTC and ETH and at least one config:** ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``,
and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-182 consumes both underlyings' options order-flow states (from the real
option-trade tape) and both underlyings' IV surfaces (atm_iv surface bars) plus
both perp series. It requires both:

* both underlyings present (cross-asset spillover needs two assets); and
* constructible toxicity states per underlying (>= 1 state on the coarsest grid);
* constructible surface atm_iv bars per underlying (EVAL-71 surface floor);
* a cross-asset alignment floor: at least ``MIN_ALIGNED_COMMON_BARS`` bar-ends
  where both underlyings carry a causal toxicity state AND a causal atm_iv bar
  on the coarsest grid (>= 1 = non-disjoint; genuinely missing-underlying or
  non-disjoint ⇒ BLOCKED, never NO-GO).

Below the floor it seals
``EVAL_182_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_BLOCKED_<UTC>``
(never a NO-GO). The EVAL-64 feasible floor that governs the EVAL-67/68/69
ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-176 measured cross-asset
atm_iv -> forward realized return variance; EVAL-159 measured cross-asset order-flow
toxicity -> forward realized return variance; EVAL-180 measured cross-asset
order-flow imbalance x atm_iv interaction -> forward realized return variance;
EVAL-182 measures the **cross-asset order-flow toxicity x atm_iv interaction
spillover** -> **forward realized return variance**, reusing the sealed EVAL-61/62/65/71/77/159/172
signal/target reconstructions and the EVAL-65 inference verbatim.

Seals ``EVAL_182_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/65/71/172 primitives verbatim (no forks, no src).
# The toxicity signal comes from EVAL-62 build_states(tox_signal="tox"),
# aligned cross-asset on the common bar grid (EVAL-77 pattern); the atm_iv surface
# bars come from EVAL-71 build_surface_bars (surface bar, NOT the term bar); the
# forward realized return target is transcribed verbatim from sealed EVAL-172.
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval172_single_asset_atm_iv_forward_variance as e172  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = (
    "EVAL_182_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_COMBINED"
)
PREREG_ID = (
    "EVAL_182_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_PREREGISTRATION"
)
BLOCKED_ID = (
    "EVAL_182_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_BLOCKED"
)

# Cross-asset order-flow toxicity x atm_iv interaction signal.
SURFACE_SIGNAL: str = "oflow_tox_atm_iv_interaction"
TARGET = "forward_variance"

# Pre-registered grid (cross-asset spillover x bar grid x forward horizons -> 6
# configs per target underlying, 12 total).
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# The cross-asset spillover is BTC <-> ETH. For target BTC the signal is ETH's
# interaction and vice versa.
BASELINE = "BTC"
RELATIVE = "ETH"

# Reuse EVAL-71 surface constants and EVAL-65/62 statistics verbatim.
SIGNAL_WINDOW_SECONDS: float = e71.SIGNAL_WINDOW_SECONDS
ATM_BAND: float = e71.ATM_BAND

PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 120
MIN_ALIGNED_COMMON_BARS = 1  # non-disjoint common bar-ends; missing/non-disjoint => BLOCKED
MIN_OLOW_STATES_PER_UNDERLYING = 1  # at least one constructible state per underlying
MIN_SURFACE_BARS_PER_UNDERLYING = 1  # at least one constructible surface bar per underlying

# Composed floor: both underlyings present + constructible toxicity states +
# constructible surface bars + cross-asset non-disjoint alignment. Not the EVAL-64 ladder floor.
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_oflow_states_per_underlying": int(MIN_OLOW_STATES_PER_UNDERLYING),
    "min_surface_bars_per_underlying": int(MIN_SURFACE_BARS_PER_UNDERLYING),
    "min_aligned_common_bars": int(MIN_ALIGNED_COMMON_BARS),
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-182 cross-asset order-flow toxicity x atm_iv interaction spillover floor: "
        "both underlyings (BTC, ETH) present, each with >= min_oflow_states_per_underlying "
        "constructible toxicity states and >= min_surface_bars_per_underlying constructible "
        "surface atm_iv bars on the coarsest grid, and >= min_aligned_common_bars "
        "non-disjoint common bar-ends where both signals coexist. Below the floor the "
        "campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval172_single_asset_atm_iv_forward_variance.py",
    "scripts/eval182_cross_asset_oflow_tox_atm_iv_interaction_spillover_forward_variance.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval182_cross_asset_oflow_tox_atm_iv_interaction_spillover_forward_variance.py "
    "tests/test_eval182_cross_asset_oflow_tox_atm_iv_interaction_spillover_forward_variance.py",
    "python3 -m pytest -q tests/test_eval182_cross_asset_oflow_tox_atm_iv_interaction_spillover_forward_variance.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval182_cross_asset_oflow_tox_atm_iv_interaction_spillover_forward_variance.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval182_cross_asset_oflow_tox_atm_iv_interaction_spillover_forward_variance.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
"EVAL182-CROSS-ASSET-OFLOW-TOX-ATM-IV-INTERACTION-SPILLOVER-FORWARD-VARIANCE",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Forward realized return variance target (transcribed verbatim from sealed
# EVAL-172; see also sealed EVAL-159/160 for the same target).
# ---------------------------------------------------------------------------
_forward_return_variance = e172._forward_return_variance


# ---------------------------------------------------------------------------
# Cross-asset order-flow toxicity + atm_iv surface alignment.
#
# Signal for bar k (OTHER underlying):
#   tox_z[k]    = e62.build_states(tox_signal="tox").signal_z[k]
#   atm_iv_z[k] = e71.build_surface_bars().atm_iv[k]  (surface bar, not term)
#   interaction[k] = tox_z[k] * atm_iv_z[k]
#
# Both are aligned to the common BTC-vs-ETH bar_ms grid, forward-filled causally,
# and expanding-z-scored end-of-bar k.
# ---------------------------------------------------------------------------
def build_cross_section(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """Align two underlyings' causal order-flow toxicity states and surface atm_iv
    bars on their common ``bar_ms`` grid.

    Returns ``{"maps": {inst: {bar_ms: {"tox_z": ..., "atm_iv": ...}}},
    "common": [bar_ms...], "bar_seconds": float}``. ``common`` is the sorted
    intersection of bar_ms keys present in *both* underlyings for BOTH signal
    sources.
    """
    tox_maps: Dict[str, Dict[int, Dict[str, Any]]] = {}
    surface_maps: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for inst, cap in captures.items():
        states = e62.build_states(cap, tox_signal="tox", bar_seconds=bar_seconds)
        tox_maps[inst] = {int(s["bar_ms"]): s for s in states}
        bars = e71.build_surface_bars(cap, bar_seconds=bar_seconds)
        surface_maps[inst] = {int(b["bar_open_ms"]): b for b in bars}
    insts = sorted(tox_maps)
    common_tox: List[int] = []
    common_surface: List[int] = []
    if len(insts) >= 2:
        common_tox = sorted(
            set.intersection(*[set(tox_maps[i]) for i in insts])
        )
        common_surface = sorted(
            set.intersection(*[set(surface_maps[i]) for i in insts])
        )
    # common = bar_ms where BOTH underlyings have BOTH a toxicity state and a surface bar
    common = sorted(set(common_tox) & set(common_surface))
    return {
        "tox_maps": tox_maps,
        "surface_maps": surface_maps,
        "common": common,
        "bar_seconds": float(bar_seconds),
        "underlyings": insts,
    }


def _closes_on_common(cs: Dict[str, Any], inst: str) -> List[float]:
    maps = cs["surface_maps"][inst]
    return [float(maps[int(m)]["close"]) for m in cs["common"]]


def _tox_on_common(cs: Dict[str, Any], inst: str) -> List[Optional[float]]:
    maps = cs["tox_maps"][inst]
    return [maps[int(m)].get("signal_z") for m in cs["common"]]


def _atm_iv_on_common(cs: Dict[str, Any], inst: str) -> List[Optional[float]]:
    maps = cs["surface_maps"][inst]
    return [maps[int(m)].get("atm_iv") for m in cs["common"]]


# ---------------------------------------------------------------------------
# Floor composition (both underlyings + constructible states + surface bars +
# non-disjoint cross-asset alignment)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any], *, bar_seconds: float) -> Dict[str, Any]:
    states = e62.build_states(capture, tox_signal="tox", bar_seconds=bar_seconds)
    bars = e71.build_surface_bars(capture, bar_seconds=bar_seconds)
    return {
        "n_tox_states": len(states),
        "n_surface_bars": len(bars),
        "ok": bool(
            len(states) >= int(MIN_OLOW_STATES_PER_UNDERLYING)
            and len(bars) >= int(MIN_SURFACE_BARS_PER_UNDERLYING)
        ),
    }


def campaign_floor(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: Optional[float] = None
) -> Dict[str, Any]:
    """Composed floor: both underlyings present, constructible toxicity states,
    constructible surface atm_iv bars, and non-disjoint cross-asset alignment."""
    bs = float(bar_seconds) if bar_seconds is not None else float(max(GRID_BAR_SECONDS))
    insts = sorted(captures)
    per_underlying = {
        i: _underlying_floor(captures[i], bar_seconds=bs) for i in insts
    }
    both_present = BASELINE in captures and RELATIVE in captures
    underlyings_ok = bool(
        both_present
        and all(per_underlying[i]["ok"] for i in (BASELINE, RELATIVE))
    )

    aligned_common_bars = 0
    if both_present:
        cs = build_cross_section(
            {BASELINE: captures[BASELINE], RELATIVE: captures[RELATIVE]},
            bar_seconds=bs,
        )
        aligned_common_bars = len(cs["common"])

    aligned_ok = aligned_common_bars >= int(MIN_ALIGNED_COMMON_BARS)
    return {
        "underlyings": insts,
        "per_underlying": per_underlying,
        "underlyings_ok": underlyings_ok,
        "aligned_common_bars": aligned_common_bars,
        "aligned_ok": aligned_ok,
        "checks": {
            "underlyings_ok": underlyings_ok,
            "aligned_ok": aligned_ok,
        },
        "ok": bool(underlyings_ok and aligned_ok),
    }


# ---------------------------------------------------------------------------
# Evaluation (cross-asset oflow tox x atm_iv interaction spillover -> forward realized return variance)
# ---------------------------------------------------------------------------
def _eval_one_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    target_inst: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    cs = build_cross_section(captures, bar_seconds=bar_seconds)
    n_common = len(cs["common"])
    other_inst = RELATIVE if target_inst == BASELINE else BASELINE

    other_tox = _tox_on_common(cs, other_inst)
    other_atm_iv = _atm_iv_on_common(cs, other_inst)

    # Interaction signal: tox_z * atm_iv_z (element-wise, None -> 0.0)
    other_interaction: List[Optional[float]] = []
    for tz, aiv in zip(other_tox, other_atm_iv):
        if tz is None or aiv is None:
            other_interaction.append(None)
        else:
            other_interaction.append(float(tz) * float(aiv))

    # Forward realized return of the TARGET underlying on the common grid.
    target_closes = _closes_on_common(cs, target_inst)
    fwd = _forward_return_variance(
        [{"close": c} for c in target_closes], horizon_bars
    )

    sig_filled = e71._forward_fill(other_interaction)
    sig_z = e61.expanding_zscore(sig_filled, ZWINDOW)

    xs: List[float] = []
    ys: List[float] = []
    n_fwd = len(fwd)
    for k in range(n_common):
        if k >= n_fwd:
            continue
        y = fwd[k]
        if y is None:
            continue
        xs.append(float(sig_z[k]) if k < len(sig_z) else 0.0)
        ys.append(float(y))

    n_pairs = len(xs)
    base = {
        "target_underlying": target_inst,
        "signal_underlying": other_inst,
        "signal": SURFACE_SIGNAL,
        "target": TARGET,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_common_bars": n_common,
        "n_pairs": n_pairs,
    }
    if n_pairs < int(MIN_USABLE_PAIRS_PER_CONFIG):
        base.update({
            "spearman_ic": float("nan"),
            "permutation_p": 1.0,
            "bootstrap_ci": [float("nan"), float("nan"), float("nan")],
            "pass": False,
            "reason": "insufficient_pairs",
        })
        return base

    ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED)
    passed = bool(ic > 0.0 and perm_p < 0.05 and ci_lo > 0.0)
    base.update({
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_median": med,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "pass": passed,
        "reason": "ok" if passed else "gate_fail",
    })
    return base


# ---------------------------------------------------------------------------
# Capture selection / orchestration
# ---------------------------------------------------------------------------
def _select_captures(capture_dir: str) -> List[Dict[str, Any]]:
    all_caps = e61._capture_inventory(capture_dir)
    best: Dict[str, Dict[str, Any]] = {}
    for c in all_caps:
        inst = c.get("underlying", "UNKNOWN")
        score = len(c.get("option_trades", []) or [])
        prev = best.get(inst)
        if prev is None or score > len(prev.get("option_trades", []) or []):
            best[inst] = c
    order = [k for k in ("BTC", "ETH") if k in best] + [k for k in sorted(best) if k not in ("BTC", "ETH")]
    return [best[k] for k in order]


def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-182",
        "title": "Cross-asset options order-flow toxicity x atm_iv surface interaction spillover "
                 "(other asset's tox_z * atm_iv_z) -> forward own-asset realized return variance "
                 "predictiveness (Spearman rank IC)",
        "extends": "EVAL-176 (cross-asset atm_iv -> realized return variance) + "
                   "EVAL-159 (cross-asset order-flow toxicity -> realized return variance) + "
                   "EVAL-180 (cross-asset order-flow imbalance x atm_iv interaction -> realized return variance) + "
                   "EVAL-151 (cross-asset order-flow toxicity x atm_iv interaction -> forward signed return mean) + "
                   "EVAL-71 (surface atm_iv verbatim) + EVAL-62 (toxicity verbatim) + "
                   "EVAL-77 (cross-asset alignment) + EVAL-172 (forward realized return variance "
                   "target verbatim) + EVAL-65 (permutation / bootstrap inference); "
                   "distinct cell: interaction spillover -> forward realized return variance",
        "supersedes": "nothing -- complements EVAL-176 (atm_iv alone), EVAL-159 (toxicity alone), "
                      "EVAL-180 (imbalance x atm_iv interaction); no traded-form claim",
        "capture_dir": str(capture_dir),
        "surface_signal": SURFACE_SIGNAL,
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "spillover_signal": "signal_k = tox_z[OTHER](k) * atm_iv_z[OTHER](k)  (interaction of "
                                "the other asset's order-flow toxicity z and near-ATM IV z)",
        },
        "signal": "causal per-bar interaction of the OTHER underlying's z-scored options order-flow "
                  "toxicity and near-ATM implied-vol level (e62.build_states tox_signal='tox' "
                  "x e71.build_surface_bars atm_iv — SURFACE bar, not the term bar), aligned to the "
                  "common BTC-vs-ETH bar grid, forward-filled and expanding-zscored end-of-bar k "
                  "(reused e71._forward_fill / e61.expanding_zscore)",
        "target_detail": "forward realized return variance = mean((r - mean(r))**2) over "
                         "the TARGET underlying's next H perp log returns (strictly after the "
                         "decision at bar k, r_i=log(close_i/close_{i-1}) over i in k+1..k+H); "
                         "transcribed verbatim from sealed EVAL-172",
        "statistic": "Spearman rank correlation IC = rho(other_interaction_z_k, own_variance_k); "
                     "directional permutation H1: IC>0 (higher other-asset order-flow toxicity x "
                     "atm_iv interaction -> higher forward realized return variance on the target)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle target series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
            "min_aligned_common_bars": int(MIN_ALIGNED_COMMON_BARS),
        },
        "go_bar": (
            "GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, "
            "directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and "
            "pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses already-acquired real on-disk three-way captures (option trades "
                    "with direction + IV + perp candles); no new acquisition, no network; "
                    "e62.build_states(tox_signal='tox') constructibility verified on "
                    "all three data/raw/eval61 tapes (289 states each); surface atm_iv via "
                    "EVAL-71 build_surface_bars on the same tapes",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval182(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL182-CROSS-ASSET-OFLOW-TOX-ATM-IV-INTERACTION-SPILLOVER-FORWARD-VARIANCE",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    selected = _select_captures(str(capture_dir_abs))
    captures = {str(c.get("underlying")): c for c in selected}

    floor = campaign_floor(captures, bar_seconds=max(GRID_BAR_SECONDS))
    floor_ok = bool(len(captures) >= int(FLOOR["min_underlyings"]) and floor["ok"])

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for target_inst in (BASELINE, RELATIVE):
        for bar_s in GRID_BAR_SECONDS:
            for horizon in FORWARD_HORIZONS_BARS:
                try:
                    res = _eval_one_config(
                        captures,
                        target_inst=target_inst,
                        bar_seconds=bar_s,
                        horizon_bars=horizon,
                    )
                except BaseException as exc:  # noqa: BLE001
                    other_inst = RELATIVE if target_inst == BASELINE else BASELINE
                    errors.append(
                        f"{target_inst}<-{other_inst}::{SURFACE_SIGNAL}::bar{bar_s}::h{horizon}: {exc!r}"
                    )
                    continue
                per_config.append(res)

    p_values = {
        f"{r['target_underlying']}<-{r['signal_underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}": _finite(r.get("permutation_p"), 1.0)
        for r in per_config if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_target: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_target.setdefault(r.get("target_underlying", "?"), []).append(r)

    target_summary: List[Dict[str, Any]] = []
    for inst, rows in by_target.items():
        valid = [r for r in rows if r.get("n_pairs", 0) > 0]
        best = max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9)) if valid else None
        pass_configs_t: List[str] = []
        for r in valid:
            key = (
                f"{r['target_underlying']}<-{r['signal_underlying']}::{r['signal']}"
                f"::bar{r['bar_seconds']}::h{r['horizon_bars']}"
            )
            if r.get("pass") and key in rejected:
                pass_configs_t.append(key)
        target_summary.append({
            "target_underlying": inst,
            "signal_underlying": RELATIVE if inst == BASELINE else BASELINE,
            "n_configs": len(rows),
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal_underlying']}->{best['target_underlying']}::"
                f"{best['signal']}::bar{best['bar_seconds']}::h{best['horizon_bars']}"
                if best else "n/a"
            ),
            "n_pass": len(pass_configs_t),
            "pass_configs": pass_configs_t,
            "any_pass": bool(pass_configs_t),
        })

    all_pass = bool(target_summary) and all(s["any_pass"] for s in target_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_182_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE"
        if floor_ok else "EVAL_182_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free Spearman rank IC between the causal cross-asset options order-flow "
            "toxicity x atm_iv interaction spillover (other asset's level product) and forward "
            "own-asset realized return variance on real captures"
            if floor_ok else "capture below the composed EVAL-182 floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_target": target_summary,
        "pooled": {"bh_fdr": bh, "all_targets_pass": all_pass, "campaign_state": campaign_state},
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
    p = report.get("protocol", {})
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report.get("generated_at"),
        "task": report.get("task"),
        "hypothesis": (
            "The causal options order-flow toxicity x near-ATM implied-vol interaction level of "
            "the OTHER underlying (cross-asset interaction spillover) has a positive monotone "
            "(Spearman rank) relationship with the subsequent forward realized return variance of "
            "the target underlying, independent of any trading wrapper; tested on real on-disk "
            "captures at the composed EVAL-182 floor."
        ),
        "extends": p.get("extends"),
        "protocol": p,
        "capture_dir": report.get("capture_dir"),
        "floor": report.get("floor", dict(FLOOR)),
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r.get("protocol", {})
    fl = p.get("floor", FLOOR)
    cs = p.get("cross_section", {})
    lines = [
        f"# {PREREG_ID} — cross-asset oflow tox x atm_iv interaction spillover -> forward realized return variance (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Hypothesis: {r.get('hypothesis')}",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Extends: {p.get('extends')}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Cross-asset spillover: baseline `{cs.get('baseline')}`, relative `{cs.get('relative')}`",
        f"- Spillover signal: {cs.get('spillover_signal')}",
        f"- Signal: {p.get('surface_signal')}",
        f"- Target: {p.get('target')} — {p.get('target_detail')}",
        f"- Bar grid (s): {p.get('bar_seconds_grid')}",
        f"- Forward horizons (bars): {p.get('forward_horizons_bars')}",
        f"- Signal detail: {p.get('signal')}",
        f"- Statistic: {p.get('statistic')}",
        f"- Stats: perm {p.get('stats', {}).get('permutation_perms')} / "
        f"bootstrap {p.get('stats', {}).get('bootstrap_resamples')} block {p.get('stats', {}).get('bootstrap_block')} / "
        f"BH-FDR alpha {p.get('stats', {}).get('fdr_alpha')} / seed {p.get('stats', {}).get('seed')} / "
        f"zwindow {p.get('stats', {}).get('zwindow')} / "
        f"min usable pairs {p.get('stats', {}).get('min_usable_pairs_per_config')} / "
        f"min aligned common bars {p.get('stats', {}).get('min_aligned_common_bars')}",
        "",
        "## Pre-declared GO bar",
        "",
        str(p.get("go_bar")),
        "",
        "## Pre-registered composed floor (both underlyings + toxicity states + surface bars + alignment)",
        "",
        f"- {fl.get('note')}",
        f"- Min underlyings: {fl.get('min_underlyings')}",
        f"- Min aligned common bars (coarsest grid): {fl.get('min_aligned_common_bars')}",
        f"- Min usable pairs per config: {fl.get('min_usable_pairs_per_config')}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r.get("campaign_floor", {})
    lines = [
        f"# {r['report_id']} — cross-asset oflow tox x atm_iv interaction spillover -> forward realized return variance (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Verdict detail: {r.get('verdict_detail')}",
        f"- Floor OK: {r.get('floor_ok')} (underlyings {', '.join(r.get('underlyings', []))})",
        f"- Aligned common bars: {fl.get('aligned_common_bars')}",
        "",
        "## Per-underlying order-flow + surface floor",
        "",
        "| underlying | floor ok | n toxicity states | n surface atm_iv bars |",
        "|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        lines.append(
            f"| {inst} | {u.get('ok')} | {u.get('n_tox_states')} | {u.get('n_surface_bars')} |"
        )
    lines += ["", "## Per-target (best config by Spearman IC)", "",
              "| target <- signal | configs | best IC | best config | n pass | any pass |",
              "|---|---|---|---|---|---|"]
    for s in r.get("per_target", []):
        lines.append(
            f"| {s['signal_underlying']}->{s['target_underlying']} | {s['n_configs']} | "
            f"{s['best_ic']:.4f} | {s['best_config']} | {s['n_pass']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r.get('pooled', {}).get('bh_fdr', {}).get('rejected')}",
              f"- All targets pass: {r.get('pooled', {}).get('all_targets_pass')}",
              f"- Campaign state: {r.get('pooled', {}).get('campaign_state')}"]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r.get("generated_at", _utc_now_iso()),
        "task": r.get("task"),
        "verdict": "BLOCKED",
        "verdict_detail": "capture below the composed EVAL-182 floor (missing/non-disjoint); no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "campaign_floor": r.get("campaign_floor", {}),
        "floor": r.get("floor", dict(FLOOR)),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — cross-asset oflow tox x atm_iv interaction spillover -> forward realized return variance: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "The capture does not meet the composed EVAL-182 floor; no predictiveness "
        "verdict is emitted (never a NO-GO).",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-182: causal cross-asset options order-flow toxicity x atm_iv interaction spillover -> forward realized return variance predictiveness (Spearman rank IC)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL182-CROSS-ASSET-OFLOW-TOX-ATM-IV-INTERACTION-SPILLOVER-FORWARD-VARIANCE")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval182(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(), "task": args.task_label,
                "capture_dir": args.capture_dir, "underlyings": [],
                "campaign_floor": {}, "floor": dict(FLOOR), "floor_ok": False,
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_target": report.get("per_target"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
