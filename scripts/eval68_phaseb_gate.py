#!/usr/bin/env python3
"""EVAL-68 Phase-B gate: the single, deterministic, idempotent arbiter of the
EVAL-68 campaign's completion contract (pooled BTC+ETH).

Why this exists
---------------
EVAL-67 is the immediate heavy action (BTC-only, gated by
``scripts/eval67_phaseb_gate.py``). EVAL-68 is the power-adequate pooled BTC+ETH
successor that the repo priority ("crypto OPTIONS surface + OPTIONS order-flow")
demands. Its heavy work is identical in kind to EVAL-67's — acquire a disjoint
forward three-way capture, dry-run the pooled statistic, seal — but it must never
compete with EVAL-67 for the single forward acquisition window. This gate encodes
that ordering and the completion contract as ONE deterministic command.

Outcomes (exit codes)
---------------------
  0   SEALED       — a COMBINED_*/BLOCKED_* EVAL-68 artifact exists with a stamp >=
                     the pre-registered task floor; the seal-gate passes. COMPLETE.
  1   FAILED       — at/after the threshold with EVAL-67 sealed, --execute ran but the
                     acquire -> dry-run -> seal -> seal-gate pipeline did not reach
                     seal-gate exit 0. Fix the reported step and re-run --execute.
  10  WAIT_EVAL67  — EVAL-67 has not sealed yet. The heavy EVAL-68 acquisition is NOT
                     due and must NOT run (it would compete with EVAL-67's forward
                     capture). Build/verify EVAL-68 code + prereg + tests only.
  20  DUE          — EVAL-67 has sealed and now >= threshold and nothing sealed yet.
                     HEAVY WORK IS REQUIRED NOW: re-run with --execute.

`--execute` is the unskippable path
-----------------------------------
Only valid once EVAL-67 has sealed AND now >= threshold. It acquires a disjoint
forward BTC+ETH capture in a single acquisition process (real, paper-only, public
read-only) -> dry-runs the pooled EVAL-68 statistic -> seals prereg +
COMBINED/BLOCKED -> runs the seal-gate, and refuses to exit 0 unless the seal-gate
exits 0. Before EVAL-67 seals, or before the threshold, it refuses to acquire.

Nothing here weakens the EVAL-64 floor, uses synthetic data, enables live trading,
or edits sealed EVAL-02..62/64..66 artifacts or src/. It is append-only and reuses
the sealed EVAL-60/65/67 runners verbatim.
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
TASK_ID = "INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS"
TASK_LABEL = "EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS"
PREREG_GLOB = "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED_*"
BLOCKED_GLOB = "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"

# Pre-registered disjointness threshold (prereg margin) and the physics behind it.
THRESHOLD_ISO = "2026-11-20T00:00:00Z"
SEALED_WINDOW_START = "2026-11-09T06:48:16Z"
SEALED_WINDOW_END = "2026-11-16T06:48:16Z"
EARLIEST_DISJOINT_CAPTURE_END = "2026-11-19T18:08:16Z"
CAPTURE_SPAN_SECONDS = 300000.0
ACQUIRE_DAYS = 3.7

UNDERLYINGS: Tuple[str, ...] = ("BTC", "ETH")
CAPTURE_DIR = ROOT / "data" / "raw" / "eval68"

# Exit codes.
EXIT_SEALED = 0
EXIT_FAILED = 1
EXIT_WAIT_EVAL67 = 10
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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-68 artifact exists with a stamp
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


def eval67_sealed(research_state_dir: Path = RS_DIR) -> bool:
    """EVAL-68 may only acquire after EVAL-67 has sealed (ordering; no competition)."""
    try:
        import scripts.eval67_phaseb_gate as g67  # noqa: E402
        return bool(g67.detect_seal(Path(research_state_dir))["sealed"])
    except Exception:
        return False


def decide_phase(
    now: datetime,
    threshold: datetime,
    sealed: bool,
    eval67_done: bool,
) -> str:
    if sealed:
        return "SEALED"
    if not eval67_done:
        return "WAIT_EVAL67"
    if now < threshold:
        # EVAL-67 cannot seal before the threshold, so this is defensive only.
        return "WAIT_EVAL67"
    return "DUE"


def disjointness_math(now: datetime) -> Dict[str, Any]:
    """Compute the trailing [--days, now] window and its disjointness from the
    sealed EVAL-64/65 three-way window (shared BTC+ETH)."""
    span = ACQUIRE_DAYS * 86400.0
    start = now.timestamp() - span
    sealed_start = parse_iso(SEALED_WINDOW_START).timestamp()
    sealed_end = parse_iso(SEALED_WINDOW_END).timestamp()
    overlap = max(0.0, min(now.timestamp(), sealed_end) - max(start, sealed_start))
    return {
        "now": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "acquire_days": ACQUIRE_DAYS,
        "underlyings": list(UNDERLYINGS),
        "window_start": datetime.fromtimestamp(start, tz=timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_end": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "span_seconds": round(now.timestamp() - start, 3),
        "meets_min_span": bool((now.timestamp() - start) >= CAPTURE_SPAN_SECONDS),
        "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
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
# Phase-B execution (only valid once EVAL-67 sealed AND at/after threshold)
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
    the caller maps it to an exit code. Refuses to run before EVAL-67 seals or
    before the threshold."""
    now = datetime.now(timezone.utc)

    if not eval67_sealed(research_state_dir):
        return {
            "ok": False,
            "step": "eval67_prereq",
            "reason": "eval67_not_sealed",
            "detail": "EVAL-68 must not acquire until EVAL-67 has sealed (single "
                      "forward window; no competition). Run "
                      "scripts/eval67_phaseb_gate.py --execute first.",
            "disjointness": disjointness_math(now),
        }
    if now.timestamp() < threshold_epoch():
        return {
            "ok": False,
            "step": "threshold",
            "reason": "before_threshold",
            "detail": "refusing to acquire before the disjointness threshold "
                      f"{THRESHOLD_ISO} (a naive capture would overlap the sealed "
                      "window and must seal BLOCKED)",
            "disjointness": disjointness_math(now),
        }

    steps: List[Dict[str, Any]] = []

    # 1) Acquire a disjoint forward BTC+ETH capture in ONE acquisition process.
    existing_btc = sorted(capture_dir.glob("three_way_BTC_*.json")) if capture_dir.is_dir() else []
    existing_eth = sorted(capture_dir.glob("three_way_ETH_*.json")) if capture_dir.is_dir() else []
    if existing_btc and existing_eth:
        steps.append({"step": "acquire", "status": "skipped",
                      "reason": "capture_exists",
                      "files": [p.name for p in existing_btc + existing_eth]})
    else:
        capture_dir.mkdir(parents=True, exist_ok=True)
        acquire_cmd = [
            sys.executable, str(ROOT / "scripts" / "eval60_acquire_three_way.py"),
            "--days", str(ACQUIRE_DAYS),
            "--end", now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "--out-dir", str(capture_dir),
            "--seal",
        ]
        for u in UNDERLYINGS:
            acquire_cmd += ["--underlying", u]
        rc, out = _run(acquire_cmd)
        steps.append({"step": "acquire", "status": "ok" if rc == 0 else "failed",
                      "rc": rc, "tail": out[-2000:]})
        if rc != 0:
            return {"ok": False, "step": "acquire", "steps": steps,
                    "detail": "acquisition failed"}

    # 2) Dry-run the pooled EVAL-68 statistic (no write) to prove usability.
    rc, out = _run([
        sys.executable, str(ROOT / "scripts" / "eval68_pooled_btc_eth_oflow_tox_rv_oos.py"),
        "--capture-dir", str(capture_dir), "--no-write",
    ])
    steps.append({"step": "dry_run", "status": "ok" if rc == 0 else "failed",
                  "rc": rc, "tail": out[-2000:]})
    if rc != 0:
        return {"ok": False, "step": "dry_run", "steps": steps,
                "detail": "dry-run failed (capture may be under-floor or non-disjoint)"}

    # 3) Seal prereg + COMBINED/BLOCKED.
    rc, out = _run([
        sys.executable, str(ROOT / "scripts" / "eval68_pooled_btc_eth_oflow_tox_rv_oos.py"),
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
        "capture_btc": sorted(p.name for p in CAPTURE_DIR.glob("three_way_BTC_*.json"))
        if CAPTURE_DIR.is_dir() else [],
        "capture_eth": sorted(p.name for p in CAPTURE_DIR.glob("three_way_ETH_*.json"))
        if CAPTURE_DIR.is_dir() else [],
        "task_id": TASK_ID,
        "threshold": THRESHOLD_ISO,
        "underlyings": list(UNDERLYINGS),
        "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
        "earliest_disjoint_capture_end": EARLIEST_DISJOINT_CAPTURE_END,
        "eval67_sealed": eval67_sealed(rs),
    }


def _emit(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-68 Phase-B gate: deterministic, idempotent completion "
                    "arbiter (SEALED / WAIT_EVAL67 / DUE / FAILED)."
    )
    ap.add_argument("--execute", action="store_true",
                    help="once EVAL-67 sealed and at/after threshold, run "
                         "acquire->dry-run->seal->seal-gate and require seal-gate exit 0")
    ap.add_argument("--capture-dir", default=str(CAPTURE_DIR))
    ap.add_argument("--research-state-dir", default=str(RS_DIR))
    ap.add_argument("--task-id", default=TASK_ID)
    args = ap.parse_args(argv)

    rs = Path(args.research_state_dir)
    now = datetime.now(timezone.utc)
    sealed = detect_seal(rs, task_id=args.task_id)
    e67_done = eval67_sealed(rs)
    phase = decide_phase(now, parse_iso(THRESHOLD_ISO), sealed["sealed"], e67_done)
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
            "note": "EVAL-68 campaign complete; idempotent no-op. Do not re-run.",
        })
        return EXIT_SEALED

    if phase == "WAIT_EVAL67":
        _emit({
            "phase": "WAIT_EVAL67",
            "exit_code": EXIT_WAIT_EVAL67,
            "now": disjoint["now"],
            "eval67_sealed": e67_done,
            "threshold": THRESHOLD_ISO,
            "disjointness": disjoint,
            "readiness": evidence,
            "contract": "EVAL-67 has not sealed (or now < threshold). Do NOT acquire "
                        "EVAL-68 data (it would compete with EVAL-67's single forward "
                        "window). Do the BUILD-ONLY heavy work: keep "
                        "scripts/eval68_pooled_btc_eth_oflow_tox_rv_oos.py + "
                        "eval68_phaseb_gate.py + their tests green and the EVAL-68 "
                        "prereg present. Then durably carry via the git-committed "
                        "handoff. At/after the threshold with EVAL-67 sealed run: "
                        "python3 scripts/eval68_phaseb_gate.py --execute",
        })
        return EXIT_WAIT_EVAL67

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