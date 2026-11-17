#!/usr/bin/env python3
"""EVAL-73: is EVAL-71's predictive-surface **GO** *temporally stable* out of
sample — does the positive surface -> forward-vol information replicate across a
**disjoint early/late split** of the real on-disk captures?

Why this rung exists (the next runnable-now heavy work)
------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``) is
*crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now line is now:

* EVAL-71 sealed ``GO CONFIRMED`` — the causal options implied-vol *surface*
  (near-ATM IV level + put-call skew, from the real Deribit option trade tape)
  predicts forward realized vol of the BTC/ETH perpetual (BTC best IC 0.335, ETH
  0.263);
* EVAL-72 sealed ``NO-GO CONFIRMED (PASS)`` — that predictive surface signal does
  **not** monetize net-of-cost via a signal-timed delta-hedged ATM straddle.

That leaves one honest, on-charter, runnable-**now** question that does **not**
re-litigate either sealed result: **is EVAL-71's single full-sample GO robust, or
a regime artifact of one period?** A GO measured on one pooled window is only as
trustworthy as its stability across time. EVAL-73 splits each underlying's real
capture into **two disjoint temporal halves** at the perp-candle midpoint and
asks whether the predictive surface signal has the **same (positive) sign in both
halves**. This is genuinely new (a temporal-stability / OOS-replication test, not
a re-run of EVAL-71), on the repo charter, and needs only the already-acquired
real on-disk captures — **no new acquisition, no network**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), each causal surface signal ``{atm_iv, skew}``
(trailing-window near-ATM trade-weighted IV level / put-minus-call IV, expanding
z-scored end-of-bar ``k``), each bar grid ``{60s, 300s}`` and each forward
horizon ``H`` bars:

* the **full-sample** Spearman rank ``IC`` and its directional permutation ``p``
  are computed exactly as in EVAL-71 (reused verbatim via
  ``e71.evaluate_predictiveness``); and
* each **disjoint half** (early ``< midpoint``, late ``>= midpoint``) carries its
  own Spearman rank ``IC`` (reused ``e65._spearman`` primitive).

A config is **STABLE** iff ``n_pairs`` in EACH half ``>= MIN_HALF_PAIRS``, the
half ICs are **both strictly positive** (``IC_early > 0`` and ``IC_late > 0``),
and the full-sample directional permutation ``p < 0.05``. **GO only if, on BOTH
BTC and ETH and at least one config, that config is STABLE and pooled BH-FDR
rejects its full-sample ``p``; else ``NO-GO CONFIRMED (PASS)``** (i.e. EVAL-71's
predictive surface GO does not replicate across the disjoint temporal split).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-73 consumes the same trade-tape IV data as EVAL-71, so it reuses the sealed
EVAL-71 trade-tape floor verbatim on the full capture (option trades / near-ATM
trades / perp candles / span) AND additionally requires each disjoint half to be
independently analyzable (a derived, *stricter* per-half adequacy floor: perp
candles and near-ATM trades per half). Neither is weakened. Below the composed
floor it seals ``EVAL_73_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64
feasible floor that governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_PREREGISTRATION_<UTC>`` then
``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
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

# Reuse the sealed EVAL-61/62 primitives + EVAL-65 statistics + EVAL-71 surface
# machinery verbatim (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_COMBINED"
PREREG_ID = "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_PREREGISTRATION"
BLOCKED_ID = "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_BLOCKED"

# Pre-registered grid: identical surface signals x bar grid x horizons as EVAL-71
# (this is a stability check of EVAL-71's exact configs, not a new grid).
SURFACE_SIGNALS: Tuple[str, ...] = ("atm_iv", "skew")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# Statistics / cost constants reused verbatim from EVAL-65 / EVAL-62 (no forks).
ZWINDOW = e62.ZWINDOW
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED

# Per-half adequacy floor (derived, STRICTER than EVAL-71's full-capture floor):
# each disjoint half must independently carry enough data to compute a rank IC.
MIN_HALF_PERP_CANDLES = 300
MIN_HALF_NEAR_ATM_TRADES = 100
# Minimum aligned (signal, rv) pairs per half for a half IC to be trustworthy.
MIN_HALF_PAIRS = 30

# Pre-registered feasible floor for THIS campaign (reuses EVAL-71's floor verbatim
# on the full capture, plus a derived per-half adequacy requirement).
FLOOR: Dict[str, Any] = {
    "min_underlyings": e71.FLOOR["min_underlyings"],
    "min_half_perp_candles": MIN_HALF_PERP_CANDLES,
    "min_half_near_atm_trades": MIN_HALF_NEAR_ATM_TRADES,
    "min_half_pairs": MIN_HALF_PAIRS,
    "note": (
        "EVAL-73 reuses the sealed EVAL-71 trade-tape IV floor verbatim on the "
        "full capture (NOT weakened) and additionally requires each disjoint "
        "early/late half to be independently analyzable (perp candles / near-ATM "
        "trades per half) -- a derived, stricter per-half adequacy floor. This is "
        "NOT the EVAL-64 options-surface snapshot floor, which governs the "
        "EVAL-67/68/69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval73_surface_iv_rv_stability_split.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval73_surface_iv_rv_stability_split.py "
    "tests/test_eval73_surface_iv_rv_stability_split.py",
    "python3 -m pytest -q tests/test_eval73_surface_iv_rv_stability_split.py",
    "# no acquisition needed -- consume the already-acquired real captures:",
    "python3 scripts/eval73_surface_iv_rv_stability_split.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval73_surface_iv_rv_stability_split.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL73-SURFACE-IV-RV-STABILITY-SPLIT",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e61._finite(x, default)


def _midpoint_ms(capture: Dict[str, Any]) -> int:
    """Temporal midpoint (ms) of the capture's perp candles; 0 if <2 candles."""
    ts = [
        int(c.get("ts") or 0)
        for c in capture.get("perp_candles", []) or []
        if int(c.get("ts") or 0) > 0
    ]
    if len(ts) < 2:
        return 0
    return (min(ts) + max(ts)) // 2


def _split_capture(
    capture: Dict[str, Any], midpoint_ms: int
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Split a capture into two **disjoint** temporal halves at ``midpoint_ms``.

    Early half: perp candles / option trades with ``ts < midpoint_ms``.
    Late half:  perp candles / option trades with ``ts >= midpoint_ms``.
    All other capture fields are shared (shallow copy); only the two data lists
    are partitioned, so the halves never share a bar or trade.
    """
    mid = int(midpoint_ms)

    def _part(key: str, pred) -> List[Dict[str, Any]]:
        return [r for r in (capture.get(key, []) or []) if pred(int(r.get("ts") or 0))]

    early = dict(capture)
    late = dict(capture)
    early["perp_candles"] = _part("perp_candles", lambda t: t < mid)
    late["perp_candles"] = _part("perp_candles", lambda t: t >= mid)
    early["option_trades"] = _part("option_trades", lambda t: t < mid)
    late["option_trades"] = _part("option_trades", lambda t: t >= mid)
    return early, late


def _align_pairs(
    bars: Sequence[Dict[str, Any]], surface_signal: str, horizon_bars: int
) -> Tuple[List[float], List[float]]:
    """Aligned (signal_z_k, forward_rv_k) pairs over a bar series.

    Assembles EVAL-71's own primitives (``build_surface_bars`` output ->
    ``_forward_rv`` -> ``_forward_fill`` -> ``e61.expanding_zscore``); the causal
    ordering and z-window are identical to EVAL-71.
    """
    h = int(horizon_bars)
    if len(bars) < h + 5:
        return [], []
    ys_all = e71._forward_rv(bars, h)
    raw = [b.get(surface_signal) for b in bars]
    sig_filled = e71._forward_fill(raw)
    sig_z = e61.expanding_zscore(sig_filled, ZWINDOW)
    xs: List[float] = []
    ys: List[float] = []
    for k in range(len(ys_all)):
        xs.append(float(sig_z[k]) if k < len(sig_z) else 0.0)
        ys.append(float(ys_all[k]))
    return xs, ys


def _half_ic(
    capture: Dict[str, Any],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Spearman rank IC of the surface signal vs forward RV **within one half**.

    Reuses ``e65._spearman`` (the exact sealed rank-IC primitive EVAL-71 uses);
    no permutation / bootstrap here (those are full-sample, EVAL-71 verbatim).
    """
    bars = e71.build_surface_bars(capture, bar_seconds=bar_seconds)
    xs, ys = _align_pairs(bars, surface_signal, horizon_bars)
    if len(xs) < 3:
        return {"ic": 0.0, "n_pairs": len(xs), "ok": False}
    return {"ic": _finite(e65._spearman(xs, ys)), "n_pairs": len(xs), "ok": True}


def evaluate_stability(
    capture: Dict[str, Any],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
    midpoint_ms: int,
) -> Dict[str, Any]:
    """Full-sample (EVAL-71 verbatim) + per-half IC -> STABLE flag for one config."""
    inst = capture.get("underlying", "UNKNOWN")
    full = e71.evaluate_predictiveness(
        capture,
        surface_signal=surface_signal,
        bar_seconds=bar_seconds,
        horizon_bars=horizon_bars,
    )
    early_cap, late_cap = _split_capture(capture, midpoint_ms)
    early = _half_ic(
        early_cap, surface_signal=surface_signal,
        bar_seconds=bar_seconds, horizon_bars=horizon_bars,
    )
    late = _half_ic(
        late_cap, surface_signal=surface_signal,
        bar_seconds=bar_seconds, horizon_bars=horizon_bars,
    )

    n_full = int(full.get("n_pairs", 0) or 0)
    n_early = int(early["n_pairs"])
    n_late = int(late["n_pairs"])
    ic_full = _finite(full.get("spearman_ic"), 0.0)
    ic_early = _finite(early["ic"], 0.0)
    ic_late = _finite(late["ic"], 0.0)
    perm_p_full = _finite(full.get("permutation_p"), 1.0)

    halves_ok = n_early >= MIN_HALF_PAIRS and n_late >= MIN_HALF_PAIRS
    sign_stable = ic_early > 0.0 and ic_late > 0.0
    stable = bool(halves_ok and sign_stable and perm_p_full < 0.05 and n_full > 0)

    return {
        "underlying": inst,
        "signal": surface_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs_full": n_full,
        "n_pairs_early": n_early,
        "n_pairs_late": n_late,
        "ic_full": ic_full,
        "ic_early": ic_early,
        "ic_late": ic_late,
        "permutation_p_full": perm_p_full,
        "bootstrap_ci_full": full.get("bootstrap_ci"),
        "halves_ok": halves_ok,
        "sign_stable": sign_stable,
        "stable": stable,
    }


# ---------------------------------------------------------------------------
# Per-underlying feasible floor (EVAL-71 floor on the full capture + per-half)
# ---------------------------------------------------------------------------
def _half_adequacy(capture_half: Dict[str, Any]) -> Dict[str, Any]:
    candles = capture_half.get("perp_candles", []) or []
    trades = capture_half.get("option_trades", []) or []
    n_near_atm = 0
    for t in trades:
        parsed = e71._parse_strike_type(t.get("instrument"))
        if parsed is None:
            continue
        iv = _finite(t.get("iv"), 0.0)
        if iv <= 0.0:
            continue
        ip = _finite(t.get("index_price"), 0.0)
        if ip > 0.0 and abs(parsed[0] / ip - 1.0) <= e71.ATM_BAND:
            n_near_atm += 1
    return {
        "n_perp_candles": len(candles),
        "n_near_atm_option_trades": n_near_atm,
        "candles_ok": len(candles) >= MIN_HALF_PERP_CANDLES,
        "near_atm_ok": n_near_atm >= MIN_HALF_NEAR_ATM_TRADES,
    }


def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    fl_full = e71._underlying_surface_floor(capture)  # sealed EVAL-71 floor, verbatim
    mid = _midpoint_ms(capture)
    early_cap, late_cap = _split_capture(capture, mid)
    early = _half_adequacy(early_cap)
    late = _half_adequacy(late_cap)
    ok = bool(
        fl_full.get("ok")
        and early["candles_ok"] and early["near_atm_ok"]
        and late["candles_ok"] and late["near_atm_ok"]
    )
    return {
        "underlying": inst,
        "midpoint_ms": int(mid),
        "eval71_floor_ok": bool(fl_full.get("ok")),
        "eval71_floor": fl_full,
        "early_half": early,
        "late_half": late,
        "checks": {
            "eval71_floor_ok": bool(fl_full.get("ok")),
            "early_candles_ok": early["candles_ok"],
            "early_near_atm_ok": early["near_atm_ok"],
            "late_candles_ok": late["candles_ok"],
            "late_near_atm_ok": late["near_atm_ok"],
        },
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-73",
        "title": "Options implied-volatility surface (EVAL-71 near-ATM IV level + "
                 "put-call skew) -> forward realized-vol predictiveness: TEMPORAL "
                 "OUT-OF-SAMPLE STABILITY of EVAL-71's GO across a disjoint "
                 "early/late split of the real on-disk captures",
        "extends": "EVAL-71 (identical Spearman rank-IC statistic, identical surface "
                   "signals / bar grid / horizons) but a different question: does "
                   "EVAL-71's predictive-surface GO replicate across two DISJOINT "
                   "temporal halves, or is it a one-period regime artifact?; no new "
                   "acquisition",
        "supersedes": "nothing -- this is the temporal-stability / OOS-replication "
                      "check of EVAL-71's GO, not a re-run; it does not re-litigate "
                      "EVAL-71 (full sample) or EVAL-72 (traded-form monetization)",
        "capture_dir": str(capture_dir),
        "surface_signals": list(SURFACE_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "split": "each underlying capture is split into two DISJOINT temporal halves "
                 "at the perp-candle midpoint (early ts < midpoint; late ts >= "
                 "midpoint); the full-sample IC/permutation are EVAL-71 verbatim and "
                 "each half carries its own Spearman rank IC (e65._spearman)",
        "stability_rule": (
            f"a config is STABLE iff n_pairs in EACH half >= {MIN_HALF_PAIRS}, "
            "IC_early > 0 and IC_late > 0, and the full-sample directional "
            "permutation p < 0.05"
        ),
        "statistic": "Spearman rank correlation IC = rho(signal_z_k, rv_forward_k); "
                     "per-half IC via e65._spearman; full-sample IC + directional "
                     "permutation via e71.evaluate_predictiveness",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle realized-vol series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
        },
        "go_bar": (
            "GO only if, on BOTH BTC and ETH and at least one config, the config is "
            "STABLE (both half ICs > 0, each half >= min_half_pairs, full-sample "
            "directional permutation p < 0.05) and pooled BH-FDR rejects its "
            "full-sample p; else NO-GO CONFIRMED (PASS) -- EVAL-71's predictive "
            "surface GO does not replicate across the disjoint temporal split."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures "
                    "(option trades with real iv + perp candles); no new acquisition, "
                    "no network; reuses EVAL-71's floor verbatim + a per-half adequacy "
                    "floor",
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


def run_eval73(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL73-SURFACE-IV-RV-STABILITY-SPLIT",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_one_capture_per_underlying(e61._capture_inventory(str(capture_dir_abs)))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor(c)

    floor_ok = bool(
        len(captures) >= int(FLOOR["min_underlyings"])
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures:
        mid = _midpoint_ms(cap)
        for sig in SURFACE_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_stability(
                            cap, surface_signal=sig, bar_seconds=bar_s,
                            horizon_bars=horizon, midpoint_ms=mid,
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{cap.get('underlying')}::{sig}::bar{bar_s}::"
                            f"h{horizon}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    # Pooled BH-FDR on the FULL-SAMPLE directional permutation p (EVAL-71 semantics).
    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}":
            _finite(r.get("permutation_p_full"), 1.0)
        for r in per_config
        if r.get("n_pairs_full", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)

    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        valid = [r for r in rows if r.get("n_pairs_full", 0) > 0]
        best = None
        if valid:
            best = max(valid, key=lambda r: _finite(r.get("ic_full"), -1e9))
        stable_configs: List[str] = []
        for r in valid:
            key = (
                f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::"
                f"h{r['horizon_bars']}"
            )
            if r.get("stable") and key in rejected:
                stable_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_ic_full": _finite(best.get("ic_full"), 0.0) if best else 0.0,
            "best_ic_early": _finite(best.get("ic_early"), 0.0) if best else 0.0,
            "best_ic_late": _finite(best.get("ic_late"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::bar{best['bar_seconds']}::h{best['horizon_bars']}"
                if best else "n/a"
            ),
            "n_stable": len(stable_configs),
            "stable_configs": stable_configs,
            "any_stable": bool(stable_configs),
        })

    all_stable = bool(inst_summary) and all(s["any_stable"] for s in inst_summary)
    go = bool(floor_ok and all_stable and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT" if floor_ok
        else "EVAL_73_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "temporal out-of-sample stability of EVAL-71's predictive-surface GO: "
            "Spearman rank IC sign-consistency across a disjoint early/late split of "
            "the real on-disk BTC+ETH captures"
            if floor_ok else "capture below the composed EVAL-71 + per-half floor; "
                              "no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": dict(FLOOR),
        "per_underlying_floor": per_underlying_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "bh_fdr": bh,
            "all_underlyings_stable": all_stable,
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
            "EVAL-71's predictive-surface GO (causal options implied-vol surface -> "
            "forward realized vol) is TEMPORALLY STABLE: the positive Spearman rank "
            "IC sign replicates across two DISJOINT temporal halves of the same real "
            "on-disk BTC/ETH captures, not an artifact of one period; tested at the "
            "sealed EVAL-71 floor plus a derived per-half adequacy floor."
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
        f"# {PREREG_ID} — EVAL-71 predictive-surface temporal stability "
        f"(disjoint early/late split)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Surface signals: {p['surface_signals']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Split: {p['split']}",
        f"- Stability rule: {p['stability_rule']}",
        f"- Statistic: {p['statistic']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']} / "
        f"zwindow {p['stats']['zwindow']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered feasible floor (EVAL-71 floor + per-half adequacy; NOT EVAL-64)",
        "",
        f"- {fl['note']}",
        f"- min underlyings: {fl['min_underlyings']}",
        f"- min perp candles/half: {fl['min_half_perp_candles']}",
        f"- min near-ATM trades/half: {fl['min_half_near_atm_trades']}",
        f"- min aligned pairs/half: {fl['min_half_pairs']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — EVAL-71 predictive-surface temporal stability "
        f"(disjoint early/late split) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor (EVAL-71 floor + per-half adequacy)",
        "",
        "| underlying | EVAL-71 floor ok | early candles | early near-ATM | late candles | late near-ATM | ok |",
        "|---|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        e = fl["early_half"]
        l = fl["late_half"]
        lines.append(
            f"| {inst} | {fl['eval71_floor_ok']} | {e['n_perp_candles']} | "
            f"{e['n_near_atm_option_trades']} | {l['n_perp_candles']} | "
            f"{l['n_near_atm_option_trades']} | {fl['ok']} |"
        )
    lines += ["", "## Per-underlying (best config by full-sample IC)", "",
              "| underlying | configs | best IC full | IC early | IC late | best config | n stable | any stable |",
              "|---|---|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_ic_full']:.4f} | "
            f"{s['best_ic_early']:.4f} | {s['best_ic_late']:.4f} | "
            f"{s['best_config']} | {s['n_stable']} | {s['any_stable']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- All underlyings stable: {r['pooled']['all_underlyings_stable']}"]
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
        f"# {BLOCKED_ID} — EVAL-71 predictive-surface temporal stability "
        f"(below the composed EVAL-71 + per-half floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the composed EVAL-71 + per-half adequacy floor, so "
        "no GO/NO-GO verdict is emitted. Do NOT weaken the floor, do NOT use "
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
        description="EVAL-73: temporal out-of-sample stability of EVAL-71's "
                    "predictive-surface GO across a disjoint early/late split on "
                    "the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL73-SURFACE-IV-RV-STABILITY-SPLIT")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval73(
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