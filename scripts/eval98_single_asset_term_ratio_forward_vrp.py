#!/usr/bin/env python3
"""EVAL-98: does the single-asset near-to-far ATM IV **term ratio** predict
subsequent **forward variance risk premium (VRP)** of the same underlying? A
distinct, on-charter, runnable-**now** predictiveness cell on the real on-disk
three-way captures.

Why this rung exists (the next runnable-now heavy work after EVAL-97)
---------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The physics-independent
runnable-now line EVAL-70..97 is sealed. EVAL-74 tested the term-structure
signals ``term_slope``/``term_ratio`` against forward **RV level** (NO-GO
portable). EVAL-84 tested the term structure against forward **vol-of-vol**
(NO-GO). EVAL-96 tested ``term_slope`` against forward **VRP** (NO-GO: BTC
strong but ETH null, not portable). EVAL-86 tested ``skew`` against forward
**VRP** (GO). EVAL-97 tested ``skew`` against forward **vol-of-vol** (GO).

The genuinely distinct, on-charter, runnable-**now** cell tested here is: does
the causal near-to-far ATM IV **term ratio** (``term_ratio = IV(near) /
IV(far) - 1``) predict that same underlying's subsequent **forward VRP**
(``VRP_k = atm_iv_k - forward_RV_{k+1..k+H}``)? This is distinct from EVAL-74
(``term_ratio`` -> own RV *level*), EVAL-84 (``term_ratio``/``term_slope`` ->
own vol-of-vol), EVAL-96 (``term_slope`` -> own VRP), EVAL-97 (``skew`` ->
own vol-of-vol), and EVAL-86 (``skew`` -> own VRP). It is **predictiveness
only** — no traded-form or monetization claim.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), each bar grid ``{60s, 300s}`` and each forward
horizon ``H`` bars:

* the causal per-bar near-to-far ATM IV ratio ``term_ratio`` is reconstructed
  exactly as EVAL-74 (``e74._term_bars``, which groups near-ATM trades by expiry
  using the EVAL-74 trailing window / ATM band / expiry-adequacy constants
  verbatim), forward-filled (``e71._forward_fill``) and expanding z-scored
  end-of-bar ``k`` (``e61.expanding_zscore``); and
* the target is the forward **VRP** over bars ``k+1..k+H`` reused verbatim from
  EVAL-86 (``e86._forward_vrp``): ``VRP_k = atm_iv_k - forward_RV_{k+1..k+H}``
  where ``forward_RV = e71._forward_rv`` (``sqrt(mean(r^2))``). A config needs
  at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

Compute Spearman rank ``IC = rho(signal_z_k, VRP_{k+1..k+H})`` with the sealed
EVAL-65 directional permutation and block bootstrap (H1: ``IC > 0`` — a higher
near/far IV ratio precedes a richer forward VRP). A config **passes** only if
``IC > 0``, directional permutation ``p < 0.05``, block-bootstrap 95% CI lower
``> 0``, and at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH and at least one config:** ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``,
and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-98 consumes the term-structure signal, so it reuses the sealed **EVAL-74
term floor verbatim** (which composes the EVAL-71 surface floor — min 2
underlyings; per underlying >= ``min_option_trades_per_underlying``=1000 option
trades, >= ``min_near_atm_option_trades_per_underlying``=400 near-ATM trades,
>= ``min_perp_candles_per_underlying``=1000 perp candles, >=
``min_perp_span_seconds_per_underlying``=82000s perp span — with term adequacy:
>= ``MIN_DISTINCT_EXPIRIES`` distinct near-ATM expiries with >=
``MIN_EXPIRY_TRADES`` trades each and >= ``MIN_BARS_WITH_TERM`` bars carrying a
non-null term signal), applied to BOTH BTC and ETH. Below the floor it seals
``EVAL_98_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 ladder floor is
untouched.

This does **not** re-litigate any sealed result: EVAL-74 measured term ratio vs
forward *RV level*; EVAL-84 measured term structure vs forward *vol-of-vol*;
EVAL-96 measured term slope vs forward *VRP*; EVAL-97 measured skew vs forward
*vol-of-vol*; EVAL-98 measures term ratio vs forward *VRP*, reusing all sealed
signal/target reconstructions and the EVAL-65 inference verbatim.

Seals ``EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP_PREREGISTRATION_<UTC>`` then
``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
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

# Reuse the sealed EVAL-61/62/65/71/74/86 primitives verbatim (no forks, no src).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402
import scripts.eval86_surface_skew_forward_vrp_predictiveness as e86  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP_COMBINED"
PREREG_ID = "EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP_PREREGISTRATION"
BLOCKED_ID = "EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP_BLOCKED"

# Single term-structure signal (near/far ATM IV ratio minus 1).
TERM_SIGNAL: str = "term_ratio"
TARGET = "forward_vrp"

# Pre-registered grid (single signal x bar grid x forward horizons -> 6 configs).
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# Reuse EVAL-74 term constants and EVAL-65/62 statistics verbatim.
SIGNAL_WINDOW_SECONDS: float = e74.SIGNAL_WINDOW_SECONDS
ATM_BAND: float = e74.ATM_BAND
MIN_EXPIRY_TRADES: int = e74.MIN_EXPIRY_TRADES
MIN_DISTINCT_EXPIRIES: int = e74.MIN_DISTINCT_EXPIRIES
MIN_BARS_WITH_TERM: int = e74.MIN_BARS_WITH_TERM

PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 120

# Forward VRP target reused VERBATIM from sealed EVAL-86 (do not fork).
_forward_vrp = e86._forward_vrp

# Composed floor: sealed EVAL-74 term floor (EVAL-71 surface + term adequacy),
# verbatim, applied to BOTH BTC and ETH. Not the EVAL-64 ladder floor.
FLOOR: Dict[str, Any] = {
    "min_underlyings": int(e74.FLOOR["min_underlyings"]),
    "min_distinct_expiries": int(MIN_DISTINCT_EXPIRIES),
    "min_expiry_trades": int(MIN_EXPIRY_TRADES),
    "min_bars_with_term": int(MIN_BARS_WITH_TERM),
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "Reuses the sealed EVAL-74 term floor verbatim (EVAL-71 surface floor: "
        "min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, "
        "min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s "
        "+ term adequacy: >= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with >= "
        "MIN_EXPIRY_TRADES trades each and >= MIN_BARS_WITH_TERM bars with a non-null term "
        "signal), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, "
        "never NO-GO. This is NOT the EVAL-64 ladder floor."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
    "scripts/eval86_surface_skew_forward_vrp_predictiveness.py",
    "scripts/eval98_single_asset_term_ratio_forward_vrp.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval98_single_asset_term_ratio_forward_vrp.py "
    "tests/test_eval98_single_asset_term_ratio_forward_vrp.py",
    "python3 -m pytest -q tests/test_eval98_single_asset_term_ratio_forward_vrp.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval98_single_asset_term_ratio_forward_vrp.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval98_single_asset_term_ratio_forward_vrp.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL98-SINGLE-ASSET-TERM-RATIO-FORWARD-VRP",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Floor composition (reuse EVAL-74 term floor verbatim)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    return e74._underlying_term_floor(capture)


def _campaign_floor(per_underlying: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    n_ok = sum(1 for v in per_underlying.values() if v.get("ok"))
    checks = {
        "underlyings_ok": n_ok >= int(FLOOR["min_underlyings"]),
        "all_underlyings_ok": bool(per_underlying) and all(v.get("ok") for v in per_underlying.values()),
    }
    return {"checks": checks, "ok": bool(all(checks.values()))}


# ---------------------------------------------------------------------------
# Evaluation (single signal: term_ratio -> forward VRP)
# ---------------------------------------------------------------------------
def _eval_one_config(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    horizon_bars: int,
    term_signal: str = TERM_SIGNAL,
) -> Dict[str, Any]:
    bars = e74._term_bars(capture, bar_seconds=bar_seconds)
    fwd = _forward_vrp(bars, horizon_bars)
    raw = [b.get(term_signal) for b in bars]
    sig_filled = e71._forward_fill(raw)
    sig_z = e61.expanding_zscore(sig_filled, ZWINDOW)

    xs: List[float] = []
    ys: List[float] = []
    # _forward_vrp returns length max(0, len(bars)-horizon_bars): y_k for bar k
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
        "signal": term_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs": n_pairs,
        "target": "forward_vrp",
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
        "eval": "EVAL-98",
        "title": "Options implied-vol term ratio (near/far ATM IV) -> forward "
                 "variance risk premium (VRP) predictiveness (Spearman rank IC)",
        "extends": "EVAL-74 (same term_ratio signal and sealed term floor) + EVAL-86 "
                   "(same forward VRP target); distinct cell: term ratio -> forward VRP",
        "supersedes": "nothing -- complements EVAL-74/84/85/86/87/96/97; no traded-form claim",
        "capture_dir": str(capture_dir),
        "term_signal": TERM_SIGNAL,
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "min_expiry_trades": int(MIN_EXPIRY_TRADES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar near-to-far ATM IV term ratio (EVAL-74 _term_bars: "
                  "IV(near expiry)/IV(far expiry) - 1), forward-filled and "
                  "expanding-zscored end-of-bar k (reused e71._forward_fill/e61.expanding_zscore)",
        "target_detail": "forward VRP = atm_iv_k - forward_RV_{k+1..k+H}, "
                         "forward_RV = e71._forward_rv = sqrt(mean(r^2)) (reused e86._forward_vrp verbatim)",
        "statistic": "Spearman rank correlation IC = rho(signal_z_k, forward_vrp_k); "
                     "directional permutation H1: IC>0 (higher near/far IV ratio -> richer forward VRP)",
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


def run_eval98(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL98-SINGLE-ASSET-TERM-RATIO-FORWARD-VRP",
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
                    errors.append(f"{cap.get('underlying')}::{TERM_SIGNAL}::bar{bar_s}::h{horizon}: {exc!r}")
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
    campaign_state = "EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP" if floor_ok else "EVAL_98_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free Spearman rank IC between causal term_ratio (near/far ATM IV) "
            "and forward VRP (implied vol - forward realized vol) on real captures"
            if floor_ok else "capture below the composed EVAL-74 term floor; no verdict"
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
            "The causal near-to-far ATM implied-vol term ratio (term_ratio) has a "
            "positive monotone (Spearman rank) relationship with subsequent forward "
            "variance risk premium (implied vol - forward realized vol) of the same "
            "underlying, independent of any trading wrapper; tested on real on-disk "
            "captures at the composed EVAL-74 term floor."
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
        f"# {PREREG_ID} — term ratio -> forward VRP predictiveness (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Hypothesis: {r.get('hypothesis')}",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Extends: {p.get('extends')}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Signal: {p.get('term_signal')}",
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
        "## Pre-registered floor (EVAL-74 term floor, not the EVAL-64 ladder floor)",
        "",
        f"- {fl.get('note')}",
        f"- Min underlyings: {fl.get('min_underlyings')}",
        f"- Min usable pairs per config: {fl.get('min_usable_pairs_per_config')}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — term ratio -> forward VRP predictiveness (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Verdict detail: {r.get('verdict_detail')}",
        f"- Floor OK: {r.get('floor_ok')} (underlyings {', '.join(r.get('underlyings', []))})",
        "",
        "## Per-underlying term floor (EVAL-74, reused verbatim)",
        "",
        "| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |",
        "|---|---|---|---|---|",
    ]
    for inst, fl in r.get("per_underlying_floor", {}).items():
        ta = fl.get("term_adequacy", {})
        lines.append(
            f"| {inst} | {fl.get('eval71_floor_ok')} | {ta.get('n_distinct_expiries')} | "
            f"{ta.get('bars_with_term_max')} | {fl.get('ok')} |"
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
        "verdict_detail": "capture below the composed EVAL-74 term floor; no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "floor": r.get("floor", dict(FLOOR)),
        "per_underlying_floor": r.get("per_underlying_floor", {}),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — term ratio -> forward VRP: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "The capture is below the composed EVAL-74 term floor; no predictiveness "
        "verdict is emitted (never a NO-GO).",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-98: causal term ratio -> forward VRP predictiveness (Spearman rank IC)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL98-SINGLE-ASSET-TERM-RATIO-FORWARD-VRP")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval98(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
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
