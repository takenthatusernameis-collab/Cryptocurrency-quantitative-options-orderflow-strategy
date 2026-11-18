#!/usr/bin/env python3
"""EVAL-103 Phase-B gate: the single, deterministic, idempotent arbiter of the
EVAL-103 campaign's completion contract.

Why this exists
---------------
EVAL-85 sealed ``skew`` against forward tail asymmetry; EVAL-86 sealed ``skew``
against forward VRP; EVAL-97 sealed ``skew`` against forward vol-of-vol;
EVAL-101 sealed ``atm_iv`` level against forward signed return; EVAL-102 sealed
``term_ratio`` against forward signed return. The genuinely distinct,
on-charter, runnable-**now** cell tested by EVAL-103 is
**single-asset near-ATM implied-vol skew (put-call IV difference) ->
forward own-asset signed log-return mean** (EVAL-81 target, EVAL-71 surface
floor).

EVAL-103 measures exactly that on the already-acquired real on-disk captures
(option trade tape with IV/strike/expiry + perp candles for BOTH underlyings),
with no acquisition and no network, so it is runnable **now**. It reuses the
sealed EVAL-61/62/65/71 signal/inference reconstructions and the EVAL-71 surface
floor verbatim; it does not re-litigate EVAL-71, EVAL-81, EVAL-85, EVAL-86,
EVAL-97, EVAL-101, EVAL-102, or any sealed campaign.

Outcomes (exit codes)
---------------------
  0   SEALED   — a COMBINED_*/BLOCKED_* EVAL-103 artifact already exists with a stamp
                 >= the pre-registered task id; the seal-gate passes. COMPLETE;
                 idempotent no-op (safe to re-run forever).
  20  DUE      — nothing sealed yet and this was a status check only (no
                 --execute). The heavy work is REQUIRED now (data is on disk):
                 re-run with --execute.
  1   FAILED   --execute was requested but the run -> seal -> seal-gate pipeline
                 did not produce a passing seal-gate exit 0. Fix and re-run.

Unlike EVAL-67/68/69 there is no NOT_DUE phase: the EVAL-103 inputs are on disk,
so the honest pre-execution state is DUE (heavy work required), never a physics
wait.

``--execute`` is the unskippable path: it runs
``eval103_single_asset_skew_forward_signed_return.py --seal`` then the
authoritative seal-gate, and refuses to exit 0 unless the seal-gate exits 0.

Nothing here weakens the EVAL-64 floor (EVAL-103 reuses the sealed EVAL-71
surface floor verbatim, not weakened), uses synthetic data, enables live trading,
or edits sealed EVAL-02..62/64..66/70..102 artifacts or src/ (EVAL-103 is
appended here). It is append-only and reuses the sealed EVAL-61/62/65/71 runners.
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
TASK_ID = "INIT-2026-11-18T18:45:00Z-EVAL103-SINGLE-ASSET-SKEW-FORWARD-SIGNED-RETURN"
TASK_LABEL = "EVAL103-SINGLE-ASSET-SKEW-FORWARD-SIGNED-RETURN"
PREREG_GLOB = "EVAL_103_SINGLE_ASSET_SKEW_FORWARD_SIGNED_RETURN_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_103_SINGLE_ASSET_SKEW_FORWARD_SIGNED_RETURN_COMBINED_*"
BLOCKED_GLOB = "EVAL_103_SINGLE_ASSET_SKEW_FORWARD_SIGNED_RETURN_BLOCKED_*"

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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-103 artifact exists with a stamp
    >= the pre-registered task timestamp (mirrors check_session_sealed.py)."""
    rs = Path(research_state_dir)
    floor = task_floor_stamp(task_id)
    hits: List[Dict[str, str]] = []
    if rs.is_dir():
        for pat, kind in ((combined_glob, "COMBINED"), (blocked_glob, "BLOCKED")):
            for path in sorted(rs.glob(pat)):
                sm = _STAMP_RE.search(path.name)
                if not sm:
                    continue
                stamp = sm.group(1)
                if stamp >= floor:
                    hits.append({"name": path.name, "stamp": stamp, "kind": kind})
    hits.sort(key=lambda h: h["stamp"])
    return {"sealed": bool(hits), "artifacts": hits, "floor_stamp": floor}


def _run(cmd: Sequence[str], *, cwd: Path = ROOT) -> Tuple[int, str]:
    import os
    env = dict(os.environ)
    venv = ROOT / ".venv-deps"
    if venv.is_dir():
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(venv) + (os.pathsep + existing if existing else "")
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            env=env,
        )
        return int(proc.returncode), (proc.stdout or "") + (proc.stderr or "")
    except BaseException as exc:  # noqa: BLE001
        return 1, repr(exc)


def run_seal_gate_check(*, research_state_dir: Path = RS_DIR) -> Tuple[int, str]:
    """Invoke the authoritative seal-gate for EVAL-103."""
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "check_session_sealed.py"),
        "--task-id",
        TASK_ID,
        "--glob",
        PREREG_GLOB,
        "--require-any-glob",
        COMBINED_GLOB,
        "--require-any-glob",
        BLOCKED_GLOB,
    ]
    if research_state_dir != RS_DIR:
        cmd.extend(["--research-state-dir", str(research_state_dir)])
    return _run(cmd)


def capture_ready(capture_dir: Path = CAPTURE_DIR) -> Dict[str, Any]:
    p = Path(capture_dir)
    btc = sorted(p.glob("three_way_BTC_*.json")) if p.is_dir() else []
    eth = sorted(p.glob("three_way_ETH_*.json")) if p.is_dir() else []
    return {
        "present": bool(btc and eth),
        "btc": [x.name for x in btc],
        "eth": [x.name for x in eth],
        "capture_dir": str(p),
    }


# ---------------------------------------------------------------------------
# Execute path
# ---------------------------------------------------------------------------
def execute_phaseb(
    *,
    capture_dir: Path = CAPTURE_DIR,
    research_state_dir: Path = RS_DIR,
) -> Dict[str, Any]:
    """Run the heavy work (seal) then the authoritative seal-gate. Returns a
    structured result with ok=True only if the seal-gate exits 0."""
    steps: List[Dict[str, Any]] = []

    cap = capture_ready(capture_dir)
    if not cap["present"]:
        return {
            "ok": False,
            "step": "capture",
            "reason": "required on-disk captures missing (need BTC and ETH three_way)",
            "capture": cap,
            "steps": steps,
        }

    rc, out = _run([
        sys.executable,
        str(ROOT / "scripts" / "eval103_single_asset_skew_forward_signed_return.py"),
        "--capture-dir",
        str(capture_dir),
        "--seal",
        "--task-label",
        TASK_LABEL,
    ])
    steps.append({"step": "run_and_seal", "rc": rc, "tail": out[-4000:]})
    if rc != 0:
        return {"ok": False, "step": "run_and_seal", "steps": steps, "capture": cap}

    sg_rc, sg_out = run_seal_gate_check(research_state_dir=research_state_dir)
    steps.append({"step": "seal_gate", "rc": sg_rc, "tail": sg_out[-4000:]})
    return {
        "ok": sg_rc == 0,
        "step": "seal_gate",
        "steps": steps,
        "capture": cap,
    }


# ---------------------------------------------------------------------------
# Main arbiter
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-103 phase-B gate (SEALED/DUE/FAILED; deterministic, idempotent)"
    )
    ap.add_argument("--execute", action="store_true",
                    help="run EVAL-103 --seal + the authoritative seal-gate (unskippable)")
    ap.add_argument("--capture-dir", default=str(CAPTURE_DIR))
    ap.add_argument("--research-state-dir", default=str(RS_DIR))
    args = ap.parse_args(argv)

    rs_dir = Path(args.research_state_dir)
    cap_dir = Path(args.capture_dir)

    seal = detect_seal(rs_dir)
    cap = capture_ready(cap_dir)
    readiness = {
        "capture": cap,
        "runnable_now": bool(cap.get("present")),
        "task_id": TASK_ID,
        "task_label": TASK_LABEL,
    }

    if seal.get("sealed"):
        sg_rc, sg_out = run_seal_gate_check(research_state_dir=rs_dir)
        payload = {
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": sg_rc,
            "artifacts": seal.get("artifacts", []),
            "seal_gate_tail": sg_out[-2000:],
            "note": "EVAL-103 campaign complete; idempotent no-op. Do not re-run.",
        }
        print(json.dumps(payload, indent=2))
        return EXIT_SEALED

    if not args.execute:
        payload = {
            "phase": "DUE",
            "exit_code": EXIT_DUE,
            "readiness": readiness,
            "note": (
                "EVAL-103 is runnable now on the on-disk real captures but has not "
                "been sealed. Heavy work is REQUIRED. Re-run with: "
                "python3 scripts/eval103_phaseb_gate.py --execute"
            ),
        }
        print(json.dumps(payload, indent=2))
        return EXIT_DUE

    result = execute_phaseb(capture_dir=cap_dir, research_state_dir=rs_dir)
    if result.get("ok"):
        seal2 = detect_seal(rs_dir)
        payload = {
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "artifacts": seal2.get("artifacts", []),
            "steps": result.get("steps", []),
        }
        print(json.dumps(payload, indent=2))
        return EXIT_SEALED

    payload = {
        "phase": "FAILED",
        "exit_code": EXIT_FAILED,
        "result": result,
        "note": "EVAL-103 execute path did not produce a passing seal-gate. Fix and rerun.",
    }
    print(json.dumps(payload, indent=2))
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
