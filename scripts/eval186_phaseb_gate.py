#!/usr/bin/env python3
"""Deterministic anti-avoidance gate for EVAL-186 TRACK A replication.

The gate is intentionally runnable before the fresh capture exists. It reports
WAIT_CAPTURE until `data/raw/eval185cap` contains both real three-way captures,
then checks the replication runner and requires `--execute` to seal an EVAL-186
artifact plus a passing session seal-gate. The acquisition window must start at or
after the EVAL-84/185 capture end; the recommended 3.7-day acquisition ends at
2026-11-26T00:00:00Z and starts at 2026-11-22T07:12:00Z.
"""

from __future__ import annotations

import argparse
import json
import os
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
TASK_ID = "INIT-2026-11-22T09:51:17Z-EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION"
TASK_LABEL = "EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION"
PREREG_GLOB = "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_COMBINED_*"
BLOCKED_GLOB = "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_BLOCKED_*"
RUNNER_REL = "scripts/eval186_track_a_fresh_window_replication.py"
CAPTURE_DIR = ROOT / "data" / "raw" / "eval185cap"
PREVIOUS_CAPTURE_DIR = ROOT / "data" / "raw" / "eval84cap"
UNDERLYINGS: Tuple[str, ...] = ("BTC", "ETH")
ACQUIRE_DAYS = 3.7
PREVIOUS_WINDOW_START = "2026-11-18T13:58:43Z"
PREVIOUS_WINDOW_END = "2026-11-22T06:46:43Z"
EARLIEST_FORWARD_CAPTURE_END = "2026-11-25T23:34:43Z"
RECOMMENDED_CAPTURE_END = "2026-11-26T00:00:00Z"
RECOMMENDED_CAPTURE_START = "2026-11-22T07:12:00Z"
SEALED_WINDOW_START = "2026-11-09T06:48:16Z"
SEALED_WINDOW_END = "2026-11-16T06:48:16Z"

EXIT_SEALED = 0
EXIT_FAILED = 1
EXIT_WAIT_CAPTURE = 10
EXIT_WAIT_RUNNER = 20
EXIT_DUE = 30

_ISO_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)")
_STAMP_RE = re.compile(r"(\d{8}T\d{6}(?:\d+)?Z)")


def _to_stamp(iso_ts: str) -> str:
    text = iso_ts.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def task_floor_stamp(task_id: str = TASK_ID) -> str:
    match = _ISO_RE.search(task_id)
    if not match:
        raise ValueError(f"task id has no ISO-8601 UTC timestamp: {task_id!r}")
    return _to_stamp(match.group(1))


def detect_seal(
    research_state_dir: Path = RS_DIR,
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
    return {"sealed": bool(hits), "artifacts": hits, "floor_stamp": floor}


def capture_inventory(capture_dir: Path = CAPTURE_DIR) -> Dict[str, Any]:
    directory = Path(capture_dir)
    btc = sorted(p.name for p in directory.glob("three_way_BTC_*.json")) if directory.is_dir() else []
    eth = sorted(p.name for p in directory.glob("three_way_ETH_*.json")) if directory.is_dir() else []
    return {
        "dir": str(directory),
        "btc": btc,
        "eth": eth,
        "present": bool(btc and eth),
    }


def _child_env() -> Dict[str, str]:
    env = dict(os.environ)
    deps = str(ROOT / ".venv-deps")
    env["PYTHONPATH"] = deps + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def runner_present_and_green(
    *, capture_dir: Path = CAPTURE_DIR, runner_rel: str = RUNNER_REL
) -> Dict[str, Any]:
    runner = ROOT / runner_rel
    if not runner.is_file():
        return {
            "runner_present": False,
            "runner_green": False,
            "runner": str(runner),
            "reason": "runner_missing",
        }
    cmd = [sys.executable, str(runner), "--capture-dir", str(capture_dir), "--no-write"]
    try:
        proc = subprocess.run(
            cmd, cwd=str(ROOT), capture_output=True, text=True, env=_child_env()
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "runner_present": True,
            "runner_green": False,
            "runner": str(runner),
            "reason": f"runner_error:{exc}",
        }
    return {
        "runner_present": True,
        "runner_green": bool(proc.returncode == 0),
        "runner": str(runner),
        "returncode": proc.returncode,
        "tail": (proc.stdout + proc.stderr)[-4000:],
    }


def decide_phase(*, sealed: bool, capture_present: bool, runner_green: bool) -> str:
    if sealed:
        return "SEALED"
    if not capture_present:
        return "WAIT_CAPTURE"
    if not runner_green:
        return "WAIT_RUNNER"
    return "DUE"


def acquisition_command(capture_dir: Path = CAPTURE_DIR) -> List[str]:
    return [
        "python3",
        "scripts/eval60_acquire_three_way.py",
        "--underlying",
        "BTC",
        "--underlying",
        "ETH",
        "--days",
        str(ACQUIRE_DAYS),
        "--end",
        RECOMMENDED_CAPTURE_END,
        "--max-per-expiry",
        "30",
        "--out-dir",
        str(capture_dir),
        "--seal",
    ]


def _readiness_evidence(
    research_state_dir: Path = RS_DIR, *, capture_dir: Path = CAPTURE_DIR
) -> Dict[str, Any]:
    prereg = sorted(Path(research_state_dir).glob(PREREG_GLOB))
    inv = capture_inventory(capture_dir)
    return {
        "task_id": TASK_ID,
        "prereg_present": bool(prereg),
        "prereg_files": [p.name for p in prereg],
        "capture_dir": str(capture_dir),
        "capture_present": inv["present"],
        "capture_btc": inv["btc"],
        "capture_eth": inv["eth"],
        "underlyings": list(UNDERLYINGS),
        "previous_capture_dir": str(PREVIOUS_CAPTURE_DIR),
        "previous_window": [PREVIOUS_WINDOW_START, PREVIOUS_WINDOW_END],
        "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
        "acquire_days": float(ACQUIRE_DAYS),
        "earliest_forward_capture_end": EARLIEST_FORWARD_CAPTURE_END,
        "recommended_capture_window": [RECOMMENDED_CAPTURE_START, RECOMMENDED_CAPTURE_END],
        "acquisition_command": acquisition_command(capture_dir),
        "runner": RUNNER_REL,
    }


def _run(cmd: Sequence[str]) -> Tuple[int, str]:
    proc = subprocess.run(
        list(cmd), cwd=str(ROOT), capture_output=True, text=True, env=_child_env()
    )
    return proc.returncode, proc.stdout + proc.stderr


def run_seal_gate_check(
    *, task_id: str = TASK_ID, research_state_dir: Path = RS_DIR
) -> Tuple[int, str]:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "check_session_sealed.py"),
        "--task-id",
        task_id,
        "--glob",
        PREREG_GLOB,
        "--require-any-glob",
        COMBINED_GLOB,
        "--require-any-glob",
        BLOCKED_GLOB,
    ]
    if Path(research_state_dir) != RS_DIR:
        env = _child_env()
        env["EVAL186_RESEARCH_STATE_DIR"] = str(research_state_dir)
        proc = subprocess.run(
            cmd, cwd=str(ROOT), capture_output=True, text=True, env=env
        )
        return proc.returncode, proc.stdout + proc.stderr
    return _run(cmd)


def execute_phaseb(
    *,
    capture_dir: Path = CAPTURE_DIR,
    research_state_dir: Path = RS_DIR,
    task_id: str = TASK_ID,
    runner_rel: str = RUNNER_REL,
) -> Dict[str, Any]:
    inv = capture_inventory(capture_dir)
    if not inv["present"]:
        return {
            "ok": False,
            "step": "capture",
            "reason": "missing_capture",
            "detail": "both real BTC and ETH three-way captures are required",
        }

    steps: List[Dict[str, Any]] = [
        {"step": "capture", "status": "ok", "files": inv["btc"] + inv["eth"]}
    ]
    green = runner_present_and_green(capture_dir=capture_dir, runner_rel=runner_rel)
    steps.append(
        {
            "step": "runner_green",
            "status": "ok" if green.get("runner_green") else "failed",
            "runner_present": green.get("runner_present"),
            "returncode": green.get("returncode"),
            "tail": green.get("tail"),
        }
    )
    if not green.get("runner_green"):
        return {
            "ok": False,
            "step": "runner_green",
            "steps": steps,
            "detail": "EVAL-186 runner dry-run failed",
        }

    rc, out = _run(
        [
            sys.executable,
            str(ROOT / runner_rel),
            "--capture-dir",
            str(capture_dir),
            "--seal",
            "--task-label",
            TASK_LABEL,
        ]
    )
    steps.append({"step": "seal", "status": "ok" if rc == 0 else "failed", "rc": rc, "tail": out[-4000:]})
    if rc != 0:
        return {"ok": False, "step": "seal", "steps": steps, "detail": "seal failed"}

    gate_rc, gate_out = run_seal_gate_check(
        task_id=task_id, research_state_dir=research_state_dir
    )
    steps.append(
        {
            "step": "seal_gate",
            "status": "ok" if gate_rc == 0 else "failed",
            "rc": gate_rc,
            "tail": gate_out[-4000:],
        }
    )
    return {"ok": bool(gate_rc == 0), "step": "seal_gate", "steps": steps}


def _emit(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="EVAL-186 TRACK A fresh-window replication arbiter"
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--capture-dir", default=str(CAPTURE_DIR))
    parser.add_argument("--research-state-dir", default=str(RS_DIR))
    parser.add_argument("--task-id", default=TASK_ID)
    parser.add_argument("--runner", default=RUNNER_REL)
    args = parser.parse_args(argv)

    capture_dir = Path(args.capture_dir)
    research_state_dir = Path(args.research_state_dir)
    sealed = detect_seal(research_state_dir, task_id=args.task_id)
    if sealed["sealed"]:
        gate_rc, gate_out = run_seal_gate_check(
            task_id=args.task_id, research_state_dir=research_state_dir
        )
        _emit(
            {
                "phase": "SEALED" if gate_rc == 0 else "FAILED",
                "exit_code": EXIT_SEALED if gate_rc == 0 else EXIT_FAILED,
                "seal_gate_rc": gate_rc,
                "artifacts": sealed["artifacts"],
                "seal_gate_tail": gate_out[-4000:],
                "note": "EVAL-186 already sealed; idempotent no-op",
            }
        )
        return EXIT_SEALED if gate_rc == 0 else EXIT_FAILED

    inv = capture_inventory(capture_dir)
    green = runner_present_and_green(capture_dir=capture_dir, runner_rel=args.runner)
    phase = decide_phase(
        sealed=False,
        capture_present=inv["present"],
        runner_green=bool(green.get("runner_green")),
    )
    evidence = _readiness_evidence(research_state_dir, capture_dir=capture_dir)
    evidence["runner_check"] = green

    if phase == "WAIT_CAPTURE":
        _emit(
            {
                "phase": phase,
                "exit_code": EXIT_WAIT_CAPTURE,
                "readiness": evidence,
                "contract": (
                    "HEAVY WORK REQUIRED: acquire a strictly forward 3.7-day real "
                    "BTC+ETH capture. The acquisition must end at or after "
                    f"{EARLIEST_FORWARD_CAPTURE_END}; use {RECOMMENDED_CAPTURE_END} "
                    "for margin. Do not substitute the EVAL-84/185 capture."
                ),
            }
        )
        return EXIT_WAIT_CAPTURE

    if phase == "WAIT_RUNNER":
        _emit(
            {
                "phase": phase,
                "exit_code": EXIT_WAIT_RUNNER,
                "readiness": evidence,
                "contract": "Build or fix the EVAL-186 runner and make --no-write green",
            }
        )
        return EXIT_WAIT_RUNNER

    if not args.execute:
        _emit(
            {
                "phase": "DUE",
                "exit_code": EXIT_DUE,
                "readiness": evidence,
                "contract": "Re-run with --execute to seal EVAL-186 and pass the seal-gate",
            }
        )
        return EXIT_DUE

    result = execute_phaseb(
        capture_dir=capture_dir,
        research_state_dir=research_state_dir,
        task_id=args.task_id,
        runner_rel=args.runner,
    )
    if result.get("ok"):
        sealed2 = detect_seal(research_state_dir, task_id=args.task_id)
        gate_rc, gate_out = run_seal_gate_check(
            task_id=args.task_id, research_state_dir=research_state_dir
        )
        _emit(
            {
                "phase": "SEALED",
                "exit_code": EXIT_SEALED,
                "seal_gate_rc": gate_rc,
                "artifacts": sealed2["artifacts"],
                "steps": result.get("steps"),
                "seal_gate_tail": gate_out[-4000:],
            }
        )
        return EXIT_SEALED

    _emit(
        {
            "phase": "FAILED",
            "exit_code": EXIT_FAILED,
            "failed_step": result.get("step"),
            "detail": result.get("detail") or result.get("reason"),
            "steps": result.get("steps"),
            "contract": "Fix the failed step and re-run with --execute",
        }
    )
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())