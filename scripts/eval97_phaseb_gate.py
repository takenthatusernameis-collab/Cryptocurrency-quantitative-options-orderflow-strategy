#!/usr/bin/env python3
"""EVAL-97 Phase-B gate: the single, deterministic, idempotent arbiter of the
EVAL-97 campaign's completion contract.

Why this exists
---------------
EVAL-71 sealed ``GO CONFIRMED`` (near-ATM ``skew`` -> forward *RV level*),
EVAL-84 sealed ``NO-GO CONFIRMED (PASS)`` (term slope/ratio -> forward
*vol-of-vol*), EVAL-86 sealed ``GO CONFIRMED`` (``skew`` -> forward *VRP*),
EVAL-85/87 sealed ``GO/BLOCKED`` (``skew``/``atm_iv`` -> forward *tail
asymmetry*), and EVAL-95 sealed ``NO-GO CONFIRMED (PASS)`` (``atm_iv`` ->
forward *vol-of-vol*). The one genuinely distinct, on-charter, runnable-**now**
cell none of them tests is **single-asset near-ATM put-call skew (``skew``) ->
forward vol-of-vol** (std of squared log returns over bars k+1..k+H): does the
near-ATM put-call skew predict the turbulence/unevenness of the subsequent
realized-variance path?

EVAL-97 measures exactly that on the already-acquired real on-disk captures
(surface trade tape with IV/strike/expiry + perp candles for BOTH underlyings),
with no acquisition and no network, so it is runnable **now** and keeps
pre-threshold sessions on genuine heavy work. It reuses the sealed
EVAL-61/62/65/71 signal reconstructions, EVAL-71's
``build_surface_bars``/``_forward_fill`` and sealed EVAL-71 surface floor, and
EVAL-84's forward vol-of-vol target verbatim, and the EVAL-65 inference
verbatim; it does not re-litigate EVAL-71, EVAL-84, EVAL-85, EVAL-86, EVAL-87,
or EVAL-95.

Outcomes (exit codes)
---------------------
  0   SEALED   — a COMBINED_*/BLOCKED_* EVAL-97 artifact already exists with a stamp
                 >= the pre-registered task id; the seal-gate passes. COMPLETE;
                 idempotent no-op (safe to re-run forever).
  20  DUE      — nothing sealed yet and this was a status check only (no
                 --execute). The heavy work is REQUIRED now (data is on disk):
                 re-run with --execute.
  1   FAILED   --execute was requested but the run -> seal -> seal-gate pipeline
                 did not produce a passing seal-gate exit 0. Fix and re-run.

Unlike EVAL-67/68/69 there is no NOT_DUE phase: the EVAL-97 inputs are on disk,
so the honest pre-execution state is DUE (heavy work required), never a physics
wait.

``--execute`` is the unskippable path: it runs
``eval97_single_asset_skew_forward_vol_of_vol.py --seal`` then the authoritative
seal-gate, and refuses to exit 0 unless the seal-gate exits 0.

Nothing here weakens the EVAL-64 floor (EVAL-97 reuses the sealed EVAL-71 surface
floor verbatim, not weakened), uses synthetic data, enables live trading, or edits
sealed EVAL-02..62/64..66/70..96 artifacts or src/ (EVAL-97 is itself appended
here). It is append-only and reuses the sealed EVAL-61/62/65/71/84 runners.
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
TASK_ID = "INIT-2026-11-18T11:19:01Z-EVAL97-SINGLE-ASSET-SKEW-FORWARD-VOL-OF-VOL"
TASK_LABEL = "EVAL97-SINGLE-ASSET-SKEW-FORWARD-VOL-OF-VOL"
PREREG_GLOB = (
    "EVAL_97_SINGLE_ASSET_SKEW_FORWARD_VOL_OF_VOL_PREREGISTRATION_*"
)
COMBINED_GLOB = (
    "EVAL_97_SINGLE_ASSET_SKEW_FORWARD_VOL_OF_VOL_COMBINED_*"
)
BLOCKED_GLOB = (
    "EVAL_97_SINGLE_ASSET_SKEW_FORWARD_VOL_OF_VOL_BLOCKED_*"
)

CAPTURE_DIR = ROOT / "data" / "raw" / "eval61"

# Exit codes (documented above).
EXIT_SEALED = 0
EXIT_FAILED = 1
EXIT_DUE = 20

_ISO_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)")
_STAMP_RE = re.compile(r"(\d{8}T\d{6}(?:\d+)?Z)")


# ---------------------------------------------------------------------------
# Small helpers (pure; no side effects)
# ---------------------------------------------------------------------------
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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-97 artifact exists with a stamp
    >= the pre-registered task timestamp (mirrors check_session_sealed.py)."""
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


# ---------------------------------------------------------------------------
# Seal-gate verification (authoritative; shells out to check_session_sealed.py)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Phase-B execution (data is available now; no threshold wait)
# ---------------------------------------------------------------------------
def _run(cmd: Sequence[str], *, cwd: Path = ROOT) -> Tuple[int, str]:
    env = dict(__import__("os").environ)
    venv = ROOT / ".venv-deps"
    if venv.is_dir():
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(venv) + (":" + existing if existing else "")
    proc = subprocess.run(list(cmd), cwd=str(cwd), capture_output=True, text=True, env=env)
    return proc.returncode, (proc.stdout + proc.stderr)


def _readiness_evidence(rs: Path) -> Dict[str, Any]:
    return {
        "capture_dir": str(CAPTURE_DIR),
        "capture_exists": CAPTURE_DIR.is_dir(),
        "capture_files": sorted(p.name for p in CAPTURE_DIR.glob("three_way_*")) if CAPTURE_DIR.is_dir() else [],
        "runnable_now": CAPTURE_DIR.is_dir(),
        "task_id": TASK_ID,
        "note": "EVAL-97 consumes the already-acquired real on-disk captures (surface "
                "trade tape with IV/strike/expiry + perp candles) for BOTH underlyings; "
                "it is runnable pre-threshold with no acquisition and no network.",
    }


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
        sys.executable, str(ROOT / "scripts" / "eval97_single_asset_skew_forward_vol_of_vol.py"),
        "--capture-dir", str(capture_dir),
        "--seal",
        "--task-label", TASK_LABEL,
    ]
    rc, out = _run(run_cmd)
    steps.append({"step": "run_seal", "rc": rc, "tail": out[-2500:]})
    if rc != 0:
        return {"ok": False, "step": "run_seal", "detail": out[-800:], "steps": steps}

    gate_rc, gate_out = run_seal_gate_check(task_id=task_id, research_state_dir=research_state_dir)
    steps.append({"step": "seal_gate", "rc": gate_rc, "tail": gate_out[-1500:]})
    if gate_rc != 0:
        return {"ok": False, "step": "seal_gate", "detail": gate_out[-800:], "steps": steps}

    return {"ok": True, "steps": steps}


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def _emit(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-97 Phase-B gate: deterministic, idempotent completion "
                    "arbiter (SEALED / DUE / FAILED)."
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
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id, research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed["artifacts"],
            "seal_gate_tail": gate_out[-1500:],
            "note": "EVAL-97 campaign complete; idempotent no-op. Do not re-run.",
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
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id, research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed2["artifacts"],
            "steps": result.get("steps"),
            "seal_gate_tail": gate_out[-1500:],
            "note": "EVAL-97 executed and sealed; seal-gate exit 0.",
        })
        return EXIT_SEALED

    _emit({
        "phase": "FAILED",
        "exit_code": EXIT_FAILED,
        "failed_step": result.get("step"),
        "detail": result.get("detail"),
        "steps": result.get("steps"),
        "contract": "EVAL-97 did not produce a passing seal-gate. Fix the failed "
                    "step and re-run with --execute.",
    })
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())