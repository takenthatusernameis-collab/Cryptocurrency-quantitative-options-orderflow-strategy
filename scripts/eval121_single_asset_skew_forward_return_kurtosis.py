#!/usr/bin/env python3
"""EVAL-121: does the single-asset causal **near-ATM put-call skew**
(``skew``) predict the subsequent **forward realized return kurtosis** (fourth
standardized moment, tail fatness) of the SAME underlying? A distinct,
on-charter, runnable-**now** predictiveness cell on the real on-disk three-way
captures.

Why this rung exists (the next runnable-now heavy work after EVAL-120)
----------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The physics-independent
runnable-now line EVAL-70..120 is sealed. Prior rungs paired the single-asset
``skew`` signal with forward **RV level** (EVAL-71), **vol-of-vol** (EVAL-97),
**VRP** (EVAL-86), **tail asymmetry** (EVAL-85), **signed return** (EVAL-103),
and **realized return skewness** (EVAL-111, third moment). The
**fourth standardized moment (kurtosis)** — forward tail *fatness* — has never
been used as a target with the ``skew`` signal in any sealed cell.

The genuinely distinct, on-charter, runnable-**now** cell tested here is: does
the causal near-ATM put-call **skew** at bar ``k`` carry monotone
information about the same underlying's subsequent **fourth standardized
moment (kurtosis)** of its per-bar log returns over bars ``k+1..k+H``? It is
**predictiveness only** — no traded-form or monetization claim. It is strictly
distinct from the third-moment (skewness) cells EVAL-109/111/112/113 and from
the quantile-spread tail-asymmetry cells EVAL-85/87/99/100: the fourth moment
is tail *fatness*, not tail *direction*.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
-------------------------------------------------------------------------------
For each underlying (BTC, ETH), each bar grid ``{60s, 300s}`` and each forward
horizon ``H`` bars:

* the causal near-ATM put-call skew ``skew`` is built exactly as EVAL-85/111
  (``e71.build_surface_bars`` with the EVAL-71 signal window / ATM band
  constants verbatim), forward-filled (``e71._forward_fill``) and expanding
  z-scored end-of-bar ``k`` (``e61.expanding_zscore``, ``e62.ZWINDOW``); and
* the target is the forward **realized return kurtosis** over bars
  ``k+1..k+H``, ``kurt_k = m4 / m2**2`` with
  ``m_j = mean(r_i - mean(r))**j`` over ``r_i = log(close_i/close_{i-1})``,
  ``i in k+1..k+H`` (the EVAL-85/117 forward-window convention: ``lr[k:k+h]``).
  Windows with zero variance (or fewer than 4 returns) yield ``None``. A config
  needs at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

Compute Spearman rank ``IC = rho(skew_z_k, kurt_{k+1..k+H})`` with the
sealed EVAL-65 directional permutation and block bootstrap (H1: ``IC > 0`` —
higher put-call skew precedes fatter forward return tails).
A config **passes** only if ``IC > 0``, directional permutation ``p < 0.05``,
block-bootstrap 95% CI lower ``> 0``, and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH and at least one config:** ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``,
and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-121 consumes the same surface signal data as EVAL-71/85/86/97/101/103/111, so it reuses
the sealed **EVAL-71 surface floor verbatim** for EACH underlying
(min 2 underlyings; per underlying >= ``min_option_trades_per_underlying``=1000 option
trades, >= ``min_near_atm_option_trades_per_underlying``=400 near-ATM trades,
>= ``min_perp_candles_per_underlying``=1000 perp candles, >=
``min_perp_span_seconds_per_underlying``=82000s perp span), applied to BOTH BTC
and ETH. Below the floor it seals ``EVAL_121_..._BLOCKED_<UTC>`` (never a
NO-GO). The EVAL-64 ladder floor is untouched.

This does **not** re-litigate any sealed result: EVAL-71 measured surface ->
forward *RV level*; EVAL-85 measured ``skew`` -> forward *tail asymmetry*;
EVAL-86 measured ``skew`` -> forward *VRP*; EVAL-97 measured ``skew`` ->
forward *vol-of-vol*; EVAL-101 measured ``atm_iv`` -> forward *signed return
mean*; EVAL-103 measured ``skew`` -> forward *signed return*; EVAL-111 measured
``skew`` -> forward *realized return skewness*. EVAL-121 measures the single-asset
``skew`` **level** -> forward **realized return kurtosis** (a new fourth-moment
target), reusing all sealed signal reconstructions and the EVAL-65 inference
verbatim.

Seals ``EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/65/71 primitives verbatim (no forks, no src).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS_COMBINED"
PREREG_ID = "EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS_PREREGISTRATION"
BLOCKED_ID = "EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS_BLOCKED"

# Single surface signal (near-ATM put-call skew, exactly EVAL-85/111's signal path).
SURFACE_SIGNAL: str = "skew"
TARGET = "realized_return_kurtosis"

# Pre-registered grid (single signal x bar grid x forward horizons -> 6 configs).
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

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

# Composed floor: sealed EVAL-71 surface floor, verbatim, applied to BOTH BTC
# and ETH. Not the EVAL-64 ladder floor.
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
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "Reuses the sealed EVAL-71 surface floor verbatim "
        "(min_option_trades_per_underlying=1000, "
        "min_near_atm_option_trades_per_underlying=400, "
        "min_perp_candles_per_underlying=1000, "
        "min_perp_span_seconds_per_underlying=82000s), applied to BOTH BTC and ETH. "
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
    "scripts/eval121_single_asset_skew_forward_return_kurtosis.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval121_single_asset_skew_forward_return_kurtosis.py "
    "tests/test_eval121_single_asset_skew_forward_return_kurtosis.py",
    "python3 -m pytest -q tests/test_eval121_single_asset_skew_forward_return_kurtosis.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval121_single_asset_skew_forward_return_kurtosis.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval121_single_asset_skew_forward_return_kurtosis.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL121-SINGLE-ASSET-SKEW-FORWARD-RETURN-KURTOSIS",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Forward realized return kurtosis target (fourth standardized moment).
#
# Same EVAL-85/117 forward-window convention as EVAL-109/111/112/113/117/119 (``lr[k : k+h]``),
# but the FOURTH moment ``m4 / m2**2`` (tail fatness) instead of the third.
# Strictly distinct from forward RV level (EVAL-71), signed mean (EVAL-101/103),
# quantile-spread tail asymmetry (EVAL-85/87/99/100), vol-of-vol (EVAL-84/95/97)
# and return skewness (EVAL-109/111/112/113).
# ---------------------------------------------------------------------------
def _forward_return_kurtosis(
    bars: Sequence[Dict[str, Any]], horizon_bars: int
) -> List[Optional[float]]:
    """Forward realized return kurtosis over the next ``H`` bars.

    ``r_i = log(close_i / close_{i-1})`` over bars ``k+1..k+H``;
    ``kurt = m4 / m2**2`` with ``m_j = mean((r - mean(r))**j)``. Windows with
    non-positive variance (or degenerate H < 4) yield ``None`` so they are
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
        if len(seg) < 4:
            out.append(None)
            continue
        mu = sum(seg) / len(seg)
        m2 = sum((v - mu) ** 2 for v in seg) / len(seg)
        if m2 <= 0.0 or not math.isfinite(m2):
            out.append(None)
            continue
        m4 = sum((v - mu) ** 4 for v in seg) / len(seg)
        val = m4 / (m2 ** 2)
        out.append(float(val) if math.isfinite(val) else None)
    return out


# ---------------------------------------------------------------------------
# Floor composition (reuse EVAL-71 surface floor verbatim)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    return e71._underlying_surface_floor(capture)


def _campaign_floor(per_underlying: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    n_ok = sum(1 for v in per_underlying.values() if v.get("ok"))
    checks = {
        "underlyings_ok": n_ok >= int(FLOOR["min_underlyings"]),
        "all_underlyings_ok": bool(per_underlying) and all(v.get("ok") for v in per_underlying.values()),
    }
    return {"checks": checks, "ok": bool(all(checks.values()))}


# ---------------------------------------------------------------------------
# Evaluation (single signal: put-call skew -> forward realized return kurtosis)
# ---------------------------------------------------------------------------
def _eval_one_config(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    horizon_bars: int,
    surface_signal: str = SURFACE_SIGNAL,
) -> Dict[str, Any]:
    bars = e71.build_surface_bars(
        capture,
        bar_seconds=bar_seconds,
        signal_window_seconds=SIGNAL_WINDOW_SECONDS,
        atm_band=ATM_BAND,
    )
    fwd = _forward_return_kurtosis(bars, horizon_bars)
    sig_filled = e71._forward_fill([b.get(surface_signal) for b in bars])
    sig_z = e61.expanding_zscore(sig_filled, ZWINDOW)

    xs: List[float] = []
    ys: List[float] = []
    n_fwd = len(fwd)
    for k in range(len(bars)):
        if k >= n_fwd:
            continue
        y = fwd[k]
        if y is None:
            continue
        xs.append(float(sig_z[k]) if k < len(sig_z) else 0.0)
        ys.append(float(y))

    n_pairs = len(xs)
    base = {
        "underlying": capture.get("underlying"),
        "signal": surface_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs": n_pairs,
        "target": TARGET,
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
        "eval": "EVAL-121",
        "title": "Options near-ATM put-call skew (skew) -> forward own-asset "
                 "realized return kurtosis predictiveness (Spearman rank IC)",
        "extends": "EVAL-71/85/86/97/101/103/111 (same skew signal path and sealed EVAL-71 surface floor) + "
                   "EVAL-85/117/119 (same forward-window convention, fourth moment instead "
                   "of third); distinct cell: single-asset skew level -> forward realized return "
                   "kurtosis",
        "supersedes": "nothing -- complements EVAL-71/85/86/97/101/103/111/117/119; no traded-form claim",
        "capture_dir": str(capture_dir),
        "surface_signal": SURFACE_SIGNAL,
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar near-ATM put-call skew (e71.build_surface_bars skew), "
                  "forward-filled and expanding-zscored end-of-bar k "
                  "(reused e71._forward_fill / e61.expanding_zscore)",
        "target_detail": "forward realized return kurtosis = m4 / m2**2 over the SAME "
                         "underlying's next H perp log returns (strictly after the decision "
                         "at bar k, lr[k:k+h]); fourth standardized moment (tail fatness)",
        "statistic": "Spearman rank correlation IC = rho(skew_z_k, kurt_k); "
                     "directional permutation H1: IC>0 (higher put-call skew -> fatter "
                     "forward return tails)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle target series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
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


def run_eval121(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL121-SINGLE-ASSET-SKEW-FORWARD-RETURN-KURTOSIS",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_captures(str(capture_dir_abs))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor(c)

    campaign_floor = _campaign_floor(per_underlying_floor)
    floor_ok = bool(campaign_floor.get("ok"))

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures:
        for bar_s in GRID_BAR_SECONDS:
            for horizon in FORWARD_HORIZONS_BARS:
                try:
                    res = _eval_one_config(cap, bar_seconds=bar_s, horizon_bars=horizon)
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{cap.get('underlying')}::{SURFACE_SIGNAL}::bar{bar_s}::h{horizon}: {exc!r}")
                    continue
                per_config.append(res)

    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}": _finite(r.get("permutation_p"), 1.0)
        for r in per_config if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r.get("underlying", "?"), []).append(r)

    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        valid = [r for r in rows if r.get("n_pairs", 0) > 0]
        best = max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9)) if valid else None
        pass_configs: List[str] = []
        for r in valid:
            key = f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}"
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (f"{best['signal']}::bar{best['bar_seconds']}::h{best['horizon_bars']}" if best else "n/a"),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS" if floor_ok else "EVAL_121_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free Spearman rank IC between causal near-ATM put-call skew and forward "
            "own-asset realized return kurtosis on real captures"
            if floor_ok else "capture below the composed EVAL-71 surface floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": dict(FLOOR),
        "per_underlying_floor": per_underlying_floor,
        "campaign_floor": campaign_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {"bh_fdr": bh, "all_underlyings_pass": all_pass, "campaign_state": campaign_state},
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
            "The causal near-ATM put-call skew (skew) has a positive monotone "
            "(Spearman rank) relationship with the subsequent forward realized "
            "return kurtosis (fourth standardized moment, tail fatness) of the same "
            "underlying, independent of any trading wrapper; tested on real on-disk "
            "captures at the EVAL-71 surface floor."
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
        f"# {PREREG_ID} — skew -> forward realized return kurtosis (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Hypothesis: {r.get('hypothesis')}",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Extends: {p.get('extends')}",
        "",
        "## Pre-declared protocol",
        "",
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
        f"min usable pairs {p.get('stats', {}).get('min_usable_pairs_per_config')}",
        "",
        "## Pre-declared GO bar",
        "",
        str(p.get("go_bar")),
        "",
        "## Pre-registered floor (EVAL-71 surface floor, not the EVAL-64 ladder floor)",
        "",
        f"- {fl.get('note')}",
        f"- Min underlyings: {fl.get('min_underlyings')}",
        f"- Min usable pairs per config: {fl.get('min_usable_pairs_per_config')}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — skew -> forward realized return kurtosis (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Verdict detail: {r.get('verdict_detail')}",
        f"- Floor OK: {r.get('floor_ok')} (underlyings {', '.join(r.get('underlyings', []))})",
        "",
        "## Per-underlying surface floor (EVAL-71, reused verbatim)",
        "",
        "| underlying | floor ok | option trades | near-ATM trades | perp candles | span (s) |",
        "|---|---|---|---|---|---|",
    ]
    for inst, fl in r.get("per_underlying_floor", {}).items():
        lines.append(
            f"| {inst} | {fl.get('ok')} | {fl.get('n_option_trades')} | "
            f"{fl.get('n_near_atm_option_trades')} | {fl.get('n_perp_candles')} | "
            f"{fl.get('perp_span_seconds')} |"
        )
    lines += ["", "## Per-underlying (best config by Spearman IC)", "",
              "| underlying | configs | best IC | best config | n pass | any pass |",
              "|---|---|---|---|---|---|"]
    for s in r.get("per_underlying", []):
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_ic']:.4f} | "
            f"{s['best_config']} | {s['n_pass']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r.get('pooled', {}).get('bh_fdr', {}).get('rejected')}",
              f"- All underlyings pass: {r.get('pooled', {}).get('all_underlyings_pass')}",
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
        "verdict_detail": "capture below the composed EVAL-71 surface floor; no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "floor": r.get("floor", dict(FLOOR)),
        "per_underlying_floor": r.get("per_underlying_floor", {}),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — skew -> forward realized return kurtosis: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "The capture is below the composed EVAL-71 surface floor; no predictiveness "
        "verdict is emitted (never a NO-GO).",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-121: causal skew -> forward realized return kurtosis predictiveness (Spearman rank IC)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL121-SINGLE-ASSET-SKEW-FORWARD-RETURN-KURTOSIS")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval121(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(), "task": args.task_label,
                "capture_dir": args.capture_dir, "underlyings": [],
                "floor": dict(FLOOR), "per_underlying_floor": {}, "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_underlying": report.get("per_underlying"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())