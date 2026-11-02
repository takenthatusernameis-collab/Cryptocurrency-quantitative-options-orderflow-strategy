#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from src.integration.phase38_risk_obs_validation_loop import Phase38RiskObsValidationLoop, Loop38Config


def main() -> None:
    cfg = Loop38Config(cycles=12, paper_only=True, modes="paper", outdir="research_state")
    loop = Phase38RiskObsValidationLoop(cfg)
    res = loop.run()
    out = Path("research_state") / "PHASE38_CAMPAIGN_RUN.json"
    out.write_text(json.dumps({"ok": True, "phase": "PHASE38", "summary": {"n_cycles": res["n_cycles"], "risk_ok_cycles": res["risk_ok_cycles"], "gates_ok": res["gates_ok"]}}, indent=2))
    print(json.dumps({"ok": True, "phase38_cycles": res["n_cycles"], "gates_ok": res["gates_ok"]}))


if __name__ == "__main__":
    main()
