#!/usr/bin/env python3
"""EVAL-165: does the single-asset causal near-ATM implied-vol **skew**
(``skew``, mean near-ATM put IV minus mean near-ATM call IV over the trailing
900s window) predict the subsequent **forward downside-semivariance share** of
the signed return of the SAME underlying? A distinct, on-charter, runnable-**now**
predictiveness cell on the real on-disk three-way captures — no acquisition, no
network, no EVAL-64 floor dependence.

Why this rung exists (anti-avoidance heavy-work backstop, runnable now)
-----------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow -> tradeable, net-of-cost
alpha on REAL public data*. The order-flow distributional sweep (EVAL-149..160)
is uniformly NO-GO CONFIRMED (PASS); the surviving directional alpha is on the
**surface** line (EVAL-101 ``atm_iv``->signed return: BTC IC 0.2313 / ETH IC
0.3442; EVAL-103 ``skew``->signed return).

The single-asset surface distributional-moment grid is nearly complete:
signed-return-mean (EVAL-101/102/103/104), return skewness (EVAL-109/111/112/
113), return kurtosis (EVAL-117/119/121/129), and expected shortfall / CVaR
(EVAL-161/162/163/164) each cover all four surface signals. The one remaining
gap is the **downside-semivariance share** (downside variance as a fraction of
total variance over the forward window): only ``atm_iv`` has been tested
(EVAL-115). EVAL-165 fills the ``skew`` cell of that grid. It is verified absent
from the sealed space (no ``skew``->downside-semivariance-share rung exists;
distinct from EVAL-115 ``atm_iv``->downside-semivariance share, EVAL-164
``skew``->CVaR, EVAL-85 ``skew``->tail asymmetry, EVAL-86 ``skew``->VRP, EVAL-97
``skew``->vol-of-vol, EVAL-111 ``skew``->return skewness, EVAL-121
``skew``->return kurtosis, and EVAL-103 ``skew``->signed-return-mean).

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), each bar grid ``{60s, 300s}`` and each forward
horizon ``H`` bars:

* the causal near-ATM implied-vol skew ``skew`` is reconstructed exactly as
  EVAL-71 / EVAL-103 (``e71.build_surface_bars``, trailing
  ``SIGNAL_WINDOW_SECONDS`` = 900s window, near-ATM band ``ATM_BAND`` = 0.05),
  forward-filled (``e71._forward_fill``) and expanding z-scored end-of-bar ``k``
  (``e61.expanding_zscore``, ``e62.ZWINDOW``); and
* the target is the forward **downside-semivariance share** over bars ``k+1..k+H``:
  ``mu = mean(r)``, ``downside = mean(min(r - mu, 0)^2)``,
  ``total = mean((r - mu)^2)``, ``share = downside / total`` over the forward log
  returns ``r_i = log(close_i/close_{i-1})``; windows with non-positive total
  variance yield ``None``.

Compute Spearman rank ``IC = rho(skew_z_k, share_{k+1..k+H})`` with the sealed
EVAL-65 directional permutation and block bootstrap (H1: ``IC > 0`` — a higher
causal near-ATM skew precedes a higher forward downside-semivariance share).
A config **passes** only if ``IC > 0``, directional permutation ``p < 0.05``,
block-bootstrap 95% CI lower ``> 0``, and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH and at least one config:** ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``,
and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-165 consumes the same trade-tape IV surface data as EVAL-71 / EVAL-115, so
it reuses the sealed **EVAL-71 surface floor verbatim** for EACH underlying
(min 2 underlyings; EVAL-71 surface floor: >=
``min_option_trades_per_underlying``=1000 option trades, >=
``min_near_atm_option_trades_per_underlying``=400 near-ATM trades, >=
``min_perp_candles_per_underlying``=1000 perp candles, >=
``min_perp_span_seconds_per_underlying``=82000s perp span), applied to BOTH
BTC and ETH. Below the floor it seals ``EVAL_165_..._BLOCKED_<UTC>`` (never a
NO-GO). The EVAL-64 ladder floor is untouched.

Seals ``EVAL_165_SINGLE_ASSET_SKEW_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_PREREGISTRATION_<UTC>``
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
REPORT_ID = "EVAL_165_SINGLE_ASSET_SKEW_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED"
PREREG_ID = "EVAL_165_SINGLE_ASSET_SKEW_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_PREREGISTRATION"
BLOCKED_ID = "EVAL_165_SINGLE_ASSET_SKEW_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_BLOCKED"

# Single surface signal (near-ATM put-call implied-vol skew, e71.build_surface_bars).
SURFACE_SIGNAL: str = "skew"
TARGET = "forward_downside_semivariance_share"

# Pre-registered grid (single signal x bar grid x forward horizons -> 6 configs).
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# Reuse EVAL-71 surface signal constants verbatim.
SIGNAL_WINDOW_SECONDS: float = e71.SIGNAL_WINDOW_SECONDS
ATM_BAND: float = e71.ATM_BAND

PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 100

# Composed floor: sealed EVAL-71 surface floor verbatim, applied to BOTH BTC
# and ETH. Not the EVAL-64 ladder floor.
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-165 consumes each underlying's causal options-surface series "
        "(real option trade tape for the IV surface, real perp candles for "
        "forward returns) and reuses the sealed EVAL-71 surface floor for "
        "EACH underlying (verbatim, neither weakened). Below the composed "
        "floor the campaign seals BLOCKED, never NO-GO. This is NOT the "
        "EVAL-64 options-surface snapshot floor, which governs the EVAL-67/"
        "68/69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval165_single_asset_skew_forward_downside_semivariance_share.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval165_single_asset_skew_forward_downside_semivariance_share.py "
    "tests/test_eval165_single_asset_skew_forward_downside_semivariance_share.py",
    "python3 -m pytest -q tests/test_eval165_single_asset_skew_forward_downside_semivariance_share.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval165_single_asset_skew_forward_downside_semivariance_share.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval165_single_asset_skew_forward_downside_semivariance_share.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL165-SINGLE-ASSET-SKEW-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Forward realized downside-semivariance share target (verbatim from EVAL-115).
#
# share = downside_semivariance / total_variance over the forward window;
# downside_semivariance = mean(min(r - mu, 0)^2), total_variance = mean((r -
# mu)^2). Strictly distinct from forward RV level (EVAL-71), signed mean
# (EVAL-101/102/104), return-tail asymmetry (EVAL-85/87), vol-of-vol
# (EVAL-95/97), expected shortfall / CVaR (EVAL-164), and realized return
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
# Per-asset causal surface z-series + forward downside semivariance share
# ---------------------------------------------------------------------------
def _asset_surface_series(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    horizon_bars: int,
    surface_signal: str = SURFACE_SIGNAL,
    signal_window_seconds: float = SIGNAL_WINDOW_SECONDS,
    atm_band: float = ATM_BAND,
) -> Dict[int, Dict[str, Any]]:
    """Causal per-bar surface signal z-series and forward downside semivariance
    share for one asset.

    Returns ``{bar_open_ms: {"skew_z", "skew", "fwd_downside_share"}}`` where:

    * ``skew_z`` is the causal near-ATM skew surface signal forward-filled then
      expanding-z-scored (EVAL-61 ``expanding_zscore``), reusing EVAL-71
      ``build_surface_bars`` verbatim;
    * ``skew`` is the near-ATM put-minus-call implied-vol skew at bar k
      (forward-filled);
    * ``fwd_downside_share`` is the forward downside-semivariance share over
      the *next* H perp bars (strictly after the decision at bar k).
    """
    bars = e71.build_surface_bars(
        capture,
        bar_seconds=bar_seconds,
        signal_window_seconds=signal_window_seconds,
        atm_band=atm_band,
    )
    fwd = _forward_downside_semivariance_share(bars, horizon_bars)

    sig_filled = e71._forward_fill([b.get(surface_signal) for b in bars])
    sig_z = e61.expanding_zscore(sig_filled, ZWINDOW)

    out: Dict[int, Dict[str, Any]] = {}
    n_fwd = len(fwd)
    for k, b in enumerate(bars):
        out[int(b["bar_open_ms"])] = {
            "skew_z": float(sig_z[k]) if k < len(sig_z) else 0.0,
            "skew": float(sig_filled[k]) if k < len(sig_filled) else 0.0,
            "fwd_downside_share": float(fwd[k]) if k < n_fwd else None,
        }
    return out


# ---------------------------------------------------------------------------
# Per-(underlying, signal, grid, horizon) predictiveness
# ---------------------------------------------------------------------------
def evaluate_config(
    capture: Dict[str, Any],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Own-asset: near-ATM skew z at bar k -> forward downside semivariance share
    over bars k+1..k+H."""
    underlying = str(capture.get("underlying", "UNDERLYING"))

    series = _asset_surface_series(
        capture,
        bar_seconds=bar_seconds,
        horizon_bars=horizon_bars,
        surface_signal=surface_signal,
    )

    xs: List[float] = []
    ys: List[float] = []
    for t in sorted(series):
        y = series[t].get("fwd_downside_share")
        if y is None:
            continue
        xs.append(float(series[t].get("skew_z", 0.0)))
        ys.append(float(y))

    n_pairs = len(xs)
    base = {
        "underlying": underlying,
        "signal": surface_signal,
        "target": TARGET,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
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
        "eval": "EVAL-165",
        "title": "Causal near-ATM implied-vol surface SKEW -> subsequent forward "
                 "downside-semivariance share (Spearman rank IC) predictiveness on "
                 "the real on-disk captures",
        "extends": "EVAL-71 (own-asset surface atm_iv+skew -> own forward RV "
                   "level) + EVAL-115 (single-asset atm_iv -> forward downside-"
                   "semivariance share): same Spearman rank-IC statistic, signal "
                   "reconstruction and target reused verbatim, but a distinct "
                   "on-charter signal x target cell — near-ATM SKEW (surface) -> "
                   "forward downside-semivariance share; no new acquisition",
        "supersedes": "nothing — completes the skew cell of the downside-"
                      "semivariance-share grid (atm_iv EVAL-115) and complements "
                      "EVAL-164 (skew -> CVaR); does not re-litigate them and "
                      "makes no traded-form claim",
        "capture_dir": str(capture_dir),
        "surface_signals": [SURFACE_SIGNAL],
        "target": TARGET,
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal near-ATM implied-vol surface SKEW z (EVAL-71 "
                  "build_surface_bars + EVAL-61 expanding_zscore, end-of-bar k)",
        "target_detail": "forward downside-semivariance share = "
                         "downside_semivariance / total_variance over the SAME "
                         "underlying's next H perp log returns (strictly after "
                         "the decision at bar k); downside semivariance = "
                         "mean(min(r - mu, 0)^2), total variance = "
                         "mean((r - mu)^2)",
        "statistic": "Spearman rank correlation IC = rho(skew_z_k, "
                     "downside_semivariance_share_k); directional "
                     "permutation H1: IC > 0",
        "go_bar": (
            "GO only if, on BOTH BTC and ETH and at least one config, Spearman "
            "IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI "
            "lower > 0, and pooled BH-FDR rejects that config; else NO-GO "
            "CONFIRMED (PASS)."
        ),
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
        "data_availability": {
            "note": "uses already-acquired real on-disk three-way captures "
                    "(option trades + perp candles); no new acquisition, no network",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval165(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL165-SINGLE-ASSET-SKEW-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE",
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
                    res = evaluate_config(
                        cap,
                        surface_signal=SURFACE_SIGNAL,
                        bar_seconds=bar_s,
                        horizon_bars=horizon,
                    )
                except BaseException as exc:  # noqa: BLE001
                    errors.append(
                        f"{cap.get('underlying')}::{SURFACE_SIGNAL}::bar{bar_s}::h{horizon}: {exc!r}"
                    )
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
        "EVAL_165_SINGLE_ASSET_SKEW_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE"
        if floor_ok
        else "EVAL_165_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free Spearman rank IC between causal near-ATM implied-vol "
            "surface SKEW and forward downside-semivariance share on real captures"
            if floor_ok
            else "capture below the composed EVAL-71 surface floor; no verdict"
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
            "The causal near-ATM implied-vol surface SKEW (near-dated near-ATM "
            "mean put IV minus mean call IV over the trailing 900s window, "
            "expanding-z-scored) has a positive monotone (Spearman rank) "
            "relationship with the subsequent forward downside-semivariance share "
            "(downside variance as a fraction of total variance over the next H "
            "perp log returns) of the SAME underlying, independent of any trading "
            "wrapper; tested on real on-disk captures at the composed EVAL-71 "
            "surface floor."
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
        f"# {PREREG_ID} — causal near-ATM implied-vol skew -> forward "
        f"downside-semivariance share (Spearman rank IC)",
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
        "## Pre-registered composed floor (EVAL-71 surface, not the EVAL-64 ladder floor)",
        "",
        f"- {fl.get('note')}",
        f"- Min underlyings: {fl.get('min_underlyings')}",
        f"- Min usable pairs per config: {fl.get('min_usable_pairs_per_config')}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r.get("campaign_floor", {})
    lines = [
        f"# {r['report_id']} — causal near-ATM implied-vol skew -> forward "
        f"downside-semivariance share (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Verdict detail: {r.get('verdict_detail')}",
        f"- Floor OK: {r.get('floor_ok')} (underlyings {', '.join(r.get('underlyings', []))})",
        "",
        "## Per-underlying surface floor (EVAL-71, reused verbatim)",
        "",
        "| underlying | n option trades | n near-ATM | n perp candles | span (s) | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        lines.append(
            f"| {inst} | {u.get('n_option_trades')} | {u.get('n_near_atm_option_trades')} | "
            f"{u.get('n_perp_candles')} | {u.get('perp_span_seconds')} | {u.get('ok')} |"
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
        "task": r.get("task", "EVAL165-SINGLE-ASSET-SKEW-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE"),
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
        f"# {BLOCKED_ID} — near-ATM implied-vol skew -> forward downside-semivariance share: BELOW FLOOR",
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
        description="EVAL-165: causal near-ATM implied-vol skew -> forward "
                    "downside-semivariance share predictiveness (Spearman rank IC)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL165-SINGLE-ASSET-SKEW-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval165(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(),
                "task": args.task_label,
                "capture_dir": args.capture_dir,
                "underlyings": [],
                "floor": dict(FLOOR),
                "per_underlying_floor": {},
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