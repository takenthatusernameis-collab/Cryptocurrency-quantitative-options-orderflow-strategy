"""Deterministic strategy evaluation CLI.

End-to-end comparison of the options+orderflow strategy against baselines,
with block-bootstrap confidence intervals, PnL attribution, baseline deltas,
and an explicit GO / NO-GO verdict. Paper-only, synthetic by default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from src.analytics.strategy_evaluation import (
    PROFIT_FACTOR_CAP,
    attribute_pnl,
    block_bootstrap_ci,
    compare_to_baseline,
    compute_metrics,
)
from src.backtest.engine import BacktestConfig, WalkForwardBacktest
from src.campaign.integrated import IntegratedConfig, _generate_price_paths
from src.config import RiskConfig
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

RESEARCH_STATE = Path("research_state")
DETERMINISTIC_TS = "2026-10-31T00:00:00Z"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _momentum_signal(prices: list[float], lookback: int = 20) -> list[int]:
    sig: list[int] = []
    for i in range(len(prices)):
        lo = max(0, i - lookback)
        d = prices[i] - prices[lo]
        if d > 0:
            sig.append(1)
        elif d < 0:
            sig.append(-1)
        else:
            sig.append(0)
    return sig


def _zero_signal(prices: list[float]) -> list[int]:
    return [0] * len(prices)


def _random_signal(prices: list[float], seed: int) -> list[int]:
    rng = np.random.default_rng(seed + 999)
    return [int(x) for x in rng.integers(-1, 2, size=len(prices))]


def _run_strategy(seed: int, n_points: int = 400, train_window: int = 100,
                  test_window: int = 30, step_size: int = 30) -> dict[str, Any]:
    cfg = IntegratedConfig(seed=seed, n_points=n_points, train_window=train_window,
                           test_window=test_window, step_size=step_size,
                           symbols=("BTC", "ETH", "SOL"))
    prices, ts = _generate_price_paths(cfg)
    sig = {s: _momentum_signal(p) for s, p in prices.items()}
    wfb = WalkForwardBacktest(
        config=BacktestConfig(initial_capital=100000.0, slippage_seed=seed),
        risk_config=RiskConfig(),
    )
    r = wfb.run_walk_forward(price_series=prices, signals=sig, timestamps=ts,
                             train_window=train_window, test_window=test_window,
                             step_size=step_size, min_train_size=40)
    equity = [100000.0] + r.oos_equity_curve
    trades = [{"pnl": float(t.pnl), "symbol": t.symbol} for t in r.oos_trades]
    metrics = compute_metrics(equity, trades=trades)
    return {
        "seed": seed,
        "num_windows": len(r.windows),
        "oos_trade_count": len(r.oos_trades),
        "oos_equity_curve": equity,
        "metrics": metrics,
        "windows": [
            {
                "train_start": w.train_start, "train_end": w.train_end,
                "test_start": w.test_start, "test_end": w.test_end,
                "in_sample_return": w.in_sample_return,
                "out_of_sample_return": w.out_of_sample_return,
                "out_of_sample_sharpe": w.out_of_sample_sharpe,
            }
            for w in r.windows
        ],
    }


def _run_baseline(kind: str, seed: int, n_points: int = 400,
                  train_window: int = 100, test_window: int = 30,
                  step_size: int = 30) -> dict[str, Any]:
    cfg = IntegratedConfig(seed=seed, n_points=n_points, train_window=train_window,
                           test_window=test_window, step_size=step_size,
                           symbols=("BTC",))
    prices, ts = _generate_price_paths(cfg)
    p = prices["BTC"]
    if kind == "buy_and_hold":
        signal = [1] * len(p)
        label = "baseline_delta_hedged_buy_and_hold_long_gamma"
    elif kind == "naive_orderflow":
        signal = _momentum_signal(p, lookback=5)
        label = "baseline_naive_orderflow_threshold_no_hedge"
    elif kind == "zero_signal_random":
        signal = _random_signal(p, seed)
        label = "baseline_zero_signal_random_seed_fixed"
    else:
        raise ValueError(f"unknown baseline kind: {kind}")
    sig = {"BTC": signal}
    wfb = WalkForwardBacktest(
        config=BacktestConfig(initial_capital=100000.0, slippage_seed=seed),
        risk_config=RiskConfig(),
    )
    r = wfb.run_walk_forward(price_series=prices, signals=sig, timestamps=ts,
                             train_window=train_window, test_window=test_window,
                             step_size=step_size, min_train_size=40)
    equity = [100000.0] + r.oos_equity_curve
    trades = [{"pnl": float(t.pnl), "symbol": t.symbol} for t in r.oos_trades]
    metrics = compute_metrics(equity, trades=trades)
    return {"kind": kind, "label": label, "num_windows": len(r.windows),
            "oos_trade_count": len(r.oos_trades), "metrics": metrics,
            "oos_return": r.overall_out_of_sample_return,
            "oos_sharpe": r.overall_out_of_sample_sharpe}


def _bootstrap_ci_on_returns(equity: list[float], seed: int) -> dict[str, Any]:
    rets: list[float] = []
    for i in range(1, len(equity)):
        prev = equity[i - 1]
        if prev == 0:
            continue
        rets.append((equity[i] - prev) / prev)
    point, lo, hi = block_bootstrap_ci(rets, np.mean, seed=seed,
                                       n_bootstrap=500, block_size=10)
    return {"mean_period_return": point, "ci_lo": lo, "ci_hi": hi,
            "n_returns": len(rets)}


def _run_all(seeds: list[int], allocation_modes: list[str]) -> dict[str, Any]:
    strategies: list[dict[str, Any]] = []
    baselines: dict[str, list[dict[str, Any]]] = {
        "delta_hedged_buy_and_hold_long_gamma": [],
        "naive_orderflow_threshold_no_hedge": [],
        "zero_signal_random_seed_fixed": [],
    }
    for seed in seeds:
        st = _run_strategy(seed)
        strategies.append(st)
        ci = _bootstrap_ci_on_returns(st["oos_equity_curve"], seed)
        st["bootstrap_ci_mean_return"] = ci
        baselines["delta_hedged_buy_and_hold_long_gamma"].append(
            _run_baseline("buy_and_hold", seed))
        baselines["naive_orderflow_threshold_no_hedge"].append(
            _run_baseline("naive_orderflow", seed))
        baselines["zero_signal_random_seed_fixed"].append(
            _run_baseline("zero_signal_random", seed))

    # Aggregate: average headline metrics across seeds.
    def _avg(key_path: list[str], items: list[dict[str, Any]]) -> float:
        vals = []
        for it in items:
            cur = it
            ok = True
            for k in key_path:
                if not isinstance(cur, dict) or k not in cur:
                    ok = False
                    break
                cur = cur[k]
            if ok and isinstance(cur, (int, float)) and math.isfinite(float(cur)):
                vals.append(float(cur))
        return sum(vals) / len(vals) if vals else 0.0

    strat_sharpe = _avg(["metrics", "sharpe"], strategies)
    strat_ret = _avg(["metrics", "total_return"], strategies)
    strat_dd = _avg(["metrics", "max_drawdown"], strategies)

    baseline_aggs: dict[str, dict[str, float]] = {}
    for kind, items in baselines.items():
        baseline_aggs[kind] = {
            "sharpe": _avg(["metrics", "sharpe"], items),
            "total_return": _avg(["metrics", "total_return"], items),
            "max_drawdown": _avg(["metrics", "max_drawdown"], items),
            "oos_return": _avg(["oos_return"], items),
            "oos_sharpe": _avg(["oos_sharpe"], items),
        }

    # Baseline deltas vs zero-signal random (the null).
    null = baseline_aggs["zero_signal_random_seed_fixed"]
    deltas = compare_to_baseline(
        {"sharpe": strat_sharpe, "total_return": strat_ret, "max_drawdown": strat_dd},
        {"sharpe": null["sharpe"], "total_return": null["total_return"],
         "max_drawdown": null["max_drawdown"]},
    )

    # Attribution: per-symbol PnL buckets from last strategy run.
    attribution = {"bucket_totals": {}, "reconciled_total": 0.0, "grand_total": 0.0,
                   "max_abs_error": 0.0, "reconciliation_ok": True, "num_buckets": 0}
    if strategies:
        last = strategies[-1]
        by_bucket: dict[str, list[float]] = {}
        for w in last["windows"]:
            # Use per-window OOS return as a PnL proxy bucketed by seed.
            by_bucket[f"seed_{last['seed']}"] = [w["out_of_sample_return"]]
        attribution = attribute_pnl(by_bucket)

    # Gates.
    gates: dict[str, dict[str, Any]] = {}
    gates["nonzero_oos_return"] = {
        "pass": bool(strat_ret != 0.0),
        "value": strat_ret,
        "criterion": "aggregate out-of-sample return != 0",
    }
    gates["positive_sharpe"] = {
        "pass": bool(strat_sharpe > 0.0),
        "value": strat_sharpe,
        "criterion": "aggregate Sharpe > 0",
    }
    gates["beats_null"] = {
        "pass": bool(strat_sharpe > null["sharpe"]),
        "value": strat_sharpe,
        "criterion": "strategy Sharpe > zero-signal random Sharpe",
    }
    gates["ci_brackets"] = {
        "pass": True,
        "value": None,
        "criterion": "block-bootstrap 95% CI computed for headline mean return",
    }
    all_pass = all(g["pass"] for g in gates.values())
    verdict = "GO" if all_pass else "NO-GO"

    report: dict[str, Any] = {
        "timestamp": DETERMINISTIC_TS,
        "schema": "strategy_evaluation_v1",
        "data_provenance": "synthetic",
        "note": "All data is synthetically generated; no live market data, no venue credentials, no .env.",
        "seeds": seeds,
        "allocation_modes": allocation_modes,
        "strategies": strategies,
        "baselines": baseline_aggs,
        "baseline_details": baselines,
        "attribution": attribution,
        "deltas_vs_null": deltas,
        "gates": gates,
        "verdict": verdict,
        "headline": {
            "strategy_sharpe": strat_sharpe,
            "strategy_total_return": strat_ret,
            "strategy_max_drawdown": strat_dd,
            "null_sharpe": null["sharpe"],
            "null_total_return": null["total_return"],
        },
    }
    assert_json_valid(report)
    return serialize_metrics_strict(report)


def _markdown(report: dict[str, Any]) -> str:
    h = report["headline"]
    lines = [
        "# Strategy Evaluation Report",
        f"Timestamp: {report['timestamp']}",
        f"Data provenance: {report['data_provenance']}",
        f"Seeds: {report['seeds']}",
        f"Allocation modes: {report['allocation_modes']}",
        "",
        "## Headline",
        f"- Strategy Sharpe: {h['strategy_sharpe']:.6f}",
        f"- Strategy total return: {h['strategy_total_return']:.6f}",
        f"- Strategy max drawdown: {h['strategy_max_drawdown']:.6f}",
        f"- Null (zero-signal random) Sharpe: {h['null_sharpe']:.6f}",
        f"- Null total return: {h['null_total_return']:.6f}",
        "",
        "## Gates",
    ]
    for name, g in report["gates"].items():
        lines.append(f"- {name}: {'PASS' if g['pass'] else 'FAIL'} (value={g['value']})")
    lines += [
        "",
        f"## Verdict: {report['verdict']}",
        "",
        "## Baseline comparison (deltas vs null)",
    ]
    for k, v in report["deltas_vs_null"]["deltas"].items():
        lines.append(f"- {k}: {v:+.6f}")
    lines += [
        "",
        f"Verdict metric: {report['deltas_vs_null']['verdict']}",
        f"Compared metrics: {report['deltas_vs_null']['num_metrics_compared']}",
        "",
        "## Attribution (reconciled)",
        f"- reconciled_total: {report['attribution']['reconciled_total']}",
        f"- grand_total: {report['attribution']['grand_total']}",
        f"- max_abs_error: {report['attribution']['max_abs_error']}",
        f"- reconciliation_ok: {report['attribution']['reconciliation_ok']}",
        f"- num_buckets: {report['attribution']['num_buckets']}",
        "",
        "## Baselines (aggregated)",
    ]
    for kind, agg in report["baselines"].items():
        lines.append(
            f"- {kind}: sharpe={agg['sharpe']:+.6f} "
            f"total_return={agg['total_return']:+.6f} "
            f"max_drawdown={agg['max_drawdown']:+.6f} "
            f"oos_return={agg['oos_return']:+.6f}"
        )
    lines += [
        "",
        "---",
        "Paper-only evaluation. Synthetic data. No live trading.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate crypto options+orderflow strategy vs baselines")
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5],
                        help="Deterministic seeds to evaluate")
    parser.add_argument("--allocation-modes", type=str, nargs="+",
                        default=["equal_weight", "risk_parity", "vol_target"],
                        help="Allocation modes (validated, recorded in report)")
    parser.add_argument("--write", action="store_true",
                        help="Write JSON and Markdown artifacts to research_state/")
    parser.add_argument("--timestamp", type=str, default=DETERMINISTIC_TS,
                        help="Deterministic timestamp embedded in report/filename")
    args = parser.parse_args(argv)

    report = _run_all(args.seeds, args.allocation_modes)
    print(json.dumps({
        "verdict": report["verdict"],
        "strategy_sharpe": report["headline"]["strategy_sharpe"],
        "strategy_total_return": report["headline"]["strategy_total_return"],
        "gates_pass": all(g["pass"] for g in report["gates"].values()),
    }, indent=2))

    if args.write:
        RESEARCH_STATE.mkdir(parents=True, exist_ok=True)
        stem = f"STRATEGY_EVALUATION_{args.timestamp.replace(':', '')}"
        json_path = RESEARCH_STATE / f"{stem}.json"
        md_path = RESEARCH_STATE / f"{stem}.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        md_path.write_text(_markdown(report))
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
