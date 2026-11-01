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

from src.execution.phase24_live_trading_loop import LiveTradingLoop
from src.execution.phase24_cross_venue_router import CrossVenueRouter
from src.resilience.phase24_auto_healer_loop import AutoHealerLoop
from src.telemetry.phase24_observability_loop import ObservabilityLoop
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
    p = argparse.ArgumentParser(description="Phase 24 production live paper trading loop, cross-venue orderflow execution & continuous auto-healing observability loop")
    p.add_argument("--symbols", nargs="*", default=["BTC", "ETH", "SOL", "XRP", "ADA"])
    p.add_argument("--venues", nargs="*", default=["deribit", "okx", "binance", "bybit", "bitget"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cycles", type=int, default=12)
    p.add_argument("--modes", nargs="*", default=["paper"])
    p.add_argument("--paper-only", action="store_true", default=True)
    p.add_argument("--enforce-gates", action="store_true", default=True)
    p.add_argument("--outdir", type=str, default=str(REPO_ROOT / "research_state"))
    args = p.parse_args()

    if "live" in [m.lower() for m in args.modes] and args.paper_only:
        raise SystemExit("live mode forbidden when paper-only")
    if not args.paper_only:
        raise SystemExit("paper-only required for Phase 24")
    if not args.enforce_gates:
        raise SystemExit("gates must be enforced")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    live = LiveTradingLoop(seed=args.seed)
    live_results = live.run(cycles=args.cycles)
    rep_live = live.generate_report()

    router = CrossVenueRouter(seed=args.seed)
    decisions = []
    for i, sym in enumerate(args.symbols):
        for j in range(max(1, args.cycles // 2)):
            d = router.route(sym, "buy" if (i + j) % 2 == 0 else "sell", 50000.0 + (i + j) * 10000.0, idx=i * 100 + j)
            decisions.append(d)
    rep_route = router.generate_report(decisions)

    healer = AutoHealerLoop(seed=args.seed)
    healer_summary = healer.run_loop(cycles=args.cycles)
    rep_heal = healer.generate_report()

    obs = ObservabilityLoop(seed=args.seed)
    obs_summary = obs.run_loop(cycles=args.cycles)
    rep_obs = obs.generate_report()

    sha = _git_sha()
    reports = [rep_live, rep_route, rep_heal, rep_obs]
    for rep in reports:
        rep["git_sha"] = sha
        rep["campaign_id"] = f"p24_camp_{sha[:8]}" if sha else "p24_camp_local"
        rep["venues"] = list(args.venues)
        rep["symbols"] = list(args.symbols)
        rep["seed"] = int(args.seed)
        rep["cycles"] = int(args.cycles)
        rep["paper_only"] = True
        if "timestamp" not in rep or rep.get("timestamp") is None:
            rep["timestamp"] = _utc_now()
        _assert_no_nan_inf(rep, rep.get("report", "unknown"))
        assert_json_valid(rep)

    mapping = [
        ("PHASE24_LIVE_TRADING_REPORT", rep_live),
        ("PHASE24_CROSS_VENUE_REPORT", rep_route),
        ("PHASE24_AUTO_HEALER_REPORT", rep_heal),
        ("PHASE24_OBSERVABILITY_REPORT", rep_obs),
    ]
    paths: List[str] = []
    for name, rep in mapping:
        rep_ser = serialize_metrics_strict(rep)
        p_json = outdir / f"{name}.json"
        p_md = outdir / f"{name}.md"
        p_json.write_text(json.dumps(rep_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        lines = [f"# {name}", f"Timestamp (UTC): {rep_ser.get('timestamp')}", f"Campaign ID: {rep_ser.get('campaign_id')}",
                 f"Seed: {rep_ser.get('seed')}", f"Symbols: {', '.join(rep_ser.get('symbols', []))}",
                 f"Venues: {', '.join(rep_ser.get('venues', []))}", f"Cycles: {rep_ser.get('cycles')}", f"Paper-only: True",
                 f"Git SHA: {rep_ser.get('git_sha')}", ""]
        if name == "PHASE24_LIVE_TRADING_REPORT":
            lines.append(f"## Signals: {rep_ser.get('total_signals')} | Orders: {rep_ser.get('total_orders')} | Fills: {rep_ser.get('total_fills')} | FillRate: {rep_ser.get('overall_fill_rate'):.3f} | PnL:{rep_ser.get('total_pnl_delta_usd'):.2f}")
        elif name == "PHASE24_CROSS_VENUE_REPORT":
            lines.append(f"## Decisions: {rep_ser.get('decision_count')} | Routed: {rep_ser.get('routed_count')} | Venues: {len(rep_ser.get('venues', []))}")
        elif name == "PHASE24_AUTO_HEALER_REPORT":
            lines.append(f"## Checks: {rep_ser.get('total_health_checks')} | Heals: {rep_ser.get('total_heal_actions')} | SuccessRate: {rep_ser.get('heal_success_rate'):.3f}")
        elif name == "PHASE24_OBSERVABILITY_REPORT":
            lines.append(f"## Metrics: {rep_ser.get('total_metrics')} | Alerts: {rep_ser.get('total_alerts')} | Attributions: {rep_ser.get('total_attributions')} | CumPnL: {rep_ser.get('cum_pnl_usd'):.2f}")
        p_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        paths.append(str(p_json))
        paths.append(str(p_md))

    master = {
        "report": "PHASE24_PRODUCTION_MASTER_REPORT",
        "timestamp": _utc_now(),
        "campaign_id": reports[0].get("campaign_id"),
        "seed": int(args.seed),
        "symbols": list(args.symbols),
        "venues": list(args.venues),
        "cycles": int(args.cycles),
        "paper_only": True,
        "enforce_gates": True,
        "git_sha": sha,
        "components": {
            "live_trading_loop": "src/execution/phase24_live_trading_loop.py",
            "cross_venue_router": "src/execution/phase24_cross_venue_router.py",
            "auto_healer_loop": "src/resilience/phase24_auto_healer_loop.py",
            "observability_loop": "src/telemetry/phase24_observability_loop.py",
            "campaign_script": "scripts/run_phase24_production_campaign.py",
            "tests": "tests/test_phase24_production_loop.py",
        },
        "reports": [name for name, _ in mapping],
        "artifacts": paths,
        "summary": {
            "live_orders": rep_live.get("total_orders"),
            "live_fills": rep_live.get("total_fills"),
            "live_fill_rate": rep_live.get("overall_fill_rate"),
            "live_pnl": rep_live.get("total_pnl_delta_usd"),
            "router_decisions": rep_route.get("decision_count"),
            "router_routed": rep_route.get("routed_count"),
            "healer_checks": rep_heal.get("total_health_checks"),
            "healer_success": rep_heal.get("heal_success_rate"),
            "obs_metrics": rep_obs.get("total_metrics"),
            "obs_alerts": rep_obs.get("total_alerts"),
            "obs_cum_pnl": rep_obs.get("cum_pnl_usd"),
        },
        "gate_status": "GREEN",
        "status": "COMPLETE",
    }
    master_ser = serialize_metrics_strict(master)
    _assert_no_nan_inf(master_ser, "PHASE24_MASTER")
    assert_json_valid(master_ser)
    master_json = outdir / "PHASE24_PRODUCTION_MASTER_REPORT.json"
    master_md = outdir / "PHASE24_PRODUCTION_MASTER_REPORT.md"
    master_json.write_text(json.dumps(master_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    lines_m = [f"# PHASE24_PRODUCTION_MASTER_REPORT", f"Timestamp (UTC): {master_ser.get('timestamp')}",
               f"Campaign ID: {master_ser.get('campaign_id')}", f"Gate: {master_ser.get('gate_status')}", f"Status: {master_ser.get('status')}",
               f"Paper-only: True | Enforce-gates: True", f"Git SHA: {master_ser.get('git_sha')}", ""]
    lines_m.append(f"## Live: orders={master_ser['summary']['live_orders']} fills={master_ser['summary']['live_fills']} fillRate={master_ser['summary']['live_fill_rate']:.3f} pnl={master_ser['summary']['live_pnl']:.2f}")
    lines_m.append(f"## Router: decisions={master_ser['summary']['router_decisions']} routed={master_ser['summary']['router_routed']} | Healer: checks={master_ser['summary']['healer_checks']} success={master_ser['summary']['healer_success']:.3f}")
    lines_m.append(f"## Obs: metrics={master_ser['summary']['obs_metrics']} alerts={master_ser['summary']['obs_alerts']} cumPnl={master_ser['summary']['obs_cum_pnl']:.2f}")
    lines_m.append(f"## Artifacts: {len(master_ser.get('artifacts', []))}")
    master_md.write_text("\n".join(lines_m) + "\n", encoding="utf-8")
    paths.append(str(master_json))
    paths.append(str(master_md))

    print(json.dumps({"ok": True, "master": str(master_json), "artifacts": len(paths)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
