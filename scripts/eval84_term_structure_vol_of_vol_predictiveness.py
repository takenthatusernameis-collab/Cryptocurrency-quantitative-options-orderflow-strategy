#!/usr/bin/env python3
"""EVAL-84: does the **options implied-volatility term structure** — the slope
between near-dated and far-dated near-ATM implied vol — predict subsequent
**forward vol-of-vol (variance-of-variance)** of the underlying? A distinct
target falsification that is runnable **now** on the real on-disk three-way
captures.

Why this rung exists (the next runnable-now heavy work after EVAL-83)
---------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now
predictiveness and monetization line EVAL-70..83 is sealed. The term-structure
*signal* cell was tested in EVAL-74 sealed ``NO-GO CONFIRMED (PASS)`` against
**forward realized volatility** (RV = sqrt(mean(log-return^2)) over the forward
window): it predicted ETH forward RV (8 BH-FDR rejections) but was **null on
BTC**, so not portable. EVAL-75 showed that term-structure signal does not
monetize via an ATM straddle. A delta-hedged straddle/VRP position's PnL is
driven by the *path* and *level* of realized variance relative to implied, and
risk-managing it depends on how violently realized variance itself moves — the
**vol-of-vol / variance-of-variance** — which is a *different* forward target
from the RV level EVAL-74 already tested.

EVAL-84 asks the genuinely distinct, on-charter, runnable-**now** question:

    Does the causal term-structure slope (near-minus-far ATM IV) carry monotone
    information about the *subsequent forward volatility of realized variance*
    (vol-of-vol) of the BTC/ETH perpetual over bars ``k+1..k+H``?

This is **not** EVAL-74 (same term-structure signal but EVAL-74's target is
forward *RV level*; EVAL-84's target is forward *vol-of-vol / variance of the
squared-return path*). It is also not EVAL-71/73/77/83 (different surface
signals/targets) and not any sealed traded-form cell. It is runnable **today** on
the already-acquired real on-disk captures (option trade tape with real
iv/strike/expiry + perp candles for both underlyings), with **no new acquisition**
and **no network**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), each causal term-structure signal
``{term_slope, term_ratio}`` (``term_slope = IV(near expiry) - IV(far expiry)``
in vol points; ``term_ratio = IV(near)/IV(far) - 1``), each bar grid
``{60s, 300s}`` and each forward horizon ``H`` bars:

* the causal per-bar near-ATM IV is grouped by option expiry; ``near`` is the
  earliest expiry and ``far`` the latest expiry (each with at least
  ``MIN_EXPIRY_TRADES`` near-ATM trades in the trailing ``SIGNAL_WINDOW_SECONDS``
  window ending at bar end ``k``); both signals are expanding z-scored
  end-of-bar ``k`` exactly as EVAL-71/74 (``e61.expanding_zscore``); and
* the target is the forward **vol-of-vol** over bars ``k+1..k+H``: let
  ``r_i = log(close_i/close_{i-1})`` for the forward window and
  ``v_i = r_i^2`` be the per-bar variance contributions; then
  ``vov_{k,H} = sqrt(mean((v_i - mean(v))^2))`` (the standard deviation of
  squared returns, i.e. the volatility of realized variance along the path).
  This is strictly distinct from EVAL-74's forward RV
  ``sqrt(mean(v_i))``. A config needs at least ``MIN_USABLE_PAIRS_PER_CONFIG``
  usable pairs.

Compute Spearman rank ``IC = rho(signal_z_k, vov_{k+1..k+H})`` with the sealed
EVAL-65 directional permutation and block bootstrap (H1: ``IC > 0`` — a steeper
near-minus-far IV slope / term premium signals more turbulent forward variance
paths). A config **passes** only if ``IC > 0``, directional permutation
``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH and at least one config:** ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and
pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)`` (the
term-structure slope does not portably predict forward vol-of-vol).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-84 consumes the same trade-tape IV data as EVAL-71/74, so it reuses the
sealed EVAL-71 trade-tape floor verbatim on the full capture (option trades /
near-ATM trades / perp candles / span) AND additionally requires the same
term-structure adequacy floor as EVAL-74 (at least ``MIN_DISTINCT_EXPIRIES``
distinct near-ATM expiries with ``MIN_EXPIRY_TRADES`` trades each, and at least
``MIN_BARS_WITH_TERM`` bars carrying a non-null term signal). Neither is
weakened. Below the composed floor it seals
``EVAL_84_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-74 measured the same
term-structure signal against forward *RV* (NO-GO portable). EVAL-84 measures it
against a *different* forward target (vol-of-vol), reusing all sealed signal
reconstructions and the sealed EVAL-65 inference verbatim.

Seals ``EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_PREREGISTRATION_<UTC>``
then ``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import bisect
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
REPORT_ID = "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_COMBINED"
PREREG_ID = "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_BLOCKED"

# Pre-registered grid: term-structure signals x bar grid x horizons (identical
# to EVAL-74's signal/space; only the forward target differs).
TERM_SIGNALS: Tuple[str, ...] = e74.TERM_SIGNALS
GRID_BAR_SECONDS: Tuple[float, ...] = e74.GRID_BAR_SECONDS
FORWARD_HORIZONS_BARS: Tuple[int, ...] = e74.FORWARD_HORIZONS_BARS

# Trailing window / near-ATM band / expiry adequacy reused verbatim from EVAL-74.
SIGNAL_WINDOW_SECONDS: float = e74.SIGNAL_WINDOW_SECONDS
ATM_BAND: float = e74.ATM_BAND
MIN_EXPIRY_TRADES: int = e74.MIN_EXPIRY_TRADES
MIN_DISTINCT_EXPIRIES: int = e74.MIN_DISTINCT_EXPIRIES
MIN_BARS_WITH_TERM: int = e74.MIN_BARS_WITH_TERM

# Statistics reused verbatim from EVAL-65.
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 100

FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_option_trades": 2000,
    "min_near_atm_trades": 200,
    "min_distinct_expiries": int(MIN_DISTINCT_EXPIRIES),
    "min_expiry_trades": int(MIN_EXPIRY_TRADES),
    "min_bars_with_term": int(MIN_BARS_WITH_TERM),
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "Composes the sealed EVAL-71 trade-tape/surface floor for each underlying "
        "(reused verbatim, not weakened) with the EVAL-74 term-structure adequacy "
        "floor (>= min_distinct_expiries distinct near-ATM expiries with >= "
        "min_expiry_trades trades each, and >= min_bars_with_term bars carrying a "
        "non-null term signal). Below the composed floor the campaign seals "
        "BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
    "scripts/eval84_term_structure_vol_of_vol_predictiveness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval84_term_structure_vol_of_vol_predictiveness.py "
    "tests/test_eval84_term_structure_vol_of_vol_predictiveness.py",
    "python3 -m pytest -q tests/test_eval84_term_structure_vol_of_vol_predictiveness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval84_term_structure_vol_of_vol_predictiveness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval84_term_structure_vol_of_vol_predictiveness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL84-TERM-STRUCTURE-VOL-OF-VOL-PREDICTIVENESS",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Forward vol-of-vol target (distinct from EVAL-74's forward RV)
# ---------------------------------------------------------------------------
def _forward_vov(bars: Sequence[Dict[str, Any]], horizon_bars: int) -> List[Optional[float]]:
    """Forward volatility-of-realized-variance over the next ``H`` bars.

    For decision bar ``k`` (target strictly after k) uses log returns
    ``r_i = log(close_i/close_{i-1})`` over bars ``k+1..k+H``. Let
    ``v_i = r_i^2`` be per-bar variance contributions. Returns
    ``vov_k = sqrt(mean((v_i - mean(v))^2))`` (std of squared returns).

    This is strictly distinct from EVAL-71/74 forward RV
    ``sqrt(mean(v_i))``: RV measures the *level* of realized variance, while
    vol-of-vol measures how uneven/turbulent that variance is along the path.

    Returns a list indexed by bar ``k`` of length ``len(bars)``; entries for
    which a full forward window is unavailable are ``None`` (the incomplete tail).
    """
    closes = [float(b["close"]) for b in bars]
    lr = [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)] if len(closes) >= 2 else []
    h = int(horizon_bars)
    out: List[Optional[float]] = [None] * len(bars)
    # Forward window for decision k uses lr[k : k+h] (H returns after k)
    for k in range(0, len(lr) - h + 1):
        seg = lr[k:k + h]
        sq = [r * r for r in seg]
        m = sum(sq) / float(h)
        var = sum((x - m) ** 2 for x in sq) / float(h)
        out[k] = math.sqrt(max(0.0, var))
    return out


# ---------------------------------------------------------------------------
# Floor composition (reuse EVAL-71 + EVAL-74 adequacy verbatim)
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
# Evaluation
# ---------------------------------------------------------------------------
def _eval_one_config(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    horizon_bars: int,
    term_signal: str,
) -> Dict[str, Any]:
    bars = e74._term_bars(capture, bar_seconds=bar_seconds)
    fwd = _forward_vov(bars, horizon_bars)
    raw = [b.get(term_signal) for b in bars]
    sig_filled = e71._forward_fill(raw)
    sig_z = e61.expanding_zscore(sig_filled, ZWINDOW)

    xs: List[float] = []
    ys: List[float] = []
    for k in range(len(bars)):
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
        "target": "forward_vol_of_vol",
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
# Report / sealing
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
    # keep deterministic order BTC, ETH if present
    order = [k for k in ("BTC", "ETH") if k in best] + [k for k in sorted(best) if k not in ("BTC", "ETH")]
    return [best[k] for k in order]


def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report.get("generated_at"),
        "task": report.get("task"),
        "hypothesis": (
            "The causal options implied-vol term structure (near-minus-far ATM IV "
            "slope / ratio) has a positive monotone (Spearman rank) relationship "
            "with subsequent forward vol-of-vol (std of squared log returns) of the "
            "BTC/ETH perpetual, independent of any trading wrapper; tested on real "
            "on-disk captures at the composed EVAL-71 + term-structure floor."
        ),
        "extends": "EVAL-74 (same term-structure signal and floor; different forward target: vol-of-vol vs RV)",
        "protocol": report.get("protocol", {}),
        "capture_dir": report.get("capture_dir"),
        "floor": report.get("floor", dict(FLOOR)),
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r.get("protocol", {})
    lines = [
        f"# {PREREG_ID} — term structure -> forward vol-of-vol predictiveness",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Extends: {r.get('extends')}",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "## Protocol",
        f"- Term signals: {p.get('term_signals')}",
        f"- Bar grids (s): {p.get('bar_seconds_grid')}",
        f"- Horizons (bars): {p.get('forward_horizons_bars')}",
        f"- Target: {p.get('target')}",
        f"- Statistic: {p.get('statistic')}",
        f"- GO bar: {p.get('go_bar')}",
        "",
        "## Floor (composed, not weakened)",
        "```json",
        json.dumps(r.get("floor", FLOOR), indent=2, default=str),
        "```",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — term structure -> forward vol-of-vol predictiveness",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Floor OK: {r.get('floor_ok')} (underlyings {', '.join(r.get('underlyings', []))})",
        "",
        "## Per-underlying (best config by Spearman IC)",
        "",
        "| underlying | configs | best IC | best config | n pass | any pass |",
        "|---|---|---|---|---|---|",
    ]
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
        "verdict_detail": "capture below the composed EVAL-71 + term-structure floor; no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "floor": r.get("floor", dict(FLOOR)),
        "per_underlying_floor": r.get("per_underlying_floor", {}),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — term structure -> forward vol-of-vol: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "The capture is below the composed EVAL-71 + term-structure adequacy floor; "
        "no predictiveness verdict is emitted (never a NO-GO).",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-84",
        "title": "Options implied-vol term structure (near-minus-far ATM IV slope) -> "
                 "forward vol-of-vol / variance-of-variance predictiveness (Spearman rank IC)",
        "extends": "EVAL-74 (same term-structure signal and composed floor; distinct "
                   "forward target: vol-of-vol = std(squared log returns) vs RV = sqrt(mean(squared returns)))",
        "supersedes": "nothing -- complements EVAL-74; does not re-litigate EVAL-71/73/74/77/83",
        "capture_dir": str(capture_dir),
        "term_signals": list(TERM_SIGNALS),
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "min_expiry_trades": int(MIN_EXPIRY_TRADES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar implied-vol term structure (term_slope = IV(near)-IV(far), "
                  "term_ratio = IV(near)/IV(far)-1) from real option trade tape, expanding-"
                  "zscored end-of-bar k (reused e74._term_bars/e61.expanding_zscore)",
        "target": "forward vol-of-vol = sqrt(mean((v_i - mean(v))^2)) where v_i = r_i^2 "
                  "are squared log returns over bars k+1..k+H (distinct from forward RV)",
        "statistic": "Spearman rank correlation IC = rho(signal_z_k, vov_forward_k); "
                     "directional permutation H1: IC>0 (steeper near-minus-far slope -> higher forward vol-of-vol)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle target series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
        },
        "go_bar": (
            "GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, "
            "directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and "
            "pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses already-acquired real on-disk three-way captures (option trades + "
                    "perp candles); no new acquisition, no network",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval84(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL84-TERM-STRUCTURE-VOL-OF-VOL-PREDICTIVENESS",
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
        for sig in TERM_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = _eval_one_config(
                            cap, bar_seconds=bar_s, horizon_bars=horizon, term_signal=sig
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(f"{cap.get('underlying')}::{sig}::bar{bar_s}::h{horizon}: {exc!r}")
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
    campaign_state = "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS" if floor_ok else "EVAL_84_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free Spearman rank IC between causal term-structure slope and forward vol-of-vol on real captures"
            if floor_ok else "capture below the composed EVAL-71 + term-structure floor; no verdict"
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


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-84: term structure -> forward vol-of-vol predictiveness (Spearman rank IC)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL84-TERM-STRUCTURE-VOL-OF-VOL-PREDICTIVENESS")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval84(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
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
