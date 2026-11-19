#!/usr/bin/env python3
"""EVAL-128: does the cross-sectional causal near-to-far ATM implied-vol **atm_iv
basis** (``atm_iv_ETH - atm_iv_BTC``) predict the subsequent **forward relative
realized return skewness spread** (skewness of ETH forward log returns minus
skewness of BTC forward log returns)? A distinct, on-charter, runnable-**now**
predictiveness cell on the real on-disk three-way captures.

Why this rung exists (mandatory next pre-threshold heavy work after EVAL-127)
-----------------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The physics-independent
runnable-now line EVAL-70..127 is sealed. EVAL-77 tested the cross-sectional
surface basis (atm_iv + skew) -> forward **realized-vol spread**; EVAL-105/106/
107/108 tested term-ratio/term-slope bases -> relative tail-asymmetry /
vol-of-vol spreads; EVAL-110/112/113 tested single-asset skew/term_ratio/
term_slope -> forward **return skewness**. None of them tests the
**cross-sectional ``atm_iv`` basis** (atm_iv_ETH - atm_iv_BTC) against the
**forward relative realized return skewness spread** — a distinct cross-sectional
third-moment predictiveness cell.

The genuinely distinct, on-charter, runnable-**now** cell tested here is: does
the causal cross-sectional atm_iv basis ``atm_iv_ETH(k) - atm_iv_BTC(k)`` carry
monotone information about the subsequent forward relative realized-return
skewness spread ``skew_fwd_ETH(k+1..k+H) - skew_fwd_BTC(k+1..k+H)``? It is
**predictiveness only** — no traded-form or monetization claim.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
-------------------------------------------------------------------------------
For each bar grid ``{60s, 300s}`` and each forward horizon ``H`` bars:

* the causal cross-sectional atm_iv basis ``rel_z_k`` is reconstructed exactly
  as EVAL-77 (``e77.build_cross_section`` with ``atm_iv`` from EVAL-71 surface
  bars, relative series ``atm_iv_ETH - atm_iv_BTC`` forward-filled then
  expanding-z-scored end-of-bar ``k`` via ``e61.expanding_zscore``);
* the target is the forward **relative realized return skewness spread**
  ``spread_k = forward_skewness(ETH closes, k+1..k+H) -
  forward_skewness(BTC closes, k+1..k+H)`` where forward skewness is the third
  standardized moment ``mean((r - mu)^3) / std^3`` of log returns
  ``r_i = log(close_i/close_{i-1})`` over the forward window. Windows with
  fewer than 3 returns or zero/non-positive variance yield ``None``. A config
  needs at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

Compute Spearman rank ``IC = rho(rel_z_k, spread_k)`` with the sealed EVAL-65
directional permutation and block bootstrap (H1: ``IC > 0``). A config **passes**
only if ``IC > 0``, directional permutation ``p < 0.05``, block-bootstrap 95% CI
lower ``> 0``, and at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if at least one config:** ``IC > 0``, directional permutation
``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, usable pairs >= floor, and
pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-128 consumes both underlyings' trade-tape IV surfaces and both perp series,
so it reuses the sealed **EVAL-77 composed surface basis floor verbatim** (the
EVAL-71 surface floor applied to BOTH BTC and ETH, plus a cross-sectional
alignment floor of >= ``min_aligned_common_bars`` common bar-ends on the coarsest
grid), applied to BOTH BTC and ETH. Below the floor it seals
``EVAL_128_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-77 measured the
cross-sectional surface basis -> forward *realized-vol spread*; EVAL-112/113
measured single-asset *term_ratio/term_slope* -> forward *return skewness*;
EVAL-116 measured cross-sectional *skew basis* -> forward *relative realized
return skewness spread*; EVAL-127 measured cross-sectional *atm_iv basis* ->
forward *relative realized return kurtosis spread*. EVAL-128 measures the
cross-sectional *atm_iv basis* -> forward **relative realized return skewness
spread** (third moment), reusing all sealed signal/target reconstructions and
the EVAL-65 inference verbatim.

Seals ``EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/65/71/77 primitives verbatim (no forks, no src).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED"
PREREG_ID = "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION"
BLOCKED_ID = "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED"

# Single cross-sectional signal (atm_iv basis, ETH - BTC).
SURFACE_SIGNALS: Tuple[str, ...] = ("atm_iv",)
TARGET = "forward_relative_return_skewness_spread"

# Pre-registered grid (single signal x bar grid x forward horizons -> 6 configs).
GRID_BAR_SECONDS: Tuple[float, ...] = e77.GRID_BAR_SECONDS
FORWARD_HORIZONS_BARS: Tuple[int, ...] = e77.FORWARD_HORIZONS_BARS

# Cross-section legs (verbatim from EVAL-77).
BASELINE = e77.BASELINE
RELATIVE = e77.RELATIVE

# Statistics reused verbatim from EVAL-65 (identical permutation / bootstrap / seed).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

# A config needs at least this many usable (relative atm_iv z, relative forward
# skewness spread) pairs to be evaluable (a result-quality guard, not a data floor).
MIN_USABLE_PAIRS_PER_CONFIG = 120

# Composed heavy-work floor: sealed EVAL-77 surface basis floor (E71 surface
# floor for both underlyings + cross-sectional alignment), verbatim, neither
# weakened. NOT the EVAL-64 options-surface snapshot floor. Identity (not a
# copy) so the sealed floor object is reused verbatim and cannot drift.
FLOOR: Dict[str, Any] = e77.FLOOR

# Sealed EVAL-77 helpers re-exported verbatim (no forks, no src).
build_cross_section = e77.build_cross_section
_closes_on_common = e77._closes_on_common
_relative_signal_series = e77._relative_signal_series

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "scripts/eval128_cross_sectional_atm_iv_basis_forward_relative_return_skewness_spread.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval128_cross_sectional_atm_iv_basis_forward_relative_return_skewness_spread.py "
    "tests/test_eval128_cross_sectional_atm_iv_basis_forward_relative_return_skewness_spread.py",
    "python3 -m pytest -q tests/test_eval128_cross_sectional_atm_iv_basis_forward_relative_return_skewness_spread.py",
    "# no acquisition needed — consume the already-acquired real captures; no network:",
    "python3 scripts/eval128_cross_sectional_atm_iv_basis_forward_relative_return_skewness_spread.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval128_cross_sectional_atm_iv_basis_forward_relative_return_skewness_spread.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL128-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD",
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
# For decision bar k (target strictly after k) uses log returns
# r_i = log(close_i / close_{i-1}) over bars k+1..k+H;
# mu = mean(r), m2 = mean((r-mu)^2), m3 = mean((r-mu)^3),
# skewness = m3 / (m2^(3/2)). Windows with < 3 returns or non-positive
# variance yield None. Strictly distinct from forward RV level (EVAL-71/77),
# signed mean (EVAL-101/102/104), return-tail asymmetry (EVAL-85/87),
# vol-of-vol (EVAL-95/97), and single-asset return skewness (EVAL-109/111-113).
# ---------------------------------------------------------------------------
def _forward_return_skewness(
    closes: Sequence[float], horizon_bars: int
) -> List[Optional[float]]:
    """Forward realized-return skewness over the next ``H`` bars.

    Returns a list indexed by bar ``k``; incomplete tail entries are omitted
    (shorter list). ``None`` where variance is non-positive or fewer than 3
    returns.
    """
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
        std = math.sqrt(m2)
        if std <= 0.0:
            out.append(None)
            continue
        val = m3 / (std ** 3)
        out.append(float(val) if math.isfinite(val) else None)
    return out


# ---------------------------------------------------------------------------
# Per-(signal, grid, horizon) cross-sectional predictiveness.
# Reuses EVAL-77 build_cross_section / _closes_on_common /
# _relative_signal_series verbatim.
# ---------------------------------------------------------------------------
def evaluate_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Cross-sectional predictiveness: causal atm_iv basis (ETH - BTC) z at bar k
    -> forward relative realized return skewness spread over bars k+1..k+H."""
    cs = e77.build_cross_section(captures, bar_seconds=bar_seconds)
    n_common = len(cs["common"])
    if n_common < int(horizon_bars) + 5:
        return {
            "signal": surface_signal,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "error": "insufficient common surface bars",
            "n_common_bars": n_common,
            "n_pairs": 0,
            "spearman_ic": float("nan"),
            "permutation_p": 1.0,
            "bootstrap_ci": [float("nan")] * 3,
            "pass": False,
        }

    closes_b = e77._closes_on_common(cs, BASELINE)
    closes_r = e77._closes_on_common(cs, RELATIVE)
    skew_b = _forward_return_skewness(closes_b, horizon_bars)
    skew_r = _forward_return_skewness(closes_r, horizon_bars)
    n = min(len(skew_b), len(skew_r))
    # Relative realized return skewness spread: skewness[RELATIVE] - skewness[BASELINE].
    spread = [float(skew_r[k]) - float(skew_b[k]) for k in range(n)]

    rel_z = e77._relative_signal_series(cs, surface_signal=surface_signal)
    xs: List[float] = []
    ys: List[float] = []
    for k in range(min(n, len(rel_z))):
        xs.append(float(rel_z[k]))
        ys.append(float(spread[k]))

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
# Composed heavy-work floor (reuse EVAL-77 surface basis floor verbatim)
# ---------------------------------------------------------------------------
def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    return e77.campaign_floor(captures)


# Re-export the sealed EVAL-77 campaign_floor verbatim (identity, not a fork).
campaign_floor = e77.campaign_floor  # noqa: F811


# ---------------------------------------------------------------------------
# Capture selection / orchestration
# ---------------------------------------------------------------------------
def _select_captures(capture_dir: str) -> Dict[str, Dict[str, Any]]:
    selected = e77._select_one_capture_per_underlying(
        e61._capture_inventory(capture_dir)
    )
    return {str(c.get("underlying")): c for c in selected}


def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-128",
        "title": "Cross-sectional causal near-to-far ATM implied-vol atm_iv basis (ETH - BTC) -> "
        "subsequent forward relative realized return skewness spread "
        "(Spearman rank IC) predictiveness on the real on-disk captures",
        "extends": "EVAL-77 (cross-sectional surface basis atm_iv+skew -> forward "
        "realized-vol spread) and EVAL-112/113 (single-asset term_ratio/term_slope "
        "-> forward return skewness) and EVAL-116 (cross-sectional skew basis -> "
        "forward relative return skewness spread): same Spearman rank-IC statistic "
        "and sealed signal reconstructions reused verbatim, but a distinct "
        "on-charter signal x target cell — the *cross-sectional* atm_iv basis "
        "(atm_iv[ETH] - atm_iv[BTC]) -> forward *relative realized return "
        "skewness spread*; no new acquisition",
        "supersedes": "nothing — complements EVAL-77/112/113/116/127; makes no "
        "traded-form claim",
        "capture_dir": str(capture_dir),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_k = atm_iv[ETH](k) - atm_iv[BTC](k)",
            "target": "spread_k = forward_skewness[ETH](k+1..k+H) - "
            "forward_skewness[BTC](k+1..k+H)",
        },
        "surface_signals": list(SURFACE_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar near-ATM implied vol surface (EVAL-71 "
        "build_surface_bars, atm_iv field) for BTC and ETH; the relative "
        "series (ETH - BTC) is forward-filled then expanding-z-scored end-of-bar "
        "k (reused e61.expanding_zscore)",
        "target": "forward realized-return skewness = third standardized moment "
        "mean((r - mu)^3) / std^3 of log returns over the next H perp bars, "
        "computed per underlying on the common aligned bar grid; target = "
        "skewness[ETH] - skewness[BTC] (relative realized return skewness spread)",
        "statistic": "Spearman rank correlation IC = rho(rel_z_k, spread_k) over "
        "the common aligned bar-ends (H1: IC > 0)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the relative "
            "forward-return-skewness spread",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": (
            "GO only if at least one config (signal x bar grid x horizon) has "
            "Spearman IC > 0, directional permutation p < 0.05, block-bootstrap "
            "95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, "
            "and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures "
            "(option trades with real iv + perp candles for BTC and ETH); no new "
            "acquisition, no network; composes the EVAL-71 surface floor for both "
            "underlyings with a cross-sectional alignment floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval128(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL128-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_captures(str(capture_dir_abs))

    floor = campaign_floor(captures)
    floor_ok = bool(
        len(captures) >= int(FLOOR["min_underlyings"]) and floor.get("ok")
    )

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for sig in SURFACE_SIGNALS:
        for bar_s in GRID_BAR_SECONDS:
            for horizon in FORWARD_HORIZONS_BARS:
                try:
                    res = evaluate_config(
                        captures,
                        surface_signal=sig,
                        bar_seconds=bar_s,
                        horizon_bars=horizon,
                    )
                except BaseException as exc:  # noqa: BLE001
                    errors.append(
                        f"{sig}::bar{bar_s}::h{horizon}: {exc!r}"
                    )
                    continue
                per_config.append(res)

    p_values = {
        f"{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}": _finite(
            r.get("permutation_p"), 1.0
        )
        for r in per_config
        if r.get("n_pairs", 0) > 0
    }
    bh = (
        _benjamini_hochberg(p_values, alpha=FDR_ALPHA)
        if p_values
        else {"rejected": []}
    )
    rejected = set(bh.get("rejected") or [])

    pass_configs: List[str] = []
    for r in per_config:
        key = f"{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}"
        if r.get("pass") and key in rejected:
            pass_configs.append(key)

    valid = [r for r in per_config if r.get("n_pairs", 0) > 0]
    best = (
        max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9))
        if valid
        else None
    )

    any_pass = bool(pass_configs)
    go = bool(floor_ok and any_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD"
        if floor_ok
        else "EVAL_128_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal cross-sectional near-to-far ATM IV atm_iv basis (ETH - BTC) "
            "and the subsequent forward relative realized return skewness spread "
            "(skewness[ETH] - skewness[BTC]) on the real on-disk captures"
            if floor_ok
            else "capture below the composed EVAL-77 surface basis floor; no verdict"
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
                if best
                else "n/a"
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
        "generated_at": report.get("generated_at"),
        "task": report.get("task"),
        "hypothesis": (
            "The causal cross-sectional near-to-far ATM implied-vol atm_iv basis "
            "(atm_iv_ETH - atm_iv_BTC, expanding-z-scored) has a positive "
            "monotone (Spearman rank) relationship with the subsequent forward "
            "relative realized return skewness spread (skewness[ETH] - "
            "skewness[BTC] over the next H perp log returns), independent of any "
            "trading wrapper; tested on real on-disk captures at the composed "
            "EVAL-77 surface basis floor."
        ),
        "extends": p.get("extends"),
        "protocol": p,
        "capture_dir": report.get("capture_dir"),
        "floor": report.get("floor", dict(FLOOR)),
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r.get("protocol", {})
    fl = p.get("floor", FLOOR)
    lines = [
        f"# {PREREG_ID} — cross-sectional atm_iv basis (ETH - BTC) -> forward relative realized return skewness spread (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Hypothesis: {r.get('hypothesis')}",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Extends: {p.get('extends')}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Surface signals: {p.get('surface_signals')}",
        f"- Target: {p.get('target')} — {p.get('target_detail')}",
        f"- Bar grid (s): {p.get('bar_seconds_grid')}",
        f"- Forward horizons (bars): {p.get('forward_horizons_bars')}",
        f"- Signal: {p.get('signal')}",
        f"- Statistic: {p.get('statistic')}",
        f"- Stats: perm {p.get('stats', {}).get('permutation_perms')} / "
        f"bootstrap {p.get('stats', {}).get('bootstrap_resamples')} block {p.get('stats', {}).get('bootstrap_block')} / "
        f"BH-FDR alpha {p.get('stats', {}).get('fdr_alpha')} / seed {p.get('stats', {}).get('seed')} / "
        f"zwindow {p.get('stats', {}).get('zwindow')} / "
        f"min usable pairs {p.get('stats', {}).get('min_usable_pairs_per_config')}",
        "",
        "## Pre-declared GO bar",
        "",
        str(p.get("go_bar")),
        "",
        "## Pre-registered composed floor (EVAL-77 surface basis, not the EVAL-64 ladder floor)",
        "",
        f"- {fl.get('note')}",
        f"- Min underlyings: {fl.get('min_underlyings')}",
        f"- Min aligned common bars: {fl.get('min_aligned_common_bars')}",
        f"- Min usable pairs per config: {fl.get('min_usable_pairs_per_config')}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r.get("campaign_floor", {})
    lines = [
        f"# {r['report_id']} — cross-sectional atm_iv basis (ETH - BTC) -> forward relative realized return skewness spread (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Verdict detail: {r.get('verdict_detail')}",
        f"- Floor OK: {r.get('floor_ok')} (underlyings {', '.join(r.get('underlyings', []))})",
        "",
        "## Per-underlying surface floor (EVAL-71, reused verbatim)",
        "",
        "| underlying | surface_floor_ok | n option trades | n near-ATM | n perp candles | span (s) | ok |",
        "|---|---|---|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        sf = u.get("surface_floor", {})
        lines.append(
            f"| {inst} | {u.get('surface_floor_ok')} | {sf.get('n_option_trades')} | "
            f"{sf.get('n_near_atm_option_trades')} | {sf.get('n_perp_candles')} | "
            f"{sf.get('perp_span_seconds')} | {u.get('ok')} |"
        )
    lines += [
        "",
        "## Alignment",
        "",
        f"- Aligned common bars by grid: {fl.get('aligned_common_bars_by_grid')}",
        f"- Aligned common bars binding (coarsest grid): {fl.get('aligned_common_bars_binding')}",
        f"- Aligned OK: {fl.get('aligned_ok')} | Underlyings OK: {fl.get('underlyings_ok')}",
        "",
        "## Per-config (best by Spearman IC)",
        "",
        "| signal | bar_seconds | horizon_bars | n_common | n_pairs | IC | perm_p | CI lo | CI hi | pass |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for c in r.get("per_config", []):
        ci = c.get("bootstrap_ci", [float("nan")] * 3)
        lines.append(
            f"| {c.get('signal')} | {c.get('bar_seconds')} | {c.get('horizon_bars')} | "
            f"{c.get('n_common_bars')} | {c.get('n_pairs')} | "
            f"{_finite(c.get('spearman_ic')):.4f} | {_finite(c.get('permutation_p'),1.0):.4g} | "
            f"{_finite(ci[0]):.4f} | {_finite(ci[1]):.4f} | {_finite(ci[2]):.4f} | {c.get('pass')} |"
        )
    lines += [
        "",
        "## Summary",
        "",
        f"- n_configs: {r.get('summary', {}).get('n_configs')}",
        f"- n_pass: {r.get('summary', {}).get('n_pass')}",
        f"- pass_configs: {r.get('summary', {}).get('pass_configs')}",
        f"- best_ic: {r.get('summary', {}).get('best_ic'):.4f}",
        f"- best_config: {r.get('summary', {}).get('best_config')}",
        "",
        "## Pooled",
        "",
        f"- BH-FDR rejected: {r.get('pooled', {}).get('bh_fdr', {}).get('rejected')}",
        f"- Any config pass: {r.get('pooled', {}).get('any_config_pass')}",
        f"- Campaign state: {r.get('pooled', {}).get('campaign_state')}",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r.get("generated_at", _utc_now_iso()),
        "task": r.get("task", "EVAL128-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD"),
        "verdict": "BLOCKED",
        "verdict_detail": "capture below the composed EVAL-77 surface basis floor; no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "floor": r.get("floor", dict(FLOOR)),
        "campaign_floor": r.get("campaign_floor", {}),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — cross-sectional atm_iv basis -> forward relative return skewness spread: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "The capture is below the composed EVAL-77 surface basis floor; no "
        "predictiveness verdict is emitted (never a NO-GO).",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-128: cross-sectional atm_iv basis (ETH - BTC) -> forward relative realized return skewness spread predictiveness (Spearman rank IC)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL128-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval128(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(),
                "task": args.task_label,
                "capture_dir": args.capture_dir,
                "underlyings": [],
                "floor": dict(FLOOR),
                "campaign_floor": {},
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(
        json.dumps(
            {
                "verdict": report.get("verdict"),
                "floor_ok": report.get("floor_ok"),
                "underlyings": report.get("underlyings"),
                "per_config": report.get("per_config"),
                "summary": report.get("summary"),
                "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
                "n_configs": len(report.get("per_config", [])),
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
