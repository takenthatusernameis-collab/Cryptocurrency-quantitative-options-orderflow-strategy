#!/usr/bin/env python3
"""EVAL-185 Phase-B gate: deterministic, idempotent arbiter of the EVAL-185
completion contract — the **surface-line traded-form ROBUSTNESS GRID**
(monetization/horizon falsification) of the EVAL-177/168/169 surface GOs.

Why this exists
---------------
The repository priority is "crypto OPTIONS surface + OPTIONS order-flow ->
tradeable, net-of-cost alpha on REAL public data". The predictiveness rungs
EVAL-02..183 are all sealed. The traded-form line is now fully resolved and BOTH
signal families monetize to NO-GO net-of-cost:
  - EVAL-69  (order-flow toxicity -> realized vol, traded-form): NO-GO CONFIRMED (PASS)
  - EVAL-184 (surface skew/atm_iv/term_slope -> var/CVaR, traded-form): NO-GO CONFIRMED (PASS)
              (COMBINED_20261122T081750Z, 0 BH-FDR rejections across 12 configs,
               floor OK BTC+ETH, disjoint OK, 2000 pooled returns, power adequate)

The genuinely-next on-charter heavy work is to **bound whether that surface NO-GO
is a monetization/horizon artifact** rather than a robust economic result: re-run
the surface-line traded-form under a PRE-REGISTERED alternative cost x horizon grid
on the same floor-compliant disjoint capture (data/raw/eval84cap), with pooled
BH-FDR across the FULL grid and a both-asset GO bar. The exact grid is 3 signals x
5 horizons {60,120,240,300,360}s x 3 cost haircuts {0.5x,1x,2x} = 45 configs.
Pre-registered GO bar: >=1 config with pooled BH-FDR rejection + Sharpe>0 +
bootstrap CI lower>0 under >=2 of 3 cost scenarios (robust to cost). Else
NO-GO CONFIRMED (PASS): the surface NO-GO is robust to monetization.

This gate encodes that ordering + the completion contract as ONE deterministic
command so future sessions cannot avoid or substitute the heavy work. It is
append-only, touches no sealed EVAL-02..62/64..69/70..184 artifact or src/, and
reuses the EVAL-184 runner machinery (e71/e74/e62 surface + mark-path helpers).

Outcomes (exit codes)
---------------------
  0   SEALED       — a COMBINED_*/BLOCKED_* EVAL-185 artifact exists with a stamp
                     >= the pre-registered task floor; the seal-gate passes. COMPLETE.
  1   FAILED       — at/after threshold with the runner green but the
                     run -> seal -> seal-gate pipeline did not reach seal-gate exit 0.
  10  WAIT_CAPTURE — no floor-compliant, disjoint capture at the capture dir.
  20  WAIT_RUNNER  — a floor-compliant disjoint capture exists but the EVAL-185
                     surface-line traded-form robustness runner is not yet green.
                     BUILD-ONLY heavy work: build/fix the runner + prereg + tests.
  30  DUE          — capture present, runner green, nothing sealed yet. HEAVY WORK
                     IS REQUIRED NOW: re-run with --execute.

``--execute`` runs the surface-line robustness grid on the disjoint capture ->
seals prereg + COMBINED/BLOCKED -> runs the seal-gate, and refuses to exit 0 unless
the seal-gate exits 0. Nothing here weakens the EVAL-64 floor, uses synthetic data,
enables live trading, or edits sealed artifacts or src/.
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
TASK_ID = "INIT-2026-11-22T08:40:00Z-EVAL185-SURFACE-TRADED-ROBUSTNESS-GRID"
TASK_LABEL = "EVAL185-SURFACE-TRADED-ROBUSTNESS-GRID"
PREREG_GLOB = "EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_COMBINED_*"
BLOCKED_GLOB = "EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_BLOCKED_*"

# Pre-registered disjointness threshold (prereg margin). The robustness grid consumes
# the SAME floor-compliant disjoint capture as EVAL-184 (data/raw/eval84cap), which is
# already disjoint from the sealed EVAL-64/65 window (2026-11-09..2026-11-16).
THRESHOLD_ISO = "2026-11-20T00:00:00Z"
SEALED_WINDOW_START = "2026-11-09T06:48:16Z"
SEALED_WINDOW_END = "2026-11-16T06:48:16Z"
EARLIEST_DISJOINT_CAPTURE_END = "2026-11-19T18:08:16Z"
CAPTURE_SPAN_SECONDS = 300000.0
ACQUIRE_DAYS = 3.7

UNDERLYINGS: Tuple[str, ...] = ("BTC", "ETH")
# Robustness grid reuses the floor-compliant disjoint capture (read-only); a fresh
# forward-window replication leg (background, TRACK A) is tracked in the handoff.
CAPTURE_DIR = ROOT / "data" / "raw" / "eval84cap"

# The surviving surface-line GO signals -> forward targets, at the GO bar horizons.
SURFACE_GO_CELLS: Tuple[Dict[str, str], ...] = (
    {"signal": "skew", "builder": "e71.build_surface_bars", "rung": "EVAL-177", "target": "forward_variance"},
    {"signal": "atm_iv", "builder": "e71.build_surface_bars", "rung": "EVAL-168", "target": "forward_cvar"},
    {"signal": "term_slope", "builder": "e74._term_bars", "rung": "EVAL-169", "target": "forward_cvar"},
)

# Exact pre-registered robustness grid: three signals x five bar horizons x three
# cost haircuts = 45 pooled configurations. Horizons are the EVAL-184 bases
# {60, 300}s plus one 60s bar on each side where positive: 60-60=0 is omitted.
BASE_HORIZONS_SECONDS: Tuple[float, ...] = (60.0, 300.0)
HORIZON_STEP_SECONDS = 60.0
HORIZON_GRID_SECONDS: Tuple[float, ...] = (60.0, 120.0, 240.0, 300.0, 360.0)
COST_HAIRCUTS: Tuple[float, ...] = (0.5, 1.0, 2.0)
GRID_CONFIG_COUNT = len(SURFACE_GO_CELLS) * len(HORIZON_GRID_SECONDS) * len(COST_HAIRCUTS)

# The runner that performs the heavy computation (built by the next session; this
# gate refuses to seal until it is present AND green).
RUNNER_REL = "scripts/eval185_surface_traded_robustness_oos.py"

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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-185 artifact exists with a stamp
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


def capture_inventory(capture_dir: Path) -> Dict[str, Any]:
    """Return the BTC/ETH three_way capture files under capture_dir (no I/O beyond
    a directory listing)."""
    d = Path(capture_dir)
    btc = sorted(p.name for p in d.glob("three_way_BTC_*.json")) if d.is_dir() else []
    eth = sorted(p.name for p in d.glob("three_way_ETH_*.json")) if d.is_dir() else []
    return {"btc": btc, "eth": eth, "present": bool(btc and eth), "dir": str(d)}


def _child_env() -> Dict[str, str]:
    """Environment for runner subprocesses: prepend ``.venv-deps`` to PYTHONPATH so
    numpy/pandas/scipy resolve on a fresh checkout (deps are gitignored, not vendored
    in ``src/``). Without this the runner subprocess raises ModuleNotFoundError and
    every ``--execute`` fails at the dry-run step."""
    env = dict(os.environ)
    deps_dir = str(ROOT / ".venv-deps")
    env["PYTHONPATH"] = deps_dir + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def runner_present_and_green(*, capture_dir: Path, runner_rel: str = RUNNER_REL) -> Dict[str, Any]:
    """Return whether the EVAL-185 runner exists and passes its --no-write dry run."""
    runner = ROOT / runner_rel
    if not runner.is_file():
        return {"runner_present": False, "runner_green": False,
                "runner": str(runner), "reason": "runner_missing"}
    cmd = [sys.executable, str(runner), "--capture-dir", str(capture_dir), "--no-write"]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                              env=_child_env())
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
        return "WAIT_CAPTURE"
    if not runner_green:
        return "WAIT_RUNNER"
    return "DUE"


def disjointness_math(now: datetime, *, capture_dir: Path = CAPTURE_DIR) -> Dict[str, Any]:
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
    proc = subprocess.run(list(cmd), cwd=str(cwd), capture_output=True, text=True,
                          env=_child_env())
    return proc.returncode, (proc.stdout + proc.stderr)


def execute_phaseb(
    *,
    capture_dir: Path = CAPTURE_DIR,
    research_state_dir: Path = RS_DIR,
    task_id: str = TASK_ID,
    runner_rel: str = RUNNER_REL,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)

    inv = capture_inventory(capture_dir)
    if not inv["present"]:
        return {
            "ok": False,
            "step": "capture",
            "reason": "missing_capture",
            "detail": f"expected floor-compliant disjoint surface capture at {capture_dir} "
                      "with three_way_BTC_*.json and three_way_ETH_*.json",
            "disjointness": disjointness_math(now, capture_dir=capture_dir),
        }
    if now.timestamp() < threshold_epoch():
        return {
            "ok": False,
            "step": "threshold",
            "reason": "before_threshold",
            "detail": "refusing to run before the disjointness threshold "
                      f"{THRESHOLD_ISO}",
            "disjointness": disjointness_math(now, capture_dir=capture_dir),
        }

    steps: List[Dict[str, Any]] = []
    steps.append({"step": "capture", "status": "ok", "files": inv["btc"] + inv["eth"]})

    green = runner_present_and_green(capture_dir=capture_dir, runner_rel=runner_rel)
    steps.append({"step": "runner_green", "status": "ok" if green.get("runner_green") else "failed",
                  "runner_present": green.get("runner_present"),
                  "returncode": green.get("returncode"),
                  "tail": green.get("tail")})
    if not green.get("runner_green"):
        return {"ok": False, "step": "runner_green", "steps": steps,
                "detail": "EVAL-185 runner is missing or its --no-write dry-run failed "
                          "(see step tail); build/fix it before sealing"}

    rc, out = _run([
        sys.executable, str(ROOT / runner_rel),
        "--capture-dir", str(capture_dir),
        "--seal", "--task-label", TASK_LABEL,
    ])
    steps.append({"step": "seal", "status": "ok" if rc == 0 else "failed",
                  "rc": rc, "tail": out[-2000:]})
    if rc != 0:
        return {"ok": False, "step": "seal", "steps": steps, "detail": "seal failed"}

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
        "base_horizons_seconds": [float(b) for b in BASE_HORIZONS_SECONDS],
        "horizon_step_seconds": float(HORIZON_STEP_SECONDS),
        "horizon_grid_seconds": [float(b) for b in HORIZON_GRID_SECONDS],
        "cost_haircuts": [float(c) for c in COST_HAIRCUTS],
        "grid_config_count": int(GRID_CONFIG_COUNT),
        "runner": RUNNER_REL,
    }


def _emit(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-185 Phase-B gate: deterministic, idempotent completion "
                    "arbiter (SEALED / WAIT_CAPTURE / WAIT_RUNNER / DUE / FAILED)."
    )
    ap.add_argument("--execute", action="store_true",
                    help="once a floor-compliant disjoint surface capture exists AND the "
                         "EVAL-185 runner is green, run the surface-line robustness grid on "
                         "the capture -> seal -> seal-gate and require seal-gate exit 0")
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
    # Efficiency: once SEALED, skip the heavy runner --no-write (minutes on the large
    # capture) — the seal is already proven by the artifact + seal-gate below.
    green = ({"runner_present": None, "runner_green": False, "runner": args.runner,
              "reason": "skipped_already_sealed"}
             if sealed["sealed"] else
             runner_present_and_green(capture_dir=cap, runner_rel=args.runner))
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
            "note": "EVAL-185 campaign complete; idempotent no-op. Do not re-run.",
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
                        "capture with scripts/eval60_acquire_three_way.py --underlying BTC "
                        "--underlying ETH --days 3.7 --end <at/after the earliest disjoint "
                        f"end> --out-dir {cap} --seal, then verify the EVAL-64 floor "
                        "(never weaken it).",
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
            "contract": "A floor-compliant disjoint capture exists but the EVAL-185 "
                        "surface-line traded-form robustness runner is missing or not "
                        "green. BUILD-ONLY HEAVY WORK: implement "
                         f"{RUNNER_REL} (the EVAL-184 runner + a PRE-REGISTERED cost x "
                         "horizon grid: 3 signals x horizons {60,120,240,300,360}s "
                         "(EVAL-184 bases {60,300}s +/- one 60s bar, dropping nonpositive) "
                         "x cost haircuts {0.5x,1x,2x} = 45 configs; scale both hedge fees "
                         "and real spreads by the haircut; pooled BH-FDR across the FULL "
                         "grid; both-asset GO bar; EVAL-64 floor verbatim; never weaken), "
                         "add its prereg + tests, and make the runner --no-write dry-run "
                         "pass. Then re-run this gate with --execute.",
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
            "contract": "HEAVY WORK REQUIRED. Re-run with --execute to run the "
                        "surface-line robustness grid on the disjoint capture -> seal -> "
                        "seal-gate and require seal-gate exit 0.",
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