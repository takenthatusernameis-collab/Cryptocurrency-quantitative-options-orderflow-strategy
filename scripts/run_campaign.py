#!/usr/bin/env python3
"""Campaign CLI with run/resume/status/abort and atomic checkpointing."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.campaign.core import CampaignOrchestrator


def default_steps():
    return [
        {"step_id": "data_prep", "name": "Data preparation and validation"},
        {"step_id": "feature_engineering", "name": "Feature engineering (orderflow/gamma/IV/liquidity)"},
        {"step_id": "walkforward_oos", "name": "Walk-forward/OOS validation"},
        {"step_id": "portfolio_scaling", "name": "Portfolio scaling with allocation/turnover controls"},
        {"step_id": "options_hedging", "name": "Options hedging robustness"},
        {"step_id": "campaign_artifacts", "name": "Generate campaign artifacts and summary"},
    ]


def dummy_executor(step, checkpoint):
    # Deterministic dummy step for validation; real runs can override
    import time

    time.sleep(0.001)
    artifact = Path("research_state") / f"CAMPAIGN_{checkpoint.campaign_id}_{step.step_id}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "campaign_id": checkpoint.campaign_id,
        "step_id": step.step_id,
        "status": "completed",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    artifact.write_text(json.dumps(data, indent=2, allow_nan=False), encoding="utf-8")
    checkpoint.artifacts.append(str(artifact))
    return str(artifact)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run/resume campaign orchestration")
    parser.add_argument("command", choices=["run", "resume", "status", "abort"], help="Command to execute")
    parser.add_argument("--campaign-id", type=str, default=None)
    parser.add_argument("--checkpoint-dir", type=str, default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    checkpoint_dir = Path(args.checkpoint_dir) if args.checkpoint_dir else Path("research_state/campaign_checkpoints")
    orch = CampaignOrchestrator(campaign_id=args.campaign_id, checkpoint_dir=checkpoint_dir, seed=args.seed)

    try:
        if args.command == "run":
            if orch.load_latest_checkpoint() is not None and orch.checkpoint and orch.checkpoint.state.value in ("in_progress", "failed"):
                # If interrupted/failed, suggest resume; but run should create fresh? Or be idempotent - create new campaign
                pass
            # Create new campaign for run
            steps = default_steps()
            orch.create_campaign(steps, metadata={"command": "run", "seed": args.seed})
            result = orch.run(dummy_executor)
            print(json.dumps({"status": result.state.value, "campaign_id": result.campaign_id}, indent=2))
            return 0
        elif args.command == "resume":
            result = orch.resume(dummy_executor)
            print(json.dumps({"status": result.state.value, "campaign_id": result.campaign_id}, indent=2))
            return 0
        elif args.command == "status":
            st = orch.status()
            print(json.dumps(st, indent=2))
            return 0
        elif args.command == "abort":
            result = orch.abort()
            print(json.dumps({"status": result.state.value, "campaign_id": result.campaign_id}, indent=2))
            return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
