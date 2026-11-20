#!/usr/bin/env python3
"""EVAL-141: does an **equal-weight z-score composite** of the two surviving
cross-asset options spillover signals — the OTHER underlying's near-ATM
``atm_iv`` level (EVAL-114 leg) and its near-minus-far ATM IV ``term_ratio =
IV(near)/IV(far) - 1`` (EVAL-139 leg) — predict the subsequent **forward
realized return skewness** of the target underlying better than either leg
alone? A distinct, on-charter, runnable-**now** composite predictiveness cell
on the real on-disk captures.

Why this rung exists (the next mandatory heavy work after EVAL-140 seals)
-----------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. EVAL-70..140 are sealed; a
green driver plus all-sealed is **not** session completion. The pre-registered
build queue (``research_state/durable_handoff.md``) makes EVAL-141 the next
mandatory build.

EVAL-114 measured cross-asset ``atm_iv`` spillover -> forward realized return
skewness (GO CONFIRMED, BTC 0.4039 / ETH 0.1173). EVAL-139 measured cross-asset
``term_ratio`` spillover -> forward realized return skewness (GO CONFIRMED,
BTC 0.2613 / ETH 0.4878, 7 BH-FDR rejections). Both legs survive, but nothing
tested whether a **composite** of the two carries *more* monotone information
about the target's forward return skewness than the better single leg. That is
the genuinely distinct, on-charter cell tested here.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
-------------------------------------------------------------------------------
For each target underlying (BTC, ETH), each bar grid ``{60s, 300s}`` and each
forward horizon ``H`` bars:

* the OTHER underlying's near-ATM ``atm_iv`` is reconstructed exactly as EVAL-71
  (``e71.build_surface_bars``) and its ``term_ratio = IV(near)/IV(far) - 1``
  exactly as EVAL-74 (``e74._term_bars``), both aligned to the common BTC-vs-ETH
  bar grid, causally forward-filled (``e71._forward_fill``) and expanding
  z-scored end-of-bar ``k`` (``e61.expanding_zscore``, ``e62.ZWINDOW``);
* the **composite** signal is the equal-weight mean of the two z-scores,
  ``0.5 * z(atm_iv_other) + 0.5 * z(term_ratio_other)``;
* the target is the forward **realized return skewness** of the *target*
  underlying over bars ``k+1..k+H`` (third standardized moment, EVAL-85 forward
  window convention ``lr[k:k+h]``), transcribed verbatim from EVAL-109/112/113/
  116.

Compute Spearman rank ``IC = rho(composite_z_k, own_skew_{k+1..k+H})`` with the
sealed EVAL-65 directional permutation and block bootstrap (H1: ``IC > 0``). A
composite config **passes** only if ``IC > 0``, directional permutation
``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH:** (a) at least one composite config passes
AND is BH-FDR-rejected in the pooled composite family; and (b) the composite's
best IC strictly **beats each leg's best IC** (the best of the ``atm_iv``-only
and ``term_ratio``-only configs, computed in the same run as descriptive
comparators). Else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-141 consumes both underlyings' trade-tape IV surfaces (``atm_iv`` needs
near-ATM trades; ``term_ratio`` needs >= 2 near-ATM expiries with trades) and
both perp series, so it composes two honestly pre-registered floors and requires
both:

* the sealed **EVAL-71 surface floor verbatim** for EACH underlying (>=
  ``min_option_trades_per_underlying``=1000 option trades, >=
  ``min_near_atm_option_trades_per_underlying``=400 near-ATM trades, >=
  ``min_perp_candles_per_underlying``=1000 perp candles, >=
  ``min_perp_span_seconds_per_underlying``=82000s perp span); and
* a cross-asset alignment floor: at least ``MIN_ALIGNED_COMMON_BARS`` bar-ends
  where both underlyings carry a causal near-ATM surface bar on the coarsest
  grid (>= 200).

Neither is weakened. Below the composed floor it seals
``EVAL_141_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-114 measured cross-asset
``atm_iv`` spillover -> forward return skewness; EVAL-139 measured cross-asset
``term_ratio`` spillover -> forward return skewness. EVAL-141 measures whether
the **equal-weight composite** of those two spillover signals beats either leg
alone on the same real captures, reusing all sealed signal/target reconstructions
and the EVAL-65 inference verbatim.

Seals ``EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/65/71/74 primitives verbatim (no forks, no src).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED"
PREREG_ID = "EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_BLOCKED"

# Composite of the two surviving cross-asset spillover GOs:
#   * ``atm_iv``     — near-ATM IV level (EVAL-114 leg, e71.build_surface_bars)
#   * ``term_ratio`` — near-minus-far ATM IV ratio (EVAL-139 leg, e74._term_bars)
ATM_LEG: str = "atm_iv"
TERM_LEG: str = "term_ratio"
COMPOSITE_SIGNAL: str = "composite_atm_iv_term_ratio"
SURFACE_SIGNALS: Tuple[str, ...] = (ATM_LEG, TERM_LEG)
TARGET = "realized_return_skewness"

# Pre-registered grid (cross-asset spillover x bar grid x forward horizons -> 6
# configs per leg/composite per target underlying, 12 composite configs total).
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# The cross-asset spillover is BTC <-> ETH. For target BTC the signal is ETH's
# surface state and vice versa.
BASELINE = "BTC"
RELATIVE = "ETH"

# Reuse EVAL-74 term-structure constants (their window/ATM band are identical to
# EVAL-71), EVAL-71 surface constants and EVAL-65/62 statistics verbatim.
SIGNAL_WINDOW_SECONDS: float = e74.SIGNAL_WINDOW_SECONDS
ATM_BAND: float = e74.ATM_BAND
MIN_EXPIRY_TRADES: int = e74.MIN_EXPIRY_TRADES

PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 120
MIN_ALIGNED_COMMON_BARS = 200

# Composed floor: sealed EVAL-71 surface floor (per underlying) + cross-asset
# alignment. Not the EVAL-64 ladder floor.
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
    "min_aligned_common_bars": int(MIN_ALIGNED_COMMON_BARS),
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "Reuses the sealed EVAL-71 surface floor verbatim "
        "(min_option_trades_per_underlying=1000, "
        "min_near_atm_option_trades_per_underlying=400, "
        "min_perp_candles_per_underlying=1000, "
        "min_perp_span_seconds_per_underlying=82000s), applied to BOTH BTC and ETH, "
        "plus a cross-asset alignment floor (>= min_aligned_common_bars bar-ends "
        "where both underlyings carry a causal near-ATM surface bar on the coarsest "
        "grid). Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT "
        "the EVAL-64 ladder floor."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
    "scripts/eval141_composite_atm_iv_term_ratio_spillover_forward_return_skewness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval141_composite_atm_iv_term_ratio_spillover_forward_return_skewness.py "
    "tests/test_eval141_composite_atm_iv_term_ratio_spillover_forward_return_skewness.py",
    "python3 -m pytest -q tests/test_eval141_composite_atm_iv_term_ratio_spillover_forward_return_skewness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval141_composite_atm_iv_term_ratio_spillover_forward_return_skewness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval141_composite_atm_iv_term_ratio_spillover_forward_return_skewness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL141-COMPOSITE-ATM-IV-TERM-RATIO-SPILLOVER-FORWARD-RETURN-SKEWNESS",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Forward realized return skewness target (third standardized moment).
#
# Transcribed verbatim from sealed EVAL-109/111/112/113 (EVAL-85 forward-window
# convention: ``lr[k : k+h]``). Strictly distinct from the forward RV level
# (EVAL-71/74), signed mean (EVAL-101/102/104), quantile-spread tail asymmetry
# (EVAL-85/87/99/100), and vol-of-vol (EVAL-95/97).
# ---------------------------------------------------------------------------
def _forward_return_skewness(
    bars: Sequence[Dict[str, Any]], horizon_bars: int
) -> List[Optional[float]]:
    """Forward realized return skewness over the next ``H`` bars.

    ``r_i = log(close_i / close_{i-1})`` over bars ``k+1..k+H``;
    ``skew = m3 / m2**1.5`` with ``m_j = mean((r - mean(r))**j)``. Windows with
    non-positive variance (or degenerate H < 3) yield ``None`` so they are
    dropped from the pair set. Returns a list indexed by bar ``k``; incomplete
    tail entries are omitted (shorter list).
    """
    closes = [float(b["close"]) for b in bars]
    lr = (
        [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)]
        if len(closes) >= 2
        else []
    )
    h = int(horizon_bars)
    out: List[Optional[float]] = []
    for k in range(0, len(lr) - h + 1):
        seg = lr[k:k + h]
        if len(seg) < 3:
            out.append(None)
            continue
        mu = sum(seg) / len(seg)
        m2 = sum((v - mu) ** 2 for v in seg) / len(seg)
        if m2 <= 0.0 or not math.isfinite(m2):
            out.append(None)
            continue
        m3 = sum((v - mu) ** 3 for v in seg) / len(seg)
        val = m3 / (m2 ** 1.5)
        out.append(float(val) if math.isfinite(val) else None)
    return out


# ---------------------------------------------------------------------------
# Cross-asset surface alignment. Each underlying carries BOTH the EVAL-71
# near-ATM ``atm_iv`` surface bar and the EVAL-74 near-minus-far ``term_ratio``
# term-structure bar; the common grid is the intersection of their bar opens.
# ---------------------------------------------------------------------------
def build_cross_section(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """Align two underlyings' causal surface + term-structure bars on one grid.

    Returns ``{"maps": {inst: {bar_open_ms: surface_bar}}, "term_maps": {inst:
    {bar_open_ms: term_bar}}, "common": [bar_open_ms...], "bar_seconds": float}``.
    ``common`` is the sorted intersection of bar-open buckets present in *all*
    maps (``e71.build_surface_bars`` and ``e74._term_bars`` derive from the same
    perp candles, so the intersection is the shared observed bar set).
    """
    maps: Dict[str, Dict[int, Dict[str, Any]]] = {}
    term_maps: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for inst, cap in captures.items():
        bars = e71.build_surface_bars(cap, bar_seconds=bar_seconds)
        maps[inst] = {int(b["bar_open_ms"]): b for b in bars}
        term_bars = e74._term_bars(cap, bar_seconds=bar_seconds)
        term_maps[inst] = {int(b["bar_open_ms"]): b for b in term_bars}

    insts = sorted(maps)
    if len(insts) < 2:
        common: List[int] = []
    else:
        keysets = [set(maps[i]) for i in insts] + [set(term_maps[i]) for i in insts]
        common = sorted(set.intersection(*keysets))
    return {
        "maps": maps,
        "term_maps": term_maps,
        "common": common,
        "bar_seconds": float(bar_seconds),
        "underlyings": insts,
    }


def _closes_on_common(cs: Dict[str, Any], inst: str) -> List[float]:
    maps = cs["maps"][inst]
    return [float(maps[int(m)]["close"]) for m in cs["common"]]


def _signal_on_common(cs: Dict[str, Any], inst: str, signal: str) -> List[Optional[float]]:
    src = cs["term_maps"][inst] if signal == TERM_LEG else cs["maps"][inst]
    return [src[int(m)].get(signal) for m in cs["common"]]


# ---------------------------------------------------------------------------
# Floor composition (reuse EVAL-71 surface floor verbatim + alignment).
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    return e71._underlying_surface_floor(capture)


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
            cs = build_cross_section(
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
# Evaluation (composite cross-asset spillover -> forward realized return skewness)
# ---------------------------------------------------------------------------
def _zscore_pair(
    cs: Dict[str, Any], other_inst: str
) -> Tuple[List[float], List[float]]:
    """Return (z(atm_iv_other), z(term_ratio_other)), each causal expanding-zscored."""
    atm_filled = e71._forward_fill(_signal_on_common(cs, other_inst, ATM_LEG))
    term_filled = e71._forward_fill(_signal_on_common(cs, other_inst, TERM_LEG))
    z_atm = e61.expanding_zscore(atm_filled, ZWINDOW)
    z_term = e61.expanding_zscore(term_filled, ZWINDOW)
    return z_atm, z_term


def _score(
    xs: Sequence[float], ys: Sequence[float]
) -> Dict[str, Any]:
    """Sealed EVAL-65 directional IC + permutation + block bootstrap."""
    ic, perm_p = e65._perm_p_ic(list(xs), list(ys), PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(
        list(xs), list(ys), BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED
    )
    passed = bool(ic > 0.0 and perm_p < 0.05 and ci_lo > 0.0)
    return {
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_median": med,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "pass": passed,
    }


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

    z_atm, z_term = _zscore_pair(cs, other_inst)
    composite = [0.5 * float(a) + 0.5 * float(t) for a, t in zip(z_atm, z_term)]

    # Forward return skewness of the TARGET underlying on the common grid.
    target_closes = _closes_on_common(cs, target_inst)
    fwd = _forward_return_skewness(
        [{"close": c} for c in target_closes], horizon_bars
    )

    n_fwd = len(fwd)
    ys: List[float] = []
    idx: List[int] = []
    for k in range(n_common):
        if k >= n_fwd:
            continue
        y = fwd[k]
        if y is None:
            continue
        ys.append(float(y))
        idx.append(k)

    n_pairs = len(ys)
    base = {
        "target_underlying": target_inst,
        "signal_underlying": other_inst,
        "signal": COMPOSITE_SIGNAL,
        "legs": list(SURFACE_SIGNALS),
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
            "leg_ic": {ATM_LEG: float("nan"), TERM_LEG: float("nan")},
        })
        return base

    comp = _score([composite[k] for k in idx], ys)
    leg_ic: Dict[str, float] = {}
    for leg, series in ((ATM_LEG, z_atm), (TERM_LEG, z_term)):
        leg_ic[leg] = float(
            e65._perm_p_ic([series[k] for k in idx], ys, PERMUTATION_PERMS, SEED)[0]
        )
    base.update({
        "spearman_ic": comp["spearman_ic"],
        "permutation_p": comp["permutation_p"],
        "bootstrap_median": comp["bootstrap_median"],
        "bootstrap_ci": comp["bootstrap_ci"],
        "pass": comp["pass"],
        "reason": "ok" if comp["pass"] else "gate_fail",
        "leg_ic": leg_ic,
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
    order = [k for k in ("BTC", "ETH") if k in best] + [
        k for k in sorted(best) if k not in ("BTC", "ETH")
    ]
    return [best[k] for k in order]


def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-141",
        "title": "Composite cross-asset spillover (other asset's near-ATM atm_iv + "
                 "term_ratio, equal-weight z-score) -> forward own-asset realized "
                 "return skewness predictiveness (Spearman rank IC) vs each leg alone",
        "extends": "EVAL-114 (cross-asset atm_iv spillover -> forward return skewness) + "
                   "EVAL-139 (cross-asset term_ratio spillover -> forward return skewness) "
                   "+ EVAL-71 (atm_iv surface bar + surface floor verbatim) + "
                   "EVAL-74 (term_ratio reconstruction _term_bars verbatim) + "
                   "EVAL-65/62 (inference verbatim); distinct cell: equal-weight z-score "
                   "composite of the two surviving spillover GOs must beat each leg alone",
        "supersedes": "nothing -- composite comparison only; no traded-form claim",
        "capture_dir": str(capture_dir),
        "surface_signals": list(SURFACE_SIGNALS),
        "composite_signal": COMPOSITE_SIGNAL,
        "composite_weights": {"atm_iv": 0.5, "term_ratio": 0.5},
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "min_expiry_trades": int(MIN_EXPIRY_TRADES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "spillover_signal": "composite_k = 0.5*z(atm_iv[OTHER](k)) + "
                                "0.5*z(term_ratio[OTHER](k))  (equal-weight z-score composite)",
            "legs": {
                ATM_LEG: "near-ATM IV level of the OTHER underlying (e71.build_surface_bars)",
                TERM_LEG: "near-minus-far ATM IV ratio of the OTHER underlying (e74._term_bars term_ratio)",
            },
        },
        "signal": "equal-weight z-score composite of the OTHER underlying's causal per-bar "
                  "near-ATM atm_iv level and near-minus-far ATM IV term_ratio, aligned to "
                  "the common BTC-vs-ETH bar grid (build_cross_section), forward-filled and "
                  "expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)",
        "target_detail": "forward realized return skewness = m3 / m2**1.5 over the TARGET "
                         "underlying's next H perp log returns (strictly after the decision "
                         "at bar k, lr[k:k+h]); third standardized moment, transcribed verbatim "
                         "from sealed EVAL-109/112/113/116",
        "statistic": "Spearman rank correlation IC = rho(composite_z_k, own_skew_k); "
                     "directional permutation H1: IC>0 (wider other-asset near/far-IV "
                     "surface -> more right-skewed forward returns on the target)",
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
            "GO only if, on BOTH BTC and ETH: (a) at least one composite config has "
            "Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI "
            "lower > 0 and is BH-FDR-rejected in the pooled composite family; AND (b) the "
            "composite's best IC strictly beats each leg's best IC (atm_iv-only and "
            "term_ratio-only, computed in the same run as descriptive comparators). Else "
            "NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses already-acquired real on-disk three-way captures (option trades "
                    "with iv/strike/expiry + perp candles); no new acquisition, no network",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval141(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL141-COMPOSITE-ATM-IV-TERM-RATIO-SPILLOVER-FORWARD-RETURN-SKEWNESS",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    selected = _select_captures(str(capture_dir_abs))
    captures = {str(c.get("underlying")): c for c in selected}

    floor = campaign_floor(captures)
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
                        f"{target_inst}<-{other_inst}::{COMPOSITE_SIGNAL}"
                        f"::bar{bar_s}::h{horizon}: {exc!r}"
                    )
                    continue
                per_config.append(res)

    p_values = {
        f"{r['target_underlying']}<-{r['signal_underlying']}::{r['signal']}"
        f"::bar{r['bar_seconds']}::h{r['horizon_bars']}": _finite(r.get("permutation_p"), 1.0)
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
        best_ic = _finite(best.get("spearman_ic"), 0.0) if best else 0.0
        leg_best: Dict[str, float] = {}
        for leg in SURFACE_SIGNALS:
            vals = [
                _finite((r.get("leg_ic") or {}).get(leg), float("nan")) for r in valid
            ]
            vals = [v for v in vals if math.isfinite(v)]
            leg_best[leg] = max(vals) if vals else float("nan")
        beats_legs = bool(
            valid
            and all(
                math.isfinite(leg_best[leg]) and best_ic > leg_best[leg]
                for leg in SURFACE_SIGNALS
            )
        )
        target_summary.append({
            "target_underlying": inst,
            "signal_underlying": RELATIVE if inst == BASELINE else BASELINE,
            "n_configs": len(rows),
            "best_ic": best_ic,
            "best_config": (
                f"{best['signal_underlying']}->{best['target_underlying']}::"
                f"{best['signal']}::bar{best['bar_seconds']}::h{best['horizon_bars']}"
                if best else "n/a"
            ),
            "leg_best_ic": leg_best,
            "beats_both_legs": beats_legs,
            "n_pass": len(pass_configs_t),
            "pass_configs": pass_configs_t,
            "any_pass": bool(pass_configs_t),
        })

    all_pass = bool(target_summary) and all(s["any_pass"] for s in target_summary)
    all_beat = bool(target_summary) and all(s["beats_both_legs"] for s in target_summary)
    go = bool(floor_ok and all_pass and all_beat and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS"
        if floor_ok else "EVAL_141_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free Spearman rank IC between the equal-weight z-score composite of "
            "the cross-asset atm_iv and term_ratio spillovers and forward own-asset realized "
            "return skewness on real captures; GO additionally requires the composite to "
            "beat each single-leg best IC on both underlyings"
            if floor_ok else "capture below the composed EVAL-71 + alignment floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_target": target_summary,
        "pooled": {
            "bh_fdr": bh,
            "all_targets_pass": all_pass,
            "all_targets_beat_both_legs": all_beat,
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
    p = report.get("protocol", {})
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report.get("generated_at"),
        "task": report.get("task"),
        "hypothesis": (
            "An equal-weight z-score composite of the OTHER underlying's causal near-ATM "
            "atm_iv level and near-minus-far ATM IV term_ratio (cross-asset spillover) has a "
            "positive monotone (Spearman rank) relationship with the subsequent forward "
            "realized return skewness (third standardized moment) of the target underlying, "
            "and that relationship is strictly stronger than either single leg's best IC, "
            "tested on real on-disk captures at the composed EVAL-71 + alignment floor."
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
        f"# {PREREG_ID} — composite cross-asset spillover -> forward realized return skewness (Spearman rank IC)",
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
        f"- Composite weights: {p.get('composite_weights')}",
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
        "## Pre-registered composed floor (EVAL-71 both underlyings + alignment)",
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
        f"# {r['report_id']} — composite cross-asset spillover -> forward realized return skewness (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Verdict detail: {r.get('verdict_detail')}",
        f"- Floor OK: {r.get('floor_ok')} (underlyings {', '.join(r.get('underlyings', []))})",
        f"- Aligned common bars by grid: {fl.get('aligned_common_bars_by_grid')}",
        "",
        "## Per-underlying EVAL-71 surface floor",
        "",
        "| underlying | surface floor ok | option trades | near-ATM | perp candles | span (s) |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        s = u.get("surface_floor", {}) if isinstance(u, dict) else {}
        lines.append(
            f"| {inst} | {u.get('surface_floor_ok')} | {s.get('n_option_trades')} | "
            f"{s.get('n_near_atm_option_trades')} | {s.get('n_perp_candles')} | "
            f"{s.get('perp_span_seconds')} |"
        )
    lines += [
        "",
        "## Per-target (composite best config vs single-leg best IC)",
        "",
        "| target <- signal | configs | composite best IC | atm_iv leg best | term_ratio leg best | beats both legs | n pass | any pass | best config |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in r.get("per_target", []):
        lb = s.get("leg_best_ic", {})
        lines.append(
            f"| {s['signal_underlying']}->{s['target_underlying']} | {s['n_configs']} | "
            f"{s['best_ic']:.4f} | {lb.get(ATM_LEG, float('nan')):.4f} | "
            f"{lb.get(TERM_LEG, float('nan')):.4f} | {s['beats_both_legs']} | "
            f"{s['n_pass']} | {s['any_pass']} | {s['best_config']} |"
        )
    lines += [
        "",
        "## Pooled",
        "",
        f"- BH-FDR rejected: {r.get('pooled', {}).get('bh_fdr', {}).get('rejected')}",
        f"- All targets pass: {r.get('pooled', {}).get('all_targets_pass')}",
        f"- All targets beat both legs: {r.get('pooled', {}).get('all_targets_beat_both_legs')}",
        f"- Campaign state: {r.get('pooled', {}).get('campaign_state')}",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r.get("generated_at", _utc_now_iso()),
        "task": r.get("task"),
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
    fl = r.get("campaign_floor", {})
    lines = [
        f"# {BLOCKED_ID} — composite cross-asset spillover -> forward realized return skewness: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "The capture does not meet the composed EVAL-71 + cross-asset alignment "
        "floor; no predictiveness verdict is emitted (never a NO-GO).",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-141: composite cross-asset atm_iv + term_ratio spillover -> "
                    "forward realized return skewness predictiveness (Spearman rank IC)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label",
        default="EVAL141-COMPOSITE-ATM-IV-TERM-RATIO-SPILLOVER-FORWARD-RETURN-SKEWNESS",
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval141(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
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
