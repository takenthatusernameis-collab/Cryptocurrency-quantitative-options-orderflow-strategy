#!/usr/bin/env python3
"""Generate phase60 adaptive execution intelligence engine depth paper evidence (additive, paper-only)."""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
sys.path.insert(0, str(REPO))

from src.execution.phase60_adaptive_execution_intelligence_engine import (
    Phase60AdaptiveExecutionIntelligenceEngine,
    Phase60AdaptiveExecutionIntelligenceConfig,
)
from src.telemetry.serialization import serialize_metrics_strict

ARTIFACT_TYPE = "PHASE60_ADAPTIVE_EXECUTION_INTELLIGENCE_ENGINE_PAPER_EVIDENCE"
VENUES = ("deribit", "okx", "binance")
SYMBOLS = ("BTC-USD", "ETH-USD")
UNDERLYINGS = ("BTC", "ETH")
COVERAGE_CYCLES = 8


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _assert_finite(obj: Any, label: str) -> List[str]:
    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool) and not math.isfinite(v):
            bad.append(p)

    walk(obj, "$")
    return [f"non_finite:{label}:{p}" for p in bad[:20]]


def build(seed: int, cycles: int, write: bool) -> Dict[str, Any]:
    cfg = Phase60AdaptiveExecutionIntelligenceConfig(seed=seed, paper_only=True, cycles=cycles,
                                                     venues=("deribit", "okx", "binance"))
    eng = Phase60AdaptiveExecutionIntelligenceEngine(cfg=cfg)
    rep = eng.run_intelligence(cycles=cycles)
    issues = _assert_finite(rep, "report")
    # determinism: rerun
    rep2 = Phase60AdaptiveExecutionIntelligenceEngine(cfg=cfg).run_intelligence(cycles=cycles)

    def _strip(obj):
        if isinstance(obj, dict):
            return {k: _strip(v) for k, v in obj.items() if k not in ("timestamp", "timestamp_utc")}
        if isinstance(obj, list):
            return [_strip(v) for v in obj]
        return obj

    deterministic = _strip(rep) == _strip(rep2)
    artifact = serialize_metrics_strict({
        "artifact_type": ARTIFACT_TYPE,
        "timestamp_utc": _utc_iso(),
        "seed": seed,
        "cycles": cycles,
        "venues": list(VENUES),
        "symbols": list(SYMBOLS),
        "underlyings": list(UNDERLYINGS),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "no_external_venue_mutation": True,
        "advisory": True,
        "deterministic": bool(deterministic),
        "finite_validated": len(issues) == 0,
        "campaign": {"paper_only": True, "cycles": cycles, "seed": seed},
        "engine_report": rep,
        "cross_refs": ["PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION_PAPER_EVIDENCE_20261107T185604Z.json"],
        "evidence_refs": ["src/execution/phase60_adaptive_execution_intelligence_engine.py"],
    })
    if write:
        ts = _utc()
        path = RS / f"PHASE60_ADAPTIVE_EXECUTION_INTELLIGENCE_ENGINE_PAPER_EVIDENCE_{ts}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, sort_keys=True, allow_nan=False)
        artifact["artifact_path"] = str(path)
    return artifact


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=80)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    write = args.write and not args.no_write
    art = build(args.seed, args.cycles, write)
    print(json.dumps({"valid": art.get("finite_validated"), "deterministic": art.get("deterministic"),
                      "paper_only": art.get("paper_only"), "path": art.get("artifact_path")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY=scripts/generate_phase60_adaptive_execution_intelligence_engine_paper_evidence.py