#!/usr/bin/env python3
"""Run Phase 41 Cross-Venue Settlement & Finality Campaign (crypto options + orderflow)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Ensure repo root on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.integration.phase41_settlement_loop import Phase41SettlementLoop, Loop41Config


def main() -> int:
    outdir = os.environ.get("PHASE41_OUTDIR", "research_state")
    cfg = Loop41Config(
        cycles=int(os.environ.get("PHASE41_CYCLES", "16")),
        outdir=outdir,
        paper_only=True,
    )
    loop = Phase41SettlementLoop(cfg)
    res = loop.run()
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())