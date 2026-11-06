#!/usr/bin/env python3
"""Integrated campaign CLI: run/resume/status for the full crypto options + orderflow stack.

Wires the entire pipeline (data -> features -> regimes -> walk-forward/OOS ->
portfolio scaling -> options hedging -> strict artifacts) into one deterministic,
resumable, fully-validated campaign.

Usage:
    python scripts/run_integrated_campaign.py run --campaign-id <id> --seed 42
    python scripts/run_integrated_campaign.py resume --campaign-id <id>
    python scripts/run_integrated_campaign.py status --campaign-id <id>
    python scripts/run_integrated_campaign.py abort --campaign-id <id>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.campaign.integrated import IntegratedCampaign, IntegratedConfig
from src.monitoring.continuous_monitor import ContinuousMonitor


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_config(argv_ns: argparse.Namespace) -> IntegratedConfig:
    return IntegratedConfig(
        seed=int(argv_ns.seed),
        initial_capital=float(argv_ns.initial_capital),
        n_points=int(argv_ns.n_points),
        train_window=int(argv_ns.train_window),
        test_window=int(argv_ns.test_window),
        step_size=int(argv_ns.step_size),
        purge=int(argv_ns.purge),
        embargo=int(argv_ns.embargo),
        allocation_mode=str(argv_ns.allocation_mode),
        vol_target=float(argv_ns.vol_target) if argv_ns.vol_target is not None else None,
        turnover_cap=float(argv_ns.turnover_cap) if argv_ns.turnover_cap is not None else None,
        risk_parity=bool(argv_ns.risk_parity),
        max_position_pct=float(argv_ns.max_position_pct),
        transaction_cost_bps=float(argv_ns.transaction_cost_bps),
        rebalance_every_step=bool(argv_ns.rebalance_every_step),
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run/resume integrated crypto options + orderflow campaign")
    parser.add_argument("command", choices=["run", "resume", "status", "abort"], help="Command to execute")
    parser.add_argument("--campaign-id", type=str, default=None)
    parser.add_argument("--checkpoint-dir", type=str, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--initial-capital", type=float, default=100000.0)
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--train-window", type=int, default=120)
    parser.add_argument("--test-window", type=int, default=40)
    parser.add_argument("--step-size", type=int, default=40)
    parser.add_argument("--purge", type=int, default=10)
    parser.add_argument("--embargo", type=int, default=5)
    parser.add_argument("--allocation-mode", type=str, default="risk_parity", choices=["equal_weight", "risk_parity", "vol_target"])
    parser.add_argument("--vol-target", type=float, default=0.10)
    parser.add_argument("--turnover-cap", type=float, default=0.05)
    parser.add_argument("--risk-parity", action="store_true", default=True)
    parser.add_argument("--no-risk-parity", action="store_true", default=False)
    parser.add_argument("--max-position-pct", type=float, default=0.20)
    parser.add_argument("--transaction-cost-bps", type=float, default=1.0)
    parser.add_argument("--rebalance-every-step", action="store_true", default=True)
    parser.add_argument("--no-rebalance-every-step", action="store_true", default=False)
    args = parser.parse_args(argv)

    if args.no_risk_parity:
        args.risk_parity = False
    if args.no_rebalance_every_step:
        args.rebalance_every_step = False

    checkpoint_dir = Path(args.checkpoint_dir) if args.checkpoint_dir else Path("research_state/campaign_checkpoints")
    config = build_config(args)
    campaign = IntegratedCampaign(
        campaign_id=args.campaign_id,
        checkpoint_dir=checkpoint_dir,
        seed=args.seed,
        config=config,
    )

    try:
        if args.command == "run":
            # If an interrupted/failed campaign exists, resume it; otherwise create fresh.
            st = campaign.status()
            if st.get("state") in ("in_progress", "failed"):
                result = campaign.resume()
            else:
                result = campaign.run()
            out = {
                "status": result.state,
                "campaign_id": result.campaign_id,
                "seed": result.seed,
                "timestamp": result.timestamp,
                "steps_completed": len([s for s in result.steps if s.get("status") == "completed"]),
                "steps_total": len(result.steps),
                "artifacts": result.artifacts,
                "integrated_metrics": result.integrated_metrics,
            }
            # Wire real reconciliation freshness into the E2E campaign runner path:
            # record a reconciliation run, emit one monitor cycle, and surface the
            # slo_reconciliation_freshness SLI/SLO evaluation so the gate is genuinely
            # exercised (paper-only, no live path).
            try:
                mon = ContinuousMonitor(service="crypto-options-orderflow", seed=42, paper_only=True)
                mon.record_reconciliation()
                snap = mon.monitor_cycle()
                slo_evals = mon.slo_monitor.evaluate_all()
                recon_eval = next(
                    (e for e in slo_evals if e.get("slo_id") == "slo_reconciliation_freshness"), None
                )
                out["reconciliation"] = {
                    "freshness": snap["metrics"]["metrics"]["reconciliation_freshness"],
                    "slo": recon_eval,
                    "slo_met": bool(recon_eval.get("met")) if recon_eval else False,
                }
            except Exception as exc:  # pragma: no cover - diagnostic only
                out["reconciliation"] = {"error": str(exc)}
            print(json.dumps(out, indent=2, allow_nan=False))
            return 0
        elif args.command == "resume":
            result = campaign.resume()
            out = {
                "status": result.state,
                "campaign_id": result.campaign_id,
                "seed": result.seed,
                "timestamp": result.timestamp,
                "steps_completed": len([s for s in result.steps if s.get("status") == "completed"]),
                "steps_total": len(result.steps),
                "artifacts": result.artifacts,
            }
            print(json.dumps(out, indent=2, allow_nan=False))
            return 0
        elif args.command == "status":
            st = campaign.status()
            print(json.dumps(st, indent=2, allow_nan=False))
            return 0
        elif args.command == "abort":
            result = campaign.abort()
            print(json.dumps({"status": result.state.value, "campaign_id": result.campaign_id}, indent=2, allow_nan=False))
            return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
