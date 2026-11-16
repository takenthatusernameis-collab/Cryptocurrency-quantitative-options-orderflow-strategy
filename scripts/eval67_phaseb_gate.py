#!/usr/bin/env python3
"""EVAL-67 Phase-B gate: the single, deterministic, idempotent arbiter of the
EVAL-67 campaign's completion contract.

Why this exists
---------------
The EVAL-67 campaign (isolated, disjoint, out-of-sample BTC replication of the
only suggestive EVAL-65 options order-flow toxicity -> realized-vol slice) has a
hard, physics-imposed schedule: the free Deribit perp 1m endpoint serves at most
300000 s, the sealed EVAL-64/65 BTC window ends 2026-11-16T06:48:16Z, so the
earliest floor-compliant, disjoint capture ends 2026-11-19T18:08:16Z (prereg
margin 2026-11-20T00:00:00Z). Before then no acquisition is possible; a naive
capture overlaps the sealed window and must seal BLOCKED.

That schedule used to be enforced only by prose in a handoff, and sessions
responded by repeatedly bumping the handoff timestamp instead of doing the
heavy work. This gate removes that ambiguity: it converts the completion
contract into ONE deterministic command with three honest outcomes.

Outcomes (exit codes)
---------------------
  0   SEALED   — a COMBINED_* or BLOCKED_* EVAL-67 artifact already exists with a
                 stamp >= the pre-registered task id; the seal-gate passes. The
                 campaign is COMPLETE. Idempotent no-op (safe to re-run forever).
  10  NOT_DUE  — now < threshold and nothing sealed yet. Correct, honest carry:
                 prints the verified readiness evidence + disjointness math and
                 tells the session to durably carry (git handoff + external cron).
                 NEVER a completion; NEVER a timestamp-only "done".
  20  DUE      — now >= threshold and nothing sealed yet, but this invocation was
                 a status check only (no --execute). The heavy Phase-B work is
                 REQUIRED; re-run with --execute.
  1   FAILED   — now >= threshold and --execute was requested, but the
                 acquire -> dry-run -> seal -> seal-gate pipeline did not produce
                 a passing seal-gate exit 0. Fix the reported step and re-run.

`--execute` is the unskippable path
-----------------------------------
At/after the threshold, `--execute` performs the real heavy work end-to-end:
acquire a disjoint forward BTC three-way capture (real, paper-only, public
read-only) -> dry-run the EVAL-67 statistic -> seal prereg + COMBINED/BLOCKED ->
run the seal-gate. It refuses to exit 0 unless the seal-gate exits 0. Before the
threshold it refuses to acquire (would seal BLOCKED) and returns NOT_DUE.

Nothing here weakens the EVAL-64 floor, uses synthetic data, enables live
trading, or edits sealed EVAL-02..62/64..66 artifacts or src/. It is append-only
and reuses the sealed EVAL-60/65/67 runners verbatim.
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
TASK_ID = "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION"
TASK_LABEL = "EVAL67-BTC-OFLOW-TOX-RV-OOS"
PREREG_GLOB = "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*"
BLOCKED_GLOB = "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"

# Pre-registered disjointness threshold (prereg margin) and the physics behind it.
THRESHOLD_ISO = "2026-11-20T00:00:00Z"
SEALED_BTC_WINDOW_START = "2026-11-09T06:48:16Z"
SEALED_BTC_WINDOW_END = "2026-11-16T06:48:16Z"
EARLIEST_DISJOINT_CAPTURE_END = "2026-11-19T18:08:16Z"
CAPTURE_SPAN_SECONDS = 300000.0
ACQUIRE_DAYS = 3.7

CAPTURE_DIR = ROOT / "data" / "raw" / "eval67"

# Exit codes (documented above).
EXIT_SEALED = 0
EXIT_FAILED = 1
EXIT_NOT_DUE = 10
EXIT_DUE = 20

_ISO_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)")
_STAMP_RE = re.compile(r"(\d{8}T\d{6}(?:\d+)?Z)")


# ---------------------------------------------------------------------------
# Small helpers (pure; no side effects)
# ---------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def threshold_epoch() -> float:
    return parse_iso(THRESHOLD_ISO).timestamp()


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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-67 artifact exists with a stamp
    >= the pre-registered task timestamp (mirrors check_session_sealed.py)."""
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
                    hits.append({"name": path.name, "stamp": top, "kind":
                                 "COMBINED" if combined_glob in pat else "BLOCKED"})
    return {"sealed": bool(hits), "artifacts": hits, "floor_stamp": floor}


def decide_phase(now: datetime, threshold: datetime, sealed: bool) -> str:
    if sealed:
        return "SEALED"
    if now < threshold:
        return "NOT_DUE"
    return "DUE"


def disjointness_math(now: datetime) -> Dict[str, Any]:
    """Compute the capture window [--days, now] and its disjointness from the
    sealed BTC window, mirroring eval67_btc_oflow_tox_rv_oos.check_disjointness."""
    span = ACQUIRE_DAYS * 86400.0
    start = now.timestamp() - span
    sealed_start = parse_iso(SEALED_BTC_WINDOW_START).timestamp()
    sealed_end = parse_iso(SEALED_BTC_WINDOW_END).timestamp()
    overlap = max(0.0, min(now.timestamp(), sealed_end) - max(start, sealed_start))
    return {
        "now": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "acquire_days": ACQUIRE_DAYS,
        "window_start": datetime.fromtimestamp(start, tz=timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_end": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "span_seconds": round(now.timestamp() - start, 3),
        "meets_min_span": bool((now.timestamp() - start) >= CAPTURE_SPAN_SECONDS),
        "sealed_window": [SEALED_BTC_WINDOW_START, SEALED_BTC_WINDOW_END],
        "overlap_seconds": round(overlap, 3),
        "disjoint": bool(overlap <= 0.0),
        "earliest_disjoint_capture_end": EARLIEST_DISJOINT_CAPTURE_END,
    }


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
# Phase-B execution (only valid at/after threshold)
# ---------------------------------------------------------------------------
def _run(cmd: Sequence[str], *, cwd: Path = ROOT) -> Tuple[int, str]:
    proc = subprocess.run(list(cmd), cwd=str(cwd), capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr)


def execute_phaseb(
    *,
    capture_dir: Path = CAPTURE_DIR,
    research_state_dir: Path = RS_DIR,
    task_id: str = TASK_ID,
) -> Dict[str, Any]:
    """Run acquire -> dry-run -> seal -> seal-gate. Returns a structured result;
    the caller maps it to an exit code. Refuses to run before the threshold."""
    now = datetime.now(timezone.utc)
    if now.timestamp() < threshold_epoch():
        return {
            "ok": False,
            "step": "threshold",
            "reason": "before_threshold",
            "detail": "refusing to acquire before the disjointness threshold "
                      f"{THRESHOLD_ISO} (a naive capture would overlap the sealed "
                      "BTC window and must seal BLOCKED)",
            "disjointness": disjointness_math(now),
        }

    steps: List[Dict[str, Any]] = []

    # 1) Acquire a disjoint forward BTC capture (skip if a real capture already exists).
    existing = sorted(capture_dir.glob("three_way_BTC_*.json")) if capture_dir.is_dir() else []
    if existing:
        steps.append({"step": "acquire", "status": "skipped",
                      "reason": "capture_exists", "files": [p.name for p in existing]})
    else:
        capture_dir.mkdir(parents=True, exist_ok=True)
        rc, out = _run([
            sys.executable, str(ROOT / "scripts" / "eval60_acquire_three_way.py"),
            "--underlying", "BTC",
            "--days", str(ACQUIRE_DAYS),
            "--end", now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "--out-dir", str(capture_dir),
            "--seal",
        ])
        steps.append({"step": "acquire", "status": "ok" if rc == 0 else "failed",
                      "rc": rc, "tail": out[-2000:]})
        if rc != 0:
            return {"ok": False, "step": "acquire", "steps": steps,
                    "detail": "acquisition failed"}

    # 2) Dry-run the EVAL-67 statistic (no write) to prove the capture is usable.
    rc, out = _run([
        sys.executable, str(ROOT / "scripts" / "eval67_btc_oflow_tox_rv_oos.py"),
        "--capture-dir", str(capture_dir), "--no-write",
    ])
    steps.append({"step": "dry_run", "status": "ok" if rc == 0 else "failed",
                  "rc": rc, "tail": out[-2000:]})
    if rc != 0:
        return {"ok": False, "step": "dry_run", "steps": steps,
                "detail": "dry-run failed (capture may be under-floor)"}

    # 3) Seal prereg + COMBINED/BLOCKED.
    rc, out = _run([
        sys.executable, str(ROOT / "scripts" / "eval67_btc_oflow_tox_rv_oos.py"),
        "--capture-dir", str(capture_dir),
        "--seal", "--task-label", TASK_LABEL,
    ])
    steps.append({"step": "seal", "status": "ok" if rc == 0 else "failed",
                  "rc": rc, "tail": out[-2000:]})
    if rc != 0:
        return {"ok": False, "step": "seal", "steps": steps,
                "detail": "seal failed"}

    # 4) Authoritative seal-gate; require exit 0.
    gate_rc, gate_out = run_seal_gate_check(task_id=task_id,
                                            research_state_dir=research_state_dir)
    steps.append({"step": "seal_gate", "status": "ok" if gate_rc == 0 else "failed",
                  "rc": gate_rc, "tail": gate_out[-2000:]})
    return {"ok": bool(gate_rc == 0), "step": "seal_gate", "steps": steps,
            "seal_gate_rc": gate_rc}


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def _readiness_evidence(research_state_dir: Path = RS_DIR) -> Dict[str, Any]:
    rs = Path(research_state_dir)
    prereg = sorted(rs.glob(PREREG_GLOB)) if rs.is_dir() else []
    return {
        "prereg_present": bool(prereg),
        "prereg_files": [p.name for p in prereg],
        "capture_dir_present": CAPTURE_DIR.is_dir(),
        "capture_files": sorted(p.name for p in CAPTURE_DIR.glob("three_way_BTC_*.json"))
        if CAPTURE_DIR.is_dir() else [],
        "task_id": TASK_ID,
        "threshold": THRESHOLD_ISO,
        "sealed_btc_window": [SEALED_BTC_WINDOW_START, SEALED_BTC_WINDOW_END],
        "earliest_disjoint_capture_end": EARLIEST_DISJOINT_CAPTURE_END,
    }


def _emit(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-67 Phase-B gate: deterministic, idempotent completion "
                    "arbiter (SEALED / NOT_DUE / DUE / FAILED)."
    )
    ap.add_argument("--execute", action="store_true",
                    help="at/after threshold, run acquire->dry-run->seal->seal-gate "
                         "end-to-end and require seal-gate exit 0 (unskippable path)")
    ap.add_argument("--capture-dir", default=str(CAPTURE_DIR))
    ap.add_argument("--research-state-dir", default=str(RS_DIR))
    ap.add_argument("--task-id", default=TASK_ID)
    args = ap.parse_args(argv)

    rs = Path(args.research_state_dir)
    now = datetime.now(timezone.utc)
    sealed = detect_seal(rs, task_id=args.task_id)
    phase = decide_phase(now, parse_iso(THRESHOLD_ISO), sealed["sealed"])
    evidence = _readiness_evidence(rs)
    disjoint = disjointness_math(now)

    if phase == "SEALED":
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id,
                                                research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed["artifacts"],
            "seal_gate_tail": gate_out[-1500:],
            "note": "EVAL-67 campaign complete; idempotent no-op. Do not re-run.",
        })
        return EXIT_SEALED

    if phase == "NOT_DUE":
        _emit({
            "phase": "NOT_DUE",
            "exit_code": EXIT_NOT_DUE,
            "now": disjoint["now"],
            "threshold": THRESHOLD_ISO,
            "earliest_disjoint_capture_end": EARLIEST_DISJOINT_CAPTURE_END,
            "disjointness": disjoint,
            "readiness": evidence,
            "contract": "CORRECT CARRY (not a completion). Durably carry via the "
                        "git-committed handoff + external */5 cron. Do NOT bump the "
                        "handoff timestamp without new verified facts. Do NOT spawn a "
                        "capture bridge (it dies with the <=6h job). At/after "
                        f"{THRESHOLD_ISO} run: python3 scripts/eval67_phaseb_gate.py --execute",
        })
        return EXIT_NOT_DUE

    # phase == DUE
    if not args.execute:
        _emit({
            "phase": "DUE",
            "exit_code": EXIT_DUE,
            "now": disjoint["now"],
            "threshold": THRESHOLD_ISO,
            "disjointness": disjoint,
            "readiness": evidence,
            "contract": "HEAVY WORK REQUIRED. Re-run with --execute to "
                        "acquire->dry-run->seal->seal-gate and require seal-gate exit 0.",
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
            "note": "Phase-B executed and sealed; seal-gate exit 0.",
        })
        return EXIT_SEALED

    _emit({
        "phase": "FAILED",
        "exit_code": EXIT_FAILED,
        "failed_step": result.get("step"),
        "detail": result.get("detail") or result.get("reason"),
        "steps": result.get("steps"),
        "disjointness": result.get("disjointness"),
        "contract": "Phase-B did not produce a passing seal-gate. Fix the failed "
                    "step and re-run with --execute.",
    })
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())