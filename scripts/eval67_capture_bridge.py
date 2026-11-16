#!/usr/bin/env python3
"""EVAL-67 persistent capture bridge.

Waits until the pre-registered disjointness threshold (2026-11-20T00:00:00Z),
then runs the real, paper-only, disjoint BTC three-way acquisition into
``data/raw/eval67`` and writes an acquisition manifest into ``research_state/``.

This is the "genuinely live persistent acquisition" path of the durable handoff
contract: it is started as a persistent background process, records its PID and
a liveness heartbeat, and refuses to acquire before the sealed EVAL-64/65 BTC
window has cleared (a naive trailing --days 7 capture would overlap and must seal
BLOCKED).

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

# Reuse the sealed helper for ISO parsing.
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402


def _now_iso() -> str:
    return e65._utc_now_iso()


def _threshold_epoch() -> float:
    dt = datetime.fromisoformat(THRESHOLD.replace("Z", "+00:00"))
    return dt.timestamp()


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

    # Threshold reached: launch the real, paper-only, disjoint acquisition as a
    # child so the bridge stays the tracked persistent process and can report
    # the child's exit code and liveness.
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONPATH"] = f"{ROOT}/.venv-deps{env.get('PYTHONPATH', '')}"
    cmd = [
        sys.executable,
        "scripts/eval60_acquire_three_way.py",
        "--underlying", "BTC",
        "--days", "3.7",
        "--end", _now_iso(),
        "--out-dir", "data/raw/eval67",
        "--seal",
    ]
    write_heartbeat(pid, "acquiring", note=" ".join(cmd))
    proc = subprocess.Popen(
        cmd, cwd=str(ROOT), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    assert proc.stdout is not None
    last_line = ""
    while True:
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        if line:
            last_line = line.rstrip()
            write_heartbeat(pid, "acquiring", note=last_line[:500])
    rc = proc.returncode
    write_heartbeat(pid, "done", rc=rc, note=f"last={last_line[:500]}")
    return int(rc if rc is not None else 0)


if __name__ == "__main__":
    raise SystemExit(main())