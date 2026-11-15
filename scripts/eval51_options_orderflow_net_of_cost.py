#!/usr/bin/env python3
"""EVAL-51: real Deribit **options order flow** net-of-cost falsification.

The repository charter is a **combined options + orderflow** strategy. Every prior
rung falsified option *candles/surface/greeks* (EVAL-46..49) or *spot* order flow
(trade tape EVAL-43/45, L2 book OFI EVAL-50). The one order-flow modality that has
never been measured is the **order flow of the options venue itself**: the signed
aggressor flow of real Deribit option trades. This script is the net-of-cost
falsification of that signal on real, historical Deribit option trades captured by
``scripts/eval51_acquire_options_orderflow.py``.

It is strictly additive: it consumes only the measured capture JSON files under
``--capture-dir`` and reuses the sealed statistics helpers (``_sharpe_of_returns``,
``_dsr_of_returns``, ``_cscv_pbo``, ``_benjamini_hochberg``, ``block_bootstrap_ci``,
``permutation_test``). It never re-runs a prior EVAL and never edits ``src/``.

Pre-declared protocol (identical for every underlying; no curve fitting):
  - resample the underlying perpetual 5m candles to a ``--bar-seconds`` grid and
    take the last close per bar;
  - for each bar, aggregate the real option trades whose timestamp falls in
    ``(bar_end - bar_seconds, bar_end]`` into three pre-registered signed-flow
    signals:
      * ``imbalance``        = (buy_amt - sell_amt) / (buy_amt + sell_amt)
      * ``notional_imbalance``= (notional_buy - notional_sell) / (notional_buy + notional_sell)
      * ``call_minus_put``   = ((call_buy-call_sell) - (put_buy-put_sell)) / total_amt
    where amounts are measured Deribit ``amount`` (underlying units) and notional
    weights by ``index_price``;
  - signal = causal expanding z-score of the per-bar signal over ``--zwindow`` bars;
  - position = ``clip(z / Z_CLAMP, -1, 1)`` (pre-registered);
  - per-bar net-of-cost return = ``pos_t * perp_return_{t->t+1}``
    ``- cost_bps * |pos_t - pos_{t-1}| / 1e4``, where ``cost_bps`` is the
    pre-registered conservative Deribit-perp taker + impact cost;
  - full-series (causal -> out-of-sample) plus rolling walk-forward Sharpe/max-DD;
  - stats: 1000-perm paired permutation (strategy vs flat), 1000-resample block
    bootstrap CI on Sharpe (block 2), CSCV PBO across the pre-registered grid,
    BH-FDR (alpha 0.1), DSR; seed 42.

Pre-declared GO bar (conservative; the campaign is TERMINATED so NO-GO is the
default and GO needs strong evidence): GO only if, on **both** BTC and ETH and
**at least one** grid config, net-of-cost Sharpe > 0, no kill-switch breach
(max-DD <= 0.20), permutation p < 0.05, and bootstrap 95% CI lower bound > 0.
Otherwise ``NO-GO CONFIRMED (PASS)``: signed options order flow is not net-of-cost
tradable on the real Deribit option tape.

Heavy-work floor (sealed): refuses to seal a verdict unless **every** underlying
independently clears ``--min-trades`` option trades, ``--min-bars`` bars,
``--min-instruments`` distinct option instruments with trades and ``--min-span``
seconds, and the roster has ``--min-underlyings`` underlyings — otherwise seals a
measured ``EVAL_51_BLOCKED_<UTC>`` (never a NO-GO). This makes a short/partial
capture unable to satisfy the campaign.

Seal ``EVAL_51_PREREGISTRATION_<UTC>.{json,md}`` (before measurement) then
``EVAL_51_OPTIONS_ORDERFLOW_COMBINED_<UTC>.{json,md}`` (or ``EVAL_51_BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import glob
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
REPORT_ID = "EVAL_51_OPTIONS_ORDERFLOW_COMBINED"
PREREG_ID = "EVAL_51_PREREGISTRATION"
BLOCKED_ID = "EVAL_51_BLOCKED"

BAR_SECONDS = 5.0
ZWINDOW = 20
Z_CLAMP = 2.0
COST_BPS = 5.0
PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
PBO_K_FOLDS = 4
PBO_N_COMBINATIONS = 16
FDR_ALPHA = 0.1
SEED = 42
KILL_SWITCH_MAX_DD = 0.20

MIN_TRADS = 2000
MIN_BARS = 240
MIN_INSTRUMENTS = 50
MIN_SPAN_SECONDS = 79200.0
MIN_UNDERLYINGS = 2

SIGNALS: Tuple[str, ...] = ("imbalance", "notional_imbalance", "call_minus_put")
GRID_BAR_SECONDS: Tuple[float, ...] = (5.0, 15.0)

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval51_acquire_options_orderflow.py",
    "scripts/eval51_options_orderflow_net_of_cost.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval51_acquire_options_orderflow.py "
    "scripts/eval51_options_orderflow_net_of_cost.py "
    "tests/test_eval51_options_orderflow_net_of_cost.py",
    "python3 -m pytest -q tests/test_eval51_options_orderflow_net_of_cost.py",
    "python3 scripts/eval51_acquire_options_orderflow.py "
    "--underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval51 --seal",
    "python3 scripts/eval51_options_orderflow_net_of_cost.py --no-write",
    "python3 scripts/eval51_options_orderflow_net_of_cost.py",
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


def _bar_end(ts_ms: int, bar_ms: int) -> int:
    return ((int(ts_ms) // bar_ms) + 1) * bar_ms


def build_bars(capture: Dict[str, Any], bar_seconds: float) -> List[Dict[str, Any]]:
    """Resample perp candles to ``bar_seconds`` and aggregate option-trade flow.

    Returns a time-ordered list of bars, each carrying the last underlying close in
    the bar, the underlying return into the next bar, and the three signed-flow
    signal components for trades in ``(bar_end - bar_seconds, bar_end]``.
    """
    bar_ms = int(float(bar_seconds) * 1000)
    candles = sorted(capture.get("perp_candles", []), key=lambda c: int(c["ts"]))
    if len(candles) < 2:
        return []

    # 1) bar closes from the underlying perpetual candles (last close per bucket).
    closes: Dict[int, float] = {}
    for c in candles:
        be = _bar_end(int(c["ts"]), bar_ms)
        try:
            px = float(c["close"])
        except (TypeError, ValueError):
            continue
        if px > 0:
            closes[be] = px

    # 2) aggregate signed option flow per bar.
    agg: Dict[int, Dict[str, float]] = {}

    def _bucket(be: int) -> Dict[str, float]:
        b = agg.get(be)
        if b is None:
            b = {
                "buy_amt": 0.0, "sell_amt": 0.0,
                "notional_buy": 0.0, "notional_sell": 0.0,
                "call_buy": 0.0, "call_sell": 0.0,
                "put_buy": 0.0, "put_sell": 0.0,
                "n_trades": 0,
            }
            agg[be] = b
        return b

    for t in capture.get("option_trades", []):
        try:
            ts = int(t["ts"])
            amt = abs(float(t.get("amount") or 0.0))
        except (TypeError, ValueError):
            continue
        if amt <= 0 or ts <= 0:
            continue
        idx = float(t.get("index_price") or 0.0)
        direction = str(t.get("direction") or "").lower()
        opt = str(t.get("option_type") or "").lower()
        be = _bar_end(ts, bar_ms)
        b = _bucket(be)
        b["n_trades"] += 1
        notional = amt * idx
        if direction == "buy":
            b["buy_amt"] += amt
            b["notional_buy"] += notional
            if opt == "call":
                b["call_buy"] += amt
            elif opt == "put":
                b["put_buy"] += amt
        elif direction == "sell":
            b["sell_amt"] += amt
            b["notional_sell"] += notional
            if opt == "call":
                b["call_sell"] += amt
            elif opt == "put":
                b["put_sell"] += amt

    # 3) assemble bars over the candle grid.
    bars: List[Dict[str, Any]] = []
    for be in sorted(closes):
        b = agg.get(be, {
            "buy_amt": 0.0, "sell_amt": 0.0,
            "notional_buy": 0.0, "notional_sell": 0.0,
            "call_buy": 0.0, "call_sell": 0.0,
            "put_buy": 0.0, "put_sell": 0.0,
            "n_trades": 0,
        })
        total_amt = b["buy_amt"] + b["sell_amt"]
        total_notional = b["notional_buy"] + b["notional_sell"]
        imbalance = (b["buy_amt"] - b["sell_amt"]) / total_amt if total_amt > 0 else 0.0
        notional_imbalance = (
            (b["notional_buy"] - b["notional_sell"]) / total_notional
            if total_notional > 0 else 0.0
        )
        cp = (b["call_buy"] - b["call_sell"]) - (b["put_buy"] - b["put_sell"])
        call_minus_put = cp / total_amt if total_amt > 0 else 0.0
        bars.append({
            "bar_end": int(be),
            "close": float(closes[be]),
            "imbalance": float(imbalance),
            "notional_imbalance": float(notional_imbalance),
            "call_minus_put": float(call_minus_put),
            "n_trades": int(b["n_trades"]),
        })

    # 4) attach causal underlying return into the next bar.
    for i, bar in enumerate(bars):
        if i + 1 < len(bars) and bar["close"] > 0 and bars[i + 1]["close"] > 0:
            bar["ret"] = bars[i + 1]["close"] / bar["close"] - 1.0
        else:
            bar["ret"] = 0.0
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
    signal: str,
    *,
    zwindow: int = ZWINDOW,
    z_clamp: float = Z_CLAMP,
    cost_bps: float = COST_BPS,
) -> Dict[str, Any]:
    """Causal signed-flow strategy: position = clip(z/z_clamp); net-of-cost returns."""
    if len(bars) < 4:
        return {"returns": [], "positions": [], "turnover": [], "nonzero": 0,
                "signal_std": 0.0, "signal_z_std": 0.0}
    xs = [float(b.get(signal, 0.0)) for b in bars]
    zs = expanding_zscore(xs, zwindow)
    positions = [max(-1.0, min(1.0, z / float(z_clamp))) for z in zs]
    returns: List[float] = []
    turnovers: List[float] = []
    prev_pos = 0.0
    for i in range(len(bars) - 1):
        pos = positions[i]
        gross = pos * float(bars[i].get("ret", 0.0))
        turnover = abs(pos - prev_pos)
        cost = float(cost_bps) * turnover / 1e4
        returns.append(gross - cost)
        turnovers.append(turnover)
        prev_pos = pos
    nonzero = sum(1 for p in positions if abs(p) > 1e-9)
    return {
        "returns": returns,
        "positions": positions,
        "turnover": turnovers,
        "nonzero": int(nonzero),
        "signal_std": _std(xs),
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
        folds.append({
            "test_start": start,
            "test_end": start + int(test),
            "oos_sharpe": _sharpe_of_returns(seg),
            "oos_max_drawdown": _max_drawdown(seg),
            "n": len(seg),
        })
        start += int(step)
    return folds


def evaluate_capture(
    capture: Dict[str, Any],
    *,
    signal: str,
    bar_seconds: float,
    z_clamp: float = Z_CLAMP,
    cost_bps: float = COST_BPS,
    ofi_zwindow: int = ZWINDOW,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    bars = build_bars(capture, bar_seconds)
    sr = strategy_returns(bars, signal, zwindow=ofi_zwindow, z_clamp=z_clamp,
                          cost_bps=cost_bps)
    rets = sr["returns"]
    if len(rets) < 3:
        return {
            "underlying": inst, "signal": signal, "bar_seconds": float(bar_seconds),
            "error": "insufficient bars/returns", "n_returns": 0, "pass": False,
        }
    sharpe = _sharpe_of_returns(rets)
    mdd = _max_drawdown(rets)
    flat = [0.0] * len(rets)
    perm = permutation_test(rets, flat, statistic=_mean,
                            n_permutations=PERMUTATION_PERMS, paired=True, seed=SEED)
    boot = block_bootstrap_ci(rets, statistic=_sharpe_of_returns,
                              n_bootstrap=BOOTSTRAP_RESAMPLES, block_size=BOOTSTRAP_BLOCK,
                              seed=SEED)
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
        and sr["signal_std"] > 0.0
    )
    return {
        "underlying": inst,
        "signal": signal,
        "bar_seconds": float(bar_seconds),
        "n_bars": len(bars),
        "n_returns": len(rets),
        "nonzero_positions": sr["nonzero"],
        "signal_std": sr["signal_std"],
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


def _capture_inventory(capture_dir: str) -> List[Dict[str, Any]]:
    """Load captures, keeping the newest capture per underlying."""
    best: Dict[str, Tuple[int, Dict[str, Any]]] = {}
    for path in sorted(glob.glob(os.path.join(capture_dir, "options_orderflow_*.json"))):
        try:
            c = json.loads(Path(path).read_text())
        except (OSError, ValueError):
            continue
        inst = c.get("underlying", "?")
        stamp = 0
        try:
            # filename stem like ..._20260101T000000Z -> 20260101000000 (int-comparable)
            stamp = int("".join(ch for ch in Path(path).stem.split("_")[-1] if ch.isdigit()))
        except ValueError:
            stamp = 0
        # Newest capture file per underlying wins; a short pre-capture that shares
        # the underlying is never double-counted.
        if inst not in best or stamp > best[inst][0]:
            best[inst] = (stamp, c)
    return [c for _, c in best.values()]


def build_protocol(
    capture_dir: str,
    signals: Sequence[str],
    bar_seconds_grid: Sequence[float],
) -> Dict[str, Any]:
    return {
        "eval": "EVAL-51",
        "title": "Real Deribit options order flow net-of-cost falsification",
        "capture_dir": str(capture_dir),
        "signals": list(signals),
        "bar_seconds_grid": [float(b) for b in bar_seconds_grid],
        "zwindow": int(ZWINDOW),
        "z_clamp": float(Z_CLAMP),
        "cost_bps": float(COST_BPS),
        "cost_model": "net-of-cost: pre-registered conservative Deribit perp taker + impact bps on turnover",
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
            "min_option_trades_per_underlying": MIN_TRADS,
            "min_bars_per_underlying": MIN_BARS,
            "min_instruments_per_underlying": MIN_INSTRUMENTS,
            "min_span_seconds_per_underlying": MIN_SPAN_SECONDS,
            "min_underlyings": MIN_UNDERLYINGS,
        },
    }


def run_eval51(
    *,
    capture_dir: str = "data/raw/eval51",
    write: bool = True,
    min_trades: int = MIN_TRADS,
    min_bars: int = MIN_BARS,
    min_instruments: int = MIN_INSTRUMENTS,
    min_span: float = MIN_SPAN_SECONDS,
    min_underlyings: int = MIN_UNDERLYINGS,
    task_label: str = "EVAL-51-OPTIONS-ORDERFLOW-NET-OF-COST",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _capture_inventory(str(capture_dir_abs))

    # Per-underlying heavy-work floor.
    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        trades = c.get("option_trades", [])
        insts = {t.get("instrument") for t in trades}
        ts = [int(t["ts"]) for t in trades if int(t.get("ts") or 0) > 0]
        span = ((max(ts) - min(ts)) / 1000.0) if len(ts) >= 2 else 0.0
        n_trades = len(trades)
        n_instruments = len({i for i in insts if i})
        bars = build_bars(c, BAR_SECONDS)
        per_underlying_floor[inst] = {
            "n_option_trades": n_trades,
            "n_instruments_with_trades": n_instruments,
            "n_bars_5m": len(bars),
            "span_seconds": round(span, 3),
            "trades_ok": bool(n_trades >= int(min_trades)),
            "bars_ok": bool(len(bars) >= int(min_bars)),
            "instruments_ok": bool(n_instruments >= int(min_instruments)),
            "span_ok": bool(span >= float(min_span)),
        }
    underlyings = sorted(per_underlying_floor)
    floor_ok = bool(
        len(captures) >= int(min_underlyings)
        and per_underlying_floor
        and all(
            v["trades_ok"] and v["bars_ok"] and v["instruments_ok"] and v["span_ok"]
            for v in per_underlying_floor.values()
        )
    )

    per_config: List[Dict[str, Any]] = []
    returns_by_config: Dict[str, List[float]] = {}
    errors: List[str] = []
    for cap in captures:
        for sig in SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                try:
                    res = evaluate_capture(cap, signal=sig, bar_seconds=bar_s)
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{cap.get('underlying')}::{sig}::bar{bar_s}: {exc!r}")
                    continue
                per_config.append(res)
                if res.get("n_returns", 0) > 0:
                    bars = build_bars(cap, bar_s)
                    sr = strategy_returns(bars, sig)
                    returns_by_config[
                        f"{cap.get('underlying')}::{sig}::bar{bar_s}"
                    ] = sr["returns"]

    pbo = _cscv_pbo(returns_by_config, n_combinations=PBO_N_COMBINATIONS,
                    k_folds=PBO_K_FOLDS, seed=SEED) if len(returns_by_config) >= 2 else {
        "overall_pbo": 0.0, "note": "insufficient configs"}
    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}": _finite(
            r.get("permutation_p"), 1.0
        )
        for r in per_config if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)
    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        best = max(rows, key=lambda r: _finite(r.get("sharpe"), -1e9))
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_sharpe": _finite(best.get("sharpe"), 0.0),
            "best_config": f"{best['signal']}::bar{best['bar_seconds']}",
            "any_pass": bool(any(r.get("pass") for r in rows)),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    verdict = "GO CONFIRMED" if (floor_ok and all_pass) else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_51_OPTIONS_ORDERFLOW" if floor_ok else "EVAL_51_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "real Deribit options order-flow net-of-cost falsification"
            if floor_ok else "capture below heavy-work floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": underlyings,
        "floor": {
            "min_option_trades_per_underlying": int(min_trades),
            "min_bars_per_underlying": int(min_bars),
            "min_instruments_per_underlying": int(min_instruments),
            "min_span_seconds_per_underlying": float(min_span),
            "min_underlyings": int(min_underlyings),
        },
        "per_underlying_floor": per_underlying_floor,
        "protocol": build_protocol(capture_dir, SIGNALS, GRID_BAR_SECONDS),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "overall_pbo": _finite(pbo.get("overall_pbo"), 0.0),
            "bh_fdr": bh,
            "all_underlyings_pass": all_pass,
            "campaign_state": campaign_state,
        },
        "errors": errors,
    }

    if not write:
        return report

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
            "Signed options order flow on real Deribit option trades carries "
            "net-of-cost tradable alpha for the underlying BTC/ETH perpetual."
        ),
        "protocol": p,
        "go_bar": p["go_bar"],
        "floor": p["floor"],
        "capture_dir": report["capture_dir"],
    }


def build_prereg_md(p: Dict[str, Any]) -> str:
    proto = p["protocol"]
    lines = [
        f"# {p['prereg_id']} — EVAL-51 options order-flow net-of-cost falsification",
        "",
        f"- Generated: `{p['generated_at']}`",
        f"- Task: `{p['task']}`",
        f"- Hypothesis: {p['hypothesis']}",
        f"- Capture dir: `{p['capture_dir']}`",
        "",
        "## Pre-declared protocol",
        "",
        f"- Signals: {proto['signals']}",
        f"- Bar grid (s): {proto['bar_seconds_grid']}",
        f"- z-window: {proto['zwindow']}; z-clamp: {proto['z_clamp']}",
        f"- Cost: {proto['cost_model']} ({proto['cost_bps']} bps)",
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
        f"- min option trades/underlying: {proto['floor']['min_option_trades_per_underlying']}",
        f"- min bars/underlying: {proto['floor']['min_bars_per_underlying']}",
        f"- min instruments/underlying: {proto['floor']['min_instruments_per_underlying']}",
        f"- min span seconds/underlying: {proto['floor']['min_span_seconds_per_underlying']}",
        f"- min underlyings: {proto['floor']['min_underlyings']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — Real Deribit options order flow net-of-cost falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])}; per-underlying floor "
        f"{r['floor']['min_option_trades_per_underlying']} trades / "
        f"{r['floor']['min_bars_per_underlying']} bars / "
        f"{r['floor']['min_instruments_per_underlying']} instruments / "
        f"{r['floor']['min_span_seconds_per_underlying']:.0f}s)",
        "",
        "## Per-underlying (best config)",
        "",
        "| underlying | configs | best Sharpe | best config | any pass |",
        "|---|---|---|---|---|",
    ]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_sharpe']:.4f} | "
            f"{s['best_config']} | {s['any_pass']} |"
        )
    lines += ["", "## Per-config (Sharpe / max-DD / perm p / CI / breach / pass)", ""]
    for c in r["per_config"]:
        ci = c.get("bootstrap_ci", [0, 0, 0])
        lines.append(
            f"- {c['underlying']} {c['signal']} bar{c['bar_seconds']}: "
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
        f"- All underlyings pass: {r['pooled']['all_underlyings_pass']}",
    ]
    if r["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# EVAL-51 BLOCKED — options order-flow net-of-cost (below heavy-work floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered heavy-work floor, so no",
        "GO/NO-GO verdict is emitted. A longer/wider real Deribit options trade",
        "capture is required.",
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
        "underlyings": r["underlyings"],
        "per_underlying_floor": r["per_underlying_floor"],
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
    ap = argparse.ArgumentParser(description="EVAL-51 real Deribit options order flow net-of-cost falsification")
    ap.add_argument("--capture-dir", default="data/raw/eval51")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--min-trades", type=int, default=MIN_TRADS)
    ap.add_argument("--min-bars", type=int, default=MIN_BARS)
    ap.add_argument("--min-instruments", type=int, default=MIN_INSTRUMENTS)
    ap.add_argument("--min-span", type=float, default=MIN_SPAN_SECONDS)
    ap.add_argument("--min-underlyings", type=int, default=MIN_UNDERLYINGS)
    ap.add_argument("--task-label", default="EVAL-51-OPTIONS-ORDERFLOW-NET-OF-COST")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval51(
            capture_dir=args.capture_dir,
            write=write,
            min_trades=args.min_trades,
            min_bars=args.min_bars,
            min_instruments=args.min_instruments,
            min_span=args.min_span,
            min_underlyings=args.min_underlyings,
            task_label=args.task_label,
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
                "floor": {
                    "min_option_trades_per_underlying": args.min_trades,
                    "min_bars_per_underlying": args.min_bars,
                    "min_instruments_per_underlying": args.min_instruments,
                    "min_span_seconds_per_underlying": args.min_span,
                    "min_underlyings": args.min_underlyings,
                },
                "floor_ok": False,
                "error": repr(exc),
            })
            _seal(BLOCKED_ID, blocked, build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_underlying_floor": report.get("per_underlying_floor"),
        "per_underlying": report.get("per_underlying"),
        "overall_pbo": report.get("pooled", {}).get("overall_pbo"),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())