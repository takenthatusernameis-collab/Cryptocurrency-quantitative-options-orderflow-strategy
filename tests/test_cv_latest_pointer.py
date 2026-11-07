"""Deterministic CV latest-pointer regression test (paper-only).

`run_continuous_validation` must refresh
`campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json` so that
downstream readiness checks see the run as fresh evidence. Without this, every
strict CV run leaves the previous checkpoint in place and readiness checks
falsely report a stale CV.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_cv_script_refreshes_latest_pointer():
    cp = REPO / "research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json"

    proc = subprocess.run(
        [sys.executable, "scripts/run_continuous_validation.py",
         "--iterations", "5", "--strict", "--symbols", "BTC,ETH", "--seed", "42"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert cp.exists(), "CV script must refresh the latest checkpoint pointer"
    after = json.loads(cp.read_text(encoding="utf-8"))
    assert after["paper_only"] is True
    assert after["live_trading_enabled"] is False
    assert after["gates"]["all_critical_passed"] is True
    assert after["gates"]["iterations_5_5"] is True
    rf = after["reconciliation_freshness"]
    assert rf["met"] is True
    assert rf["measurements_per_iteration"] == [1, 1, 1, 1, 1]
    # Pointer must reference the freshly written immutable artifact.
    cv_ref = after["artifacts"]["continuous_validation"]
    immutable = REPO / cv_ref
    assert immutable.exists(), f"missing immutable CV ref {cv_ref}"
    imm = json.loads(immutable.read_text(encoding="utf-8"))
    assert imm["campaign"]["status"] == "complete"