#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from src.integration.phase39_live_readiness_loop import Phase39LiveReadinessLoop, Loop39Config


def main() -> None:
    cfg = Loop39Config(seed=39039, cycles=12, paper_only=True, modes="paper", outdir="research_state")
    loop = Phase39LiveReadinessLoop(cfg)
    res = loop.run()
    out = Path("research_state/PHASE39_LIVE_READINESS_CAMPAIGN_RESULT.json")
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps({"phase": res["phase"], "n_cycles": res["n_cycles"], "trading_enabled_cycles": res["trading_enabled_cycles"], "gates_ok": res["gates_ok"]}))


if __name__ == "__main__":
    main()
