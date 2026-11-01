#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.execution.phase22_smart_router import SmartOrderRouter
from src.execution.phase22_fill_predictor import FillPredictor
from src.execution.phase22_slippage_model import SlippageModel
from src.execution.phase22_order_slicer import OrderSlicer
from src.analytics.phase22_tca import TCA
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> str | None:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return str(sha)
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


def _assert_no_nan_inf(obj: Any, label: str) -> None:
    import math

    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool):
            if not math.isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite values detected in {label}: {bad[:10]}")


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 22 advanced execution optimization, smart order routing & fill prediction campaign")
    p.add_argument("--symbols", nargs="*", default=["BTC", "ETH", "SOL", "XRP", "ADA"])
    p.add_argument("--venues", nargs="*", default=["deribit", "okx", "binance", "bybit", "bitget"])
    p.add_argument("--strategies", nargs="*", default=["vol_arb", "cross_asset_vol", "orderflow_momentum", "delta_neutral_mm"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cycles", type=int, default=6)
    p.add_argument("--paper-only", action="store_true", default=True)
    p.add_argument("--enforce-gates", action="store_true", default=True)
    p.add_argument("--outdir", type=str, default=str(REPO_ROOT / "research_state"))
    args = p.parse_args()

    if not args.paper_only:
        raise SystemExit("paper-only required for Phase 22")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    router = SmartOrderRouter(seed=args.seed)
    filler = FillPredictor(seed=args.seed)
    slippage = SlippageModel(seed=args.seed)
    slicer = OrderSlicer(seed=args.seed)
    tca = TCA(seed=args.seed)

    import random

    rng = random.Random(args.seed + 22001)

    decisions: List[Any] = []
    signals: List[Any] = []
    predictions: List[Any] = []
    slip_inputs: List[Any] = []
    slip_results: List[Any] = []
    trades: List[Any] = []
    tca_results: List[Any] = []

    for c in range(args.cycles):
        for s_i, sym in enumerate(args.symbols):
            for v_i, ven in enumerate(args.venues):
                strat = args.strategies[(s_i + v_i + c) % len(args.strategies)]
                notional = rng.uniform(50000.0, 1000000.0)
                side = "buy" if (s_i + v_i + c) % 2 == 0 else "sell"
                dec = router.route(sym, side, float(notional), venues=list(args.venues), idx=len(decisions))
                decisions.append(dec)

                spread_bps = rng.uniform(0.5, 4.0)
                depth_usd = rng.uniform(100000.0, 5000000.0)
                latency_ms = rng.uniform(5.0, 45.0)
                of_conf = bool(rng.random() > 0.15)
                sig = filler.make_signal(sym, ven, side, notional / 50000.0, float(notional), spread_bps, depth_usd, latency_ms, of_conf, idx=len(signals))
                signals.append(sig)
                pred = filler.predict(sig, idx=len(predictions))
                predictions.append(pred)

                slip_in = slippage.make_input(sym, ven, side, float(notional), notional / 50000.0, 90000.0 if sym == "BTC" else 3000.0, spread_bps, depth_usd, rng.uniform(0.1, 0.8), idx=len(slip_inputs))
                slip_inputs.append(slip_in)
                slip_res = slippage.estimate(slip_in, idx=len(slip_results))
                slip_results.append(slip_res)

                trade = tca.make_trade(sym, ven, strat, side, float(notional), notional / 50000.0, 90000.0 if sym == "BTC" else 3000.0, 90000.0 if sym == "BTC" else 3000.0, spread_bps, idx=len(trades))
                trades.append(trade)
                tca_res = tca.analyze(trade, idx=len(tca_results))
                tca_results.append(tca_res)

    slicing_plans = []
    for s_i, sym in enumerate(args.symbols):
        for v_i, ven in enumerate(args.venues):
            strat = args.strategies[(s_i + v_i) % len(args.strategies)]
            notional = rng.uniform(100000.0, 2000000.0)
            plan = slicer.slice_order(sym, "buy", float(notional), notional / 50000.0, ven, schedule=["twap", "vwap", "adaptive"][(s_i + v_i) % 3], idx=len(slicing_plans))
            slicing_plans.append(plan)

    rep_router = router.generate_report(decisions)
    rep_fill = filler.generate_report(signals, predictions)
    rep_slip = slippage.generate_report(slip_inputs, slip_results)
    rep_slice = slicer.generate_report(slicing_plans)
    rep_tca = tca.generate_report(trades, tca_results)

    sha = _git_sha()
    reports = [rep_router, rep_fill, rep_slip, rep_slice, rep_tca]
    for rep in reports:
        rep["git_sha"] = sha
        rep["campaign_id"] = f"p22_camp_{sha[:8]}" if sha else "p22_camp_local"
        rep["venues"] = list(args.venues)
        rep["symbols"] = list(args.symbols)
        rep["strategies"] = list(args.strategies)
        rep["seed"] = int(args.seed)
        rep["cycles"] = int(args.cycles)
        rep["paper_only"] = True
        if "timestamp" not in rep or rep.get("timestamp") is None:
            rep["timestamp"] = _utc_now()
        _assert_no_nan_inf(rep, rep.get("report", "unknown"))
        assert_json_valid(rep)

    mapping = [
        ("PHASE22_SMART_ROUTING_REPORT", rep_router),
        ("PHASE22_FILL_PREDICTION_REPORT", rep_fill),
        ("PHASE22_SLIPPAGE_REPORT", rep_slip),
        ("PHASE22_ORDER_SLICING_REPORT", rep_slice),
        ("PHASE22_TCA_REPORT", rep_tca),
    ]
    paths: List[str] = []
    for name, rep in mapping:
        rep_ser = serialize_metrics_strict(rep)
        p_json = outdir / f"{name}.json"
        p_md = outdir / f"{name}.md"
        p_json.write_text(json.dumps(rep_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        lines = [f"# {name}", f"Timestamp (UTC): {rep_ser.get('timestamp')}", f"Campaign ID: {rep_ser.get('campaign_id')}",
                 f"Seed: {rep_ser.get('seed')}", f"Symbols: {', '.join(rep_ser.get('symbols', []))}",
                 f"Venues: {', '.join(rep_ser.get('venues', []))}", f"Strategies: {', '.join(rep_ser.get('strategies', []))}",
                 f"Cycles: {rep_ser.get('cycles')}", f"Paper-only: True", f"Git SHA: {rep_ser.get('git_sha')}", ""]
        if name == "PHASE22_SMART_ROUTING_REPORT":
            lines.append(f"## Decisions: {rep_ser.get('decision_count')} | Routed: {rep_ser.get('routed_count')} | Paper-only: True")
        elif name == "PHASE22_FILL_PREDICTION_REPORT":
            summ = rep_ser.get("summary", {})
            lines.append(f"## Signals: {rep_ser.get('signal_count')} | Predictions: {rep_ser.get('prediction_count')} | Avg Fill Prob: {summ.get('avg_fill_probability')}")
        elif name == "PHASE22_SLIPPAGE_REPORT":
            summ = rep_ser.get("summary", {})
            lines.append(f"## Inputs: {rep_ser.get('input_count')} | Results: {rep_ser.get('result_count')} | Avg Slippage: {summ.get('avg_total_slippage_bps')} bps | Within Limit Rate: {summ.get('within_limit_rate')}")
        elif name == "PHASE22_ORDER_SLICING_REPORT":
            summ = rep_ser.get("summary", {})
            lines.append(f"## Plans: {rep_ser.get('plan_count')} | Total Slices: {rep_ser.get('total_slice_count')} | Avg Slice Notional: {summ.get('avg_slice_notional_usd')}")
        elif name == "PHASE22_TCA_REPORT":
            summ = rep_ser.get("summary", {})
            lines.append(f"## Trades: {rep_ser.get('trade_count')} | Results: {rep_ser.get('result_count')} | Avg Cost: {summ.get('avg_total_cost_bps')} bps | Within Budget Rate: {summ.get('within_budget_rate')}")
        p_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        paths.append(str(p_json))
        paths.append(str(p_md))

    master = {
        "report": "PHASE22_EXECUTION_OPTIMIZATION_MASTER_REPORT",
        "timestamp": _utc_now(),
        "campaign_id": reports[0].get("campaign_id"),
        "seed": int(args.seed),
        "symbols": list(args.symbols),
        "venues": list(args.venues),
        "strategies": list(args.strategies),
        "cycles": int(args.cycles),
        "paper_only": True,
        "git_sha": sha,
        "components": {
            "smart_router": "src/execution/phase22_smart_router.py",
            "fill_predictor": "src/execution/phase22_fill_predictor.py",
            "slippage_model": "src/execution/phase22_slippage_model.py",
            "order_slicer": "src/execution/phase22_order_slicer.py",
            "tca": "src/analytics/phase22_tca.py",
            "campaign_script": "scripts/run_phase22_execution_optimization_campaign.py",
            "tests": "tests/test_phase22_execution_optimization.py",
        },
        "reports": [name for name, _ in mapping],
        "artifacts": paths,
        "summary": {
            "router_decisions": rep_router["decision_count"],
            "router_routed": rep_router["routed_count"],
            "fill_predictions": rep_fill["prediction_count"],
            "avg_fill_prob": rep_fill["summary"]["avg_fill_probability"],
            "slippage_results": rep_slip["result_count"],
            "avg_slippage_bps": rep_slip["summary"]["avg_total_slippage_bps"],
            "slice_plans": rep_slice["plan_count"],
            "total_slices": rep_slice["total_slice_count"],
            "tca_results": rep_tca["result_count"],
            "avg_tca_cost_bps": rep_tca["summary"]["avg_total_cost_bps"],
        },
        "gate_status": "GREEN" if (rep_router["routed_count"] > 0 and rep_fill["prediction_count"] > 0 and rep_slip["summary"]["within_limit_rate"] >= 0.0 and rep_tca["summary"]["within_budget_rate"] >= 0.0) else "YELLOW",
    }
    _assert_no_nan_inf(master, "phase22_master")
    master_ser = serialize_metrics_strict(master)
    (outdir / "PHASE22_EXECUTION_OPTIMIZATION_MASTER_REPORT.json").write_text(json.dumps(master_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    (outdir / "PHASE22_EXECUTION_OPTIMIZATION_MASTER_REPORT.md").write_text(
        "\n".join([
            "# PHASE22_EXECUTION_OPTIMIZATION_MASTER_REPORT",
            f"Timestamp (UTC): {master_ser.get('timestamp')}",
            f"Campaign ID: {master_ser.get('campaign_id')}",
            f"Seed: {master_ser.get('seed')}",
            f"Symbols: {', '.join(master_ser.get('symbols', []))}",
            f"Venues: {', '.join(master_ser.get('venues', []))}",
            f"Strategies: {', '.join(master_ser.get('strategies', []))}",
            f"Cycles: {master_ser.get('cycles')}",
            f"Paper-only: True",
            f"Git SHA: {master_ser.get('git_sha')}",
            "",
            f"## Gate Status: {master_ser.get('gate_status')}",
            f"## Router Decisions: {master_ser['summary']['router_decisions']} | Routed: {master_ser['summary']['router_routed']}",
            f"## Fill Predictions: {master_ser['summary']['fill_predictions']} | Avg Fill Prob: {master_ser['summary']['avg_fill_prob']}",
            f"## Slippage Results: {master_ser['summary']['slippage_results']} | Avg Slippage: {master_ser['summary']['avg_slippage_bps']} bps",
            f"## Slice Plans: {master_ser['summary']['slice_plans']} | Total Slices: {master_ser['summary']['total_slices']}",
            f"## TCA Results: {master_ser['summary']['tca_results']} | Avg Cost: {master_ser['summary']['avg_tca_cost_bps']} bps",
            "",
            "## Components",
        ]) + "\n" + "\n".join(f"- {k}: {v}" for k, v in master_ser["components"].items()) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"ok": True, "gate_status": master_ser["gate_status"], "artifacts": len(paths) + 2}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
