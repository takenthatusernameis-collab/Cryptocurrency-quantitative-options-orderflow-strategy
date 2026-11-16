#!/usr/bin/env python3
"""EVAL-67 persistent, SELF-COMPLETING capture+seal bridge.

Waits until the pre-registered disjointness threshold (2026-11-20T00:00:00Z),
then runs the full heavy EVAL-67 pipeline as a tracked persistent process:

    acquire (real, paper-only, disjoint BTC 3-way) -> dry-run evaluate -> seal
    -> seal-gate -> completion manifest

This is the "genuinely live persistent acquisition" path of the durable handoff
contract, upgraded so the campaign CANNOT stall after acquisition if no agent
session happens to be alive on 2026-11-20: the bridge itself carries the work
through to a sealed artifact + gate exit code and records a completion manifest
(``research_state/EVAL_67_BRIDGE_COMPLETE_<pid>.json``).

It refuses to acquire before the sealed EVAL-64/65 BTC window has cleared (a
naive trailing ``--days 7`` capture would overlap and must seal BLOCKED).

Liveness: writes ``research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_<pid>.json``
every HEARTBEAT_SECONDS with {pid, started_at, threshold, now, phase, rc}.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Ensure the vendored deps dir is importable for this process too (the sealed
# EVAL scripts import numpy/pandas/scipy from .venv-deps).
_DEPS = ROOT / ".venv-deps"
if str(_DEPS) not in sys.path:
    sys.path.insert(0, str(_DEPS))

THRESHOLD = "2026-11-20T00:00:00Z"
HEARTBEAT_SECONDS = 60.0
LIVENESS_DIR = ROOT / "research_state"

# Authoritative EVAL-67 task id (parseable by check_session_sealed.py).
TASK_ID = "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION"
TASK_LABEL = "EVAL67-BTC-OFLOW-TOX-RV-OOS"
CAPTURE_DIR = "data/raw/eval67"

# Reuse the sealed helper for ISO parsing.
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402


def _now_iso() -> str:
    return e65._utc_now_iso()


def _threshold_epoch() -> float:
    dt = datetime.fromisoformat(THRESHOLD.replace("Z", "+00:00"))
    return dt.timestamp()


def _child_env() -> dict:
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONPATH"] = f"{ROOT}/.venv-deps{env.get('PYTHONPATH', '')}"
    return env


def write_heartbeat(pid: int, phase: str, rc: int | None = None, note: str = "") -> None:
    payload = {
        "pid": pid,
        "started_at": _now_iso(),
        "threshold": THRESHOLD,
        "phase": phase,
        "rc": rc,
        "note": note,
        "host": os.uname().nodename if hasattr(os, "uname") else "?",
    }
    path = LIVENESS_DIR / f"EVAL_67_CAPTURE_BRIDGE_LIVENESS_{pid}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _run_streaming(pid: int, phase: str, cmd: list[str]) -> tuple[int, str]:
    """Run a child command, streaming its last output line into the heartbeat."""
    write_heartbeat(pid, phase, note=" ".join(cmd))
    proc = subprocess.Popen(
        cmd, cwd=str(ROOT), env=_child_env(),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    assert proc.stdout is not None
    last_line = ""
    for line in proc.stdout:
        last_line = line.rstrip()
        write_heartbeat(pid, phase, note=last_line[:500])
    rc = proc.returncode
    return int(rc if rc is not None else 0), last_line


def main() -> int:
    pid = os.getpid()
    started = _now_iso()
    write_heartbeat(pid, "boot", note=f"started {started}")
    threshold_epoch = _threshold_epoch()

    # Install a no-op handler so SIGTERM/SIGINT are caught gracefully for a
    # clean final heartbeat instead of a silent kill.
    def _handle(_sig, _frame):
        write_heartbeat(pid, "signalled", note="received termination signal")
        raise SystemExit(130)
    signal.signal(signal.SIGTERM, _handle)
    signal.signal(signal.SIGINT, _handle)

    while True:
        now_epoch = time.time()
        now_iso = _now_iso()
        write_heartbeat(pid, "waiting", note=f"now={now_iso} threshold={THRESHOLD}")
        if now_epoch >= threshold_epoch:
            break
        time.sleep(min(HEARTBEAT_SECONDS, max(1.0, threshold_epoch - now_epoch)))

    # ---- Threshold reached: full heavy pipeline (self-completing) ----------
    completion: dict = {
        "pid": pid,
        "task_id": TASK_ID,
        "task_label": TASK_LABEL,
        "threshold": THRESHOLD,
        "started_at": started,
        "steps": {},
    }

    def _record(step: str, rc: int, detail: str) -> None:
        completion["steps"][step] = {"rc": rc, "detail": detail[:800]}
        _write_completion(pid, completion, phase="running")

    # 1) Real, paper-only, disjoint BTC three-way acquisition (+ manifest).
    (ROOT / "data/raw/eval67").mkdir(parents=True, exist_ok=True)
    acq_cmd = [
        sys.executable, "scripts/eval60_acquire_three_way.py",
        "--underlying", "BTC", "--days", "3.7", "--end", _now_iso(),
        "--out-dir", CAPTURE_DIR, "--seal",
    ]
    acq_rc, acq_last = _run_streaming(pid, "acquiring", acq_cmd)
    _record("acquire", acq_rc, acq_last)
    if acq_rc != 0:
        completion["result"] = "ACQUIRE_FAILED"
        _write_completion(pid, completion, phase="acquire_failed")
        write_heartbeat(pid, "acquire_failed", rc=acq_rc, note=acq_last[:500])
        return acq_rc

    # 2) Dry-run evaluate (compute + print, seal nothing) — sanity gate.
    dry_cmd = [
        sys.executable, "scripts/eval67_btc_oflow_tox_rv_oos.py",
        "--capture-dir", CAPTURE_DIR, "--no-write",
    ]
    dry_rc, dry_last = _run_streaming(pid, "evaluating", dry_cmd)
    _record("dry_run", dry_rc, dry_last)
    if dry_rc != 0:
        completion["result"] = "DRYRUN_FAILED"
        _write_completion(pid, completion, phase="dryrun_failed")
        write_heartbeat(pid, "dryrun_failed", rc=dry_rc, note=dry_last[:500])
        return dry_rc

    # 3) Seal prereg + COMBINED/BLOCKED verdict.
    seal_cmd = [
        sys.executable, "scripts/eval67_btc_oflow_tox_rv_oos.py",
        "--capture-dir", CAPTURE_DIR, "--seal", "--task-label", TASK_LABEL,
    ]
    seal_rc, seal_last = _run_streaming(pid, "sealing", seal_cmd)
    _record("seal", seal_rc, seal_last)

    # 4) Seal gate — must exit 0.
    gate_cmd = [
        sys.executable, "scripts/check_session_sealed.py",
        "--task-id", TASK_ID,
        "--glob", "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*",
        "--require-any-glob", "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*",
        "--require-any-glob", "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*",
    ]
    gate_rc, gate_last = _run_streaming(pid, "gating", gate_cmd)
    _record("gate", gate_rc, gate_last)

    completion["result"] = "COMPLETE" if gate_rc == 0 else "GATE_FAILED"
    completion["seal_rc"] = seal_rc
    completion["gate_rc"] = gate_rc
    completion["finished_at"] = _now_iso()
    _write_completion(pid, completion, phase="done" if gate_rc == 0 else "gate_failed")
    write_heartbeat(
        pid, "done" if gate_rc == 0 else "gate_failed", rc=gate_rc,
        note=f"result={completion['result']} gate_rc={gate_rc}",
    )
    return gate_rc


def _write_completion(pid: int, completion: dict, phase: str) -> None:
    completion = dict(completion)
    completion["phase"] = phase
    completion["updated_at"] = _now_iso()
    path = LIVENESS_DIR / f"EVAL_67_BRIDGE_COMPLETE_{pid}.json"
    path.write_text(json.dumps(completion, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())