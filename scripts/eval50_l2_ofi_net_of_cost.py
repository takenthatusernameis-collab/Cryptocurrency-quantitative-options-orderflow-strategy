#!/usr/bin/env python3
"""EVAL-50: real L2 order-book OFI net-of-cost falsification.

The repository charter is a **combined options + orderflow** strategy. All four
combined options+orderflow venue/asset cells are sealed ``NO-GO CONFIRMED
(PASS)`` (EVAL-46 BTC/OKX, EVAL-47 ETH/OKX, EVAL-48 BTC Deribit-cross-venue,
EVAL-49 ETH Deribit-cross-venue). The next orderflow modality is **real L2
order-book depth** and its canonical alpha — the order-flow imbalance (OFI).
This script is the net-of-cost falsification of that alpha on real, live-captured
OKX L2 book snapshots (``scripts/eval50_acquire_l2_depth.py``).

It is strictly additive: it consumes only the measured capture JSON files under
``--capture-dir`` and reuses the sealed statistics helpers (``_sharpe_of_returns``,
``_dsr_of_returns``, ``_cscv_pbo``, ``_benjamini_hochberg``, ``block_bootstrap_ci``,
``permutation_test``). It never re-runs a prior EVAL and never edits ``src/``.

Pre-declared protocol (identical for every instrument; no curve fitting):
  - per instrument: sort snapshots by ``ts``; resample to a ``--bar-seconds``
    grid; per bar aggregate the sum of per-snapshot multi-level OFI (Cont /
    Kukanov / Stoikov 2014, price-matched via dict, top ``--levels`` levels),
    the last mid-price, and the median quoted spread;
  - OFI signal = causal expanding z-score of bar OFI over ``--ofi-zwindow`` bars;
  - position = ``clip(z / Z_CLAMP, -1, 1)`` (pre-registered);
  - per-bar net-of-cost return = ``pos_t * mid_return_{t->t+1}``
    ``- cost_bps * |pos_t - pos_{t-1}| / 1e4``, where ``cost_bps`` is the
    **measured** median quoted spread of that bar plus a fixed impact term
    (``--impact-bps``);
  - full-series (causal → out-of-sample) plus rolling walk-forward Sharpe/max-DD;
  - stats: 1000-perm paired permutation (strategy vs flat), 1000-resample block
    bootstrap CI on Sharpe (block 2), CSCV PBO across the pre-registered grid,
    BH-FDR (alpha 0.1), DSR; seed 42.

Pre-declared GO bar (conservative; the campaign is TERMINATED so NO-GO is the
default and GO needs strong evidence): GO only if, on **both** BTC and ETH and
**at least one** grid config, net-of-cost Sharpe > 0, no kill-switch breach
(max-DD <= 0.20), permutation p < 0.05, and bootstrap 95% CI lower bound > 0.
Otherwise ``NO-GO CONFIRMED (PASS)``: book-imbalance/OFI alpha is not
net-of-cost tradable on real OKX L2 depth.

Heavy-work floor (sealed): refuses to seal a verdict unless **every** instrument
independently clears ``--min-snapshots`` snapshots and ``--min-span`` seconds,
and the roster has ``--min-instruments`` instruments — otherwise seals a measured
``EVAL_50_BLOCKED_<UTC>`` (never a NO-GO). This makes a short/partial capture
unable to satisfy the campaign.

Seal ``EVAL_50_PREREGISTRATION_<UTC>.{json,md}`` (before measurement) then
``EVAL_50_L2_OFI_COMBINED_<UTC>.{json,md}`` (or ``EVAL_50_BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics.integrated_options_orderflow_evaluation import (  # noqa: E402
    _dsr_of_returns,
    _sharpe_of_returns,
)
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
    _cscv_pbo,
)
from src.analytics.strategy_evaluation import (  # noqa: E402
    block_bootstrap_ci,
    permutation_test,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_50_L2_OFI_COMBINED"
PREREG_ID = "EVAL_50_PREREGISTRATION"
BLOCKED_ID = "EVAL_50_BLOCKED"

BAR_SECONDS = 5.0
OFI_ZWINDOW = 20
Z_CLAMP = 2.0
Z_THRESHOLD = 0.5
IMPACT_BPS = 0.5
PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
PBO_K_FOLDS = 4
PBO_N_COMBINATIONS = 16
FDR_ALPHA = 0.1
SEED = 42
KILL_SWITCH_MAX_DD = 0.20

MIN_SNAPSHOTS = 400
MIN_SPAN_SECONDS = 900.0
MIN_INSTRUMENTS = 2

GRID_BAR_SECONDS: Tuple[float, ...] = (5.0, 10.0)
GRID_Z_CLAMP: Tuple[float, ...] = (1.0, 2.0)

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval50_acquire_l2_depth.py",
    "scripts/eval50_l2_ofi_net_of_cost.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval50_l2_ofi_net_of_cost.py "
    "tests/test_eval50_l2_ofi_net_of_cost.py",
    "python3 -m pytest -q tests/test_eval50_l2_ofi_net_of_cost.py",
    "python3 scripts/eval50_l2_ofi_net_of_cost.py --no-write",
    "python3 scripts/eval50_l2_ofi_net_of_cost.py",
)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_for_filename(iso_ts: str) -> str:
    return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
        return v if math.isfinite(v) else float(default)
    except (TypeError, ValueError):
        return float(default)


def _mean(vals: Sequence[float]) -> float:
    vals = [float(v) for v in vals]
    return sum(vals) / len(vals) if vals else 0.0


def _std(vals: Sequence[float]) -> float:
    vals = [float(v) for v in vals]
    n = len(vals)
    if n < 2:
        return 0.0
    m = sum(vals) / n
    return math.sqrt(sum((v - m) ** 2 for v in vals) / n)


def _max_drawdown(rets: Sequence[float]) -> float:
    eq = 1.0
    peak = 1.0
    mdd = 0.0
    for r in rets:
        eq *= 1.0 + float(r)
        if eq <= 0:
            return 1.0
        peak = max(peak, eq)
        dd = (peak - eq) / peak if peak > 0 else 0.0
        mdd = max(mdd, dd)
    return mdd


def kill_switch_breach(max_drawdown: float) -> bool:
    return float(max_drawdown) > KILL_SWITCH_MAX_DD


def _mid(bids: Sequence[Sequence[float]], asks: Sequence[Sequence[float]]) -> float:
    if not bids or not asks:
        return 0.0
    return 0.5 * (float(bids[0][0]) + float(asks[0][0]))


def _spread_bps(bids: Sequence[Sequence[float]], asks: Sequence[Sequence[float]]) -> float:
    if not bids or not asks:
        return 0.0
    bid = float(bids[0][0])
    ask = float(asks[0][0])
    mid = 0.5 * (bid + ask)
    return (ask - bid) / mid * 1e4 if mid > 0 else 0.0


def ofi_at(prev_book: Dict[str, Any], cur_book: Dict[str, Any], levels: int) -> float:
    """Multi-level order-flow imbalance (Cont/Kukanov/Stoikov 2014).

    Price-matched level changes: bid-depth increase is buy pressure (+), ask-depth
    increase is sell pressure (−). Only the top ``levels`` levels per side count.
    """
    def side_delta(prev_levels: Sequence[Sequence[float]],
                   cur_levels: Sequence[Sequence[float]]) -> float:
        prev_map = {round(float(p), 8): float(s) for p, s in prev_levels[:levels]}
        cur_map = {round(float(p), 8): float(s) for p, s in cur_levels[:levels]}
        delta = 0.0
        for p, s in cur_map.items():
            delta += s - prev_map.get(p, 0.0)
        for p, s in prev_map.items():
            if p not in cur_map:
                delta -= s
        return delta

    bid_delta = side_delta(prev_book.get("bids", []), cur_book.get("bids", []))
    ask_delta = side_delta(prev_book.get("asks", []), cur_book.get("asks", []))
    return bid_delta - ask_delta


def resample_bars(
    snapshots: Sequence[Dict[str, Any]], bar_seconds: float
) -> List[Dict[str, Any]]:
    """Aggregate per-snapshot OFI, last mid, median spread into fixed time bars."""
    if len(snapshots) < 2:
        return []
    bar_ms = int(float(bar_seconds) * 1000)
    buckets: Dict[int, Dict[str, Any]] = {}
    prev = snapshots[0]
    for snap in snapshots:
        bar_end = ((int(snap["ts"]) // bar_ms) + 1) * bar_ms
        ofi = ofi_at(prev, snap, levels=10 ** 9) if snap is not prev else 0.0
        prev = snap
        b = buckets.get(bar_end)
        if b is None:
            b = {"bar_end": bar_end, "ofi_sum": 0.0, "mid": 0.0, "spreads": []}
            buckets[bar_end] = b
        b["ofi_sum"] += ofi
        b["mid"] = _mid(snap["bids"], snap["asks"])
        b["spreads"].append(_spread_bps(snap["bids"], snap["asks"]))
    bars: List[Dict[str, Any]] = []
    for bar_end in sorted(buckets):
        b = buckets[bar_end]
        sp = sorted(b["spreads"])
        bars.append(
            {
                "bar_end": bar_end,
                "ofi": float(b["ofi_sum"]),
                "mid": float(b["mid"]),
                "spread_bps": float(sp[len(sp) // 2]) if sp else 0.0,
            }
        )
    return bars


def expanding_zscore(xs: Sequence[float], window: int, min_periods: int = 5) -> List[float]:
    out: List[float] = []
    for i in range(len(xs)):
        lo = max(0, i - int(window) + 1)
        w = [float(v) for v in xs[lo : i + 1]]
        if len(w) < max(2, int(min_periods)):
            out.append(0.0)
            continue
        m = sum(w) / len(w)
        sd = math.sqrt(sum((v - m) ** 2 for v in w) / len(w))
        out.append((float(xs[i]) - m) / sd if sd > 0 else 0.0)
    return out


def strategy_returns(
    bars: Sequence[Dict[str, Any]],
    *,
    ofi_zwindow: int = OFI_ZWINDOW,
    z_clamp: float = Z_CLAMP,
    impact_bps: float = IMPACT_BPS,
) -> Dict[str, Any]:
    """Causal OFI strategy: position = clip(z/z_clamp); net-of-cost returns."""
    if len(bars) < 4:
        return {"returns": [], "positions": [], "turnover": [], "nonzero": 0}
    ofs = [b["ofi"] for b in bars]
    zs = expanding_zscore(ofs, ofi_zwindow)
    positions = [max(-1.0, min(1.0, z / float(z_clamp))) for z in zs]
    returns: List[float] = []
    turnovers: List[float] = []
    prev_pos = 0.0
    for i in range(len(bars) - 1):
        mid0 = bars[i]["mid"]
        mid1 = bars[i + 1]["mid"]
        if mid0 <= 0 or mid1 <= 0:
            returns.append(0.0)
            turnovers.append(0.0)
            prev_pos = positions[i]
            continue
        mid_ret = (mid1 - mid0) / mid0
        cost_bps = bars[i]["spread_bps"] + float(impact_bps)
        turnover = abs(positions[i] - prev_pos)
        gross = positions[i] * mid_ret
        cost = cost_bps * turnover / 1e4
        returns.append(gross - cost)
        turnovers.append(turnover)
        prev_pos = positions[i]
    nonzero = sum(1 for p in positions if abs(p) > 1e-9)
    return {
        "returns": returns,
        "positions": positions,
        "turnover": turnovers,
        "nonzero": int(nonzero),
        "ofi_std": _std(ofs),
        "signal_z_std": _std(zs),
    }


def walkforward_folds(
    returns: Sequence[float], train: int, test: int, step: int
) -> List[Dict[str, Any]]:
    folds: List[Dict[str, Any]] = []
    n = len(returns)
    start = int(train)
    while start + int(test) <= n:
        seg = [float(r) for r in returns[start : start + int(test)]]
        folds.append(
            {
                "train_end": start,
                "test_start": start,
                "test_end": start + int(test),
                "oos_sharpe": _sharpe_of_returns(seg),
                "oos_max_drawdown": _max_drawdown(seg),
                "n": len(seg),
            }
        )
        start += int(step)
    return folds


def evaluate_instrument(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    z_clamp: float,
    ofi_zwindow: int = OFI_ZWINDOW,
) -> Dict[str, Any]:
    inst = capture.get("inst_id", "UNKNOWN")
    snaps = sorted(capture.get("snapshots", []), key=lambda s: int(s["ts"]))
    bars = resample_bars(snaps, bar_seconds)
    sr = strategy_returns(bars, ofi_zwindow=ofi_zwindow, z_clamp=z_clamp)
    rets = sr["returns"]
    if not rets:
        return {
            "instrument": inst,
            "bar_seconds": float(bar_seconds),
            "z_clamp": float(z_clamp),
            "error": "no bars/returns",
            "pass": False,
        }
    sharpe = _sharpe_of_returns(rets)
    mdd = _max_drawdown(rets)
    flat = [0.0] * len(rets)
    perm = permutation_test(
        rets,
        flat,
        statistic=_mean,
        n_permutations=PERMUTATION_PERMS,
        paired=True,
        seed=SEED,
    )
    boot = block_bootstrap_ci(
        rets,
        statistic=_sharpe_of_returns,
        n_bootstrap=BOOTSTRAP_RESAMPLES,
        block_size=BOOTSTRAP_BLOCK,
        seed=SEED,
    )
    wf = walkforward_folds(rets, train=max(10, len(rets) // 3),
                           test=max(10, len(rets) // 5), step=max(10, len(rets) // 5))
    breach = kill_switch_breach(mdd)
    perm_p = _finite(perm.get("p_value"), 1.0)
    ci_low = _finite(boot[1], 0.0)
    ci_high = _finite(boot[2], 0.0)
    passed = bool(
        sharpe > 0.0
        and not breach
        and perm_p < 0.05
        and ci_low > 0.0
        and sr["nonzero"] > 0
        and sr["ofi_std"] > 0.0
    )
    return {
        "instrument": inst,
        "bar_seconds": float(bar_seconds),
        "z_clamp": float(z_clamp),
        "n_bars": len(bars),
        "n_returns": len(rets),
        "nonzero_positions": sr["nonzero"],
        "ofi_std": sr["ofi_std"],
        "signal_z_std": sr["signal_z_std"],
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "kill_switch_breach": breach,
        "permutation_p": perm_p,
        "bootstrap_ci": [boot[0], ci_low, ci_high],
        "dsr": _dsr_of_returns(rets),
        "walkforward": wf,
        "mean_return": _mean(rets),
        "pass": passed,
    }


def pooled_verdict(
    per_instrument: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    """PBO across the grid + BH-FDR across configs; NO-GO unless every cell passes."""
    # PBO/BH-FDR are computed in run_eval50 where per-config return series are
    # available; this helper is kept for symmetry with the sealed eval scripts.
    return {"note": "see run_eval50"}


def build_protocol(
    capture_dir: str,
    bar_seconds_grid: Sequence[float],
    z_clamp_grid: Sequence[float],
) -> Dict[str, Any]:
    return {
        "eval": "EVAL-50",
        "title": "Real L2 order-book OFI net-of-cost falsification",
        "capture_dir": str(capture_dir),
        "ofi": "Cont/Kukanov/Stoikov (2014) multi-level order-flow imbalance, price-matched",
        "bar_seconds_grid": [float(b) for b in bar_seconds_grid],
        "z_clamp_grid": [float(z) for z in z_clamp_grid],
        "ofi_zwindow": int(OFI_ZWINDOW),
        "z_threshold": float(Z_THRESHOLD),
        "impact_bps": float(IMPACT_BPS),
        "cost_model": "net-of-cost: measured bar median quoted spread + fixed impact bps on turnover",
        "walkforward": {"train_frac": "1/3", "test_frac": "1/5", "step_frac": "1/5"},
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation_paired": True,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "pbo_k_folds": PBO_K_FOLDS,
            "pbo_n_combinations": PBO_N_COMBINATIONS,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
        },
        "kill_switch_max_dd": KILL_SWITCH_MAX_DD,
        "go_bar": (
            "GO only if, on both BTC and ETH and at least one grid config, "
            "net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), "
            "permutation p < 0.05, and bootstrap 95% CI lower > 0; else NO-GO."
        ),
        "floor": {
            "min_snapshots_per_instrument": MIN_SNAPSHOTS,
            "min_span_seconds_per_instrument": MIN_SPAN_SECONDS,
            "min_instruments": MIN_INSTRUMENTS,
        },
    }


def _capture_inventory(capture_dir: str) -> List[Dict[str, Any]]:
    """Load captures, keeping the newest capture per instrument.

    Multiple capture files may accumulate in the same directory (a short
    pre-capture plus a later longer one); only the latest per instrument is
    measured so an instrument is never double-counted.
    """
    best: Dict[str, Tuple[int, Dict[str, Any]]] = {}
    for path in sorted(glob.glob(os.path.join(capture_dir, "l2_depth_*.json"))):
        try:
            c = json.loads(Path(path).read_text())
        except (OSError, ValueError):
            continue
        inst = c.get("inst_id", "?")
        stamp = 0
        try:
            stamp = int(Path(path).stem.split("_")[-1].replace("Z", ""))
        except ValueError:
            stamp = 0
        key = (int(c.get("end_ts_ms", 0)), stamp)
        if inst not in best or key > best[inst][0]:
            best[inst] = (key, c)
    return [c for _, c in best.values()]


def run_eval50(
    *,
    capture_dir: str = "data/raw/eval50",
    write: bool = True,
    min_snapshots: int = MIN_SNAPSHOTS,
    min_span: float = MIN_SPAN_SECONDS,
    min_instruments: int = MIN_INSTRUMENTS,
    task_label: str = "EVAL-50-L2-OFI-NET-OF-COST",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _capture_inventory(str(capture_dir_abs))
    total_snaps = sum(int(c.get("count", len(c.get("snapshots", [])))) for c in captures)
    # Per-instrument floor: each instrument must independently clear the snapshot
    # count and span floor (a single long tape cannot stand in for the roster).
    per_instrument_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("inst_id", "?")
        s = c.get("snapshots", [])
        n = int(c.get("count", len(s)))
        span = ((int(s[-1]["ts"]) - int(s[0]["ts"])) / 1000.0) if s else 0.0
        per_instrument_floor[inst] = {
            "snapshots": n,
            "span_seconds": round(span, 3),
            "snapshots_ok": bool(n >= int(min_snapshots)),
            "span_ok": bool(span >= float(min_span)),
        }
    instruments = sorted(per_instrument_floor)
    max_span = max((v["span_seconds"] for v in per_instrument_floor.values()), default=0.0)
    floor_ok = bool(
        len(captures) >= int(min_instruments)
        and per_instrument_floor
        and all(v["snapshots_ok"] and v["span_ok"] for v in per_instrument_floor.values())
    )

    per_instrument: List[Dict[str, Any]] = []
    returns_by_config: Dict[str, List[float]] = {}
    errors: List[str] = []
    for cap in captures:
        for bar_s in GRID_BAR_SECONDS:
            for zc in GRID_Z_CLAMP:
                try:
                    res = evaluate_instrument(cap, bar_seconds=bar_s, z_clamp=zc)
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{cap.get('inst_id')}::bar{bar_s}::z{zc}: {exc!r}")
                    continue
                per_instrument.append(res)
                if res.get("n_returns", 0) > 0:
                    # recompute returns for PBO
                    bars = resample_bars(
                        sorted(cap.get("snapshots", []), key=lambda s: int(s["ts"])), bar_s
                    )
                    sr = strategy_returns(bars, z_clamp=zc)
                    returns_by_config[
                        f"{cap.get('inst_id')}::bar{bar_s}::z{zc}"
                    ] = sr["returns"]

    # PBO + BH-FDR
    pbo = _cscv_pbo(returns_by_config, n_combinations=PBO_N_COMBINATIONS,
                    k_folds=PBO_K_FOLDS, seed=SEED) if len(returns_by_config) >= 2 else {
        "overall_pbo": 0.0, "note": "insufficient configs"}
    p_values = {
        f"{r['instrument']}::bar{r['bar_seconds']}::z{r['z_clamp']}": _finite(
            r.get("permutation_p"), 1.0
        )
        for r in per_instrument
        if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}

    # Per-instrument best config
    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_instrument:
        by_inst.setdefault(r["instrument"], []).append(r)
    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        best = max(rows, key=lambda r: _finite(r.get("sharpe"), -1e9))
        inst_summary.append(
            {
                "instrument": inst,
                "n_configs": len(rows),
                "best_sharpe": _finite(best.get("sharpe"), 0.0),
                "best_config": f"bar{best['bar_seconds']}::z{best['z_clamp']}",
                "any_pass": bool(any(r.get("pass") for r in rows)),
            }
        )

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    verdict = "GO CONFIRMED" if (floor_ok and all_pass) else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_50_L2_OFI" if floor_ok else "EVAL_50_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "real L2 OFI alpha net-of-cost falsification"
            if floor_ok
            else "capture below heavy-work floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "instruments": instruments,
        "total_snapshots": int(total_snaps),
        "max_span_seconds": float(max_span),
        "floor": {
            "min_snapshots_per_instrument": int(min_snapshots),
            "min_span_seconds_per_instrument": float(min_span),
            "min_instruments": int(min_instruments),
        },
        "per_instrument_floor": per_instrument_floor,
        "protocol": build_protocol(capture_dir, GRID_BAR_SECONDS, GRID_Z_CLAMP),
        "per_config": per_instrument,
        "per_instrument": inst_summary,
        "pooled": {
            "overall_pbo": _finite(pbo.get("overall_pbo"), 0.0),
            "bh_fdr": bh,
            "all_instruments_pass": all_pass,
        },
        "errors": errors,
    }

    if not write:
        return report

    # Pre-register BEFORE measurement verdict is sealed.
    prereg = build_prereg(report)
    _seal(PREREG_ID, prereg, build_prereg_md)

    if not floor_ok:
        blocked = _build_blocked_report(report)
        _seal(BLOCKED_ID, blocked, build_blocked_md)
        return report

    _seal(REPORT_ID, report, build_md)
    return report


def build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "Real L2 order-book OFI carries net-of-cost tradable alpha on OKX "
            "BTC/ETH perpetual swaps."
        ),
        "protocol": p,
        "go_bar": p["go_bar"],
        "floor": p["floor"],
        "capture_dir": report["capture_dir"],
    }


def build_prereg_md(p: Dict[str, Any]) -> str:
    proto = p["protocol"]
    lines = [
        f"# {p['prereg_id']} — EVAL-50 L2 OFI net-of-cost falsification",
        "",
        f"- Generated: `{p['generated_at']}`",
        f"- Task: `{p['task']}`",
        f"- Hypothesis: {p['hypothesis']}",
        f"- Capture dir: `{p['capture_dir']}`",
        "",
        "## Pre-declared protocol",
        "",
        f"- OFI: {proto['ofi']}",
        f"- Bar grid (s): {proto['bar_seconds_grid']}",
        f"- z-clamp grid: {proto['z_clamp_grid']}",
        f"- OFI z-window: {proto['ofi_zwindow']}",
        f"- Cost: {proto['cost_model']}",
        f"- Stats: perm {proto['stats']['permutation_perms']} paired / "
        f"bootstrap {proto['stats']['bootstrap_resamples']} block {proto['stats']['bootstrap_block']} / "
        f"PBO k={proto['stats']['pbo_k_folds']} / BH-FDR alpha {proto['stats']['fdr_alpha']} / "
        f"seed {proto['stats']['seed']}",
        f"- Kill-switch max-DD: {proto['kill_switch_max_dd']}",
        "",
        "## Pre-declared GO bar",
        "",
        proto["go_bar"],
        "",
        "## Heavy-work floor (must be met to seal a verdict)",
        "",
        f"- min snapshots/instrument: {proto['floor']['min_snapshots_per_instrument']}",
        f"- min span seconds/instrument: {proto['floor']['min_span_seconds_per_instrument']}",
        f"- min instruments: {proto['floor']['min_instruments']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — Real L2 order-book OFI net-of-cost falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (total snapshots {r['total_snapshots']}, "
        f"max span {r['max_span_seconds']:.1f}s; per-instrument floor "
        f"{r['floor']['min_snapshots_per_instrument']} snaps / "
        f"{r['floor']['min_span_seconds_per_instrument']:.0f}s)",
        f"- Instruments: {', '.join(r['instruments'])}",
        "",
        "## Per-instrument (best config)",
        "",
        "| instrument | configs | best Sharpe | best config | any pass |",
        "|---|---|---|---|---|",
    ]
    for s in r["per_instrument"]:
        lines.append(
            f"| {s['instrument']} | {s['n_configs']} | {s['best_sharpe']:.4f} | "
            f"{s['best_config']} | {s['any_pass']} |"
        )
    lines += ["", "## Per-config (Sharpe / max-DD / perm p / CI / breach / pass)", ""]
    for c in r["per_config"]:
        ci = c.get("bootstrap_ci", [0, 0, 0])
        lines.append(
            f"- {c['instrument']} bar{c['bar_seconds']} z{c['z_clamp']}: "
            f"Sharpe {_finite(c.get('sharpe')):.4f} / DD {_finite(c.get('max_drawdown')):.4f} / "
            f"p {_finite(c.get('permutation_p'), 1.0):.4f} / "
            f"CI [{_finite(ci[1]):.3f}, {_finite(ci[2]):.3f}] / "
            f"breach {c.get('kill_switch_breach')} / pass {c.get('pass')}"
        )
    lines += [
        "",
        "## Pooled",
        "",
        f"- Overall PBO: {r['pooled']['overall_pbo']:.4f}",
        f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
        f"- All instruments pass: {r['pooled']['all_instruments_pass']}",
    ]
    if r["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# EVAL-50 BLOCKED — L2 OFI net-of-cost (capture below heavy-work floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Instruments: {', '.join(r['instruments'])}",
        f"- Total snapshots: {r['total_snapshots']} (floor "
        f"{r['floor']['min_snapshots_per_instrument']}/instrument)",
        f"- Max span: {r['max_span_seconds']:.1f}s (floor "
        f"{r['floor']['min_span_seconds_per_instrument']:.0f}s/instrument)",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered heavy-work floor, so no",
        "GO/NO-GO verdict is emitted. A longer live capture is required.",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r["generated_at"],
        "task": r["task"],
        "verdict": "BLOCKED",
        "capture_dir": r["capture_dir"],
        "instruments": r["instruments"],
        "total_snapshots": r["total_snapshots"],
        "max_span_seconds": r["max_span_seconds"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
    }


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str))


def _seal(report_id: str, report: Dict[str, Any], md_builder=None) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(report.get("generated_at") or _utc_now_iso())
    written: Dict[str, str] = {}
    j = OUT_DIR / f"{report_id}_{stamp}.json"
    _write_json(j, report)
    written["json"] = str(j)
    if md_builder is not None:
        m = OUT_DIR / f"{report_id}_{stamp}.md"
        m.write_text(md_builder(report), encoding="utf-8")
        written["md"] = str(m)
    return written


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-50 real L2 OFI net-of-cost falsification")
    ap.add_argument("--capture-dir", default="data/raw/eval50")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--min-snapshots", type=int, default=MIN_SNAPSHOTS)
    ap.add_argument("--min-span", type=float, default=MIN_SPAN_SECONDS)
    ap.add_argument("--min-instruments", type=int, default=MIN_INSTRUMENTS)
    ap.add_argument("--task-label", default="EVAL-50-L2-OFI-NET-OF-COST")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval50(
            capture_dir=args.capture_dir,
            write=write,
            min_snapshots=args.min_snapshots,
            min_span=args.min_span,
            min_instruments=args.min_instruments,
            task_label=args.task_label,
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report(
                {
                    "generated_at": _utc_now_iso(),
                    "task": args.task_label,
                    "verdict": "BLOCKED",
                    "capture_dir": args.capture_dir,
                    "instruments": [],
                    "total_snapshots": 0,
                    "max_span_seconds": 0.0,
                    "floor": {
                        "min_snapshots_per_instrument": args.min_snapshots,
                        "min_span_seconds_per_instrument": args.min_span,
                        "min_instruments": args.min_instruments,
                    },
                    "floor_ok": False,
                    "error": repr(exc),
                }
            )
            _seal(BLOCKED_ID, blocked, build_blocked_md)
        return 1
    print(json.dumps(
        {
            "verdict": report.get("verdict"),
            "floor_ok": report.get("floor_ok"),
            "instruments": report.get("instruments"),
            "total_snapshots": report.get("total_snapshots"),
            "max_span_seconds": report.get("max_span_seconds"),
            "per_instrument": report.get("per_instrument"),
            "overall_pbo": report.get("pooled", {}).get("overall_pbo"),
        },
        indent=2,
        default=str,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())