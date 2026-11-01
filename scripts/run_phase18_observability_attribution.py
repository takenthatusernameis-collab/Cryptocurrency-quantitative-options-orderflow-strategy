#!/usr/bin/env python3
"""Run Phase 18: Production Observability, PnL Attribution & Live Greeks Hardening."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Ensure repo root on path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.alpha.phase17_campaign import Phase17Campaign, _assert_no_nan_inf
from src.analytics.phase18_attribution import Phase18Attribution
from src.analytics.phase18_greeks_snapshot import Phase18GreeksSnapshot
from src.monitoring.phase18_observability import Phase18Observability
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> str | None:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return sha
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 18 observability + attribution campaign")
    p.add_argument("--symbols", nargs="*", default=["BTC", "ETH", "SOL", "XRP", "ADA"])
    p.add_argument("--venues", nargs="*", default=["deribit", "okx", "binance", "bybit", "bitget"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cycles", type=int, default=5)
    p.add_argument("--paper-only", action="store_true", default=True)
    p.add_argument("--outdir", type=str, default=str(REPO_ROOT / "research_state"))
    p.add_argument("--emit-slo", action="store_true", default=True)
    args = p.parse_args()

    if not args.paper_only:
        raise SystemExit("paper-only required for Phase 18")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Run Phase 17 to get intents/confirmations
    camp17 = Phase17Campaign(symbols=tuple(args.symbols), seed=args.seed, venues=tuple(args.venues),
                             paper_only=True, outdir=outdir, cycles=args.cycles)
    res17 = camp17.run()

    intents = camp17.intents
    confirmations = camp17.confirmations
    killed = bool(res17.get("killed", False))
    kill_reason = res17.get("kill_reason")
    kill_count = 1 if killed else 0

    # Phase 18 components
    attr = Phase18Attribution(seed=args.seed, paper_only=True)
    obs = Phase18Observability(seed=args.seed, paper_only=True)
    greeks_snap = Phase18GreeksSnapshot(seed=args.seed, paper_only=True)

    rep_attr = attr.generate_report(intents, artifacts=res17.get("artifacts"))
    rep_obs = obs.generate_report(intents, confirmations, kill_switch_triggered=killed, kill_count=kill_count, venues=tuple(args.venues))
    rep_greeks = greeks_snap.generate_report(intents)

    sha = _git_sha()
    for rep in [rep_attr, rep_obs, rep_greeks]:
        rep["git_sha"] = sha
        rep["campaign_id"] = camp17.campaign_id
        rep["venues"] = list(args.venues)
        rep["symbols"] = list(args.symbols)
        rep["seed"] = int(args.seed)
        rep["timestamp"] = _utc_now()
        _assert_no_nan_inf(rep, rep.get("report", "unknown"))
        assert_json_valid(rep)

    paths: List[str] = []
    mapping = [
        ("PHASE18_PNL_ATTRIBUTION_REPORT", rep_attr),
        ("PHASE18_OBSERVABILITY_SLO_REPORT", rep_obs),
        ("PHASE18_GREEKS_SNAPSHOT_REPORT", rep_greeks),
    ]
    for name, rep in mapping:
        rep_ser = serialize_metrics_strict(rep)
        p_json = outdir / f"{name}.json"
        p_md = outdir / f"{name}.md"
        p_json.write_text(json.dumps(rep_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        # write simple md
        lines = [f"# {name}", f"Timestamp (UTC): {rep_ser.get('timestamp')}", f"Campaign ID: {rep_ser.get('campaign_id')}",
                 f"Seed: {rep_ser.get('seed')}", f"Symbols: {', '.join(rep_ser.get('symbols', []))}",
                 f"Paper-only: True", f"Git SHA: {rep_ser.get('git_sha')}", ""]
        if "summary" in rep_ser:
            lines.append("## Summary")
            for k, v in rep_ser["summary"].items():
                lines.append(f"- {k}: {v}")
            lines.append("")
        p_md.write_text("\n".join(lines), encoding="utf-8")
        paths.extend([str(p_json), str(p_md)])

    master = {
        "report": "PHASE18_OBSERVABILITY_ATTRIBUTION_MASTER_REPORT",
        "campaign": "phase18_observability_attribution",
        "campaign_id": camp17.campaign_id,
        "timestamp": _utc_now(),
        "seed": args.seed,
        "symbols": list(args.symbols),
        "venues": list(args.venues),
        "paper_only": True,
        "status": "completed",
        "phase17_status": res17.get("status"),
        "killed": killed,
        "kill_reason": kill_reason,
        "git_sha": sha,
        "artifacts": [
            "PHASE18_PNL_ATTRIBUTION_REPORT.json",
            "PHASE18_PNL_ATTRIBUTION_REPORT.md",
            "PHASE18_OBSERVABILITY_SLO_REPORT.json",
            "PHASE18_OBSERVABILITY_SLO_REPORT.md",
            "PHASE18_GREEKS_SNAPSHOT_REPORT.json",
            "PHASE18_GREEKS_SNAPSHOT_REPORT.md",
        ],
        "counts": {
            "intents": len(intents),
            "confirmations": len(confirmations),
            "attribution_lines": len(rep_attr.get("attribution_lines", [])),
            "greeks_snapshots": len(rep_greeks.get("greeks", [])),
        },
    }
    _assert_no_nan_inf(master, "phase18_master")
    master_ser = serialize_metrics_strict(master)
    m_json = outdir / "PHASE18_OBSERVABILITY_ATTRIBUTION_MASTER_REPORT.json"
    m_md = outdir / "PHASE18_OBSERVABILITY_ATTRIBUTION_MASTER_REPORT.md"
    m_json.write_text(json.dumps(master_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    m_md.write_text("\n".join([f"# {master_ser['report']}", f"Timestamp: {master_ser['timestamp']}", f"Status: {master_ser['status']}", ""]), encoding="utf-8")
    paths.extend([str(m_json), str(m_md)])

    print(json.dumps({"status": "ok", "artifacts": paths, "campaign_id": camp17.campaign_id}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
