#!/usr/bin/env python3
"""Run Phase 40 Post-Trade Reconciliation, Margin/Collateral & Position Auditing Campaign."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Ensure repo root on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.integration.phase40_reconciliation_loop import Phase40ReconciliationLoop, Loop40Config


def main() -> int:
    outdir = os.environ.get("PHASE40_OUTDIR", "research_state")
    cfg = Loop40Config(cycles=int(os.environ.get("PHASE40_CYCLES", "16")), outdir=outdir, paper_only=True)
    loop = Phase40ReconciliationLoop(cfg)
    res = loop.run()
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
