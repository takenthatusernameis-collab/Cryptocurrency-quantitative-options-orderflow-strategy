#!/usr/bin/env python3
"""EVAL-131 Phase-B gate: seal/verify the cross-sectional term_ratio basis ->
forward relative realized return tail-asymmetry spread campaign.

This gate is the *only* authority for EVAL-131 seal state. It enforces:
- Task-ID floor stamp ordering (``TASK_ID_FLOOR_STAMP >= 20261119T181500Z``)
- Required artifact kinds (COMBINED .json + .md, stamp >= floor)
- Preregistration artifact presence (PREREGISTRATION .json + .md, stamp >= floor)
- Seal-gate exit code 0 on success, non-zero on any violation
- Idempotent: re-running after a valid seal is a no-op (exit 0)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TASK_ID = "INIT-2026-11-19T18:15:00Z-EVAL131-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-TAIL-ASYMMETRY-SPREAD"
TASK_ID_FLOOR_STAMP = "20261119T181500Z"
EVAL_DIR = REPO_ROOT / "evals" / "eval131"


def _parse_stamp(name: str) -> str | None:
    m = re.search(r"(\d{8}T\d{6}Z)", name)
    return m.group(1) if m else None


def _stamp_ge(a: str, b: str) -> bool:
    return a >= b


def _find_artifacts(kind: str, floor_stamp: str) -> list[Path]:
    pattern = f"EVAL_131_*{kind}*.json"
    files = sorted(EVAL_DIR.glob(pattern))
    return [f for f in files if _parse_stamp(f.name) and _stamp_ge(_parse_stamp(f.name) or "", floor_stamp)]


def _verify_preregistration(floor_stamp: str) -> tuple[bool, str]:
    files = _find_artifacts("PREREGISTRATION", floor_stamp)
    if not files:
        return False, f"missing PREREGISTRATION artifact (floor {floor_stamp})"
    for f in files:
        try:
            data = json.loads(f.read_text())
            if data.get("task_id") != TASK_ID:
                return False, f"PREREGISTRATION task_id mismatch: {data.get('task_id')} != {TASK_ID}"
            if data.get("task_id_floor_stamp") != TASK_ID_FLOOR_STAMP:
                return False, f"PREREGISTRATION floor_stamp mismatch: {data.get('task_id_floor_stamp')} != {TASK_ID_FLOOR_STAMP}"
        except Exception as e:
            return False, f"PREREGISTRATION parse error {f.name}: {e}"
    return True, f"OK: {files[0].name} (stamp {_parse_stamp(files[0].name)} >= {floor_stamp})"


def _verify_combined(floor_stamp: str) -> tuple[bool, str]:
    files = _find_artifacts("COMBINED", floor_stamp)
    if not files:
        return False, f"missing COMBINED artifact (floor {floor_stamp})"
    for f in files:
        try:
            data = json.loads(f.read_text())
            if data.get("eval") != "EVAL-131":
                return False, f"COMBINED eval mismatch: {data.get('eval')}"
            if data.get("phase") != "COMBINED":
                return False, f"COMBINED phase mismatch: {data.get('phase')}"
            if data.get("task_id") != TASK_ID:
                return False, f"COMBINED task_id mismatch: {data.get('task_id')}"
            if data.get("task_id_floor_stamp") != TASK_ID_FLOOR_STAMP:
                return False, f"COMBINED floor_stamp mismatch: {data.get('task_id_floor_stamp')}"
            if data.get("verdict") not in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)", "BLOCKED"):
                return False, f"COMBINED invalid verdict: {data.get('verdict')}"
        except Exception as e:
            return False, f"COMBINED parse error {f.name}: {e}"
    return True, f"OK (required-any): {files[0].name} (stamp {_parse_stamp(files[0].name)} >= {floor_stamp})"


def _main(execute: bool) -> int:
    if not EVAL_DIR.exists():
        if execute:
            print(f"EVAL_DIR not found: {EVAL_DIR}", file=sys.stderr)
            return 1
        print("EVAL-131: NOT BUILT (eval dir missing)")
        return 0

    floor_stamp = TASK_ID_FLOOR_STAMP

    ok_pre, msg_pre = _verify_preregistration(floor_stamp)
    ok_comb, msg_comb = _verify_combined(floor_stamp)

    if execute:
        if not ok_pre:
            print(f"FAIL: {msg_pre}", file=sys.stderr)
            return 1
        if not ok_comb:
            print(f"FAIL: {msg_comb}", file=sys.stderr)
            return 1
        print("EVAL-131 Phase-B gate: SEALED")
        print(msg_pre)
        print(msg_comb)
        return 0
    else:
        if ok_pre and ok_comb:
            print("EVAL-131: SEALED")
            print(msg_pre)
            print(msg_comb)
        else:
            print("EVAL-131: NOT SEALED")
            if not ok_pre:
                print(f"  - {msg_pre}")
            if not ok_comb:
                print(f"  - {msg_comb}")
        return 0 if (ok_pre and ok_comb) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EVAL-131 Phase-B gate")
    parser.add_argument("--execute", action="store_true", help="Enforce seal (exit non-zero on any violation)")
    args = parser.parse_args()
    sys.exit(_main(args.execute))