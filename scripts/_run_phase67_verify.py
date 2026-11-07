#!/usr/bin/env python3
"""Subprocess verifier for phase67 generator with os._exit to avoid observability thread hang."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "no-write"
    cmd = [
        sys.executable,
        "scripts/generate_phase67_adaptive_toxicity_resilient_recovery_orchestrator_paper_evidence.py",
        "--cycles",
        "80",
        "--seed",
        "67160",
        "--no-write" if mode == "no-write" else "--write",
    ]
    res = subprocess.run(
        cmd,
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
        env={"PYTHONPATH": str(REPO), "PATH": "/usr/share/miniconda/bin:/usr/bin:/bin"},
    )
    print("RETURN_CODE:", res.returncode)
    if res.stdout:
        print("STDOUT_TAIL:", res.stdout[-2000:])
    if res.stderr:
        print("STDERR_TAIL:", res.stderr[-2000:])
    return 0


if __name__ == "__main__":
    main()
    os._exit(0)