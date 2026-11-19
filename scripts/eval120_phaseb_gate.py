#!/usr/bin/env python3
"""EVAL-120 Phase-B gate: the single, deterministic, idempotent arbiter of the
EVAL-120 campaign's completion contract.

EVAL-120: cross-sectional term-ratio basis (ETH - BTC) -> forward relative
realized return skewness spread predictiveness (Spearman rank IC).
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
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402

# Authoritative pre-registered identifiers (parseable by check_session_sealed.py).
TASK_ID = "INIT-2026-11-19T06:10:00Z-EVAL120-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-RETURN-SKEWNESS-SPREAD"
TASK_LABEL = "EVAL120-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-RETURN-SKEWNESS-SPREAD"
PREREG_GLOB = "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION_*"
COMBINED_GLOB = "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED_*"
BLOCKED_GLOB = "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED_*"

# Exit codes
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
    """Return whether a COMBINED_*/BLOCKED_* EVAL-120 artifact exists with a stamp
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
    """Invoke the authoritative seal-gate for EVAL-120."""
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
REPORT_ID = "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED"
PREREG_ID = "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION"
BLOCKED_ID = "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED"

FLOOR: Dict[str, Any] = e77.FLOOR

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

REQUIRED_FLOOR_KEYS: Tuple[str, ...] = (
    "min_underlyings", "min_aligned_common_bars", "min_usable_pairs_per_config", "note",
)

EXPECTED_BASELINE = "BTC"
EXPECTED_RELATIVE = "ETH"

PREREG_FLOOR_TS = "2026-11-19T06:10:00Z"


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

        if proto.get("term_signals") != ["term_ratio"]:
            errors.append(f"PREREG: term_signals must be ['term_ratio'], got {proto.get('term_signals')}")

        if proto.get("bar_seconds_grid") != [60.0, 300.0]:
            errors.append(f"PREREG: bar_seconds_grid mismatch: {proto.get('bar_seconds_grid')}")
        if proto.get("forward_horizons_bars") != [6, 24, 72]:
            errors.append(f"PREREG: forward_horizons_bars mismatch: {proto.get('forward_horizons_bars')}")

        stats = proto.get("stats", {})
        if stats.get("permutation_perms") != 1000:
            errors.append(f"PREREG: permutation_perms mismatch: {stats.get('permutation_perms')}")
        if stats.get("bootstrap_resamples") != 1000:
            errors.append(f"PREREG: bootstrap_resamples mismatch: {stats.get('bootstrap_resamples')}")
        if stats.get("bootstrap_block") != 2:
            errors.append(f"PREREG: bootstrap_block mismatch: {stats.get('bootstrap_block')}")
        if stats.get("fdr_alpha") != 0.1:
            errors.append(f"PREREG: fdr_alpha mismatch: {stats.get('fdr_alpha')}")
        if stats.get("seed") != 42:
            errors.append(f"PREREG: seed mismatch: {stats.get('seed')}")
        if stats.get("zwindow") != 20:
            errors.append(f"PREREG: zwindow mismatch: {stats.get('zwindow')}")
        if stats.get("min_usable_pairs_per_config") != 120:
            errors.append(f"PREREG: min_usable_pairs_per_config mismatch: {stats.get('min_usable_pairs_per_config')}")

    floor = data.get("floor", {})
    for key in REQUIRED_FLOOR_KEYS:
        if key not in floor:
            errors.append(f"PREREG: floor missing required key '{key}'")

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
        if "aligned_ok" not in cf:
            errors.append("COMBINED: campaign_floor missing aligned_ok")
        if "ok" not in cf:
            errors.append("COMBINED: campaign_floor missing ok")

    per_config = data.get("per_config", [])
    if not isinstance(per_config, list) or len(per_config) != 6:
        errors.append(f"COMBINED: expected 6 configs (1 signal x 2 grids x 3 horizons), got {len(per_config)}")
    else:
        for i, c in enumerate(per_config):
            if not isinstance(c, dict):
                errors.append(f"COMBINED: config {i} is not a dict")
                continue
            for key in ("signal", "bar_seconds", "horizon_bars", "n_pairs", "pass"):
                if key not in c:
                    errors.append(f"COMBINED: config {i} missing key '{key}'")
            if c.get("signal") != "term_ratio":
                errors.append(f"COMBINED: config {i} signal must be 'term_ratio', got {c.get('signal')}")

    summary = data.get("summary", {})
    for key in ("n_configs", "n_pass", "pass_configs", "best_ic", "best_config"):
        if key not in summary:
            errors.append(f"COMBINED: summary missing key '{key}'")

    pooled = data.get("pooled", {})
    for key in ("bh_fdr", "any_config_pass", "campaign_state"):
        if key not in pooled:
            errors.append(f"COMBINED: pooled missing key '{key}'")

    cs = pooled.get("campaign_state", "")
    if cs not in (
        "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD",
        "EVAL_120_BLOCKED_FLOOR",
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
def execute_phaseb(*, research_state_dir: Path = RS_DIR) -> Dict[str, Any]:
    """Run the verification then the authoritative seal-gate."""
    steps: List[Dict[str, Any]] = []

    ok, errors = run_verification()
    steps.append({"step": "verification", "ok": ok, "errors": errors})
    if not ok:
        return {"ok": False, "step": "verification", "steps": steps}

    sg_rc, sg_out = run_seal_gate_check(research_state_dir=research_state_dir)
    steps.append({"step": "seal_gate", "rc": sg_rc, "tail": sg_out[-4000:]})
    return {
        "ok": sg_rc == 0,
        "step": "seal_gate",
        "steps": steps,
    }


# ---------------------------------------------------------------------------
# Main arbiter
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-120 phase-B gate (SEALED/DUE/FAILED; deterministic, idempotent)"
    )
    ap.add_argument("--execute", action="store_true",
                    help="run EVAL-120 verification + the authoritative seal-gate (unskippable)")
    ap.add_argument("--research-state-dir", default=str(RS_DIR))
    args = ap.parse_args(argv)

    rs_dir = Path(args.research_state_dir)

    seal = detect_seal(rs_dir)

    if seal.get("sealed"):
        sg_rc, sg_out = run_seal_gate_check(research_state_dir=rs_dir)
        payload = {
            "phase": "SEALED",
            "exit_code": EXIT_SEALED,
            "seal_gate_rc": sg_rc,
            "artifacts": seal.get("artifacts", []),
            "seal_gate_tail": sg_out[-2000:],
            "note": "EVAL-120 campaign complete; idempotent no-op. Do not re-run.",
        }
        print(json.dumps(payload, indent=2))
        return EXIT_SEALED

    if not args.execute:
        payload = {
            "phase": "DUE",
            "exit_code": EXIT_DUE,
            "readiness": {
                "runnable_now": True,
                "task_id": TASK_ID,
                "task_label": TASK_LABEL,
            },
            "note": (
                "EVAL-120 is runnable now on the on-disk real captures but has not "
                "been sealed. Heavy work is REQUIRED. Re-run with: "
                "python3 scripts/eval120_phaseb_gate.py --execute"
            ),
        }
        print(json.dumps(payload, indent=2))
        return EXIT_DUE

    result = execute_phaseb(research_state_dir=rs_dir)
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
        "note": "EVAL-120 execute path did not produce a passing seal-gate. Fix and rerun.",
    }
    print(json.dumps(payload, indent=2))
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())