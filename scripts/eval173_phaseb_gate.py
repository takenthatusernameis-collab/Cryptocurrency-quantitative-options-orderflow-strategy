#!/usr/bin/env python3
"""EVAL-173 Phase-B gate: deterministic, idempotent completion arbiter.

EVAL-173 measures the single-asset causal near-ATM implied-vol ``skew`` surface
signal against forward realized return variance on the real on-disk captures.
The gate has three outcomes: SEALED (0), DUE (20), and FAILED (1).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RS_DIR = ROOT / "research_state"

TASK_ID = "INIT-2026-11-21T21:17:00Z-EVAL173-SINGLE-ASSET-SKEW-FORWARD-VARIANCE"
TASK_LABEL = "EVAL173-SINGLE-ASSET-SKEW-FORWARD-VARIANCE"
PREREG_GLOB = "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_COMBINED_*"
BLOCKED_GLOB = "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_BLOCKED_*"

CAPTURE_DIR = ROOT / "data" / "raw" / "eval61"

EXIT_SEALED = 0
EXIT_FAILED = 1
EXIT_DUE = 20

_ISO_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)")
_STAMP_RE = re.compile(r"(\d{8}T\d{6}(?:\d+)?Z)")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_stamp(iso_ts: str) -> str:
    text = iso_ts.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def task_floor_stamp(task_id: str) -> str:
    match = _ISO_RE.search(task_id)
    if not match:
        raise ValueError(f"task id has no ISO-8601 UTC timestamp: {task_id!r}")
    return _to_stamp(match.group(1))


def detect_seal(
    research_state_dir: Path,
    *,
    task_id: str = TASK_ID,
    combined_glob: str = COMBINED_GLOB,
    blocked_glob: str = BLOCKED_GLOB,
) -> Dict[str, Any]:
    rs = Path(research_state_dir)
    floor = task_floor_stamp(task_id)
    hits: List[Dict[str, str]] = []
    if rs.is_dir():
        for pattern, kind in ((combined_glob, "COMBINED"), (blocked_glob, "BLOCKED")):
            for path in sorted(rs.glob(pattern)):
                if not path.is_file():
                    continue
                stamps = _STAMP_RE.findall(path.name)
                if not stamps:
                    continue
                top = max(stamps)
                if top >= floor:
                    hits.append({"name": path.name, "stamp": top, "kind": kind})
    hits.sort(key=lambda item: item["stamp"])
    return {"sealed": bool(hits), "artifacts": hits, "floor_stamp": floor}


def run_seal_gate_check(
    *,
    task_id: str = TASK_ID,
    research_state_dir: Path = RS_DIR,
    script_path: Optional[Path] = None,
) -> Tuple[int, str]:
    rs = Path(research_state_dir)
    if rs != RS_DIR:
        floor = task_floor_stamp(task_id)
        prereg = any(
            path.is_file() and bool(_STAMP_RE.findall(path.name))
            and max(_STAMP_RE.findall(path.name)) >= floor
            for path in rs.glob(PREREG_GLOB)
        ) if rs.is_dir() else False
        sealed = detect_seal(rs, task_id=task_id)["sealed"]
        return (0, "OK: temporary research_state seal detected") if prereg and sealed else (
            1,
            "FAIL: temporary research_state seal incomplete",
        )

    script = Path(script_path) if script_path else ROOT / "scripts" / "check_session_sealed.py"
    cmd = [
        sys.executable,
        str(script),
        "--task-id",
        task_id,
        "--glob",
        PREREG_GLOB,
        "--require-any-glob",
        COMBINED_GLOB,
        "--require-any-glob",
        BLOCKED_GLOB,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr)


def _run(cmd: Sequence[str], *, cwd: Path = ROOT) -> Tuple[int, str]:
    proc = subprocess.run(list(cmd), cwd=str(cwd), capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr)


def execute_phaseb(
    *,
    capture_dir: Path = CAPTURE_DIR,
    research_state_dir: Path = RS_DIR,
    task_id: str = TASK_ID,
) -> Dict[str, Any]:
    if not Path(capture_dir).is_dir():
        return {
            "ok": False,
            "step": "capture",
            "detail": f"capture dir not found: {capture_dir}",
        }

    steps: List[Dict[str, Any]] = []
    rc, out = _run([
        sys.executable,
        str(ROOT / "scripts" / "eval173_single_asset_skew_forward_variance.py"),
        "--capture-dir",
        str(capture_dir),
        "--seal",
        "--task-label",
        TASK_LABEL,
    ])
    steps.append({"step": "measure_and_seal", "rc": rc, "tail": out[-4000:]})
    if rc != 0:
        return {"ok": False, "step": "measure_and_seal", "steps": steps}

    gate_rc, gate_out = run_seal_gate_check(task_id=task_id, research_state_dir=research_state_dir)
    steps.append({"step": "seal_gate", "rc": gate_rc, "tail": gate_out[-4000:]})
    return {"ok": gate_rc == 0, "step": "seal_gate", "steps": steps, "seal_gate_rc": gate_rc}


def _readiness_evidence(research_state_dir: Path = RS_DIR) -> Dict[str, Any]:
    rs = Path(research_state_dir)
    prereg = sorted(rs.glob(PREREG_GLOB)) if rs.is_dir() else []
    return {
        "prereg_present": bool(prereg),
        "prereg_files": [path.name for path in prereg],
        "capture_dir_present": CAPTURE_DIR.is_dir(),
        "capture_files": sorted(path.name for path in CAPTURE_DIR.glob("three_way_*.json"))
        if CAPTURE_DIR.is_dir()
        else [],
        "task_id": TASK_ID,
        "runnable_now": True,
        "note": "EVAL-173 consumes the already-acquired real on-disk captures.",
    }


def _emit(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="EVAL-173 Phase-B gate")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--capture-dir", default=str(CAPTURE_DIR))
    parser.add_argument("--research-state-dir", default=str(RS_DIR))
    parser.add_argument("--task-id", default=TASK_ID)
    args = parser.parse_args(argv)

    rs = Path(args.research_state_dir)
    sealed = detect_seal(rs, task_id=args.task_id)
    evidence = _readiness_evidence(rs)

    if sealed["sealed"]:
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id, research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed["artifacts"],
            "seal_gate_tail": gate_out[-1500:],
            "note": "EVAL-173 complete; idempotent no-op.",
        })
        return EXIT_SEALED

    if not args.execute:
        _emit({
            "phase": "DUE",
            "exit_code": EXIT_DUE,
            "now": now_iso(),
            "readiness": evidence,
            "contract": "HEAVY WORK REQUIRED NOW. Re-run with --execute.",
        })
        return EXIT_DUE

    result = execute_phaseb(capture_dir=Path(args.capture_dir), research_state_dir=rs, task_id=args.task_id)
    if result.get("ok"):
        sealed_after = detect_seal(rs, task_id=args.task_id)
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id, research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed_after["artifacts"],
            "steps": result.get("steps"),
            "seal_gate_tail": gate_out[-1500:],
        })
        return EXIT_SEALED

    _emit({
        "phase": "FAILED",
        "exit_code": EXIT_FAILED,
        "failed_step": result.get("step"),
        "steps": result.get("steps"),
        "contract": "EVAL-173 did not produce a passing seal-gate.",
    })
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())