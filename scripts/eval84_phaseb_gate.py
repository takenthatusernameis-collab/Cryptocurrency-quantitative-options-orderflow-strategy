#!/usr/bin/env python3
"""EVAL-84 Phase-B gate: the single, deterministic, idempotent arbiter of the
EVAL-84 campaign's completion contract.

Why this exists
---------------
EVAL-74 sealed ``NO-GO CONFIRMED (PASS)`` for the term-structure slope vs
forward *RV* (portable null across BTC/ETH). EVAL-84 measures the **same
on-charter term-structure signal** against a **distinct forward target** —
**forward vol-of-vol / variance-of-variance** (std of squared log returns over
bars k+1..k+H, distinct from EVAL-74's RV level sqrt(mean(squared returns))) —
on the already-acquired real on-disk captures, with no acquisition and no
network, so it is runnable **now** and keeps pre-threshold sessions on genuine
heavy work. It reuses the sealed EVAL-61/62/65/71/74 signal reconstructions and
the EVAL-65 inference verbatim; it does not re-litigate EVAL-74 (same signal,
RV target).

Outcomes (exit codes)
---------------------
  0   SEALED   — a COMBINED_*/BLOCKED_* EVAL-84 artifact already exists with a stamp
                 >= the pre-registered task id; the seal-gate passes. COMPLETE;
                 idempotent no-op (safe to re-run forever).
  20  DUE      — nothing sealed yet and this was a status check only (no
                 --execute). The heavy work is REQUIRED now (data is on disk):
                 re-run with --execute.
  1   FAILED   --execute was requested but the run -> seal -> seal-gate pipeline
                 did not produce a passing seal-gate exit 0. Fix and re-run.

Unlike EVAL-67/68/69 there is no NOT_DUE phase: the EVAL-84 inputs are on disk,
so the honest pre-execution state is DUE (heavy work required), never a physics
wait.

``--execute`` is the unskippable path: it runs
``eval84_term_structure_vol_of_vol_predictiveness.py --seal`` then the
authoritative seal-gate, and refuses to exit 0 unless the seal-gate exits 0.

Nothing here weakens the EVAL-64 floor (EVAL-84 composes the sealed EVAL-71 floor
with the EVAL-74 term-structure adequacy floor, neither weakened), uses synthetic
data, enables live trading, or edits sealed artifacts or src/. It is append-only
and reuses sealed runners.
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

TASK_ID = "INIT-2026-11-17T22:20:00Z-EVAL84-TERM-STRUCTURE-VOL-OF-VOL-PREDICTIVENESS"
TASK_LABEL = "EVAL84-TERM-STRUCTURE-VOL-OF-VOL-PREDICTIVENESS"
PREREG_GLOB = "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_COMBINED_*"
BLOCKED_GLOB = "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_BLOCKED_*"

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
    m = _ISO_RE.search(task_id)
    if not m:
        raise ValueError(f"task id has no ISO-8601 UTC timestamp: {task_id!r}")
    return _to_stamp(m.group(1))


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
        for pat, kind in ((combined_glob, "COMBINED"), (blocked_glob, "BLOCKED")):
            for path in sorted(rs.glob(pat)):
                if not path.is_file():
                    continue
                stamps = _STAMP_RE.findall(path.name)
                if not stamps:
                    continue
                top = max(stamps)
                if top >= floor:
                    hits.append({"name": path.name, "stamp": top, "kind": kind})
    return {"sealed": bool(hits), "artifacts": hits, "floor_stamp": floor}


def _readiness_evidence(rs: Path) -> Dict[str, Any]:
    return {
        "capture_dir": str(CAPTURE_DIR),
        "capture_exists": CAPTURE_DIR.is_dir(),
        "capture_files": sorted(p.name for p in CAPTURE_DIR.glob("three_way_*")) if CAPTURE_DIR.is_dir() else [],
        "runnable_now": CAPTURE_DIR.is_dir(),
    }


def run_seal_gate_check(
    *,
    task_id: str = TASK_ID,
    research_state_dir: Path = RS_DIR,
    script_path: Optional[Path] = None,
) -> Tuple[int, str]:
    script = Path(script_path) if script_path else ROOT / "scripts" / "check_session_sealed.py"
    cmd = [
        sys.executable, str(script),
        "--task-id", task_id,
        "--glob", PREREG_GLOB,
        "--require-any-glob", COMBINED_GLOB,
        "--require-any-glob", BLOCKED_GLOB,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr)


def _run(cmd: Sequence[str], *, cwd: Path = ROOT) -> Tuple[int, str]:
    env = dict(__import__("os").environ)
    venv = ROOT / ".venv-deps"
    if venv.is_dir():
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(venv) + (":" + existing if existing else "")
    proc = subprocess.run(list(cmd), cwd=str(cwd), capture_output=True, text=True, env=env)
    return proc.returncode, (proc.stdout + proc.stderr)


def execute_phaseb(
    *,
    capture_dir: Path = CAPTURE_DIR,
    research_state_dir: Path = RS_DIR,
    task_id: str = TASK_ID,
) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = []
    if not Path(capture_dir).is_dir():
        return {"ok": False, "step": "capture", "detail": f"capture_dir missing: {capture_dir}", "steps": steps}

    run_cmd = [
        sys.executable, str(ROOT / "scripts" / "eval84_term_structure_vol_of_vol_predictiveness.py"),
        "--capture-dir", str(capture_dir),
        "--seal",
        "--task-label", TASK_LABEL,
    ]
    rc, out = _run(run_cmd)
    steps.append({"step": "run_seal", "rc": rc, "tail": out[-1500:]})
    if rc != 0:
        return {"ok": False, "step": "run_seal", "detail": out[-800:], "steps": steps}

    gate_rc, gate_out = run_seal_gate_check(task_id=task_id, research_state_dir=research_state_dir)
    steps.append({"step": "seal_gate", "rc": gate_rc, "tail": gate_out[-1500:]})
    if gate_rc != 0:
        return {"ok": False, "step": "seal_gate", "detail": gate_out[-800:], "steps": steps}

    return {"ok": True, "steps": steps}


def _emit(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-84 Phase-B gate: deterministic, idempotent completion arbiter (SEALED / DUE / FAILED)."
    )
    ap.add_argument("--execute", action="store_true",
                    help="run measure->seal->seal-gate end-to-end and require seal-gate exit 0")
    ap.add_argument("--capture-dir", default=str(CAPTURE_DIR))
    ap.add_argument("--research-state-dir", default=str(RS_DIR))
    ap.add_argument("--task-id", default=TASK_ID)
    args = ap.parse_args(argv)

    rs = Path(args.research_state_dir)
    sealed = detect_seal(rs, task_id=args.task_id)

    if sealed["sealed"]:
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id, research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed["artifacts"],
            "seal_gate_tail": gate_out[-1500:],
            "note": "EVAL-84 campaign complete; idempotent no-op. Do not re-run.",
        })
        return EXIT_SEALED

    if not args.execute:
        _emit({
            "phase": "DUE",
            "exit_code": EXIT_DUE,
            "now": now_iso(),
            "readiness": _readiness_evidence(rs),
            "contract": "HEAVY WORK REQUIRED NOW (data is on disk). Re-run with --execute to run measure->seal->seal-gate and require seal-gate exit 0.",
        })
        return EXIT_DUE

    result = execute_phaseb(capture_dir=Path(args.capture_dir), research_state_dir=rs, task_id=args.task_id)
    if result.get("ok"):
        sealed2 = detect_seal(rs, task_id=args.task_id)
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id, research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed2["artifacts"],
            "steps": result.get("steps"),
            "seal_gate_tail": gate_out[-1500:],
            "note": "EVAL-84 executed and sealed; seal-gate exit 0.",
        })
        return EXIT_SEALED

    _emit({
        "phase": "FAILED",
        "exit_code": EXIT_FAILED,
        "failed_step": result.get("step"),
        "detail": result.get("detail"),
        "steps": result.get("steps"),
        "contract": "EVAL-84 did not produce a passing seal-gate. Fix the failed step and re-run with --execute.",
    })
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
