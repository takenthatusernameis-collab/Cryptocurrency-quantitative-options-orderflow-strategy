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

from src.risk.phase21_risk_aggregator import Phase21RiskAggregator
from src.risk.phase21_stress_tester import Phase21StressTester
from src.risk.phase21_pre_trade_validator import Phase21PreTradeValidator, TradeIntent
from src.monitoring.phase21_risk_monitor import Phase21RiskMonitor
from src.analytics.phase21_risk_attribution import Phase21RiskAttribution
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
    p = argparse.ArgumentParser(description="Phase 21 real-time risk aggregation, stress testing & pre-trade validation campaign")
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
        raise SystemExit("paper-only required for Phase 21")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    agg = Phase21RiskAggregator(seed=args.seed)
    stress = Phase21StressTester(seed=args.seed)
    validator = Phase21PreTradeValidator(seed=args.seed)
    monitor = Phase21RiskMonitor(seed=args.seed)
    attrib = Phase21RiskAttribution(seed=args.seed)

    snapshots = agg.aggregate_exposures(list(args.strategies), list(args.venues), list(args.symbols))
    rep_agg = agg.generate_report(snapshots)

    scenarios = stress.build_scenarios()
    results = stress.run_stress(scenarios)
    rep_stress = stress.generate_report(scenarios, results)

    intents: List[TradeIntent] = []
    import random

    rng = random.Random(args.seed + 21001)
    for i in range(40):
        sym = args.symbols[i % len(args.symbols)]
        ven = args.venues[i % len(args.venues)]
        strat = args.strategies[i % len(args.strategies)]
        notional = rng.uniform(5000.0, 200000.0)
        intents.append(
            TradeIntent(
                intent_id=f"p21_int_{i:04d}",
                symbol=sym.upper(),
                venue=ven.lower(),
                strategy=strat,
                side="buy" if i % 2 == 0 else "sell",
                qty=notional / 50000.0,
                notional_usd=float(notional),
                delta_est=float(rng.uniform(-150.0, 150.0)),
                vega_est=float(rng.uniform(-2000.0, 2000.0)),
                gamma_est=float(rng.uniform(0.0001, 0.01)),
                orderflow_confirmed=bool(rng.random() > 0.1),
                paper_only=True,
            )
        )
    decisions = validator.validate(intents, aggregated_delta=float(rep_agg["limits"]["totals"]["delta"]), aggregated_vega=float(rep_agg["limits"]["totals"]["vega"]), aggregated_notional=float(rep_agg["limits"]["totals"]["notional_usd"]))
    rep_pretrade = validator.generate_report(intents, decisions)

    attr_lines = attrib.attribute(snapshots)
    rep_attr = attrib.generate_report(snapshots, attr_lines)

    rep_monitor = monitor.generate_report(rep_agg["limits"], stress_summary=rep_stress["summary"], pretrade_summary=rep_pretrade["summary"], drift_summary={"within_bounds": True})

    sha = _git_sha()
    reports = [rep_agg, rep_stress, rep_pretrade, rep_monitor, rep_attr]
    for rep in reports:
        rep["git_sha"] = sha
        rep["campaign_id"] = f"p21_camp_{sha[:8]}" if sha else "p21_camp_local"
        rep["venues"] = list(args.venues)
        rep["symbols"] = list(args.symbols)
        rep["strategies"] = list(args.strategies)
        rep["seed"] = int(args.seed)
        if "timestamp" not in rep or rep.get("timestamp") is None:
            rep["timestamp"] = _utc_now()
        _assert_no_nan_inf(rep, rep.get("report", "unknown"))
        assert_json_valid(rep)

    mapping = [
        ("PHASE21_RISK_AGGREGATION_REPORT", rep_agg),
        ("PHASE21_STRESS_TESTING_REPORT", rep_stress),
        ("PHASE21_PRE_TRADE_VALIDATION_REPORT", rep_pretrade),
        ("PHASE21_RISK_MONITORING_REPORT", rep_monitor),
        ("PHASE21_RISK_ATTRIBUTION_REPORT", rep_attr),
    ]
    paths: List[str] = []
    for name, rep in mapping:
        rep_ser = serialize_metrics_strict(rep)
        p_json = outdir / f"{name}.json"
        p_md = outdir / f"{name}.md"
        p_json.write_text(json.dumps(rep_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        lines = [f"# {name}", f"Timestamp (UTC): {rep_ser.get('timestamp')}", f"Campaign ID: {rep_ser.get('campaign_id')}",
                 f"Seed: {rep_ser.get('seed')}", f"Symbols: {', '.join(rep_ser.get('symbols', []))}",
                 f"Venues: {', '.join(rep_ser.get('venues', []))}", f"Paper-only: True", f"Git SHA: {rep_ser.get('git_sha')}", ""]
        if name == "PHASE21_RISK_AGGREGATION_REPORT":
            lim = rep_ser.get("limits", {})
            lines.append(f"## Totals: notional={lim.get('totals', {}).get('notional_usd')}, delta={lim.get('totals', {}).get('delta')}, vega={lim.get('totals', {}).get('vega')}")
            lines.append(f"## Passed: {lim.get('passed')} | Breaches: {len(lim.get('breaches', []))}")
        elif name == "PHASE21_STRESS_TESTING_REPORT":
            summ = rep_ser.get("summary", {})
            lines.append(f"## Scenarios: {rep_ser.get('scenario_count')} | Breach Count: {summ.get('breach_count')} | Worst PnL: {summ.get('worst_pnl_impact_usd')}")
        elif name == "PHASE21_PRE_TRADE_VALIDATION_REPORT":
            summ = rep_ser.get("summary", {})
            lines.append(f"## Intents: {rep_ser.get('intent_count')} | Blocked: {summ.get('blocked_count')} | Approved: {summ.get('approved_count')}")
        elif name == "PHASE21_RISK_MONITORING_REPORT":
            mon = rep_ser.get("monitoring", {})
            lines.append(f"## Alerts: {mon.get('alert_count')} | Critical: {mon.get('critical_count')} | Healthy: {mon.get('healthy')}")
        elif name == "PHASE21_RISK_ATTRIBUTION_REPORT":
            lines.append(f"## Lines: {rep_ser.get('line_count')} | Total PnL Attrib: {rep_ser.get('total_pnl_attrib_usd')}")
        p_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        paths.append(str(p_json))
        paths.append(str(p_md))

    master = {
        "report": "PHASE21_RISK_STRESS_MASTER_REPORT",
        "timestamp": _utc_now(),
        "campaign_id": reports[0].get("campaign_id"),
        "seed": int(args.seed),
        "symbols": list(args.symbols),
        "venues": list(args.venues),
        "strategies": list(args.strategies),
        "paper_only": True,
        "git_sha": sha,
        "components": {
            "risk_aggregator": "src/risk/phase21_risk_aggregator.py",
            "stress_tester": "src/risk/phase21_stress_tester.py",
            "pre_trade_validator": "src/risk/phase21_pre_trade_validator.py",
            "risk_monitor": "src/monitoring/phase21_risk_monitor.py",
            "risk_attribution": "src/analytics/phase21_risk_attribution.py",
            "campaign_script": "scripts/run_phase21_risk_stress_campaign.py",
            "tests": "tests/test_phase21_risk_stress.py",
        },
        "reports": [name for name, _ in mapping],
        "artifacts": paths,
        "summary": {
            "agg_passed": rep_agg["limits"]["passed"],
            "stress_breaches": rep_stress["summary"]["breach_count"],
            "pretrade_blocked": rep_pretrade["summary"]["blocked_count"],
            "monitor_healthy": rep_monitor["monitoring"]["healthy"],
            "attr_lines": rep_attr["line_count"],
        },
        "gate_status": "GREEN" if (rep_agg["limits"]["passed"] and rep_stress["summary"]["all_passed"] and rep_monitor["monitoring"]["healthy"]) else "YELLOW",
    }
    _assert_no_nan_inf(master, "phase21_master")
    master_ser = serialize_metrics_strict(master)
    (outdir / "PHASE21_RISK_STRESS_MASTER_REPORT.json").write_text(json.dumps(master_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    (outdir / "PHASE21_RISK_STRESS_MASTER_REPORT.md").write_text(
        "\n".join([
            "# PHASE21_RISK_STRESS_MASTER_REPORT",
            f"Timestamp (UTC): {master_ser.get('timestamp')}",
            f"Campaign ID: {master_ser.get('campaign_id')}",
            f"Seed: {master_ser.get('seed')}",
            f"Symbols: {', '.join(master_ser.get('symbols', []))}",
            f"Venues: {', '.join(master_ser.get('venues', []))}",
            f"Paper-only: True",
            f"Git SHA: {master_ser.get('git_sha')}",
            "",
            f"## Gate Status: {master_ser.get('gate_status')}",
            f"## Agg Passed: {master_ser['summary']['agg_passed']} | Stress Breaches: {master_ser['summary']['stress_breaches']} | Pretrade Blocked: {master_ser['summary']['pretrade_blocked']} | Monitor Healthy: {master_ser['summary']['monitor_healthy']} | Attr Lines: {master_ser['summary']['attr_lines']}",
            "",
            "## Components",
        ]) + "\n" + "\n".join(f"- {k}: {v}" for k, v in master_ser["components"].items()) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"ok": True, "gate_status": master_ser["gate_status"], "artifacts": len(paths) + 2}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
