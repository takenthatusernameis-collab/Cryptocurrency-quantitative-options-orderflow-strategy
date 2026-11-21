#!/usr/bin/env python3
"""EVAL-176 Phase-B gate: deterministic, idempotent completion arbiter.

EVAL-176 measures the **cross-asset causal near-ATM implied-vol spillover**
(the OTHER underlying's ``atm_iv``) against the target underlying's forward
realized return variance on the real on-disk captures. The gate has three
outcomes: SEALED (0), DUE (20), and FAILED (1).

Unlike EVAL-67/68/69 there is no NOT_DUE phase: the EVAL-176 inputs are on
disk, so the honest pre-execution state is DUE (heavy work required), never a
physics wait.

``--execute`` is the unskippable path: it runs
``eval176_cross_asset_atm_iv_spillover_forward_variance.py --seal`` then the
authoritative seal-gate, and refuses to exit 0 unless the seal-gate exits 0.

Nothing here weakens the EVAL-64 floor, uses synthetic data, enables live
trading, or edits sealed EVAL-02..62/64..66/70..175 artifacts or src/ (EVAL-176
is appended here). It is append-only and reuses the sealed EVAL-61/62/65/71/148/
172 runners.
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

# Authoritative pre-registered identifiers (parseable by check_session_sealed.py).
TASK_ID = "INIT-2026-11-21T22:39:32Z-EVAL176-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-VARIANCE"
TASK_LABEL = "EVAL176-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-VARIANCE"
PREREG_GLOB = "EVAL_176_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_VARIANCE_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_176_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_VARIANCE_COMBINED_*"
BLOCKED_GLOB = "EVAL_176_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_VARIANCE_BLOCKED_*"

CAPTURE_DIR = ROOT / "data" / "raw" / "eval61"

# Exit codes (documented above).
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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-176 artifact exists with a
    stamp >= the pre-registered task id timestamp."""
    rs = Path(research_state_dir)
    floor = task_floor_stamp(task_id)
    hits: List[Dict[str, str]] = []
    if rs.is_dir():
        for pat in (combined_glob, blocked_glob):
            for path in sorted(rs.glob(pat)):
                if not path.is_file():
                    continue
                stamps = _STAMP_RE.findall(path.name)
                if not stamps:
                    continue
                top = max(stamps)
                if top >= floor:
                    hits.append(
                        {
                            "name": path.name,
                            "stamp": top,
                            "kind": "COMBINED" if combined_glob in pat else "BLOCKED",
                        }
                    )
    hits.sort(key=lambda h: h["stamp"])
    return {"sealed": bool(hits), "artifacts": hits, "floor_stamp": floor}


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
    proc = subprocess.run(list(cmd), cwd=str(cwd), capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr)


def execute_phaseb(
    *,
    capture_dir: Path = CAPTURE_DIR,
    research_state_dir: Path = RS_DIR,
    task_id: str = TASK_ID,
) -> Dict[str, Any]:
    """Run the EVAL-176 runner (--seal) -> authoritative seal-gate. Returns a
    structured result; the caller maps it to an exit code."""
    if not capture_dir.is_dir():
        return {
            "ok": False,
            "step": "capture",
            "detail": f"capture dir not found: {capture_dir} (EVAL-176 needs the "
            "already-acquired real on-disk three-way captures)",
        }

    steps: List[Dict[str, Any]] = []

    rc, out = _run([
        sys.executable,
        str(ROOT / "scripts" / "eval176_cross_asset_atm_iv_spillover_forward_variance.py"),
        "--capture-dir",
        str(capture_dir),
        "--seal",
        "--task-label",
        TASK_LABEL,
    ])
    steps.append({"step": "measure_and_seal", "status": "ok" if rc == 0 else "failed",
                  "rc": rc, "tail": out[-2500:]})
    if rc != 0:
        return {"ok": False, "step": "measure_and_seal", "steps": steps,
                "detail": "EVAL-176 measurement/seal failed"}

    gate_rc, gate_out = run_seal_gate_check(task_id=task_id,
                                            research_state_dir=research_state_dir)
    steps.append({"step": "seal_gate", "status": "ok" if gate_rc == 0 else "failed",
                  "rc": gate_rc, "tail": gate_out[-2500:]})
    return {"ok": bool(gate_rc == 0), "step": "seal_gate", "steps": steps,
            "seal_gate_rc": gate_rc}


def _readiness_evidence(research_state_dir: Path = RS_DIR) -> Dict[str, Any]:
    rs = Path(research_state_dir)
    prereg = sorted(rs.glob(PREREG_GLOB)) if rs.is_dir() else []
    return {
        "prereg_present": bool(prereg),
        "prereg_files": [p.name for p in prereg],
        "capture_dir_present": CAPTURE_DIR.is_dir(),
        "capture_files": sorted(p.name for p in CAPTURE_DIR.glob("three_way_*.json"))
        if CAPTURE_DIR.is_dir()
        else [],
        "task_id": TASK_ID,
        "runnable_now": True,
        "note": "EVAL-176 consumes the already-acquired real on-disk captures; "
                "it is runnable pre-threshold with no acquisition and no network.",
    }


def _emit(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-176 Phase-B gate: deterministic, idempotent "
                    "completion arbiter (SEALED / DUE / FAILED)."
    )
    ap.add_argument("--execute", action="store_true",
                    help="run measure->seal->seal-gate end-to-end and require "
                         "seal-gate exit 0 (unskippable path)")
    ap.add_argument("--capture-dir", default=str(CAPTURE_DIR))
    ap.add_argument("--research-state-dir", default=str(RS_DIR))
    ap.add_argument("--task-id", default=TASK_ID)
    args = ap.parse_args(argv)

    rs = Path(args.research_state_dir)
    sealed = detect_seal(rs, task_id=args.task_id)
    evidence = _readiness_evidence(rs)

    if sealed["sealed"]:
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id,
                                                research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed["artifacts"],
            "seal_gate_tail": gate_out[-1500:],
            "note": "EVAL-176 campaign complete; idempotent no-op. Do not re-run.",
        })
        return EXIT_SEALED

    if not args.execute:
        _emit({
            "phase": "DUE",
            "exit_code": EXIT_DUE,
            "now": now_iso(),
            "readiness": evidence,
            "contract": "HEAVY WORK REQUIRED NOW (data is on disk). Re-run with "
                        "--execute to run measure->seal->seal-gate and require "
                        "seal-gate exit 0.",
        })
        return EXIT_DUE

    result = execute_phaseb(capture_dir=Path(args.capture_dir),
                            research_state_dir=rs, task_id=args.task_id)
    if result.get("ok"):
        sealed2 = detect_seal(rs, task_id=args.task_id)
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id,
                                                research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed2["artifacts"],
            "steps": result.get("steps"),
            "seal_gate_tail": gate_out[-1500:],
            "note": "EVAL-176 executed and sealed; seal-gate exit 0.",
        })
        return EXIT_SEALED

    _emit({
        "phase": "FAILED",
        "exit_code": EXIT_FAILED,
        "failed_step": result.get("step"),
        "detail": result.get("detail"),
        "steps": result.get("steps"),
        "contract": "EVAL-176 did not produce a passing seal-gate. Fix "
                    "the failed step and re-run with --execute.",
    })
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())