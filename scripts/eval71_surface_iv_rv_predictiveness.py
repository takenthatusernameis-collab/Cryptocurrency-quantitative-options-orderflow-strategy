#!/usr/bin/env python3
"""EVAL-71: does the **options implied-volatility surface** predict subsequent
realized volatility? — a wrapper-free, information-content falsification that is
runnable **now** on the real on-disk three-way captures.

Why this rung exists (the one signal source EVAL-65/70 leave open)
-----------------------------------------------------------------
The three active ladder campaigns (EVAL-67/68/69) are hard-gated on a *disjoint
forward* window that cannot be acquired before ``2026-11-20T00:00:00Z`` (free
Deribit perp 1m retention is 300000 s). That physics is not a fixable
inefficiency — but it leaves pre-threshold sessions with no genuine heavy work,
so they degenerate into timestamp-only carries (the exact failure the EVAL-70
gate was built to remove; EVAL-70 then sealed, reopening the gap).

EVAL-65 answered "does the **options order-flow** toxicity signal predict forward
realized volatility?" (sealed ``NO-GO CONFIRMED``). EVAL-70 answered the
complementary "does the **underlying perp** order-flow predict forward realized
vol / signed return?" (sealed ``NO-GO CONFIRMED``). Neither asked the remaining,
on-charter question about the **options surface itself**:

    Does the causal, implied-volatility *surface* — the near-ATM implied-vol
    level and the put-call skew, reconstructed from the real Deribit option
    trade tape (every trade carries a real ``iv``) — carry monotone information
    about subsequent forward realized volatility of the BTC/ETH perpetual?

This is genuinely new (a *surface* signal, not an order-flow signal; EVAL-57
tested the VRP surface only as a *traded* delta-hedged straddle net-of-cost P&L,
never as a wrapper-free information-content predictiveness measurement), it is
on the repo charter ("crypto options **surface** + options order-flow + underlying
order-flow -> tradeable, net-of-cost alpha on REAL public data"), and it is
runnable **today** because it needs only the already-acquired real three-way
captures (option trades with real IV + perp candles), with **no new acquisition**
and **no network**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
-------------------------------------------------------------------------------
For each underlying (BTC, ETH), each causal surface signal ``{atm_iv, skew}``
(trailing-window near-ATM trade-weighted mean IV / put-minus-call IV, expanding
z-scored end-of-bar ``k``), each bar grid ``{60s, 300s}`` and each forward
horizon ``H`` bars, compute the Spearman rank ``IC = rho(signal_z_k, rv_{k+1..k+H})``
where ``rv`` is the forward realized volatility of the real perp. **GO only if, on
BOTH BTC and ETH and at least one config:** ``IC > 0``, directional permutation
``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and pooled BH-FDR rejects that
config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
The EVAL-64 feasible floor is an *options-surface snapshot* floor that governs the
EVAL-67/68/69 ladder and is **not** weakened here. EVAL-71 measures a *trade-tape
IV* signal, so it carries its own, honestly pre-registered floor matched to the
data it actually consumes (option trades / near-ATM trades / perp candles / span).
Below that floor it seals ``EVAL_71_..._BLOCKED_<UTC>`` (never a NO-GO).

Seals ``EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_PREREGISTRATION_<UTC>`` then
``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
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

# Reuse the sealed EVAL-61 measurement helpers + EVAL-65 statistics verbatim.
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_COMBINED"
PREREG_ID = "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_BLOCKED"

# Pre-registered grid (surface signals x bar grid x forward horizons).
SURFACE_SIGNALS: Tuple[str, ...] = ("atm_iv", "skew")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)
# Trailing window (seconds) over which option trades are aggregated into the
# surface signal at each bar end; 3x the 300s bar so sparse trade tapes still
# yield a well-populated near-ATM IV estimate.
SIGNAL_WINDOW_SECONDS: float = 900.0
# Near-ATM band: |strike / spot - 1| <= ATM_BAND keeps the front of the surface.
ATM_BAND: float = 0.05

# Statistics reused verbatim from EVAL-65 (identical permutation / bootstrap / seed).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

# Pre-registered feasible floor for the trade-tape IV signal (NOT the EVAL-64 floor).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_option_trades_per_underlying": 1000,
    "min_near_atm_option_trades_per_underlying": 400,
    "min_perp_candles_per_underlying": 1000,
    "min_perp_span_seconds_per_underlying": 82000.0,
    "note": (
        "EVAL-71 measures a trade-tape implied-vol surface signal, so it carries "
        "its own pre-registered floor (option trades / near-ATM trades / perp "
        "candles / span). This is NOT a weakening of the EVAL-64 options-surface "
        "snapshot floor, which governs the EVAL-67/68/69 ladder and is reused "
        "verbatim there."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval71_surface_iv_rv_predictiveness.py "
    "tests/test_eval71_surface_iv_rv_predictiveness.py",
    "python3 -m pytest -q tests/test_eval71_surface_iv_rv_predictiveness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval71_surface_iv_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval71_surface_iv_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL71-SURFACE-IV-RV-PREDICTIVENESS",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return v


def _parse_strike_type(instrument: Any) -> Optional[Tuple[float, str]]:
    """Parse ``BTC-27NOV26-65000-P`` -> ``(65000.0, 'P')``; ``None`` if malformed."""
    try:
        parts = str(instrument).split("-")
        strike = float(parts[-2])
        typ = parts[-1].strip().upper()
        if typ not in ("C", "P"):
            return None
        return strike, typ
    except (IndexError, ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Surface signal + forward target (real option trade tape -> implied-vol surface)
# ---------------------------------------------------------------------------
def build_surface_bars(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    signal_window_seconds: float = SIGNAL_WINDOW_SECONDS,
    atm_band: float = ATM_BAND,
) -> List[Dict[str, Any]]:
    """Per-bar causal implied-vol *surface* states on the ``bar_seconds`` grid.

    Each bar carries the perp close in the bucket (the reference spot at bar end
    ``k``) and two causal surface signals reconstructed from the real Deribit
    option trade tape over the trailing ``signal_window_seconds`` window ending at
    bar end ``k``:

    * ``atm_iv`` — amount-weighted mean ``iv`` of near-ATM option trades
      (``|strike/spot - 1| <= atm_band``), the implied-vol *level*;
    * ``skew``   — mean(put ``iv``) - mean(call ``iv``) over the same near-ATM
      trades, the put-call *skew*.

    Signals are ``None`` for bars with no near-ATM trades (forward-filled by the
    caller). Bars are ascending and non-overlapping.
    """
    bar_ms = int(float(bar_seconds) * 1000)
    win_ms = int(float(signal_window_seconds) * 1000)

    candles = sorted(capture.get("perp_candles", []) or [], key=lambda c: int(c.get("ts") or 0))
    closes: Dict[int, float] = {}
    for c in candles:
        px = _finite(c.get("close"), 0.0)
        ts = int(c.get("ts") or 0)
        if px > 0.0 and ts > 0:
            closes[(ts // bar_ms) * bar_ms] = px  # last (largest ts) wins

    trades: List[Dict[str, Any]] = []
    for t in capture.get("option_trades", []) or []:
        parsed = _parse_strike_type(t.get("instrument"))
        if parsed is None:
            continue
        strike, typ = parsed
        iv = _finite(t.get("iv"), 0.0)
        ts = int(t.get("ts") or 0)
        amt = abs(_finite(t.get("amount"), 0.0))
        if ts <= 0 or iv <= 0.0:
            continue
        trades.append({"ts": ts, "strike": strike, "type": typ, "iv": iv, "amount": amt})
    trades.sort(key=lambda t: t["ts"])
    trade_ts = [t["ts"] for t in trades]

    bars: List[Dict[str, Any]] = []
    for bo in sorted(closes):
        spot = float(closes[bo])
        bar_end = bo + bar_ms
        lo = bar_end - win_ms
        lo_i = bisect.bisect_left(trade_ts, lo)
        hi_i = bisect.bisect_left(trade_ts, bar_end)
        window = trades[lo_i:hi_i]
        atm = [t for t in window if spot > 0.0 and abs(t["strike"] / spot - 1.0) <= atm_band]
        atm_iv: Optional[float] = None
        skew: Optional[float] = None
        if atm:
            tot_amt = sum(t["amount"] for t in atm)
            if tot_amt > 0.0:
                atm_iv = sum(t["iv"] * t["amount"] for t in atm) / tot_amt
            else:
                atm_iv = sum(t["iv"] for t in atm) / len(atm)
            put_ivs = [t["iv"] for t in atm if t["type"] == "P"]
            call_ivs = [t["iv"] for t in atm if t["type"] == "C"]
            if put_ivs and call_ivs:
                skew = (sum(put_ivs) / len(put_ivs)) - (sum(call_ivs) / len(call_ivs))
        bars.append({
            "bar_open_ms": int(bo),
            "close": spot,
            "atm_iv": atm_iv,
            "skew": skew,
            "n_window_trades": len(window),
            "n_atm_trades": len(atm),
        })
    return bars


def _forward_rv(bars: Sequence[Dict[str, Any]], horizon_bars: int) -> List[float]:
    """Forward realized-vol series over the next ``H`` bars.

    Returns a list indexed by bar ``k`` (decision at bar ``k``, target over bars
    ``k+1..k+H``); length is ``max(0, len(bars) - horizon_bars)``.
    """
    closes = [float(b["close"]) for b in bars]
    lr = [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)] if len(closes) >= 2 else []
    h = int(horizon_bars)
    rv: List[float] = []
    for k in range(0, len(lr) - h + 1):
        seg = lr[k:k + h]
        rv.append(math.sqrt(sum(r * r for r in seg) / float(h)))
    return rv


def _forward_fill(raw: Sequence[Optional[float]]) -> List[float]:
    """Causal forward-fill of a sparse signal: carry forward the last valid value;
    leading ``None`` -> ``0.0`` (neutral, pre-first-signal)."""
    out: List[float] = []
    last = 0.0
    for v in raw:
        if v is not None:
            last = float(v)
        out.append(last)
    return out


def evaluate_predictiveness(
    capture: Dict[str, Any],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    bars = build_surface_bars(capture, bar_seconds=bar_seconds)
    ys_all = _forward_rv(bars, horizon_bars)
    if len(bars) < horizon_bars + 5:
        return {
            "underlying": inst, "signal": surface_signal,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient surface bars", "n_pairs": 0, "pass": False,
        }

    raw = [b.get(surface_signal) for b in bars]
    sig_filled = _forward_fill(raw)
    sig_z = e61.expanding_zscore(sig_filled, ZWINDOW)

    xs: List[float] = []
    ys: List[float] = []
    for k in range(len(ys_all)):
        xs.append(float(sig_z[k]) if k < len(sig_z) else 0.0)
        ys.append(float(ys_all[k]))

    if len(xs) < 8:
        return {
            "underlying": inst, "signal": surface_signal,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient aligned pairs", "n_pairs": len(xs), "pass": False,
        }

    ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED)
    passed = bool(ic > 0.0 and perm_p < 0.05 and ci_lo > 0.0 and len(xs) >= 20)
    n_atm = int(sum(1 for b in bars if b.get("n_atm_trades", 0) > 0))
    return {
        "underlying": inst,
        "signal": surface_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs": len(xs),
        "n_surface_bars": len(bars),
        "n_bars_with_atm": n_atm,
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Per-underlying feasible floor (trade-tape IV availability)
# ---------------------------------------------------------------------------
def _underlying_surface_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    candles = capture.get("perp_candles", []) or []
    trades = capture.get("option_trades", []) or []
    ts = [int(c.get("ts") or 0) for c in candles if int(c.get("ts") or 0) > 0]
    span = (max(ts) - min(ts)) / 1000.0 if ts else 0.0

    n_option_trades = 0
    n_near_atm = 0
    for t in trades:
        parsed = _parse_strike_type(t.get("instrument"))
        if parsed is None:
            continue
        iv = _finite(t.get("iv"), 0.0)
        if iv <= 0.0:
            continue
        n_option_trades += 1
        ip = _finite(t.get("index_price"), 0.0)
        if ip > 0.0 and abs(parsed[0] / ip - 1.0) <= ATM_BAND:
            n_near_atm += 1

    checks = {
        "option_trades_ok": n_option_trades >= int(FLOOR["min_option_trades_per_underlying"]),
        "near_atm_ok": n_near_atm >= int(FLOOR["min_near_atm_option_trades_per_underlying"]),
        "candles_ok": len(candles) >= int(FLOOR["min_perp_candles_per_underlying"]),
        "span_ok": span >= float(FLOOR["min_perp_span_seconds_per_underlying"]),
    }
    return {
        "underlying": inst,
        "n_option_trades": n_option_trades,
        "n_near_atm_option_trades": n_near_atm,
        "n_perp_candles": len(candles),
        "perp_span_seconds": span,
        "checks": checks,
        "ok": bool(all(checks.values())),
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-71",
        "title": "Options implied-volatility surface (near-ATM IV level + put-call "
                 "skew) -> subsequent realized volatility: wrapper-free rank "
                 "information coefficient (predictiveness) falsification on the real "
                 "on-disk three-way captures",
        "extends": "EVAL-65 (identical Spearman rank-IC statistic) but a different, "
                   "on-charter signal source: the options *surface* (trade-tape IV) "
                   "rather than the options *order-flow* tape; no new acquisition",
        "supersedes": "nothing — this is the surface complement to EVAL-65 (options "
                      "order-flow) and EVAL-70 (underlying perp order-flow) that is "
                      "runnable pre-threshold; EVAL-57 tested the VRP surface only as "
                      "a traded net-of-cost straddle, never as information content",
        "capture_dir": str(capture_dir),
        "surface_signals": list(SURFACE_SIGNALS),
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar near-ATM implied-vol surface from the real Deribit "
                  "option trade tape: atm_iv = amount-weighted mean iv of near-ATM "
                  "trades (|strike/spot-1|<=atm_band) over the trailing window; "
                  "skew = mean(put iv) - mean(call iv) over the same trades; both "
                  "forward-filled then expanding-zscored end-of-bar k (reused "
                  "e61.expanding_zscore)",
        "target": "rv = sqrt(mean(log-return^2)) over the next H perp bars "
                  "(forward realized vol, strictly after the decision at k)",
        "statistic": "Spearman rank correlation IC = rho(signal_z_k, rv_forward_k)",
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
            "GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, "
            "directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and "
            "pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures "
                    "(option trades with real iv + perp candles); no new acquisition, "
                    "no network; carries its own pre-registered trade-tape IV floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _select_one_capture_per_underlying(captures: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Richest (most real option trades) real capture per underlying; deterministic."""
    best: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = str(c.get("underlying") or "?")
        score = len(c.get("option_trades", []) or [])
        if inst not in best or score > len(best[inst].get("option_trades", []) or []):
            best[inst] = c
    return [best[k] for k in sorted(best)]


def run_eval71(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL71-SURFACE-IV-RV-PREDICTIVENESS",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_one_capture_per_underlying(e61._capture_inventory(str(capture_dir_abs)))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_surface_floor(c)

    floor_ok = bool(
        len(captures) >= int(FLOOR["min_underlyings"])
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures:
        for sig in SURFACE_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_predictiveness(
                            cap, surface_signal=sig, bar_seconds=bar_s,
                            horizon_bars=horizon,
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{cap.get('underlying')}::{sig}::bar{bar_s}::"
                            f"h{horizon}: {exc!r}"
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
        "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS" if floor_ok
        else "EVAL_71_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between causal "
            "options implied-vol surface (near-ATM IV level / put-call skew) and "
            "forward realized volatility on the real on-disk captures"
            if floor_ok else "capture below the pre-registered trade-tape IV floor; "
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
# Seal artifact builders
# ---------------------------------------------------------------------------
def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "The causal options implied-volatility surface (near-ATM IV level and "
            "put-call skew, reconstructed from the real Deribit option trade tape) "
            "has a positive monotone (Spearman rank) relationship with subsequent "
            "forward realized volatility of the BTC/ETH perpetual, independent of "
            "any trading wrapper; tested on the already-acquired real on-disk "
            "captures at the pre-registered trade-tape IV floor."
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
        f"# {PREREG_ID} — options implied-vol surface -> realized-vol "
        f"predictiveness (wrapper-free Spearman rank IC)",
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
        f"- Signal window (s): {p['signal_window_seconds']}",
        f"- Near-ATM band: {p['atm_band']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Signal: {p['signal']}",
        f"- Target: {p['target']}",
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
        "## Pre-registered feasible floor (trade-tape IV; NOT the EVAL-64 floor)",
        "",
        f"- {fl['note']}",
        f"- min underlyings: {fl['min_underlyings']}",
        f"- min option trades/underlying: {fl['min_option_trades_per_underlying']}",
        f"- min near-ATM option trades/underlying: {fl['min_near_atm_option_trades_per_underlying']}",
        f"- min perp candles/underlying: {fl['min_perp_candles_per_underlying']}",
        f"- min perp span seconds/underlying: {fl['min_perp_span_seconds_per_underlying']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — options implied-vol surface -> realized-vol "
        f"predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor",
        "",
        "| underlying | option trades | near-ATM | perp candles | perp span s | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['n_option_trades']} | {fl['n_near_atm_option_trades']} | "
            f"{fl['n_perp_candles']} | {fl['perp_span_seconds']:.0f} | {fl['ok']} |"
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
        f"# {BLOCKED_ID} — options implied-vol surface -> realized-vol "
        f"predictiveness (below the pre-registered trade-tape IV floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered trade-tape IV floor, so no "
        "GO/NO-GO verdict is emitted. Do NOT weaken the floor, do NOT use synthetic "
        "data, and do NOT emit NO-GO on under-floor data.",
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
        description="EVAL-71: wrapper-free options implied-vol surface -> "
                    "realized-vol predictiveness (Spearman rank IC) on the real "
                    "on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL71-SURFACE-IV-RV-PREDICTIVENESS")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval71(
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