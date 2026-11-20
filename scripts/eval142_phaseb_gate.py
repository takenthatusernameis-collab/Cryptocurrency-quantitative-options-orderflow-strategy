#!/usr/bin/env python3
"""EVAL-142 Phase-B gate: the single, deterministic, idempotent arbiter of the
EVAL-142 campaign's completion contract.

Why this exists
---------------
EVAL-139 sealed ``GO CONFIRMED`` for the cross-asset ``term_ratio`` spillover ->
forward realized return skewness (BTC 0.2613 / ETH 0.4878, 7 pooled BH-FDR
rejections) — predictiveness only, no traded-form claim. Sealed EVAL-135 paired
the *term_slope* spillover with the risk-reversal traded form and sealed
``BLOCKED`` at the EVAL-64 capture floor. EVAL-76 sealed the surface-**skew**
timed risk reversal (NO-GO). The remaining distinct, on-charter, runnable-**now**
traded-form question is whether the cross-asset term-*ratio* spillover (other
asset's z-scored ``term_ratio``) monetizes net-of-cost through a signal-timed
delta-hedged risk reversal, at the sealed EVAL-64 feasible floor. EVAL-142
measures exactly that on the already-acquired real on-disk captures (no
acquisition, no network), so it is runnable **now** and keeps pre-threshold
sessions on genuine heavy work.

EVAL-142 reuses the sealed EVAL-61/62/65/71/74 inference, the EVAL-76
risk-reversal trade construction + EVAL-62 mark-path net-of-cost P&L, the
EVAL-139 cross-asset term_ratio signal path, and the sealed EVAL-64 feasible
floor verbatim; it does not re-litigate EVAL-64, EVAL-76, EVAL-135, EVAL-139, or
any sealed campaign.

Outcomes (exit codes)
---------------------
  0   SEALED   — a COMBINED_*/BLOCKED_* EVAL-142 artifact already exists with a
                  stamp >= the pre-registered task id; the seal-gate passes.
                  COMPLETE; idempotent no-op (safe to re-run forever).
  20  DUE      — nothing sealed yet and this was a status check only (no
                  --execute). The heavy work is REQUIRED now (data is on disk):
                  re-run with --execute.
  1   FAILED   --execute was requested but the run -> seal -> seal-gate pipeline
                  did not produce a passing seal-gate exit 0. Fix and re-run.

Unlike EVAL-67/68/69 there is no NOT_DUE phase: the EVAL-142 inputs are on disk,
so the honest pre-execution state is DUE (heavy work required), never a physics
wait. An under-floor capture seals ``BLOCKED`` (never ``NO-GO``).

``--execute`` is the unskippable path: it runs
``eval142_cross_asset_term_ratio_spillover_risk_reversal_net_of_cost.py --seal``
then the authoritative seal-gate, and refuses to exit 0 unless the seal-gate
exits 0.

Nothing here weakens the EVAL-64 floor (EVAL-142 reuses it verbatim via
e64._underlying_floor_strict), uses synthetic data, enables live trading, or
edits sealed EVAL-02..62/64..66/70..141 artifacts or src/ (EVAL-142 is appended
here). It is append-only and reuses the sealed EVAL-61/62/65/71/74 runners.
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
# Task id timestamp is the session start time (never a projected future time;
# see durable_handoff bottleneck #9: TASK_ID ISO stamp must be <= artifact stamp).
TASK_ID = "INIT-2026-11-20T13:51:59Z-EVAL142-CROSS-ASSET-TERM-RATIO-SPILLOVER-RISK-REVERSAL-NET-OF-COST"
TASK_LABEL = "EVAL142-CROSS-ASSET-TERM-RATIO-SPILLOVER-RISK-REVERSAL-NET-OF-COST"
PREREG_GLOB = "EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_COMBINED_*"
BLOCKED_GLOB = "EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_BLOCKED_*"

CAPTURE_DIR = ROOT / "data" / "raw" / "eval68"

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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-142 artifact exists with a stamp
    >= the pre-registered task timestamp (mirrors check_session_sealed.py)."""
    rs = Path(research_state_dir)
    floor = task_floor_stamp(task_id)
    hits: List[Dict[str, str]] = []
    if rs.is_dir():
        for pat, kind in ((combined_glob, "COMBINED"), (blocked_glob, "BLOCKED")):
            for path in sorted(rs.glob(pat)):
                if not path.is_file():
                    continue
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
    """Invoke the authoritative seal-gate for EVAL-142."""
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

    rc, out = _run(
        [
            sys.executable,
            str(
                ROOT
                / "scripts"
                / "eval142_cross_asset_term_ratio_spillover_risk_reversal_net_of_cost.py"
            ),
            "--capture-dir",
            str(capture_dir),
            "--seal",
            "--task-label",
            TASK_LABEL,
        ]
    )
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
        description="EVAL-142 phase-B gate (SEALED/DUE/FAILED; deterministic, idempotent)"
    )
    ap.add_argument("--execute", action="store_true",
                    help="run EVAL-142 --seal + the authoritative seal-gate (unskippable)")
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
            "note": "EVAL-142 campaign complete; idempotent no-op. Do not re-run.",
        }
        print(json.dumps(payload, indent=2))
        return EXIT_SEALED

    if not args.execute:
        payload = {
            "phase": "DUE",
            "exit_code": EXIT_DUE,
            "readiness": readiness,
            "note": (
                "EVAL-142 is runnable now on the on-disk real captures but has not "
                "been sealed. Heavy work is REQUIRED. Re-run with: "
                "python3 scripts/eval142_phaseb_gate.py --execute"
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
        "note": "EVAL-142 execute path did not produce a passing seal-gate. Fix and rerun.",
    }
    print(json.dumps(payload, indent=2))
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
