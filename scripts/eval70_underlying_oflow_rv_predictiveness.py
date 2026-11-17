#!/usr/bin/env python3
"""EVAL-70: does the **underlying (OKX perpetual) order flow** predict subsequent
realized volatility and signed return? — a wrapper-free, information-content
falsification that is runnable **now** on the real on-disk captures.

Why this rung exists
--------------------
The three active ladder campaigns (EVAL-67/68/69) are hard-gated on a *disjoint
forward* window that cannot be acquired before ``2026-11-20T00:00:00Z`` (free
Deribit perp 1m retention is 300000 s; the sealed EVAL-64/65 BTC window ends
2026-11-16T06:48:16Z). That physics is not a fixable inefficiency — but it left
pre-threshold sessions with no genuine heavy work, so they degenerated into
timestamp-only carries.

EVAL-65 answered "does the **options** order-flow toxicity signal predict forward
realized volatility?" on the real 7d captures (sealed ``NO-GO CONFIRMED``). It did
NOT ask the complementary, on-charter question about the **underlying** tape:

    Does the causal, signed-aggressor order-flow imbalance of the BTC/ETH
    perpetual itself carry monotone information about (a) subsequent realized
    volatility and (b) the subsequent signed return?

This is genuinely new (a different signal source — the perp tape, not the options
tape), it is on the repo charter ("crypto options surface + options order-flow +
**underlying order-flow** -> tradeable, net-of-cost alpha on REAL public data"),
and it is runnable **today** because it needs only the already-acquired real
three-way captures (surface + perp candles + OKX perp trades), with **no new
acquisition** and **no network**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
-------------------------------------------------------------------------------
For each underlying (BTC, ETH), each causal perp order-flow signal
``{tox, imbalance}`` (expanding z-score, end-of-bar ``k``), each bar grid
``{60s, 300s}`` and each forward horizon ``H`` bars, compute the Spearman rank
``IC = rho(signal_z_k, target_{k+1..k+H})`` where ``target`` is either the forward
realized volatility (``rv``) or the forward signed log-return (``signed_return``)
of the real perp. **GO only if, on BOTH BTC and ETH and at least one config:**
``IC > 0``, directional permutation ``p < 0.05``, block-bootstrap 95% CI lower
``> 0``, and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
The EVAL-64 feasible floor is an *options-surface* floor (surface snapshots,
Deribit option trades, 300000 s perp span) that governs the EVAL-67/68/69 ladder
and is **not** weakened here. EVAL-70 measures a *perp-tape* signal, so it carries
its own, honestly pre-registered floor matched to the data it actually consumes
(perp trades / candles / span). Below that floor it seals
``EVAL_70_..._BLOCKED_<UTC>`` (never a NO-GO).

Seals ``EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_<UTC>`` then
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

# Reuse the sealed EVAL-61/62 measurement helpers + EVAL-65 statistics verbatim.
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED"
PREREG_ID = "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_BLOCKED"

# Pre-registered grid (perp-tape signals x bar grid x forward horizons).
TOX_SIGNALS: Tuple[str, ...] = ("tox", "imbalance")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)
# signal -> target pairing: unsigned toxicity only speaks to volatility; the signed
# imbalance also speaks to direction.
SIGNAL_TARGETS: Tuple[Tuple[str, str], ...] = (
    ("tox", "rv"),
    ("imbalance", "rv"),
    ("imbalance", "signed_return"),
)

# Statistics reused verbatim from EVAL-65 (identical permutation / bootstrap / seed).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

# Pre-registered feasible floor for the perp-tape signal (NOT the EVAL-64 floor).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_perp_trades_per_underlying": 50000,
    "min_perp_candles_per_underlying": 1000,
    "min_perp_span_seconds_per_underlying": 82000.0,
    "min_perp_bars_5m_per_underlying": 240,
    "note": (
        "EVAL-70 measures a perp-tape order-flow signal, so it carries its own "
        "pre-registered floor (perp trades/candles/span). This is NOT a weakening "
        "of the EVAL-64 options-surface floor, which governs the EVAL-67/68/69 "
        "ladder and is reused verbatim there."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval70_underlying_oflow_rv_predictiveness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval70_underlying_oflow_rv_predictiveness.py "
    "tests/test_eval70_underlying_oflow_rv_predictiveness.py",
    "python3 -m pytest -q tests/test_eval70_underlying_oflow_rv_predictiveness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval70_underlying_oflow_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval70_underlying_oflow_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL70-UNDERLYING-OFLOW-TOX-RV-PREDICTIVENESS",
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


# ---------------------------------------------------------------------------
# Perp-tape signal + forward targets (no options surface needed)
# ---------------------------------------------------------------------------
def build_perp_bars(capture: Dict[str, Any], *, bar_seconds: float) -> List[Dict[str, Any]]:
    """Per-bar causal perp-tape states on the ``bar_seconds`` grid.

    Each bar carries the last 1m perp close in the bucket, the signed-aggressor
    order-flow imbalance ``(buy_vol - sell_vol) / (buy_vol + sell_vol)`` and its
    absolute (toxicity) variant, aggregated from the real OKX perp trade tape.
    Bars are ascending and non-overlapping.
    """
    bar_ms = int(float(bar_seconds) * 1000)
    candles = sorted(capture.get("perp_candles", []) or [], key=lambda c: int(c.get("ts") or 0))
    closes: Dict[int, float] = {}
    for c in candles:
        px = _finite(c.get("close"), 0.0)
        ts = int(c.get("ts") or 0)
        if px > 0.0 and ts > 0:
            closes[(ts // bar_ms) * bar_ms] = px  # last (largest ts) wins

    flow: Dict[int, Dict[str, float]] = {}
    for t in capture.get("okx_perp_trades", []) or []:
        try:
            ts = int(t.get("ts") or 0)
            sz = abs(_finite(t.get("sz"), 0.0))
        except (TypeError, ValueError):
            continue
        if ts <= 0 or sz <= 0.0:
            continue
        bo = (ts // bar_ms) * bar_ms
        b = flow.setdefault(bo, {"buy": 0.0, "sell": 0.0})
        side = str(t.get("side") or "").lower()
        if side == "buy":
            b["buy"] += sz
        elif side == "sell":
            b["sell"] += sz

    bars: List[Dict[str, Any]] = []
    for bo in sorted(closes):
        f = flow.get(bo, {"buy": 0.0, "sell": 0.0})
        buy, sell = float(f["buy"]), float(f["sell"])
        tot = buy + sell
        imb = (buy - sell) / tot if tot > 0.0 else 0.0
        bars.append({
            "bar_open_ms": int(bo),
            "close": float(closes[bo]),
            "buy_vol": buy,
            "sell_vol": sell,
            "imbalance": imb,
            "tox": abs(imb),
        })
    return bars


def _forward_targets(bars: Sequence[Dict[str, Any]], horizon_bars: int) -> Dict[str, List[float]]:
    """Forward realized-vol and signed-return series over the next ``H`` bars.

    Returns aligned lists indexed by bar ``k`` (decision at bar ``k``, target over
    bars ``k+1..k+H``); length is ``max(0, len(bars) - horizon_bars)``.
    """
    closes = [float(b["close"]) for b in bars]
    lr = [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)] if len(closes) >= 2 else []
    h = int(horizon_bars)
    rv: List[float] = []
    signed: List[float] = []
    for k in range(0, len(lr) - h + 1):
        seg = lr[k:k + h]
        rv.append(math.sqrt(sum(r * r for r in seg) / float(h)))
        signed.append(sum(seg))
    return {"rv": rv, "signed_return": signed}


def evaluate_predictiveness(
    capture: Dict[str, Any],
    *,
    tox_signal: str,
    bar_seconds: float,
    horizon_bars: int,
    target: str,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    bars = build_perp_bars(capture, bar_seconds=bar_seconds)
    tgts = _forward_targets(bars, horizon_bars)
    ys_all = tgts.get(target)
    if ys_all is None:
        return {
            "underlying": inst, "signal": tox_signal, "target": target,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": f"unknown target {target!r}", "n_pairs": 0, "pass": False,
        }
    if len(bars) < horizon_bars + 5:
        return {
            "underlying": inst, "signal": tox_signal, "target": target,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient perp bars", "n_pairs": 0, "pass": False,
        }

    sig_raw = [float(b["tox"] if tox_signal == "tox" else b["imbalance"]) for b in bars]
    sig_z = e61.expanding_zscore(sig_raw, ZWINDOW)

    xs: List[float] = []
    ys: List[float] = []
    for k in range(len(ys_all)):
        xs.append(float(sig_z[k]) if k < len(sig_z) else 0.0)
        ys.append(float(ys_all[k]))

    if len(xs) < 8:
        return {
            "underlying": inst, "signal": tox_signal, "target": target,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient aligned pairs", "n_pairs": len(xs), "pass": False,
        }

    ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED)
    passed = bool(ic > 0.0 and perm_p < 0.05 and ci_lo > 0.0 and len(xs) >= 20)
    return {
        "underlying": inst,
        "signal": tox_signal,
        "target": target,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs": len(xs),
        "n_perp_bars": len(bars),
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Per-underlying feasible floor (perp-tape availability)
# ---------------------------------------------------------------------------
def _underlying_oflow_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    candles = capture.get("perp_candles", []) or []
    trades = capture.get("okx_perp_trades", []) or []
    ts = [int(c.get("ts") or 0) for c in candles if int(c.get("ts") or 0) > 0]
    span = (max(ts) - min(ts)) / 1000.0 if ts else 0.0
    bars_5m = len({(t // 300000) for t in ts})
    n_candles = len(candles)
    n_trades = len(trades)
    checks = {
        "trades_ok": n_trades >= int(FLOOR["min_perp_trades_per_underlying"]),
        "candles_ok": n_candles >= int(FLOOR["min_perp_candles_per_underlying"]),
        "span_ok": span >= float(FLOOR["min_perp_span_seconds_per_underlying"]),
        "bars_5m_ok": bars_5m >= int(FLOOR["min_perp_bars_5m_per_underlying"]),
    }
    return {
        "underlying": inst,
        "n_perp_trades": n_trades,
        "n_perp_candles": n_candles,
        "perp_span_seconds": span,
        "n_perp_bars_5m": bars_5m,
        "checks": checks,
        "ok": bool(all(checks.values())),
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-70",
        "title": "Underlying (OKX perp) order-flow toxicity -> subsequent realized "
                 "volatility and signed return: wrapper-free rank information "
                 "coefficient (predictiveness) falsification on the real on-disk "
                 "three-way captures",
        "extends": "EVAL-65 (identical Spearman rank-IC statistic) but a different, "
                   "on-charter signal source: the underlying perp tape rather than "
                   "the options tape; no options surface needed; no new acquisition",
        "supersedes": "nothing — this is the underlying-tape complement to EVAL-65 "
                      "(options tape) that is runnable pre-threshold",
        "capture_dir": str(capture_dir),
        "tox_signals": list(TOX_SIGNALS),
        "signal_targets": [list(st) for st in SIGNAL_TARGETS],
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar signed-aggressor order-flow imbalance "
                  "(buy_vol - sell_vol)/(buy_vol + sell_vol) from real OKX perp "
                  "trades, and its absolute (tox) variant, expanding-zscored "
                  "end-of-bar k (reused e61.expanding_zscore)",
        "target": "over the next H perp bars: rv = sqrt(mean(log-return^2)); "
                  "signed_return = sum(log-return) (strictly after the decision at k)",
        "statistic": "Spearman rank correlation IC = rho(signal_z_k, target_forward_k)",
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
            "note": "uses the already-acquired real on-disk three-way captures "
                    "(surface + perp candles + OKX perp trades); no new acquisition, "
                    "no network; carries its own pre-registered perp-tape floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _select_one_capture_per_underlying(captures: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Richest (most perp trades) real capture per underlying; deterministic."""
    best: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = str(c.get("underlying") or "?")
        score = len(c.get("okx_perp_trades", []) or [])
        if inst not in best or score > len(best[inst].get("okx_perp_trades", []) or []):
            best[inst] = c
    return [best[k] for k in sorted(best)]


def run_eval70(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL70-UNDERLYING-OFLOW-TOX-RV-PREDICTIVENESS",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_one_capture_per_underlying(e61._capture_inventory(str(capture_dir_abs)))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_oflow_floor(c)

    floor_ok = bool(
        len(captures) >= int(FLOOR["min_underlyings"])
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures:
        for sig, target in SIGNAL_TARGETS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_predictiveness(
                            cap, tox_signal=sig, bar_seconds=bar_s,
                            horizon_bars=horizon, target=target,
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{cap.get('underlying')}::{sig}::{target}::bar{bar_s}::"
                            f"h{horizon}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    p_values = {
        f"{r['underlying']}::{r['signal']}::{r['target']}::bar{r['bar_seconds']}::"
        f"h{r['horizon_bars']}": _finite(r.get("permutation_p"), 1.0)
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
                f"{r['underlying']}::{r['signal']}::{r['target']}::"
                f"bar{r['bar_seconds']}::h{r['horizon_bars']}"
            )
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::{best['target']}::bar{best['bar_seconds']}::"
                f"h{best['horizon_bars']}" if best else "n/a"
            ),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS" if floor_ok
        else "EVAL_70_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between causal "
            "underlying (OKX perp) order-flow toxicity/imbalance and forward realized "
            "volatility / signed return on the real on-disk captures"
            if floor_ok else "capture below the pre-registered perp-tape floor; no verdict"
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
            "The causal underlying (OKX perp) order-flow imbalance / toxicity has a "
            "positive monotone (Spearman rank) relationship with subsequent forward "
            "realized volatility and signed return, independent of any trading "
            "wrapper; tested on the already-acquired real on-disk captures at the "
            "pre-registered perp-tape floor."
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
        f"# {PREREG_ID} — underlying order-flow -> realized-vol / signed-return "
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
        f"- Signals: {p['tox_signals']}",
        f"- Signal -> target pairs: {p['signal_targets']}",
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
        "## Pre-registered feasible floor (perp-tape; NOT the EVAL-64 floor)",
        "",
        f"- {fl['note']}",
        f"- min underlyings: {fl['min_underlyings']}",
        f"- min perp trades/underlying: {fl['min_perp_trades_per_underlying']}",
        f"- min perp candles/underlying: {fl['min_perp_candles_per_underlying']}",
        f"- min perp span seconds/underlying: {fl['min_perp_span_seconds_per_underlying']}",
        f"- min perp 5m bars/underlying: {fl['min_perp_bars_5m_per_underlying']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — underlying order-flow -> realized-vol / signed-return "
        f"predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor",
        "",
        "| underlying | perp trades | perp candles | perp span s | 5m bars | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['n_perp_trades']} | {fl['n_perp_candles']} | "
            f"{fl['perp_span_seconds']:.0f} | {fl['n_perp_bars_5m']} | {fl['ok']} |"
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
        f"# {BLOCKED_ID} — underlying order-flow -> realized-vol / signed-return "
        f"predictiveness (below the pre-registered perp-tape floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered perp-tape floor, so no GO/NO-GO "
        "verdict is emitted. Do NOT weaken the floor, do NOT use synthetic data, and do "
        "NOT emit NO-GO on under-floor data.",
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
        description="EVAL-70: wrapper-free underlying (OKX perp) order-flow -> "
                    "realized-vol / signed-return predictiveness (Spearman rank IC) "
                    "on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL70-UNDERLYING-OFLOW-TOX-RV-PREDICTIVENESS")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval70(
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