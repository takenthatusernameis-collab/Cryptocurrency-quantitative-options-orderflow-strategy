#!/usr/bin/env python3
"""EVAL-167 TRACK B: does the single-asset causal near-to-far ATM implied-vol
**term slope** (``term_slope`` = IV(near expiry) - IV(far expiry)) predict the
subsequent **forward downside-semivariance share** of the signed return of the
SAME underlying? A distinct, on-charter, runnable-**now** predictiveness cell on
the real on-disk three-way captures — no acquisition, no network, no EVAL-64
floor dependence.

Why this rung exists (anti-avoidance heavy-work backstop, runnable now)
-----------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow -> tradeable, net-of-cost
alpha on REAL public data*. The order-flow distributional sweep (EVAL-149..160)
is uniformly NO-GO CONFIRMED (PASS); the surviving directional alpha is on the
**surface** line (EVAL-104 ``term_slope``->signed return: BTC IC 0.4058 / ETH IC
0.2600). The terminal traded-form deliverable is DATA-BLOCKED on the EVAL-64
floor (no on-disk capture passes). EVAL-167 TRACK B is the runnable-now
predictiveness fallback: it fills the ``term_slope`` cell of the single-asset
surface **downside-semivariance-share** grid (only ``atm_iv`` EVAL-115 and
``skew`` EVAL-165 were sealed). It pairs the single-asset ``term_slope`` signal
with forward **downside-semivariance share** — a genuinely new distributional
target verified absent from the sealed space (no ``downside_semivariance_share``
predictiveness rung on ``term_slope`` exists; distinct from the
``term_slope``->signed-return-*mean* rung EVAL-104, the ``term_slope``->CVaR
rung EVAL-161, and the ``term_ratio``->downside-share rung EVAL-166).

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), each bar grid ``{60s, 300s}`` and each forward
horizon ``H`` bars:

* the causal near-to-far ATM implied-vol term slope ``term_slope`` is
  reconstructed exactly as EVAL-74 (``e74._term_bars``), forward-filled
  (``e71._forward_fill``) and expanding z-scored end-of-bar ``k``
  (``e61.expanding_zscore``, ``e62.ZWINDOW``); and
* the target is the forward **downside-semivariance share** over bars
  ``k+1..k+H``: ``mu = mean(r)``, ``downside = mean(min(r - mu, 0)^2)``,
  ``total = mean((r - mu)^2)``, ``share = downside / total`` over the forward
  log returns ``r_i = log(close_i/close_{i-1})``; windows with non-positive
  total variance yield ``None``.

Compute Spearman rank ``IC = rho(term_slope_z_k, share_{k+1..k+H})`` with the
sealed EVAL-65 directional permutation and block bootstrap (H1: ``IC > 0`` — a
higher causal near-vs-far ATM IV slope precedes a higher forward
downside-semivariance share). A config **passes** only if ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and
at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH and at least one config:** ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and
pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
------------------------------------------------------------------------------
EVAL-167 consumes the same term-structure signal data as EVAL-74/98/99/100/102/
162, so it reuses the sealed **EVAL-74 term floor verbatim** for EACH underlying
(min 2 underlyings; EVAL-71 surface floor: >=
``min_option_trades_per_underlying``=1000 option trades, >=
``min_near_atm_option_trades_per_underlying``=400 near-ATM trades, >=
``min_perp_candles_per_underlying``=1000 perp candles, >=
``min_perp_span_seconds_per_underlying``=82000s perp span; plus term adequacy:
>= ``MIN_DISTINCT_EXPIRIES`` distinct near-ATM expiries with >=
``MIN_EXPIRY_TRADES`` trades each and >= ``MIN_BARS_WITH_TERM`` bars with a
non-null term signal), applied to BOTH BTC and ETH. Below the floor it seals
``EVAL_167_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 ladder floor is
untouched.

Seals ``EVAL_167_SINGLE_ASSET_TERM_SLOPE_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_PREREGISTRATION_<UTC>``
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
REPORT_ID = "EVAL_167_SINGLE_ASSET_TERM_SLOPE_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED"
PREREG_ID = "EVAL_167_SINGLE_ASSET_TERM_SLOPE_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_PREREGISTRATION"
BLOCKED_ID = "EVAL_167_SINGLE_ASSET_TERM_SLOPE_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_BLOCKED"

# Single term-structure signal.
TERM_SIGNAL: str = "term_slope"
TARGET = "forward_downside_semivariance_share"

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
    "scripts/eval167_single_asset_term_slope_forward_downside_semivariance_share.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval167_single_asset_term_slope_forward_downside_semivariance_share.py "
    "tests/test_eval167_single_asset_term_slope_forward_downside_semivariance_share.py",
    "python3 -m pytest -q tests/test_eval167_single_asset_term_slope_forward_downside_semivariance_share.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval167_single_asset_term_slope_forward_downside_semivariance_share.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval167_single_asset_term_slope_forward_downside_semivariance_share.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL167-SINGLE-ASSET-TERM-SLOPE-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Forward realized downside-semivariance share target (verbatim from EVAL-115 /
# EVAL-165).
#
# share = downside_semivariance / total_variance over the forward window;
# downside_semivariance = mean(min(r - mu, 0)^2), total_variance = mean((r -
# mu)^2). Strictly distinct from forward RV level (EVAL-71), signed mean
# (EVAL-101/102/104), return-tail asymmetry (EVAL-85/87), vol-of-vol
# (EVAL-95/97), expected shortfall / CVaR (EVAL-161/164), and realized return
# skewness (EVAL-109/111/112/113).
# ---------------------------------------------------------------------------
def _forward_downside_semivariance_share(
    bars: Sequence[Dict[str, Any]], horizon_bars: int
) -> List[Optional[float]]:
    """Forward downside-semivariance share over the next ``H`` bars.

    For decision bar ``k`` (target strictly after k) uses log returns
    ``r_i = log(close_i / close_{i-1})`` over bars ``k+1..k+H``;
    ``mu = mean(r)``, ``downside_semivar = mean(min(r - mu, 0)**2)``,
    ``total_var = mean((r - mu)**2)``, ``share = downside_semivar / total_var``.
    Windows with non-positive total variance yield ``None`` so they are dropped
    from the pair set. Returns a list indexed by bar ``k``; incomplete tail
    entries are omitted (shorter list).
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
        downside = sum(min(v - mu, 0.0) ** 2 for v in seg) / len(seg)
        val = downside / m2
        out.append(float(val) if math.isfinite(val) else None)
    return out


# ---------------------------------------------------------------------------
# Floor composition (reuse EVAL-74 term floor verbatim)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    return e74._underlying_term_floor(capture)


def _campaign_floor(per_underlying: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    n_ok = sum(1 for v in per_underlying.values() if v.get("ok"))
    checks = {
        "underlyings_ok": n_ok >= int(FLOOR["min_underlyings"]),
        "all_underlyings_ok": bool(per_underlying)
        and all(v.get("ok") for v in per_underlying.values()),
    }
    return {"checks": checks, "ok": bool(all(checks.values()))}


# ---------------------------------------------------------------------------
# Evaluation (single signal: term_slope -> forward downside-semivariance share)
# ---------------------------------------------------------------------------
def _eval_one_config(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    horizon_bars: int,
    term_signal: str = TERM_SIGNAL,
) -> Dict[str, Any]:
    bars = e74._term_bars(capture, bar_seconds=bar_seconds)
    fwd = _forward_downside_semivariance_share(bars, horizon_bars)
    raw = [b.get(term_signal) for b in bars]
    sig_filled = e71._forward_fill(raw)
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
        "signal": term_signal,
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
        inst = str(c.get("underlying", "UNKNOWN"))
        score = len(c.get("option_trades", []) or [])
        prev = best.get(inst)
        if prev is None or score > len(prev.get("option_trades", []) or []):
            best[inst] = c
    order = [k for k in ("BTC", "ETH") if k in best] + [k for k in sorted(best) if k not in ("BTC", "ETH")]
    return [best[k] for k in order]


def run_eval167(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL167-SINGLE-ASSET-TERM-SLOPE-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    selected = _select_captures(str(capture_dir_abs))
    captures = {str(c.get("underlying")): c for c in selected}

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures.values():
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor(c)

    campaign_floor = _campaign_floor(per_underlying_floor)
    floor_ok = bool(campaign_floor.get("ok"))

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures.values():
        for bar_s in GRID_BAR_SECONDS:
            for horizon in FORWARD_HORIZONS_BARS:
                try:
                    res = _eval_one_config(
                        cap, bar_seconds=bar_s, horizon_bars=horizon,
                    )
                except BaseException as exc:  # noqa: BLE001
                    errors.append(
                        f"{cap.get('underlying')}::term_slope::bar{bar_s}::h{horizon}: {exc!r}"
                    )
                    continue
                per_config.append(res)

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
        pass_configs: List[str] = []
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
        "EVAL_167_SINGLE_ASSET_TERM_SLOPE_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE" if floor_ok
        else "EVAL_167_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal options implied-vol TERM SLOPE and forward downside-semivariance "
            "share of the signed return on the real on-disk captures"
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


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-167",
        "title": "Single-asset options implied-vol term slope (near/far "
                 "near-ATM IV) -> forward downside-semivariance share of the signed "
                 "return predictiveness (Spearman rank IC)",
        "extends": "EVAL-74 (identical term_slope signal via _term_bars) + "
                   "EVAL-104 (single-asset term_slope signal path verbatim) + "
                   "EVAL-115/EVAL-165 (forward downside-semivariance-share target "
                   "verbatim) + EVAL-65 (permutation / bootstrap inference) + "
                   "EVAL-62 (FDR / seed / zwindow); distinct cell: single-asset "
                   "term_slope -> forward downside-semivariance share",
        "supersedes": "nothing -- fills the term_slope cell of the downside-"
                      "semivariance-share grid (atm_iv EVAL-115, skew EVAL-165); "
                      "complements EVAL-104 (term_slope -> signed return mean) and "
                      "EVAL-161 (term_slope -> CVaR) with a distributional-dispersion "
                      "target; no traded-form claim",
        "capture_dir": str(capture_dir),
        "term_signal": TERM_SIGNAL,
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "min_expiry_trades": int(MIN_EXPIRY_TRADES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar implied-vol term structure from the real "
                  "Deribit option trade tape: term_slope = IV(near expiry) - IV(far "
                  "expiry), forward-filled then expanding-zscored "
                  "end-of-bar k (reused e61.expanding_zscore)",
        "target_detail": "forward downside-semivariance share = "
                         "downside_semivariance / total_variance over the SAME "
                         "underlying's next H perp log returns (strictly after the "
                         "decision at bar k); downside semivariance = "
                         "mean(min(r - mu, 0)^2), total variance = mean((r - mu)^2)",
        "statistic": "Spearman rank correlation IC = rho(term_slope_z_k, "
                     "downside_share_forward_k); directional "
                     "permutation H1: IC>0 (higher near/far IV slope "
                     "-> higher forward downside-semivariance share)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle downside-semivariance-share series",
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
            "note": "uses the already-acquired real on-disk three-way captures "
                    "(option trades with real iv/strike/expiry + perp candles); no new "
                    "acquisition, no network; reuses EVAL-74's term floor verbatim",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _select_one_capture_per_underlying(
    captures: Sequence[Dict[str, Any]]
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
# Seal artifact builders
# ---------------------------------------------------------------------------
def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "The causal options implied-volatility TERM SLOPE (near-dated divided "
            "by far-dated near-ATM IV, minus one) has a positive monotone (Spearman "
            "rank) relationship with the subsequent forward downside-semivariance "
            "share (downside variance as a fraction of total variance over the next H "
            "perp log returns) of the same underlying's perpetual, independent of any "
            "trading wrapper; tested on the already-acquired real on-disk captures at "
            "the composed EVAL-74 term floor."
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
        f"# {PREREG_ID} — single-asset term slope -> forward downside-semivariance "
        f"share predictiveness (wrapper-free Spearman rank IC)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Term signal: {p['term_signal']}",
        f"- Target: {p['target']}",
        f"- Signal window (s): {p['signal_window_seconds']}",
        f"- Near-ATM band: {p['atm_band']}",
        f"- Min trades per expiry bucket: {p['min_expiry_trades']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Signal: {p['signal']}",
        f"- Target detail: {p['target_detail']}",
        f"- Statistic: {p['statistic']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']} / "
        f"zwindow {p['stats']['zwindow']} / min usable pairs "
        f"{p['stats']['min_usable_pairs_per_config']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered feasible floor (EVAL-74 term floor; NOT EVAL-64)",
        "",
        f"- {fl['note']}",
        f"- min underlyings: {fl['min_underlyings']}",
        f"- min distinct near-ATM expiries: {fl['min_distinct_expiries']}",
        f"- min trades per expiry bucket: {fl['min_expiry_trades']}",
        f"- min bars with a term signal: {fl['min_bars_with_term']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — single-asset term slope -> forward downside-"
        f"semivariance share predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor (EVAL-74 term floor = EVAL-71 surface + term adequacy)",
        "",
        "| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |",
        "|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        ta = fl["term_adequacy"]
        lines.append(
            f"| {inst} | {fl['eval71_floor_ok']} | {ta['n_distinct_expiries']} | "
            f"{ta['bars_with_term_max']} | {fl['ok']} |"
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
        f"# {BLOCKED_ID} — single-asset term slope -> forward downside-semivariance "
        f"share: BELOW FLOOR",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r['capture_dir']}`",
        "",
        "The capture does not meet the composed EVAL-74 term floor, so no GO/NO-GO "
        "verdict is emitted (never a NO-GO). Do NOT weaken the floor, do NOT use "
        "synthetic data, and do NOT emit NO-GO on under-floor data.",
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
        description="EVAL-167 TRACK B: single-asset term slope -> forward "
                    "downside-semivariance share of signed return predictiveness on "
                    "the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL167-SINGLE-ASSET-TERM-SLOPE-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval167(
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
        "per_underlying": report.get("per_underlying"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())