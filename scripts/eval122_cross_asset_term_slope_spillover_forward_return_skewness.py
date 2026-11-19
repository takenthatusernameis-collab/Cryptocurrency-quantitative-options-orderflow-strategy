#!/usr/bin/env python3
"""EVAL-122: does the **cross-asset term-structure slope spillover** (the OTHER
underlying's ``term_slope``) predict the subsequent **forward realized return
skewness** of the target underlying? A distinct, on-charter, runnable-**now**
predictiveness cell on the real on-disk three-way captures.

Why this rung exists (the next runnable-now heavy work after EVAL-121)
----------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The physics-independent
runnable-now line EVAL-70..121 is sealed. EVAL-114 tested the **cross-asset
``atm_iv`` spillover** -> forward realized return skewness (GO, BTC 0.4039 /
ETH 0.1173). It did **not** test the cross-asset *term-structure* spillover:
does ETH's near-minus-far ATM IV slope carry information about BTC's subsequent
return skewness (and vice versa)?

The genuinely distinct, on-charter, runnable-**now** cell tested here is: does
the causal near-minus-far ATM IV term slope of the *other* underlying at bar
``k`` carry monotone information about the target underlying's subsequent
**third standardized moment (skewness)** of its per-bar log returns over bars
``k+1..k+H``? It is **predictiveness only** — no traded-form or monetization
claim.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
-------------------------------------------------------------------------------
For each target underlying (BTC, ETH), each bar grid ``{60s, 300s}`` and each
forward horizon ``H`` bars:

* the causal term slope ``term_slope = IV(near expiry) - IV(far expiry)`` of the
  **other** underlying is reconstructed exactly as EVAL-113
  (``e74._term_bars``), aligned to the common BTC-vs-ETH bar grid
  (``build_cross_section``), forward-filled causally (``e71._forward_fill``) and
  expanding z-scored end-of-bar ``k`` (``e61.expanding_zscore``,
  ``e62.ZWINDOW``); and
* the target is the forward **realized return skewness** of the *target*
  underlying over bars ``k+1..k+H``, ``skew_k = m3 / m2**1.5`` with
  ``m_j = mean(r_i - mean(r))**j`` over ``r_i = log(close_i/close_{i-1})``,
  ``i in k+1..k+H`` (the EVAL-85 forward-window convention: ``lr[k:k+h]``),
  transcribed verbatim from EVAL-109/111/112/113. Windows with zero variance
  yield ``None``. A config needs at least ``MIN_USABLE_PAIRS_PER_CONFIG``
  usable pairs.

Compute Spearman rank ``IC = rho(other_term_slope_z_k, own_skew_{k+1..k+H})``
with the sealed EVAL-65 directional permutation and block bootstrap (H1:
``IC > 0`` — the other asset's steeper near-minus-far slope precedes more
right-skewed forward returns on the target). A config **passes** only if
``IC > 0``, directional permutation ``p < 0.05``, block-bootstrap 95% CI lower
``> 0``, and at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH and at least one config:** ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``,
and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-122 consumes both underlyings' trade-tape IV surfaces and both perp series,
so it composes two honestly pre-registered floors and requires both:

* the sealed **EVAL-71 surface floor verbatim** for EACH underlying (>=
  ``min_option_trades_per_underlying``=1000 option trades, >=
  ``min_near_atm_option_trades_per_underlying``=400 near-ATM trades, >=
  ``min_perp_candles_per_underlying``=1000 perp candles, >=
  ``min_perp_span_seconds_per_underlying``=82000s perp span); and
* a cross-asset alignment floor: at least ``MIN_ALIGNED_COMMON_BARS`` bar-ends
  where both underlyings carry a causal term slope on the coarsest grid
  (>= 200).

Neither is weakened. Below the composed floor it seals
``EVAL_122_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-114 measured the
cross-asset ``atm_iv`` level spillover -> forward *return skewness*; EVAL-113
measured single-asset ``term_slope`` -> forward *return skewness*; EVAL-74
measured single-asset term structure -> forward *RV level*. EVAL-122 measures
the **cross-asset** ``term_slope`` **spillover** (other asset's slope) -> **own
forward realized return skewness**, reusing all sealed signal/target
reconstructions and the EVAL-65 inference verbatim.

Seals ``EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION_<UTC>``
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
REPORT_ID = "EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED"
PREREG_ID = "EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_BLOCKED"

# Single surface signal (near-minus-far ATM IV slope, exactly EVAL-113's path).
SURFACE_SIGNAL: str = "term_slope"
TARGET = "realized_return_skewness"

# Pre-registered grid (cross-asset spillover x bar grid x forward horizons -> 6
# configs per target underlying, 12 total).
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# The cross-asset spillover is BTC <-> ETH. For target BTC the signal is ETH's
# term_slope and vice versa.
BASELINE = "BTC"
RELATIVE = "ETH"

# Reuse EVAL-74 term-structure constants, EVAL-71 surface constants and
# EVAL-65/62 statistics verbatim.
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
        "where both underlyings carry a causal term slope on the coarsest grid). "
        "Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the "
        "EVAL-64 ladder floor."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
    "scripts/eval122_cross_asset_term_slope_spillover_forward_return_skewness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval122_cross_asset_term_slope_spillover_forward_return_skewness.py "
    "tests/test_eval122_cross_asset_term_slope_spillover_forward_return_skewness.py",
    "python3 -m pytest -q tests/test_eval122_cross_asset_term_slope_spillover_forward_return_skewness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval122_cross_asset_term_slope_spillover_forward_return_skewness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval122_cross_asset_term_slope_spillover_forward_return_skewness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL122-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-SKEWNESS",
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
# Cross-asset term-slope alignment (mirror EVAL-114 build_cross_section, but
# using EVAL-74 term bars so ``term_slope`` is present).
# ---------------------------------------------------------------------------
def build_cross_section(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """Align two underlyings' causal term-structure bars on their common grid.

    Returns ``{"maps": {inst: {bar_open_ms: bar}}, "common": [bar_open_ms...],
    "bar_seconds": float}``. ``common`` is the sorted intersection of bar-open
    buckets present in *both* underlyings.
    """
    maps: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for inst, cap in captures.items():
        bars = e74._term_bars(cap, bar_seconds=bar_seconds)
        maps[inst] = {int(b["bar_open_ms"]): b for b in bars}
    insts = sorted(maps)
    if len(insts) < 2:
        common: List[int] = []
    else:
        common = sorted(set.intersection(*[set(maps[i]) for i in insts]))
    return {
        "maps": maps,
        "common": common,
        "bar_seconds": float(bar_seconds),
        "underlyings": insts,
    }


def _closes_on_common(cs: Dict[str, Any], inst: str) -> List[float]:
    maps = cs["maps"][inst]
    return [float(maps[int(m)]["close"]) for m in cs["common"]]


def _term_slope_on_common(cs: Dict[str, Any], inst: str) -> List[Optional[float]]:
    maps = cs["maps"][inst]
    return [maps[int(m)].get(SURFACE_SIGNAL) for m in cs["common"]]


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
# Evaluation (cross-asset term_slope spillover -> forward realized return skewness)
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

    other_slope = _term_slope_on_common(cs, other_inst)

    # Forward return skewness of the TARGET underlying on the common grid.
    target_closes = _closes_on_common(cs, target_inst)
    fwd = _forward_return_skewness(
        [{"close": c} for c in target_closes], horizon_bars
    )

    sig_filled = e71._forward_fill(other_slope)
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
        "eval": "EVAL-122",
        "title": "Cross-asset term-structure slope spillover (other asset's term_slope) -> "
                 "forward own-asset realized return skewness predictiveness (Spearman rank IC)",
        "extends": "EVAL-113/114 (same term_slope signal path and EVAL-65 inference) + "
                   "EVAL-74 (term-structure reconstruction _term_bars) + "
                   "EVAL-71 (surface floor verbatim) + EVAL-77-style cross-asset alignment + "
                   "EVAL-85/109 (forward-window return-skewness target); distinct cell: "
                   "cross-asset term_slope spillover -> forward realized return skewness",
        "supersedes": "nothing -- complements EVAL-113/114; no traded-form claim",
        "capture_dir": str(capture_dir),
        "surface_signal": SURFACE_SIGNAL,
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "min_expiry_trades": int(MIN_EXPIRY_TRADES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "spillover_signal": "signal_k = term_slope[OTHER](k)  "
                                "(other asset's near-minus-far ATM IV slope)",
        },
        "signal": "causal per-bar near-minus-far ATM IV term slope of the OTHER underlying "
                  "(e74._term_bars term_slope), aligned to the common BTC-vs-ETH bar grid "
                  "(build_cross_section), forward-filled and expanding-zscored end-of-bar k "
                  "(reused e71._forward_fill / e61.expanding_zscore)",
        "target_detail": "forward realized return skewness = m3 / m2**1.5 over the TARGET "
                         "underlying's next H perp log returns (strictly after the decision "
                         "at bar k, lr[k:k+h]); third standardized moment, transcribed verbatim "
                         "from sealed EVAL-109/111/112/113",
        "statistic": "Spearman rank correlation IC = rho(other_term_slope_z_k, own_skew_k); "
                     "directional permutation H1: IC>0 (steeper other-asset near-minus-far "
                     "slope -> more right-skewed forward returns on the target)",
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
                    "with iv/strike/expiry + perp candles); no new acquisition, no network",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval122(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL122-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-SKEWNESS",
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

    pass_configs: List[str] = []
    for r in per_config:
        key = (
            f"{r['target_underlying']}<-{r['signal_underlying']}::{r['signal']}"
            f"::bar{r['bar_seconds']}::h{r['horizon_bars']}"
        )
        if r.get("pass") and key in rejected:
            pass_configs.append(key)

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
        "EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS" if floor_ok
        else "EVAL_122_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free Spearman rank IC between the causal cross-asset term-slope "
            "spillover (other asset's slope) and forward own-asset realized return "
            "skewness on real captures"
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
            "The causal near-minus-far ATM IV term slope of the OTHER underlying "
            "(cross-asset term_slope spillover) has a positive monotone (Spearman rank) "
            "relationship with the subsequent forward realized return skewness (third "
            "standardized moment) of the target underlying, independent of any trading "
            "wrapper; tested on real on-disk captures at the composed EVAL-71 + alignment "
            "floor."
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
        f"# {PREREG_ID} — cross-asset term_slope spillover -> forward realized return skewness (Spearman rank IC)",
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
        f"# {r['report_id']} — cross-asset term_slope spillover -> forward realized return skewness (Spearman rank IC)",
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
        f"# {BLOCKED_ID} — cross-asset term_slope spillover -> forward realized return skewness: BELOW FLOOR",
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
        description="EVAL-122: causal cross-asset term_slope spillover -> forward realized return skewness predictiveness (Spearman rank IC)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL122-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-SKEWNESS")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval122(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
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
