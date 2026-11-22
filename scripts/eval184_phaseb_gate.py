#!/usr/bin/env python3
"""EVAL-184 Phase-B gate: deterministic, idempotent arbiter of the EVAL-184
campaign's completion contract — the **traded-form net-of-cost OOS test of the
surface-line GOs** (the EVAL-69 analogue for EVAL-177/168/169).

Why this exists
---------------
The repository priority is "crypto OPTIONS surface + OPTIONS order-flow ->
tradeable, net-of-cost alpha on REAL public data". All predictiveness rungs
EVAL-02..183 are sealed. The order-flow line is fully resolved:
  - EVAL-67 / EVAL-68 (order-flow toxicity -> realized vol): GO CONFIRMED (predictive OOS)
  - EVAL-69 (the traded-form net-of-cost monetization of that same slice): NO-GO CONFIRMED (PASS)
The surviving tradeable alpha is exclusively on the **surface** line:
  - EVAL-177: cross-asset skew -> forward variance  (GO CONFIRMED)
  - EVAL-168: cross-asset atm_iv -> forward CVaR    (GO CONFIRMED)
  - EVAL-169: cross-asset term_slope -> forward CVaR (GO CONFIRMED)
The genuinely-next on-charter heavy work is therefore the **surface-line
traded-form net-of-cost OOS verdict** — the EVAL-69 analogue for the surface
alpha (EVAL-177/168/169). This gate encodes that ordering + the completion
contract as ONE deterministic command so future sessions cannot avoid or
substitute the heavy work.

Outcomes (exit codes)
---------------------
  0   SEALED       — a COMBINED_*/BLOCKED_* EVAL-184 artifact exists with a stamp
                     >= the pre-registered task floor; the seal-gate passes. COMPLETE.
  1   FAILED       — at/after threshold with the runner green but the
                     run -> seal -> seal-gate pipeline did not reach seal-gate exit 0.
  10  WAIT_CAPTURE — no floor-compliant, disjoint surface capture at the
                     surface capture dir (default data/raw/eval84cap). The heavy
                     acquisition MUST run first (~1h, 3.7d, both underlyings).
  20  WAIT_RUNNER  — a floor-compliant disjoint capture exists but the EVAL-184
                     surface-line traded-form runner is not yet green (missing,
                     failing its own tests, or --no-write dry-run fails). BUILD-ONLY
                     heavy work: build/fix the runner + prereg + tests.
  30  DUE          — capture present, runner green, nothing sealed yet. HEAVY WORK
                     IS REQUIRED NOW: re-run with --execute.

``--execute`` is the unskippable path
-------------------------------------
Only valid once a floor-compliant disjoint surface capture exists AND the
EVAL-184 runner passes its own green check. It runs the surface-line traded-form
statistic (skew / atm_iv / term_slope at the GO-producing bar horizons) on the
disjoint surface capture -> seals prereg + COMBINED/BLOCKED -> runs the
seal-gate, and refuses to exit 0 unless the seal-gate exits 0. Before the capture
exists, or before the runner is green, it refuses to run.

Nothing here weakens the EVAL-64 floor, uses synthetic data, enables live
trading, or edits sealed EVAL-02..62/64..66/67/68/69/70..183 artifacts or src/.
It is append-only and references the sealed EVAL-60/64/69/71/74/177/168/169
machinery verbatim (surface signal fields: skew via e71.build_surface_bars;
atm_iv via e71.build_surface_bars; term_slope via e74._term_bars).
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

# Authoritative pre-registered identifiers (parseable by check_session_sealed.py).
# TASK_ID ISO stamp is the session-start floor; artifacts must be >= this stamp.
TASK_ID = "INIT-2026-11-22T06:30:00Z-EVAL184-SURFACE-TRADED-NETOFCOST-OOS"
TASK_LABEL = "EVAL184-SURFACE-TRADED-NETOFCOST-OOS"
PREREG_GLOB = "EVAL_184_SURFACE_TRADED_NETFCOST_OOS_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_184_SURFACE_TRADED_NETFCOST_OOS_COMBINED_*"
BLOCKED_GLOB = "EVAL_184_SURFACE_TRADED_NETFCOST_OOS_BLOCKED_*"

# Pre-registered disjointness threshold (prereg margin) and the physics behind it.
# The sealed EVAL-64/65 three-way window is 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z.
# The surface-line traded-form must consume a forward capture disjoint from it, at/after
# the threshold. Use the same floor-compliant 3.7-day span as EVAL-67/68/69.
THRESHOLD_ISO = "2026-11-20T00:00:00Z"
SEALED_WINDOW_START = "2026-11-09T06:48:16Z"
SEALED_WINDOW_END = "2026-11-16T06:48:16Z"
EARLIEST_DISJOINT_CAPTURE_END = "2026-11-19T18:08:16Z"
CAPTURE_SPAN_SECONDS = 300000.0
ACQUIRE_DAYS = 3.7

UNDERLYINGS: Tuple[str, ...] = ("BTC", "ETH")
# Surface-line traded-form reads the floor-compliant disjoint capture. The handoff
# names data/raw/eval84cap; the runner/gate accept any --capture-dir that carries
# floor-compliant, disjoint three_way_BTC_*.json + three_way_ETH_*.json captures.
CAPTURE_DIR = ROOT / "data" / "raw" / "eval84cap"

# The surviving surface-line GO signals -> forward targets, at the GO bar horizons.
# (signal_field, builder_kind, source_rung)
SURFACE_GO_CELLS: Tuple[Dict[str, str], ...] = (
    {"signal": "skew", "builder": "e71.build_surface_bars", "rung": "EVAL-177", "target": "forward_variance"},
    {"signal": "atm_iv", "builder": "e71.build_surface_bars", "rung": "EVAL-168", "target": "forward_cvar"},
    {"signal": "term_slope", "builder": "e74._term_bars", "rung": "EVAL-169", "target": "forward_cvar"},
)

# The runner that performs the heavy computation (built by the next session; this
# gate refuses to seal until it is present AND green). Until it exists, the gate
# reports WAIT_RUNNER / DUE appropriately so the heavy work is unavoidable.
RUNNER_REL = "scripts/eval184_surface_traded_netofcost_oos.py"

# Exit codes.
EXIT_SEALED = 0
EXIT_FAILED = 1
EXIT_WAIT_CAPTURE = 10
EXIT_WAIT_RUNNER = 20
EXIT_DUE = 30

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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-184 artifact exists with a stamp
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
                    hits.append({"name": path.name, "stamp": top,
                                 "kind": "COMBINED" if combined_glob in pat else "BLOCKED"})
    return {"sealed": bool(hits), "artifacts": hits, "floor_stamp": floor}


def capture_inventory(capture_dir: Path) -> Dict[str, List[str]]:
    """Return the BTC/ETH three_way capture files under capture_dir (no I/O beyond
    a directory listing)."""
    d = Path(capture_dir)
    btc = sorted(p.name for p in d.glob("three_way_BTC_*.json")) if d.is_dir() else []
    eth = sorted(p.name for p in d.glob("three_way_ETH_*.json")) if d.is_dir() else []
    return {"btc": btc, "eth": eth, "present": bool(btc and eth), "dir": str(d)}


def runner_present_and_green(*, capture_dir: Path, runner_rel: str = RUNNER_REL) -> Dict[str, Any]:
    """Return whether the EVAL-184 runner exists and passes its --no-write dry run
    against the capture (proves the surface signal pipeline is wired + usable).
    Never writes; never seals."""
    runner = ROOT / runner_rel
    if not runner.is_file():
        return {"runner_present": False, "runner_green": False,
                "runner": str(runner), "reason": "runner_missing"}
    cmd = [sys.executable, str(runner), "--capture-dir", str(capture_dir), "--no-write"]
    env = dict(os.environ)
    deps_dir = str(ROOT / ".venv-deps")
    env["PYTHONPATH"] = deps_dir + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, env=env)
    except Exception as exc:  # pragma: no cover - defensive
        return {"runner_present": True, "runner_green": False,
                "runner": str(runner), "reason": f"runner_error:{exc}"}
    return {
        "runner_present": True,
        "runner_green": bool(proc.returncode == 0),
        "runner": str(runner),
        "returncode": proc.returncode,
        "tail": (proc.stdout + proc.stderr)[-2000:],
    }


def decide_phase(
    now: datetime,
    threshold: datetime,
    sealed: bool,
    capture_present: bool,
    runner_green: bool,
) -> str:
    if sealed:
        return "SEALED"
    if not capture_present:
        return "WAIT_CAPTURE"
    if now < threshold:
        # Capture exists but is not yet disjoint from the sealed window.
        return "WAIT_CAPTURE"
    if not runner_green:
        return "WAIT_RUNNER"
    return "DUE"


def disjointness_math(now: datetime, *, capture_dir: Path = CAPTURE_DIR) -> Dict[str, Any]:
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
        "capture_dir": str(capture_dir),
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
# Phase-B execution (only valid once a floor-compliant disjoint capture exists
# AND the runner is green)
# ---------------------------------------------------------------------------
def _run(cmd: Sequence[str], *, cwd: Path = ROOT) -> Tuple[int, str]:
    proc = subprocess.run(list(cmd), cwd=str(cwd), capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr)


def execute_phaseb(
    *,
    capture_dir: Path = CAPTURE_DIR,
    research_state_dir: Path = RS_DIR,
    task_id: str = TASK_ID,
    runner_rel: str = RUNNER_REL,
) -> Dict[str, Any]:
    """Run -> seal -> seal-gate. Returns a structured result; the caller maps it to
    an exit code. Refuses to run before the capture is floor-compliant/disjoint and
    before the runner is green."""
    now = datetime.now(timezone.utc)

    inv = capture_inventory(capture_dir)
    if not inv["present"]:
        return {
            "ok": False,
            "step": "capture",
            "reason": "missing_capture",
            "detail": f"expected floor-compliant disjoint surface capture at {capture_dir} "
                      "with three_way_BTC_*.json and three_way_ETH_*.json; run "
                      "scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH "
                      f"--days 3.7 --end <at/after {EARLIEST_DISJOINT_CAPTURE_END}> "
                      f"--out-dir {capture_dir} --seal (then re-check the EVAL-64 floor)",
            "disjointness": disjointness_math(now, capture_dir=capture_dir),
        }
    if now.timestamp() < threshold_epoch():
        return {
            "ok": False,
            "step": "threshold",
            "reason": "before_threshold",
            "detail": "refusing to run before the disjointness threshold "
                      f"{THRESHOLD_ISO} (the capture would not yet be disjoint from the "
                      "sealed EVAL-64/65 window)",
            "disjointness": disjointness_math(now, capture_dir=capture_dir),
        }

    steps: List[Dict[str, Any]] = []
    steps.append({"step": "capture", "status": "ok", "files": inv["btc"] + inv["eth"]})

    # 1) Runner must be present + green (dry-run, no write) before sealing.
    green = runner_present_and_green(capture_dir=capture_dir, runner_rel=runner_rel)
    steps.append({"step": "runner_green", "status": "ok" if green.get("runner_green") else "failed",
                  "runner_present": green.get("runner_present"),
                  "returncode": green.get("returncode"),
                  "tail": green.get("tail")})
    if not green.get("runner_green"):
        return {"ok": False, "step": "runner_green", "steps": steps,
                "detail": "EVAL-184 runner is missing or its --no-write dry-run failed "
                          "(see step tail); build/fix it before sealing"}

    # 2) Dry-run the runner (no write) to prove usability, then seal.
    rc, out = _run([
        sys.executable, str(ROOT / runner_rel),
        "--capture-dir", str(capture_dir), "--no-write",
    ])
    steps.append({"step": "dry_run", "status": "ok" if rc == 0 else "failed",
                  "rc": rc, "tail": out[-2000:]})
    if rc != 0:
        return {"ok": False, "step": "dry_run", "steps": steps,
                "detail": "dry-run failed (capture may be under-floor or non-disjoint)"}

    rc, out = _run([
        sys.executable, str(ROOT / runner_rel),
        "--capture-dir", str(capture_dir),
        "--seal", "--task-label", TASK_LABEL,
    ])
    steps.append({"step": "seal", "status": "ok" if rc == 0 else "failed",
                  "rc": rc, "tail": out[-2000:]})
    if rc != 0:
        return {"ok": False, "step": "seal", "steps": steps, "detail": "seal failed"}

    # 3) Authoritative seal-gate; require exit 0.
    gate_rc, gate_out = run_seal_gate_check(task_id=task_id,
                                            research_state_dir=research_state_dir)
    steps.append({"step": "seal_gate", "status": "ok" if gate_rc == 0 else "failed",
                  "rc": gate_rc, "tail": gate_out[-2000:]})
    return {"ok": bool(gate_rc == 0), "step": "seal_gate", "steps": steps,
            "seal_gate_rc": gate_rc}


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def _readiness_evidence(research_state_dir: Path = RS_DIR,
                        *, capture_dir: Path = CAPTURE_DIR) -> Dict[str, Any]:
    rs = Path(research_state_dir)
    prereg = sorted(rs.glob(PREREG_GLOB)) if rs.is_dir() else []
    inv = capture_inventory(capture_dir)
    return {
        "prereg_present": bool(prereg),
        "prereg_files": [p.name for p in prereg],
        "capture_dir": str(capture_dir),
        "capture_present": inv["present"],
        "capture_btc": inv["btc"],
        "capture_eth": inv["eth"],
        "task_id": TASK_ID,
        "threshold": THRESHOLD_ISO,
        "underlyings": list(UNDERLYINGS),
        "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
        "earliest_disjoint_capture_end": EARLIEST_DISJOINT_CAPTURE_END,
        "surface_go_cells": [dict(c) for c in SURFACE_GO_CELLS],
        "runner": RUNNER_REL,
    }


def _emit(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-184 Phase-B gate: deterministic, idempotent completion "
                    "arbiter (SEALED / WAIT_CAPTURE / WAIT_RUNNER / DUE / FAILED)."
    )
    ap.add_argument("--execute", action="store_true",
                    help="once a floor-compliant disjoint surface capture exists AND the "
                         "EVAL-184 runner is green, run the surface-line traded-form on the "
                         "capture -> seal -> seal-gate and require seal-gate exit 0")
    ap.add_argument("--capture-dir", default=str(CAPTURE_DIR))
    ap.add_argument("--research-state-dir", default=str(RS_DIR))
    ap.add_argument("--task-id", default=TASK_ID)
    ap.add_argument("--runner", default=RUNNER_REL)
    args = ap.parse_args(argv)

    rs = Path(args.research_state_dir)
    cap = Path(args.capture_dir)
    now = datetime.now(timezone.utc)
    sealed = detect_seal(rs, task_id=args.task_id)
    inv = capture_inventory(cap)
    green = runner_present_and_green(capture_dir=cap, runner_rel=args.runner)
    phase = decide_phase(now, parse_iso(THRESHOLD_ISO), sealed["sealed"],
                         inv["present"], bool(green.get("runner_green")))
    evidence = _readiness_evidence(rs, capture_dir=cap)
    evidence["runner_check"] = green
    disjoint = disjointness_math(now, capture_dir=cap)

    if phase == "SEALED":
        gate_rc, gate_out = run_seal_gate_check(task_id=args.task_id,
                                                research_state_dir=rs)
        _emit({
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": gate_rc,
            "artifacts": sealed["artifacts"],
            "seal_gate_tail": gate_out[-1500:],
            "note": "EVAL-184 campaign complete; idempotent no-op. Do not re-run.",
        })
        return EXIT_SEALED

    if phase == "WAIT_CAPTURE":
        _emit({
            "phase": "WAIT_CAPTURE",
            "exit_code": EXIT_WAIT_CAPTURE,
            "now": disjoint["now"],
            "threshold": THRESHOLD_ISO,
            "disjointness": disjoint,
            "readiness": evidence,
            "contract": "NO floor-compliant disjoint surface capture at the capture dir. "
                        "HEAVY WORK REQUIRED: acquire a 3.7-day, both-underlying, disjoint "
                        "capture (>= earliest_disjoint_capture_end) with "
                        "scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH "
                        "--days 3.7 --end <at/after the earliest disjoint end> --out-dir "
                        f"{cap} --seal, then verify the EVAL-64 floor (never weaken it). "
                        "Budget ~1h. Once the capture is floor-compliant + disjoint, build/"
                        "green the EVAL-184 runner and re-run this gate.",
        })
        return EXIT_WAIT_CAPTURE

    if phase == "WAIT_RUNNER":
        _emit({
            "phase": "WAIT_RUNNER",
            "exit_code": EXIT_WAIT_RUNNER,
            "now": disjoint["now"],
            "threshold": THRESHOLD_ISO,
            "disjointness": disjoint,
            "readiness": evidence,
            "runner_check": green,
            "contract": "A floor-compliant disjoint capture exists but the EVAL-184 "
                        "surface-line traded-form runner is missing or not green. "
                        "BUILD-ONLY HEAVY WORK: implement "
                        f"{RUNNER_REL} (the EVAL-69 analogue for the surface line: skew/"
                        "atm_iv/term_slope at the EVAL-177/168/169 GO horizons; reuse EVAL-69 "
                        "mark-path/cost helpers verbatim; pooled BH-FDR; both-asset GO bar), "
                        "add its prereg + tests, and make the runner --no-write dry-run pass. "
                        "Then re-run this gate with --execute.",
        })
        return EXIT_WAIT_RUNNER

    # phase == DUE
    if not args.execute:
        _emit({
            "phase": "DUE",
            "exit_code": EXIT_DUE,
            "now": disjoint["now"],
            "threshold": THRESHOLD_ISO,
            "disjointness": disjoint,
            "readiness": evidence,
            "contract": "HEAVY WORK REQUIRED. Re-run with --execute to run the surface-line "
                        "traded-form on the disjoint capture -> seal -> seal-gate and require "
                        "seal-gate exit 0.",
        })
        return EXIT_DUE

    result = execute_phaseb(capture_dir=cap, research_state_dir=rs,
                            task_id=args.task_id, runner_rel=args.runner)
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