#!/usr/bin/env python3
"""EVAL-77: does the **cross-sectional options implied-volatility surface basis**
(BTC-vs-ETH relative near-ATM IV) predict the subsequent **relative realized
volatility** of the two perps? — a distinct, runnable-**now** signal-family
falsification on the real on-disk three-way captures.

Why this rung exists (the distinct signal EVAL-71/74 leave open)
---------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now surface line
so far is:

* EVAL-71 sealed ``GO CONFIRMED`` — the *single-underlying* options implied-vol
  surface (near-ATM IV **level** + put-call **skew**) predicts forward RV;
* EVAL-73 sealed ``GO CONFIRMED (PASS)`` — that predictiveness is stable OOS;
* EVAL-74 sealed ``NO-GO CONFIRMED (PASS)`` — the *term-structure* slope predicts
  ETH forward RV but is null on BTC;
* EVAL-72 / EVAL-75 / EVAL-76 sealed ``NO-GO CONFIRMED (PASS)`` — the surface
  level/skew and term-structure signals do **not** monetize net-of-cost through
  an ATM straddle (EVAL-72/75) or a skew-isolating risk reversal (EVAL-76).

Every rung above is **single-underlying** (or a same-underlying term structure).
The one genuinely distinct, on-charter, runnable-**now** *signal* that none of
them tests is the **cross-sectional** surface: the *relative* near-ATM implied
vol between BTC and ETH. The economic question is relative-value mean reversion:

    When ETH's near-ATM implied vol is rich relative to BTC's (equivalently BTC
    is cheap), does BTC subsequently realize *higher* volatility relative to ETH
    (and vice versa)? I.e. is the causal BTC-vs-ETH implied-vol **basis**
    informative about the subsequent BTC-vs-ETH **realized-vol spread**?

This is a distinct *signal family* (cross-sectional relative IV, not
single-underlying level/skew or term structure), it is on the repo charter, and
it is runnable **today** because it needs only the already-acquired real
three-way captures (per-bar near-ATM option trade IV for BTC and ETH + both perp
candle series) — **no new acquisition, no network**. It does not re-litigate any
sealed result:

* EVAL-71/73/74 measured *within-underlying* surface predictiveness;
* EVAL-72/75/76 traded *within-underlying* surface signals net-of-cost;
* **EVAL-77** measures the *cross-sectional* BTC-vs-ETH implied-vol basis ->
  realized-vol **spread** relationship.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each causal surface signal ``{atm_iv, skew}`` and each bar grid
``{60s, 300s}`` and each forward horizon ``H`` bars, define

    rel_k   = signal_ETH(k) - signal_BTC(k)              (relative richness)
    spread_k = rv_BTC(k+1..k+H) - rv_ETH(k+1..k+H)       (relative realized vol)

on the **common aligned** bar grid (bar-ends where BOTH underlyings have a
causal surface value and a perp close). ``rel`` is forward-filled causally and
expanding-z-scored end-of-bar ``k``. Compute the Spearman rank
``IC = rho(rel_z_k, spread_k)``. **GO only if at least one config** has
``IC > 0`` (ETH richness predicts a higher subsequent BTC-minus-ETH realized-vol
spread, i.e. relative-value mean reversion), directional permutation
``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs, and pooled BH-FDR rejects that
config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-77 consumes BOTH underlyings' trade-tape IV surfaces and both perp series,
so it composes two honestly pre-registered floors and requires both:

* the EVAL-71 surface floor (option trades / near-ATM trades / perp candles /
  span) for **each** of BTC and ETH, reused verbatim; and
* a cross-sectional alignment floor: at least
  ``MIN_ALIGNED_COMMON_BARS`` bar-ends where both underlyings carry a causal
  near-ATM IV on the coarsest grid.

Neither is weakened. Below the composed floor it seals
``EVAL_77_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61 measurement helpers, EVAL-62 constants, EVAL-65
# statistics, and the EVAL-71 surface reconstruction verbatim (no forks, no src
# edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_COMBINED"
PREREG_ID = "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_BLOCKED"

# Pre-registered grid (surface signals x bar grid x forward horizons).
SURFACE_SIGNALS: Tuple[str, ...] = ("atm_iv", "skew")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# The cross-section is BTC-vs-ETH. ``BASELINE`` is the subtracted leg, so
# ``rel = signal[RELATIVE] - signal[BASELINE]`` and the target spread is
# ``rv[BASELINE] - rv[RELATIVE]``; H1 is IC > 0 (relative richness mean-reverts).
BASELINE = "BTC"
RELATIVE = "ETH"

# Statistics reused verbatim from EVAL-65 (identical permutation / bootstrap / seed).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

# A config needs at least this many usable (signal, spread) pairs to be evaluable
# (a result-quality guard, not a data floor).
MIN_USABLE_PAIRS_PER_CONFIG = 120

# Composed heavy-work floor (EVAL-71 floor for both underlyings AND alignment).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_aligned_common_bars": 200,
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-77 consumes both underlyings' trade-tape IV surfaces and both perp "
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
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py "
    "tests/test_eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "python3 -m pytest -q tests/test_eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL77-CROSS-SECTIONAL-SURFACE-BASIS-RV",
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
    """Richest (most real option trades) real capture per underlying; deterministic."""
    best: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = str(c.get("underlying") or "?")
        score = len(c.get("option_trades", []) or [])
        if inst not in best or score > len(best[inst].get("option_trades", []) or []):
            best[inst] = c
    return [best[k] for k in sorted(best)]


# ---------------------------------------------------------------------------
# Cross-sectional surface basis + forward realized-vol spread
# ---------------------------------------------------------------------------
def build_cross_section(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """Align two underlyings' causal surface bars on their common bar grid.

    Returns ``{"maps": {inst: {bar_open_ms: bar}}, "common": [bar_open_ms...],
    "bar_seconds": float}``. ``common`` is the sorted intersection of bar-open
    buckets present in *both* underlyings (a real per-bar causal surface value may
    still be ``None`` at a given bar; the caller forward-fills causally).
    """
    maps: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for inst, cap in captures.items():
        bars = e71.build_surface_bars(cap, bar_seconds=bar_seconds)
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


def _rv_series(closes: Sequence[float], horizon_bars: int) -> List[float]:
    """Forward realized vol on the aligned grid (identical definition to
    EVAL-71 ``_forward_rv``): ``sqrt(mean(log-return^2))`` over the next H bars."""
    lr = (
        [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)]
        if len(closes) >= 2
        else []
    )
    h = int(horizon_bars)
    rv: List[float] = []
    for k in range(0, len(lr) - h + 1):
        seg = lr[k:k + h]
        rv.append(math.sqrt(sum(r * r for r in seg) / float(h)))
    return rv


def _relative_signal_series(
    cs: Dict[str, Any], *, surface_signal: str
) -> List[float]:
    """Causal expanding-z-scored relative surface signal ``signal[ETH] -
    signal[BTC]`` on the common bar grid.

    ``None`` where either underlying has no causal surface value at that bar;
    forward-filled causally, then expanding-z-scored end-of-bar ``k`` (reusing the
    sealed ``e61.expanding_zscore``).
    """
    maps = cs["maps"]
    raw: List[Optional[float]] = []
    for m in cs["common"]:
        b = maps[BASELINE][int(m)].get(surface_signal)
        r = maps[RELATIVE][int(m)].get(surface_signal)
        raw.append(
            float(r) - float(b)
            if (b is not None and r is not None)
            else None
        )
    filled = e71._forward_fill(raw)
    return e61.expanding_zscore(filled, ZWINDOW)


def evaluate_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Cross-sectional predictiveness for one (signal, grid, horizon) config."""
    cs = build_cross_section(captures, bar_seconds=bar_seconds)
    n_common = len(cs["common"])
    if n_common < int(horizon_bars) + 5:
        return {
            "signal": surface_signal,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "error": "insufficient common surface bars",
            "n_common_bars": n_common,
            "n_pairs": 0,
            "pass": False,
        }

    closes_b = _closes_on_common(cs, BASELINE)
    closes_r = _closes_on_common(cs, RELATIVE)
    rv_b = _rv_series(closes_b, horizon_bars)
    rv_r = _rv_series(closes_r, horizon_bars)
    n = min(len(rv_b), len(rv_r))
    rv_spread = [float(rv_b[k]) - float(rv_r[k]) for k in range(n)]

    rel_z = _relative_signal_series(cs, surface_signal=surface_signal)
    xs: List[float] = []
    ys: List[float] = []
    for k in range(min(n, len(rel_z))):
        xs.append(float(rel_z[k]))
        ys.append(float(rv_spread[k]))

    if len(xs) < int(MIN_USABLE_PAIRS_PER_CONFIG):
        return {
            "signal": surface_signal,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "error": "insufficient aligned pairs",
            "n_common_bars": n_common,
            "n_pairs": len(xs),
            "pass": False,
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
        "n_common_bars": n_common,
        "n_pairs": len(xs),
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "pass": passed,
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
            cs = build_cross_section(
                {BASELINE: captures[BASELINE], RELATIVE: captures[RELATIVE]},
                bar_seconds=bar_s,
            )
            aligned_by_grid[str(bar_s)] = len(cs["common"])

    # The coarsest grid is the binding alignment constraint.
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
        "eval": "EVAL-77",
        "title": "Cross-sectional options implied-volatility surface basis "
                 "(BTC-vs-ETH relative near-ATM IV / skew) -> subsequent relative "
                 "realized volatility (BTC-minus-ETH RV spread): wrapper-free rank "
                 "information coefficient (predictiveness) falsification on the real "
                 "on-disk three-way captures",
        "extends": "EVAL-71 / EVAL-73 / EVAL-74 (identical Spearman rank-IC statistic "
                   "and surface reconstruction) but a different, on-charter signal "
                   "family: the *cross-sectional* BTC-vs-ETH implied-vol basis rather "
                   "than a single-underlying level/skew or term structure; no new "
                   "acquisition",
        "supersedes": "nothing — this is the cross-sectional complement to EVAL-71 "
                      "(single-underlying level/skew), EVAL-73 (OOS stability) and "
                      "EVAL-74 (term structure). EVAL-72/75/76 traded within-"
                      "underlying signals net-of-cost; none measured the BTC-vs-ETH "
                      "relative surface basis",
        "capture_dir": str(capture_dir),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_k = signal[ETH](k) - signal[BTC](k)",
            "target": "spread_k = rv[BTC](k+1..k+H) - rv[ETH](k+1..k+H)",
        },
        "surface_signals": list(SURFACE_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar near-ATM implied-vol surface (EVAL-71 "
                  "build_surface_bars) for BTC and ETH: atm_iv = amount-weighted mean "
                  "iv of near-ATM trades; skew = mean(put iv) - mean(call iv); the "
                  "relative series (ETH - BTC) is forward-filled then expanding-"
                  "zscored end-of-bar k (reused e61.expanding_zscore)",
        "target": "rv = sqrt(mean(log-return^2)) over the next H perp bars, computed "
                  "per underlying on the common aligned bar grid; target = rv[BTC] - "
                  "rv[ETH] (relative realized vol)",
        "statistic": "Spearman rank correlation IC = rho(rel_z_k, spread_k) over the "
                     "common aligned bar-ends (H1: IC > 0, relative richness "
                     "mean-reverts)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the realized-vol spread",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": (
            "GO only if at least one config (surface signal x bar grid x horizon) has "
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


def run_eval77(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL77-CROSS-SECTIONAL-SURFACE-BASIS-RV",
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
                    errors.append(
                        f"{sig}::bar{bar_s}::h{horizon}: {exc!r}"
                    )
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
        "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS" if floor_ok
        else "EVAL_77_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal cross-sectional options implied-vol basis (ETH - BTC near-ATM IV / "
            "skew) and the subsequent BTC-minus-ETH forward realized-vol spread on the "
            "real on-disk captures"
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
            "The causal cross-sectional options implied-volatility surface basis "
            "(BTC-vs-ETH relative near-ATM IV / put-call skew, reconstructed from the "
            "real Deribit option trade tapes) has a positive monotone (Spearman rank) "
            "relationship with the subsequent relative realized volatility "
            "(BTC-minus-ETH forward RV spread): relative implied-vol richness "
            "mean-reverts. Tested on the already-acquired real on-disk captures at the "
            "composed EVAL-71 + alignment floor."
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
        f"# {PREREG_ID} — cross-sectional options implied-vol surface basis -> "
        f"relative realized-vol predictiveness (wrapper-free Spearman rank IC)",
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
        f"- Target detail: {p['target']}",
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
        f"# {r['report_id']} — cross-sectional options implied-vol surface basis -> "
        f"relative realized-vol predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        f"- Aligned common bars by grid: {fl['aligned_common_bars_by_grid']}",
        "",
        "## Per-underlying EVAL-71 floor",
        "",
        "| underlying | surface floor ok | option trades | near-ATM | perp candles | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl["per_underlying"].items():
        s = u["surface_floor"]
        lines.append(
            f"| {inst} | {u['surface_floor_ok']} | {s.get('n_option_trades')} | "
            f"{s.get('n_near_atm_option_trades')} | {s.get('n_perp_candles')} | "
            f"{u['ok']} |"
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
    if r["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r["generated_at"],
        "task": r["task"],
        "verdict": "BLOCKED",
        "capture_dir": r["capture_dir"],
        "underlyings": r["underlyings"],
        "campaign_floor": r["campaign_floor"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {BLOCKED_ID} — cross-sectional options implied-vol surface basis -> "
        f"relative realized-vol predictiveness (below the composed EVAL-71 + "
        f"alignment floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Underlyings floor met: {fl['underlyings_ok']}",
        f"- Aligned common bars by grid: {fl['aligned_common_bars_by_grid']}",
        f"- Aligned floor met: {fl['aligned_ok']}",
        "",
        "The capture does not meet the composed EVAL-71 + cross-sectional alignment "
        "floor, so no GO/NO-GO verdict is emitted. Do NOT weaken either floor, do NOT "
        "use synthetic data, and do NOT emit NO-GO on under-floor data.",
        "",
        "## Per-underlying EVAL-71 floor",
        "",
    ]
    for inst, u in fl["per_underlying"].items():
        lines.append(
            f"- {inst}: surface_floor_ok={u.get('surface_floor_ok')} "
            f"checks={json.dumps(u.get('checks'))}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-77: cross-sectional options implied-vol surface basis -> "
                    "relative realized-vol predictiveness (Spearman rank IC) on the "
                    "real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label", default="EVAL77-CROSS-SECTIONAL-SURFACE-BASIS-RV"
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval77(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(),
                "task": args.task_label,
                "verdict": "BLOCKED",
                "capture_dir": args.capture_dir,
                "underlyings": [],
                "campaign_floor": {},
                "floor": dict(FLOOR),
                "floor_ok": False,
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