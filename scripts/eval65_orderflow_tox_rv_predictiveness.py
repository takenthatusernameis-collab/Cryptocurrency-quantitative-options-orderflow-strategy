#!/usr/bin/env python3
"""EVAL-65: **does the options order-flow toxicity signal predict subsequent
realized volatility at all?** — a wrapper-free, information-content falsification.

Why this rung exists (the one question EVAL-62/64 leave open)
------------------------------------------------------------
EVAL-62 and EVAL-64 both sealed ``NO-GO CONFIRMED (PASS)`` for the *trade* form of
the namesake hypothesis (signal-timed delta-hedged ATM straddle, correct mark-path
net-of-cost P&L): on the heaviest achievable real sample (BTC best Sharpe -0.5837,
ETH -0.0954, any_pass=false) the traded strategy does not survive. But a negative
*traded* result cannot distinguish two very different worlds:

  (A) the options order-flow toxicity signal is **informationally null** — it has
      no monotone relationship with subsequent realized volatility, so no wrapper
      (straddle, variance swap, risk-reversal) could ever monetize it; or
  (B) the signal **does** carry information, but the specific ATM-straddle wrapper
      and its costs (2-leg spread, hedge fees, discrete delta hedging) destroy it.

EVAL-65 answers this directly and decisively: it strips away the wrapper and
measures the **rank information coefficient (Spearman) between the causal options
order-flow toxicity signal at bar ``k`` and the forward realized volatility over the
next ``H`` bars**, on the **same real 7d BTC+ETH captures** (no new acquisition, no
network). This is genuinely new (a predictiveness measurement, not a P&L), heavy
(full capture load + multi-horizon forward RV + permutation + block bootstrap +
BH-FDR), and reusable: it imports the sealed EVAL-62 ``build_states`` so the
toxicity signal and spot series are **byte-for-byte identical** to EVAL-62/64.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of EVAL-62/64)
-------------------------------------------------------------------------
For each underlying (BTC, ETH), each toxicity variant ``{tox, imbalance}``, each bar
grid ``{60s, 300s}`` and each forward horizon ``H`` bars, compute the Spearman rank
correlation ``IC = rho(signal_z_k, rv_{k+1..k+H})`` where ``rv`` is the forward
realized volatility from real perp 1m/5m log returns. **GO only if, on BOTH BTC and
ETH and at least one config:** ``IC > 0``, directional permutation ``p < 0.05``,
block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else
``NO-GO CONFIRMED (PASS)``.

If EVAL-65 seals **NO-GO**, the namesake options-order-flow -> volatility hypothesis
is informationally null on real data (world A): the strategy cannot be rescued by a
different wrapper, and the campaign is honestly, finally closed. If it seals **GO**,
that is a major finding that re-opens the traded-form investigation with a known-
predictive signal.

Feasible floor: identical to EVAL-64 (reused verbatim from the sealed EVAL-64 module:
``e64._underlying_floor_strict`` / ``e64.MIN_UNDERLYINGS``), i.e. the heaviest floor
the free Deribit/OKX public API can deliver on these captures. Below floor seals
``EVAL_65_..._BLOCKED_<UTC>`` (never a NO-GO).

Seal ``EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_<UTC>.{json,md}`` (before
measurement) then ``EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_<UTC>.{json,md}``
(or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the sealed EVAL-61/EVAL-62 measurement + EVAL-64 feasible floor verbatim.
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED"
PREREG_ID = "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_BLOCKED"

# Grid (pre-registered; identical signals/bar-grid to EVAL-62/64).
TOX_SIGNALS: Tuple[str, ...] = e62.TOX_SIGNALS
GRID_BAR_SECONDS: Tuple[float, ...] = e62.GRID_BAR_SECONDS
# Forward realized-vol horizons in bars (multi-scale: minutes -> hours).
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# Stats (pre-registered).
PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED

# Feasible floor reused verbatim from the sealed EVAL-64 module.
_underlying_floor_strict = e64._underlying_floor_strict
MIN_UNDERLYINGS = e64.MIN_UNDERLYINGS

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval60_acquire_three_way.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval64_orderflow_realized_vol_markpath_feasible.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval65_orderflow_tox_rv_predictiveness.py "
    "tests/test_eval65_orderflow_tox_rv_predictiveness.py",
    "python3 -m pytest -q tests/test_eval65_orderflow_tox_rv_predictiveness.py",
    "# reuse the already-acquired real 7d captures (no re-acquisition needed):",
    "python3 scripts/eval65_orderflow_tox_rv_predictiveness.py "
    "--capture-dir data/raw/eval63 --no-write",
    "python3 scripts/eval65_orderflow_tox_rv_predictiveness.py "
    "--capture-dir data/raw/eval63 --seal --task-label EVAL65-OFLOW-TOX-RV-PREDICTIVENESS",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_for_filename(iso_ts: str) -> str:
    return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return v


def _rankdata(xs: Sequence[float]) -> List[float]:
    """Average ranks (ties share the mean rank)."""
    n = len(xs)
    order = sorted(range(n), key=lambda i: xs[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(x: Sequence[float], y: Sequence[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((v - mx) ** 2 for v in x)
    syy = sum((v - my) ** 2 for v in y)
    if sxx <= 0.0 or syy <= 0.0:
        return 0.0
    sxy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    return sxy / math.sqrt(sxx * syy)


def _spearman(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    return _pearson(_rankdata(x), _rankdata(y))


def _perm_p_ic(x: Sequence[float], y: Sequence[float], n_perm: int, seed: int) -> Tuple[float, float]:
    """Directional permutation p for H1: IC > 0 (shuffle the realized-vol series)."""
    obs = _spearman(x, y)
    rng = random.Random(seed)
    yy = list(y)
    n = len(yy)
    cnt = 0
    for _ in range(n_perm):
        rng.shuffle(yy)
        if _spearman(x, yy) >= obs:
            cnt += 1
    return obs, (1.0 + cnt) / (1.0 + n_perm)


def _boot_ci_ic(
    x: Sequence[float], y: Sequence[float],
    n_boot: int, block: int, seed: int,
) -> Tuple[float, float, float]:
    """Block-bootstrap 95% CI for the Spearman IC over paired (signal, rv) points."""
    n = len(x)
    if n < 4:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    block = max(1, int(block))
    stats: List[float] = []
    for _ in range(n_boot):
        idx: List[int] = []
        while len(idx) < n:
            start = rng.randint(0, max(0, n - block))
            for b in range(block):
                if len(idx) < n:
                    idx.append(min(n - 1, start + b))
        xs = [x[i] for i in idx]
        ys = [y[i] for i in idx]
        stats.append(_spearman(xs, ys))
    stats.sort()
    lo = stats[int(0.025 * (len(stats) - 1))]
    hi = stats[int(0.975 * (len(stats) - 1))]
    med = stats[len(stats) // 2]
    return med, lo, hi


# ---------------------------------------------------------------------------
# Per-config predictiveness (reuses EVAL-62 build_states for signal + spot)
# ---------------------------------------------------------------------------
def evaluate_predictiveness(
    capture: Dict[str, Any],
    *,
    tox_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    states = e62.build_states(capture, tox_signal=tox_signal, bar_seconds=bar_seconds)
    pts = [
        (float(s["spot"]), float(s.get("signal_z", 0.0)))
        for s in states
        if float(s.get("spot", 0.0)) > 0.0
    ]
    if len(pts) < horizon_bars + 5:
        return {
            "underlying": inst, "signal": tox_signal,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient priced states", "n_pairs": 0, "pass": False,
        }
    spot = [p[0] for p in pts]
    sigz = [p[1] for p in pts]
    lr = [math.log(spot[i + 1] / spot[i]) for i in range(len(spot) - 1)]

    xs: List[float] = []
    ys: List[float] = []
    for k in range(0, len(lr) - horizon_bars + 1):
        seg = lr[k:k + horizon_bars]
        rv = math.sqrt(sum(r * r for r in seg) / float(horizon_bars))
        xs.append(sigz[k])
        ys.append(rv)

    if len(xs) < 8:
        return {
            "underlying": inst, "signal": tox_signal,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient aligned pairs", "n_pairs": len(xs), "pass": False,
        }

    ic, perm_p = _perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = _boot_ci_ic(xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED)
    passed = bool(ic > 0.0 and perm_p < 0.05 and ci_lo > 0.0 and len(xs) >= 20)
    return {
        "underlying": inst,
        "signal": tox_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs": len(xs),
        "n_states": len(states),
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-65",
        "title": "Options order-flow toxicity -> subsequent realized volatility: "
                 "wrapper-free rank information coefficient (predictiveness) "
                 "falsification on real 7d BTC+ETH captures",
        "extends": "EVAL-62/EVAL-64 (identical causal toxicity signal + spot series "
                   "via sealed build_states; feasible floor reused verbatim from "
                   "EVAL-64; no P&L, no wrapper)",
        "supersedes": "nothing — this is the information-content follow-up that "
                      "disambiguates EVAL-62/64 NO-GO (null signal vs. wrapper cost)",
        "capture_dir": str(capture_dir),
        "tox_signals": list(TOX_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "signal_z_k = expanding-zscore of per-bar options order-flow "
                  "toxicity (tox) / signed-aggressor imbalance (imbalance), reused "
                  "verbatim from EVAL-61/EVAL-62 (causal, end-of-bar k)",
        "target": "rv_{k+1..k+H} = sqrt(mean(log-return^2)) over the next H perp "
                  "1m/5m bars (forward realized vol, strictly after the decision at k)",
        "statistic": "Spearman rank correlation IC = rho(signal_z_k, rv_forward_k)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle realized-vol series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "pbo_k_folds": e62.PBO_K_FOLDS,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
        },
        "go_bar": (
            "GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, "
            "directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and "
            "pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses the already-acquired real 7d captures; no new acquisition, "
                    "no network; the feasible floor is reused verbatim from sealed EVAL-64",
            "measured_capture": "data/raw/eval63/three_way_BTC_20261116T064816Z.json, "
                                "data/raw/eval63/three_way_ETH_20261116T064816Z.json",
        },
        "floor": e64.build_protocol(str(capture_dir))["floor"],
    }


def run_eval65(
    *,
    capture_dir: str = "data/raw/eval63",
    write: bool = True,
    task_label: str = "EVAL65-OFLOW-TOX-RV-PREDICTIVENESS",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = e61._capture_inventory(str(capture_dir_abs))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor_strict(c)

    floor_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures:
        for sig in TOX_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_predictiveness(
                            cap, tox_signal=sig, bar_seconds=bar_s, horizon_bars=horizon
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{cap.get('underlying')}::{sig}::bar{bar_s}::h{horizon}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    # BH-FDR over all config permutation p-values (pooled).
    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}":
            _finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)

    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        valid = [r for r in rows if r.get("n_pairs", 0) > 0]
        best = None
        if valid:
            best = max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9))
        pass_configs = []
        for r in valid:
            key = (
                f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::"
                f"h{r['horizon_bars']}"
            )
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::bar{best['bar_seconds']}::h{best['horizon_bars']}"
                if best else "n/a"
            ),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS" if floor_ok else "EVAL_65_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between causal "
            "options order-flow toxicity and forward realized volatility on the real "
            "7d BTC+ETH captures (reused EVAL-62 signal + EVAL-64 feasible floor)"
            if floor_ok else "capture below the pre-registered feasible floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": build_protocol(capture_dir)["floor"],
        "per_underlying_floor": per_underlying_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "bh_fdr": bh,
            "all_underlyings_pass": all_pass,
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


def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "The causal options order-flow toxicity signal (tox / signed-aggressor "
            "imbalance) has a positive monotone (Spearman rank) relationship with "
            "subsequent forward realized volatility on the BTC/ETH perpetual, "
            "independent of any trading wrapper; tested on the already-acquired real "
            "7d captures at the EVAL-64 feasible floor."
        ),
        "extends": p["extends"],
        "data_availability": p["data_availability"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    fl = p["floor"]
    lines = [
        f"# {PREREG_ID} — options order-flow toxicity -> realized-vol predictiveness "
        f"(wrapper-free Spearman rank IC)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Tox signals: {p['tox_signals']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Signal: {p['signal']}",
        f"- Target: {p['target']}",
        f"- Statistic: {p['statistic']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered feasible floor (reused verbatim from sealed EVAL-64)",
        "",
        f"- min surface snapshots/underlying: {fl['min_surface_snapshots_per_underlying']}",
        f"- min surface 5m bars/underlying: {fl['min_surface_bars_5m_per_underlying']}",
        f"- min Deribit option trades/underlying: {fl['min_option_trades_per_underlying']}",
        f"- min perp 5m bars/underlying: {fl['min_perp_bars_5m_per_underlying']}",
        f"- min perp span seconds/underlying: {fl['min_perp_span_seconds_per_underlying']}",
        f"- min common 5m bars/underlying: {fl['min_common_bars_per_underlying']}",
        f"- min underlyings: {fl['min_underlyings']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — options order-flow toxicity -> realized-vol "
        f"predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor",
        "",
        "| underlying | snaps | surf inst | 5m bars | deribit trades | perp bars | perp span s | common 5m | ok |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['n_surface_snapshots']} | {fl['n_surface_instruments']} | "
            f"{fl['n_surface_bars_5m']} | {fl['n_option_trades']} | "
            f"{fl['n_perp_bars_5m']} | {fl['perp_span_seconds']:.0f} | "
            f"{fl['n_common_bars_5m']} | {fl['ok']} |"
        )
    lines += ["", "## Per-underlying (best config by Spearman IC)", "",
              "| underlying | configs | best IC | best config | n pass | any pass |",
              "|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_ic']:.4f} | "
            f"{s['best_config']} | {s['n_pass']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- All underlyings pass: {r['pooled']['all_underlyings_pass']}"]
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
        "per_underlying_floor": r["per_underlying_floor"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — options order-flow toxicity -> realized-vol predictiveness "
        f"(below the pre-registered feasible floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered feasible floor (reused from "
        "sealed EVAL-64), so no GO/NO-GO verdict is emitted. Do NOT weaken the floor, "
        "do NOT use synthetic data, and do NOT emit NO-GO on under-floor data.",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(f"- {inst}: {json.dumps(fl['checks'])}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-65: wrapper-free options order-flow toxicity -> realized-vol "
                    "predictiveness (Spearman rank IC) on real 7d BTC/ETH captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval63")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL65-OFLOW-TOX-RV-PREDICTIVENESS")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval65(
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
                "per_underlying_floor": {},
                "floor": build_protocol(args.capture_dir)["floor"],
                "floor_ok": False,
                "errors": [repr(exc)],
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