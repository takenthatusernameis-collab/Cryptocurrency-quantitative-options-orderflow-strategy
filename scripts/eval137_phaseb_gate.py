#!/usr/bin/env python3
"""EVAL-137 Phase-B gate: the single, deterministic, idempotent arbiter of the
EVAL-137 campaign's completion contract.

Why this exists
---------------
EVAL-125 sealed the cross-sectional ``term_ratio`` basis (term_ratio_ETH -
term_ratio_BTC) -> forward relative realized return kurtosis spread as its
strongest surviving unmonetized GO (IC 0.4128, 2 pooled BH-FDR rejections) —
predictiveness only, no traded-form claim. EVAL-137 asks the monetization
question: does the cross-sectional term-ratio basis z-score timed a signal-timed
cross-sectional relative-value delta-hedged ATM straddle spread (long the
cheap-term leg, short the rich-term leg) yield a positive net-of-cost mean on
the real on-disk captures at the sealed EVAL-64 feasible floor?
EVAL-137 measures exactly that on the already-acquired real on-disk captures
(no acquisition, no network), so it is runnable **now**.

EVAL-137 reuses the sealed EVAL-61/62/64/71/74/77/80/125 inference, the
EVAL-80 relative-value straddle-spread trade construction, the EVAL-62
mark-path net-of-cost P&L + permutation/bootstrap inference, and the sealed
EVAL-64 feasible floor verbatim; it does not re-litigate EVAL-64, EVAL-80,
EVAL-125, or any sealed campaign.

Outcomes (exit codes)
---------------------
  0   SEALED   — a COMBINED_*/BLOCKED_* EVAL-137 artifact already exists with a
                  stamp >= the pre-registered task id; the seal-gate passes.
                  COMPLETE; idempotent no-op (safe to re-run forever).
  20  DUE      — nothing sealed yet and this was a status check only (no
                  --execute). The heavy work is REQUIRED now (data is on disk):
                  re-run with --execute.
  1   FAILED   --execute was requested but the run -> seal -> seal-gate pipeline
                  did not produce a passing seal-gate exit 0. Fix and re-run.

Unlike EVAL-67/68/69 there is no NOT_DUE phase: the EVAL-137 inputs are on disk,
so the honest pre-execution state is DUE (heavy work required), never a physics
wait.

``--execute`` is the unskippable path: it runs
``eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py --seal``
then the authoritative seal-gate, and refuses to exit 0 unless the seal-gate
exits 0.

Nothing here weakens the EVAL-64 floor (EVAL-137 reuses it verbatim via
e64._underlying_floor_strict), uses synthetic data, enables live trading, or
edits sealed EVAL-02..62/64..66/70..136 artifacts or src/ (EVAL-137 is appended
here). It is append-only and reuses the sealed EVAL-61/62/64/71/74/77/80/125
runners.
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

import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402

# Authoritative pre-registered identifiers (parseable by check_session_sealed.py).
# Task id timestamp is the session start time (never a projected future time;
# see durable_handoff bottleneck #9: TASK_ID ISO stamp must be <= artifact stamp).
TASK_ID = "INIT-2026-11-20T07:08:01Z-EVAL137-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VALUE-STRADDLE-SPREAD-NET-OF-COST"
TASK_LABEL = "EVAL137-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VALUE-STRADDLE-SPREAD-NET-OF-COST"
PREREG_GLOB = "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_COMBINED_*"
BLOCKED_GLOB = "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_BLOCKED_*"

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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-137 artifact exists with a stamp
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


CAPTURE_DIR = ROOT / "data" / "raw" / "eval61"


def capture_ready(capture_dir: Path = CAPTURE_DIR) -> Dict[str, Any]:
    """Report whether the EVAL-137 capture directory holds both-asset three-way captures."""
    p = Path(capture_dir)
    btc = sorted(p.glob("three_way_BTC_*.json")) if p.is_dir() else []
    eth = sorted(p.glob("three_way_ETH_*.json")) if p.is_dir() else []
    return {
        "present": bool(btc and eth),
        "btc": [x.name for x in btc],
        "eth": [x.name for x in eth],
        "capture_dir": str(p),
    }


def run_seal_gate_check(*, research_state_dir: Path = RS_DIR) -> Tuple[int, str]:
    """Invoke the authoritative seal-gate for EVAL-137."""
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


# ---------------------------------------------------------------------------
# Verification logic (extracted from original gate)
# ---------------------------------------------------------------------------
REPORT_ID = "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_COMBINED"
PREREG_ID = "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_PREREGISTRATION"
BLOCKED_ID = "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_BLOCKED"

REQUIRED_COMBINED_FIELDS: Tuple[str, ...] = (
    "report_id", "generated_at", "task", "verdict", "verdict_detail",
    "floor_ok", "capture_dir", "underlyings", "floor", "campaign_floor",
    "protocol", "per_config", "summary", "pooled", "errors",
)

REQUIRED_PREREG_FIELDS: Tuple[str, ...] = (
    "prereg_id", "generated_at", "task", "hypothesis", "extends",
    "protocol", "capture_dir", "floor",
)

REQUIRED_BLOCKED_FIELDS: Tuple[str, ...] = (
    "report_id", "generated_at", "task", "verdict", "verdict_detail",
    "floor_ok", "capture_dir", "underlyings", "floor", "campaign_floor", "errors",
)

ALLOWED_VERDICTS = ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)", "BLOCKED")

EXPECTED_BASELINE = "BTC"
EXPECTED_RELATIVE = "ETH"

PREREG_FLOOR_TS = "2026-11-20T07:08:01Z"

REQUIRED_FLOOR_KEYS: Tuple[str, ...] = (
    "min_underlyings", "min_surface_snapshots_per_underlying",
    "min_surface_instruments_per_underlying", "min_surface_bars_5m_per_underlying",
    "min_option_trades_per_underlying", "min_of_instruments_per_underlying",
    "min_of_span_seconds_per_underlying", "min_of_bars_5m_per_underlying",
    "min_perp_bars_5m_per_underlying", "min_perp_span_seconds_per_underlying",
    "min_common_bars_per_underlying", "note",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _find_artifact(pattern: str) -> Optional[Path]:
    matches = list(ROOT.glob(f"research_state/{pattern}"))
    if not matches:
        return None
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0]


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _verify_prereg(prereg_path: Path) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    data = _load_json(prereg_path)
    if data is None:
        errors.append(f"PREREG: invalid JSON or unreadable: {prereg_path}")
        return False, errors

    for field in REQUIRED_PREREG_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"PREREG: missing required field '{field}'")

    if data.get("prereg_id") != PREREG_ID:
        errors.append(f"PREREG: prereg_id mismatch: expected {PREREG_ID}, got {data.get('prereg_id')}")

    hyp = data.get("hypothesis", "")
    if not hyp or len(hyp) < 50:
        errors.append("PREREG: hypothesis missing or too short")

    proto = data.get("protocol", {})
    if not proto:
        errors.append("PREREG: protocol missing or empty")
    else:
        cs = proto.get("cross_section", {})
        if cs.get("baseline") != EXPECTED_BASELINE:
            errors.append(f"PREREG: cross_section.baseline must be '{EXPECTED_BASELINE}', got {cs.get('baseline')}")
        if cs.get("relative") != EXPECTED_RELATIVE:
            errors.append(f"PREREG: cross_section.relative must be '{EXPECTED_RELATIVE}', got {cs.get('relative')}")
        if "term_ratio" not in cs.get("relative_signal", ""):
            errors.append("PREREG: cross_section.relative_signal must reference term_ratio")

        if proto.get("basis_signals") != ["term_ratio"]:
            errors.append(f"PREREG: basis_signals must be ['term_ratio'], got {proto.get('basis_signals')}")
        if proto.get("bar_seconds_grid") != [60.0, 300.0]:
            errors.append(f"PREREG: bar_seconds_grid mismatch: {proto.get('bar_seconds_grid')}")

        stats = proto.get("stats", {})
        if stats.get("permutation_perms") != e62.PERMUTATION_PERMS:
            errors.append(f"PREREG: permutation_perms mismatch: {stats.get('permutation_perms')}")
        if stats.get("bootstrap_resamples") != e62.BOOTSTRAP_RESAMPLES:
            errors.append(f"PREREG: bootstrap_resamples mismatch: {stats.get('bootstrap_resamples')}")
        if stats.get("bootstrap_block") != e62.BOOTSTRAP_BLOCK:
            errors.append(f"PREREG: bootstrap_block mismatch: {stats.get('bootstrap_block')}")
        if stats.get("fdr_alpha") != e62.FDR_ALPHA:
            errors.append(f"PREREG: fdr_alpha mismatch: {stats.get('fdr_alpha')}")
        if stats.get("seed") != e62.SEED:
            errors.append(f"PREREG: seed mismatch: {stats.get('seed')}")
        if proto.get("zwindow") != e62.ZWINDOW:
            errors.append(f"PREREG: zwindow mismatch: {proto.get('zwindow')}")
        if stats.get("min_states_per_config") != 100:
            errors.append(f"PREREG: min_states_per_config mismatch: {stats.get('min_states_per_config')}")

    floor = data.get("floor", {})
    for key in REQUIRED_FLOOR_KEYS:
        if key not in floor:
            errors.append(f"PREREG: floor missing required key '{key}'")
    note = floor.get("note", "")
    if "EVAL-64" not in note or "NOT weakened" not in note:
        errors.append("PREREG: floor note must identify the sealed EVAL-64 floor verbatim, NOT weakened")

    gen_ts = data.get("generated_at", "")
    if gen_ts and gen_ts < PREREG_FLOOR_TS:
        errors.append(f"PREREG: generated_at {gen_ts} is before pre-registration floor {PREREG_FLOOR_TS}")

    return len(errors) == 0, errors


def _verify_combined(combined_path: Path) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    data = _load_json(combined_path)
    if data is None:
        errors.append(f"COMBINED: invalid JSON or unreadable: {combined_path}")
        return False, errors

    for field in REQUIRED_COMBINED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"COMBINED: missing required field '{field}'")

    if data.get("report_id") != REPORT_ID:
        errors.append(f"COMBINED: report_id mismatch: expected {REPORT_ID}, got {data.get('report_id')}")

    verdict = data.get("verdict")
    if verdict not in ALLOWED_VERDICTS:
        errors.append(f"COMBINED: invalid verdict '{verdict}'; allowed: {ALLOWED_VERDICTS}")

    floor_ok = data.get("floor_ok")
    if not isinstance(floor_ok, bool):
        errors.append(f"COMBINED: floor_ok must be bool, got {type(floor_ok)}")

    underlyings = data.get("underlyings", [])
    if not isinstance(underlyings, list) or len(underlyings) != 2:
        errors.append(f"COMBINED: underlyings must be a list of 2, got {underlyings}")
    else:
        if "BTC" not in underlyings:
            errors.append("COMBINED: underlyings must include 'BTC'")
        if "ETH" not in underlyings:
            errors.append("COMBINED: underlyings must include 'ETH'")

    cf = data.get("campaign_floor", {})
    if not cf:
        errors.append("COMBINED: campaign_floor missing or empty")
    else:
        if "underlyings_ok" not in cf:
            errors.append("COMBINED: campaign_floor missing underlyings_ok")
        if "ok" not in cf:
            errors.append("COMBINED: campaign_floor missing ok")

    per_config = data.get("per_config", [])
    if not isinstance(per_config, list) or len(per_config) != 2:
        errors.append(f"COMBINED: expected 2 configs (1 signal x 2 grids), got {len(per_config)}")
    else:
        for i, c in enumerate(per_config):
            if not isinstance(c, dict):
                errors.append(f"COMBINED: config {i} is not a dict")
                continue
            for key in ("signal", "bar_seconds", "n_returns", "pass"):
                if key not in c:
                    errors.append(f"COMBINED: config {i} missing key '{key}'")
            if c.get("signal") != "term_ratio":
                errors.append(f"COMBINED: config {i} signal must be 'term_ratio', got {c.get('signal')}")

    summary = data.get("summary", {})
    for key in ("n_configs", "n_pass", "pass_configs", "best_mean_return", "best_config"):
        if key not in summary:
            errors.append(f"COMBINED: summary missing key '{key}'")

    pooled = data.get("pooled", {})
    for key in ("bh_fdr", "any_config_pass", "campaign_state"):
        if key not in pooled:
            errors.append(f"COMBINED: pooled missing key '{key}'")

    cs = pooled.get("campaign_state", "")
    if cs not in (
        "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST",
        "EVAL_137_BLOCKED_FLOOR",
    ):
        errors.append(f"COMBINED: unexpected campaign_state '{cs}'")

    if not floor_ok and verdict != "BLOCKED":
        errors.append(f"COMBINED: floor_ok is False but verdict is '{verdict}' (must be BLOCKED)")

    if floor_ok and verdict == "BLOCKED":
        errors.append(f"COMBINED: floor_ok is True but verdict is BLOCKED")

    return len(errors) == 0, errors


def _verify_blocked(blocked_path: Path) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    data = _load_json(blocked_path)
    if data is None:
        errors.append(f"BLOCKED: invalid JSON or unreadable: {blocked_path}")
        return False, errors

    for field in REQUIRED_BLOCKED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"BLOCKED: missing required field '{field}'")

    if data.get("report_id") != BLOCKED_ID:
        errors.append(f"BLOCKED: report_id mismatch: expected {BLOCKED_ID}, got {data.get('report_id')}")

    if data.get("verdict") != "BLOCKED":
        errors.append(f"BLOCKED: verdict must be 'BLOCKED', got {data.get('verdict')}")

    if data.get("floor_ok") is not False:
        errors.append(f"BLOCKED: floor_ok must be False, got {data.get('floor_ok')}")

    return len(errors) == 0, errors


def run_verification() -> Tuple[bool, List[str]]:
    """Run the verification logic. Returns (ok, errors)."""
    all_errors: List[str] = []

    prereg_path = _find_artifact(f"{PREREG_ID}*.json")
    combined_path = _find_artifact(f"{REPORT_ID}*.json")
    blocked_path = _find_artifact(f"{BLOCKED_ID}*.json")

    if not prereg_path:
        all_errors.append(f"PREREG artifact not found (pattern: {PREREG_ID}*.json)")
        return False, all_errors
    if not combined_path and not blocked_path:
        all_errors.append(f"Neither COMBINED ({REPORT_ID}*.json) nor BLOCKED ({BLOCKED_ID}*.json) artifact found")
        return False, all_errors

    ok, errs = _verify_prereg(prereg_path)
    if not ok:
        all_errors.extend(errs)

    if combined_path:
        ok, errs = _verify_combined(combined_path)
        if not ok:
            all_errors.extend(errs)
    if blocked_path:
        ok, errs = _verify_blocked(blocked_path)
        if not ok:
            all_errors.extend(errs)

    if combined_path and blocked_path:
        all_errors.append("Both COMBINED and BLOCKED artifacts exist — only one should be present")

    return len(all_errors) == 0, all_errors


# ---------------------------------------------------------------------------
# Execute path
# ---------------------------------------------------------------------------
def execute_phaseb(
    *,
    capture_dir: Path = CAPTURE_DIR,
    research_state_dir: Path = RS_DIR,
) -> Dict[str, Any]:
    """Run the heavy work (runner --seal) then the verification + authoritative
    seal-gate. Returns a structured result with ok=True only if the seal-gate
    exits 0."""
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
        str(ROOT / "scripts" / "eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py"),
        "--capture-dir",
        str(capture_dir),
        "--seal",
        "--task-label",
        TASK_LABEL,
    ])
    steps.append({"step": "run_and_seal", "rc": rc, "tail": out[-4000:]})
    if rc != 0:
        return {"ok": False, "step": "run_and_seal", "steps": steps, "capture": cap}

    ok, errors = run_verification()
    steps.append({"step": "verification", "ok": ok, "errors": errors})
    if not ok:
        return {"ok": False, "step": "verification", "steps": steps, "capture": cap}

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
        description="EVAL-137 phase-B gate (SEALED/DUE/FAILED; deterministic, idempotent)"
    )
    ap.add_argument("--execute", action="store_true",
                    help="run EVAL-137 --seal + verification + the authoritative seal-gate (unskippable)")
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
            "note": "EVAL-137 campaign complete; idempotent no-op. Do not re-run.",
        }
        print(json.dumps(payload, indent=2))
        return EXIT_SEALED

    if not args.execute:
        payload = {
            "phase": "DUE",
            "exit_code": EXIT_DUE,
            "readiness": readiness,
            "note": (
                "EVAL-137 is runnable now on the on-disk real captures but has not "
                "been sealed. Heavy work is REQUIRED. Re-run with: "
                "python3 scripts/eval137_phaseb_gate.py --execute"
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
        "note": "EVAL-137 execute path did not produce a passing seal-gate. Fix and rerun.",
    }
    print(json.dumps(payload, indent=2))
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
