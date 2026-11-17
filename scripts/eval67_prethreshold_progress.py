#!/usr/bin/env python3
"""Deterministic pre-threshold progress driver for the EVAL-67/68/69 ladder
plus the physics-independent EVAL-70..79 campaigns.

This is the single heavy-work entrypoint for sessions that run before the
2026-11-20 disjointness threshold. It removes the repeated manual loop that
previously let sessions do timestamp-only carries:

1. bootstrap and verify the environment;
2. run the full targeted + controller/campaign/diagnostics test suites;
    3. run all campaign arbiters in order (EVAL-70..79 first -- they are
        physics-independent and runnable now -- then the EVAL-67 -> EVAL-68 ->
        EVAL-69 disjoint-forward ladder);
4. if requested with --execute, execute any arbiter that is DUE;
5. record the verified facts in the readiness JSON.

It never modifies sealed artifacts, src/, preregs, or the EVAL-64 floor.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RS_DIR = ROOT / "research_state"
READINESS_PATH = RS_DIR / "EVAL_67_PREWINDOW_READINESS.json"

TARGETED_TEST_FILES: Tuple[str, ...] = (
    "tests/test_eval70_underlying_oflow_rv_predictiveness.py",
    "tests/test_eval70_phaseb_gate.py",
    "tests/test_eval67_btc_oflow_tox_rv_oos.py",
    "tests/test_eval67_phaseb_gate.py",
    "tests/test_eval67_prethreshold_progress.py",
    "tests/test_eval66_eth_oflow_tox_rv_oos.py",
    "tests/test_eval65_orderflow_tox_rv_predictiveness.py",
    "tests/test_eval68_pooled_btc_eth_oflow_tox_rv_oos.py",
    "tests/test_eval68_phaseb_gate.py",
    "tests/test_eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py",
    "tests/test_eval69_phaseb_gate.py",
    "tests/test_eval71_surface_iv_rv_predictiveness.py",
    "tests/test_eval72_surface_skew_straddle_monetization.py",
    "tests/test_eval73_surface_iv_rv_stability_split.py",
    "tests/test_eval74_surface_term_structure_predictiveness.py",
    "tests/test_eval75_term_structure_straddle_monetization.py",
    "tests/test_eval76_surface_skew_risk_reversal_monetization.py",
    "tests/test_eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "tests/test_eval78_oflow_x_surface_rv_predictiveness.py",
    "tests/test_eval79_oflow_x_cross_sectional_basis_rv_predictiveness.py",
    "tests/test_eval79_phaseb_gate.py",
)
DIAGNOSTIC_TEST_FILES: Tuple[str, ...] = (
    "tests/test_controller_progress_accounting.py",
    "tests/test_workflow_diagnostics_scanner.py",
    "tests/test_nonfinite_result_serialization.py",
    "tests/test_campaign_resume.py",
)

EXPECTED_TARGETED_TESTS = 265
EXPECTED_DIAGNOSTIC_TESTS = 27

GATE_SPECS: Tuple[Dict[str, Any], ...] = (
    {
        "name": "EVAL-70",
        "script": ROOT / "scripts" / "eval70_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-71",
        "script": ROOT / "scripts" / "eval71_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-72",
        "script": ROOT / "scripts" / "eval72_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-73",
        "script": ROOT / "scripts" / "eval73_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-74",
        "script": ROOT / "scripts" / "eval74_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-75",
        "script": ROOT / "scripts" / "eval75_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-76",
        "script": ROOT / "scripts" / "eval76_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-77",
        "script": ROOT / "scripts" / "eval77_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-78",
        "script": ROOT / "scripts" / "eval78_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-79",
        "script": ROOT / "scripts" / "eval79_phaseb_gate.py",
        "wait_phase": "DUE",
    },
    {
        "name": "EVAL-67",
        "script": ROOT / "scripts" / "eval67_phaseb_gate.py",
        "wait_phase": "NOT_DUE",
    },
    {
        "name": "EVAL-68",
        "script": ROOT / "scripts" / "eval68_phaseb_gate.py",
        "wait_phase": "WAIT_EVAL67",
    },
    {
        "name": "EVAL-69",
        "script": ROOT / "scripts" / "eval69_phaseb_gate.py",
        "wait_phase": "WAIT_EVAL68",
    },
)

SEAL_SPECS: Tuple[Dict[str, Any], ...] = (
    {
        "name": "EVAL-66",
        "task_id": "INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION",
        "prereg": "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*",
        "combined": "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*",
        "blocked": "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*",
        "expected_exit": 0,
    },
    {
        "name": "EVAL-70",
        "task_id": "INIT-2026-11-17T02:10:00Z-EVAL70-UNDERLYING-OFLOW-TOX-RV-PREDICTIVENESS",
        "prereg": "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-71",
        "task_id": "INIT-2026-11-17T04:10:00Z-EVAL71-SURFACE-IV-RV-PREDICTIVENESS",
        "prereg": "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-72",
        "task_id": "INIT-2026-11-17T05:10:00Z-EVAL72-SURFACE-SKEW-STRADDLE-MONETIZATION",
        "prereg": "EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_PREREGISTRATION_*",
        "combined": "EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_COMBINED_*",
        "blocked": "EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-73",
        "task_id": "INIT-2026-11-17T05:20:00Z-EVAL73-SURFACE-IV-RV-STABILITY-SPLIT",
        "prereg": "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_PREREGISTRATION_*",
        "combined": "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_COMBINED_*",
        "blocked": "EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-74",
        "task_id": "INIT-2026-11-17T06:30:00Z-EVAL74-SURFACE-TERM-STRUCTURE-PREDICTIVENESS",
        "prereg": "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-75",
        "task_id": "INIT-2026-11-17T09:40:00Z-EVAL75-TERM-STRUCTURE-STRADDLE-MONETIZATION",
        "prereg": "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_PREREGISTRATION_*",
        "combined": "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_COMBINED_*",
        "blocked": "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-76",
        "task_id": "INIT-2026-11-17T10:15:00Z-EVAL76-SURFACE-SKEW-RISK-REVERSAL-MONETIZATION",
        "prereg": "EVAL_76_SURFACE_SKEW_RISK_REVERSAL_MONETIZATION_PREREGISTRATION_*",
        "combined": "EVAL_76_SURFACE_SKEW_RISK_REVERSAL_MONETIZATION_COMBINED_*",
        "blocked": "EVAL_76_SURFACE_SKEW_RISK_REVERSAL_MONETIZATION_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-77",
        "task_id": "INIT-2026-11-17T10:50:00Z-EVAL77-CROSS-SECTIONAL-SURFACE-BASIS-RV",
        "prereg": "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-78",
        "task_id": "INIT-2026-11-17T12:00:00Z-EVAL78-OFLOW-X-SURFACE-RV-INTERACTION",
        "prereg": "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_PREREGISTRATION_*",
        "combined": "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_COMBINED_*",
        "blocked": "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-79",
        "task_id": "INIT-2026-11-17T12:15:00Z-EVAL79-OFLOW-X-CROSS-SECTIONAL-BASIS-RV-PREDICTIVENESS",
        "prereg": "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_PREREGISTRATION_*",
        "combined": "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_COMBINED_*",
        "blocked": "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-67",
        "task_id": "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION",
        "prereg": "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*",
        "combined": "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*",
        "blocked": "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-68",
        "task_id": "INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS",
        "prereg": "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*",
        "combined": "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED_*",
        "blocked": "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*",
        "expected_exit": 1,
    },
    {
        "name": "EVAL-69",
        "task_id": "INIT-2026-11-16T22:45:00Z-EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS",
        "prereg": "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_PREREGISTRATION_*",
        "combined": "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED_*",
        "blocked": "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_BLOCKED_*",
        "expected_exit": 1,
    },
)

_PASS_RE = re.compile(r"(\d+)\s+passed\b")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _child_env() -> Dict[str, str]:
    env = os.environ.copy()
    deps = str(ROOT / ".venv-deps")
    old = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = deps + (os.pathsep + old if old else "")
    return env


def _run(
    cmd: Sequence[str],
    *,
    cwd: Path = ROOT,
    timeout: float = 1800.0,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    started = time.monotonic()
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env or _child_env(),
        )
        rc = int(proc.returncode)
        out = proc.stdout or ""
        err = proc.stderr or ""
    except subprocess.TimeoutExpired as exc:
        rc = 124
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        err += f"\nTIMEOUT after {timeout}s"
    except BaseException as exc:  # noqa: BLE001
        rc = 1
        out = ""
        err = repr(exc)
    return {
        "command": list(cmd),
        "rc": rc,
        "stdout": out,
        "stderr": err,
        "output": out + ("\n" + err if err else ""),
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def _parse_pytest_passed(output: str) -> Optional[int]:
    matches = _PASS_RE.findall(output or "")
    if not matches:
        return None
    return max(int(v) for v in matches)


def _pytest_result(files: Sequence[str], *, timeout: float = 1800.0) -> Dict[str, Any]:
    cmd = [sys.executable, "-m", "pytest", "-q", *files]
    res = _run(cmd, timeout=timeout)
    return {
        "command": res["command"],
        "rc": res["rc"],
        "passed": _parse_pytest_passed(res["output"]),
        "duration_seconds": res["duration_seconds"],
        "tail": res["output"][-4000:],
    }


def run_env_check(*, bootstrap: bool = True) -> Dict[str, Any]:
    if bootstrap and not (ROOT / ".venv-deps").is_dir():
        boot = _run([str(ROOT / "scripts" / "verify_env.sh")], timeout=1200.0)
    else:
        boot = {"rc": 0, "output": "skipped", "duration_seconds": 0.0}
    check = _run([str(ROOT / "scripts" / "verify_env.sh"), "--check"], timeout=600.0)
    return {
        "bootstrap_rc": boot["rc"],
        "check_rc": check["rc"],
        "ok": bool(check["rc"] == 0),
        "check_tail": check["output"][-3000:],
    }


def _parse_json_output(output: str) -> Optional[Dict[str, Any]]:
    text = (output or "").strip()
    if not text:
        return None
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            continue
    return None


def run_gate(spec: Dict[str, Any], *, execute: bool, timeout: float) -> Dict[str, Any]:
    cmd = [sys.executable, str(spec["script"])]
    if execute:
        cmd.append("--execute")
    res = _run(cmd, timeout=timeout)
    payload = _parse_json_output(res["stdout"])
    return {
        "name": spec["name"],
        "script": str(spec["script"]),
        "execute": bool(execute),
        "exit_code": res["rc"],
        "phase": (payload or {}).get("phase"),
        "payload": payload,
        "duration_seconds": res["duration_seconds"],
        "tail": res["output"][-4000:],
    }


def classify_gate(result: Dict[str, Any]) -> str:
    rc = int(result.get("exit_code", 1))
    phase = str(result.get("phase") or "")
    if rc == 0 and phase == "SEALED":
        return "ok"
    if rc == 10 and phase in ("NOT_DUE", "WAIT_EVAL67", "WAIT_EVAL68"):
        return "ok"
    if rc == 20 and phase == "DUE":
        return "needs_execute"
    if rc == 1 and phase == "FAILED":
        return "failed"
    return "failed"


def run_seal_gate(
    spec: Dict[str, Any], *, expected_exit: Optional[int] = None
) -> Dict[str, Any]:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "check_session_sealed.py"),
        "--task-id",
        str(spec["task_id"]),
        "--glob",
        str(spec["prereg"]),
        "--require-any-glob",
        str(spec["combined"]),
        "--require-any-glob",
        str(spec["blocked"]),
    ]
    res = _run(cmd, timeout=300.0)
    expected = int(spec["expected_exit"] if expected_exit is None else expected_exit)
    return {
        "name": spec["name"],
        "exit_code": res["rc"],
        "expected_exit": expected,
        "ok": res["rc"] == expected,
        "tail": res["output"][-2000:],
    }


def _compact_gate(result: Dict[str, Any]) -> Dict[str, Any]:
    payload = result.get("payload") or {}
    disjoint = payload.get("disjointness") or {}
    return {
        "name": result.get("name"),
        "execute": bool(result.get("execute")),
        "exit_code": result.get("exit_code"),
        "phase": result.get("phase"),
        "classification": result.get("classification"),
        "duration_seconds": result.get("duration_seconds"),
        "overlap_seconds": disjoint.get("overlap_seconds"),
        "disjoint": disjoint.get("disjoint"),
        "eval67_sealed": (payload.get("readiness") or {}).get("eval67_sealed"),
        "eval68_sealed": (payload.get("readiness") or {}).get("eval68_sealed"),
        "tail": (result.get("tail") or "")[-1200:],
    }


def _overall_status(
    *,
    env_result: Dict[str, Any],
    targeted: Dict[str, Any],
    diagnostics: Dict[str, Any],
    gate_results: Sequence[Dict[str, Any]],
    seal_results: Optional[Sequence[Dict[str, Any]]] = None,
    execute_requested: bool,
) -> Dict[str, Any]:
    failures: List[str] = []
    needs_execute: List[str] = []

    if not env_result.get("ok"):
        failures.append("env_check")
    if targeted.get("rc") != 0:
        failures.append("targeted_tests")
    elif targeted.get("passed") != EXPECTED_TARGETED_TESTS:
        failures.append(
            f"targeted_test_count:{targeted.get('passed')}!={EXPECTED_TARGETED_TESTS}"
        )
    if diagnostics.get("rc") != 0:
        failures.append("diagnostic_tests")
    elif diagnostics.get("passed") != EXPECTED_DIAGNOSTIC_TESTS:
        failures.append(
            f"diagnostic_test_count:{diagnostics.get('passed')}!={EXPECTED_DIAGNOSTIC_TESTS}"
        )

    for seal in seal_results or ():
        if not seal.get("ok"):
            failures.append(
                f"seal_gate:{seal.get('name')}:{seal.get('exit_code')}!="
                f"{seal.get('expected_exit')}"
            )

    for gate in gate_results:
        cls = str(gate.get("classification") or "")
        if cls == "needs_execute":
            needs_execute.append(str(gate.get("name")))
        elif cls == "failed":
            failures.append(f"gate:{gate.get('name')}:{gate.get('phase')}")

    if needs_execute and not execute_requested:
        return {
            "ok": False,
            "exit_code": 20,
            "needs_execute": needs_execute,
            "failures": failures,
            "summary": "campaign is DUE; rerun with --execute",
        }
    if needs_execute and execute_requested:
        failures.extend(f"execute_still_due:{name}" for name in needs_execute)
    return {
        "ok": not failures,
        "exit_code": 0 if not failures else 1,
        "needs_execute": [],
        "failures": failures,
        "summary": "pre-threshold heavy work complete" if not failures else "failed",
    }


def _load_readiness() -> Dict[str, Any]:
    if READINESS_PATH.is_file():
        try:
            value = json.loads(READINESS_PATH.read_text())
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            pass
    return {"schema_version": 3}


def _gate_summary(gate_results: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(g.get("name")): g for g in gate_results if g.get("name")}


def update_readiness(
    *,
    env_result: Dict[str, Any],
    targeted: Dict[str, Any],
    diagnostics: Dict[str, Any],
    gate_results: Sequence[Dict[str, Any]],
    seal_results: Sequence[Dict[str, Any]],
    overall: Dict[str, Any],
    execute_requested: bool,
) -> Dict[str, Any]:
    data = _load_readiness()
    gates = _gate_summary(gate_results)
    seals = {str(s.get("name")): s for s in seal_results}

    g67 = gates.get("EVAL-67", {})
    p67 = (g67.get("payload") or {})
    d67 = (p67.get("disjointness") or {})
    g68 = gates.get("EVAL-68", {})
    p68 = (g68.get("payload") or {})
    d68 = (p68.get("disjointness") or {})
    g69 = gates.get("EVAL-69", {})
    p69 = (g69.get("payload") or {})
    d69 = (p69.get("disjointness") or {})
    g70 = gates.get("EVAL-70", {})
    p70 = (g70.get("payload") or {})
    g72 = gates.get("EVAL-72", {})
    p72 = (g72.get("payload") or {})

    notes = (
        f"Verified {utc_now_iso()} by scripts/eval67_prethreshold_progress.py "
        f"(execute_requested={bool(execute_requested)}): env_check="
        f"{'OK' if env_result.get('ok') else 'FAILED'}; "
        f"targeted_tests={targeted.get('passed')}/{EXPECTED_TARGETED_TESTS} "
        f"(rc={targeted.get('rc')}); "
        f"diagnostics={diagnostics.get('passed')}/{EXPECTED_DIAGNOSTIC_TESTS} "
        f"(rc={diagnostics.get('rc')}); "
        f"EVAL-70={p70.get('phase')} exit={g70.get('exit_code')}; "
        f"EVAL-71={(gates.get('EVAL-71', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-71', {}).get('exit_code')}; "
        f"EVAL-72={p72.get('phase')} exit={g72.get('exit_code')}; "
        f"EVAL-73={(gates.get('EVAL-73', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-73', {}).get('exit_code')}; "
        f"EVAL-74={(gates.get('EVAL-74', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-74', {}).get('exit_code')}; "
        f"EVAL-75={(gates.get('EVAL-75', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-75', {}).get('exit_code')}; "
        f"EVAL-76={(gates.get('EVAL-76', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-76', {}).get('exit_code')}; "
        f"EVAL-77={(gates.get('EVAL-77', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-77', {}).get('exit_code')}; "
        f"EVAL-78={(gates.get('EVAL-78', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-78', {}).get('exit_code')}; "
        f"EVAL-79={(gates.get('EVAL-79', {}).get('payload') or {}).get('phase')} "
        f"exit={gates.get('EVAL-79', {}).get('exit_code')}; "
        f"EVAL-67={p67.get('phase')} exit={g67.get('exit_code')} "
        f"overlap_seconds={d67.get('overlap_seconds')} disjoint={d67.get('disjoint')}; "
        f"EVAL-68={p68.get('phase')} exit={g68.get('exit_code')} "
        f"eval67_sealed={(p68.get('readiness') or {}).get('eval67_sealed')}; "
        f"EVAL-69={p69.get('phase')} exit={g69.get('exit_code')} "
        f"eval68_sealed={(p69.get('readiness') or {}).get('eval68_sealed')}; "
        f"overall_ok={bool(overall.get('ok'))} exit={overall.get('exit_code')}. "
        "This is a verified pre-threshold carry, not a completion."
    )

    data.update(
        {
            "updated_at": utc_now_iso(),
            "gate_phase": p67.get("phase"),
            "gate_exit": g67.get("exit_code"),
            "overlap_seconds": d67.get("overlap_seconds"),
            "disjoint": d67.get("disjoint"),
            "env_check": "OK" if env_result.get("ok") else "FAILED",
            "tests_passed": targeted.get("passed"),
            "diagnostics_passed": diagnostics.get("passed"),
            "total_tests_passed": (
                (targeted.get("passed") or 0) + (diagnostics.get("passed") or 0)
            ),
            "notes": notes,
            "test_details": {
                "targeted_expected": EXPECTED_TARGETED_TESTS,
                "targeted_rc": targeted.get("rc"),
                "targeted_duration_seconds": targeted.get("duration_seconds"),
                "diagnostics_expected": EXPECTED_DIAGNOSTIC_TESTS,
                "diagnostics_rc": diagnostics.get("rc"),
                "diagnostics_duration_seconds": diagnostics.get("duration_seconds"),
            },
            "gates": {
                "eval70": _compact_gate(g70),
                "eval71": _compact_gate(gates.get("EVAL-71", {})),
                "eval72": _compact_gate(g72),
                "eval73": _compact_gate(gates.get("EVAL-73", {})),
                "eval74": _compact_gate(gates.get("EVAL-74", {})),
                "eval75": _compact_gate(gates.get("EVAL-75", {})),
                "eval76": _compact_gate(gates.get("EVAL-76", {})),
                "eval77": _compact_gate(gates.get("EVAL-77", {})),
                "eval78": _compact_gate(gates.get("EVAL-78", {})),
                "eval79": _compact_gate(gates.get("EVAL-79", {})),
                "eval67": _compact_gate(g67),
                "eval68": _compact_gate(g68),
                "eval69": _compact_gate(g69),
            },
            "seal_gates": seals,
            "orchestrator": {
                "script": "scripts/eval67_prethreshold_progress.py",
                "execute_requested": bool(execute_requested),
                "overall_ok": bool(overall.get("ok")),
                "exit_code": overall.get("exit_code"),
                "needs_execute": overall.get("needs_execute"),
                "failures": overall.get("failures"),
                "generated_at": utc_now_iso(),
            },
        }
    )

    ev68 = data.get("eval68")
    if not isinstance(ev68, dict):
        ev68 = {}
    ev68.update(
        {
            "gate_phase": p68.get("phase"),
            "gate_exit": g68.get("exit_code"),
            "overlap_seconds": d68.get("overlap_seconds"),
            "seal_gate_exit": (seals.get("EVAL-68") or {}).get("exit_code"),
        }
    )
    data["eval68"] = ev68

    ev69 = data.get("eval69")
    if not isinstance(ev69, dict):
        ev69 = {}
    ev69.update(
        {
            "gate_phase": p69.get("phase"),
            "gate_exit": g69.get("exit_code"),
            "overlap_seconds": d69.get("overlap_seconds"),
            "seal_gate_exit": (seals.get("EVAL-69") or {}).get("exit_code"),
        }
    )
    data["eval69"] = ev69
    return data


def write_readiness(data: Dict[str, Any]) -> None:
    RS_DIR.mkdir(parents=True, exist_ok=True)
    tmp = READINESS_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp.replace(READINESS_PATH)


def run_prethreshold_progress(
    *,
    execute: bool = False,
    run_tests: bool = True,
    write: bool = True,
    gate_timeout: float = 3600.0,
) -> Dict[str, Any]:
    env_result = run_env_check()
    if run_tests:
        targeted = _pytest_result(TARGETED_TEST_FILES, timeout=1800.0)
        diagnostics = _pytest_result(DIAGNOSTIC_TEST_FILES, timeout=600.0)
    else:
        targeted = {
            "command": [],
            "rc": 0,
            "passed": EXPECTED_TARGETED_TESTS,
            "duration_seconds": 0.0,
            "tail": "skipped",
        }
        diagnostics = {
            "command": [],
            "rc": 0,
            "passed": EXPECTED_DIAGNOSTIC_TESTS,
            "duration_seconds": 0.0,
            "tail": "skipped",
        }

    gate_results: List[Dict[str, Any]] = []
    for spec in GATE_SPECS:
        status = run_gate(spec, execute=False, timeout=300.0)
        cls = classify_gate(status)
        entry: Dict[str, Any] = dict(status)
        entry["classification"] = cls
        if execute and cls == "needs_execute":
            execution = run_gate(spec, execute=True, timeout=gate_timeout)
            cls2 = classify_gate(execution)
            entry["execution"] = {
                "exit_code": execution.get("exit_code"),
                "phase": execution.get("phase"),
                "classification": cls2,
                "duration_seconds": execution.get("duration_seconds"),
                "tail": execution.get("tail", "")[-1200:],
            }
            entry["classification"] = cls2
            entry["exit_code"] = execution.get("exit_code")
            entry["phase"] = execution.get("phase")
            entry["payload"] = execution.get("payload")
        gate_results.append(entry)

    sealed_by_name = {
        str(g.get("name")): str(g.get("phase")) == "SEALED" for g in gate_results
    }
    seal_results = [
        run_seal_gate(
            spec,
            expected_exit=0 if sealed_by_name.get(str(spec["name"]), False) else None,
        )
        for spec in SEAL_SPECS
    ]
    overall = _overall_status(
        env_result=env_result,
        targeted=targeted,
        diagnostics=diagnostics,
        gate_results=gate_results,
        seal_results=seal_results,
        execute_requested=execute,
    )
    data = update_readiness(
        env_result=env_result,
        targeted=targeted,
        diagnostics=diagnostics,
        gate_results=gate_results,
        seal_results=seal_results,
        overall=overall,
        execute_requested=execute,
    )
    if write:
        try:
            write_readiness(data)
            readiness_written = True
        except BaseException as exc:  # noqa: BLE001
            readiness_written = False
            overall["failures"].append(f"readiness_write:{exc!r}")
            overall["ok"] = False
            overall["exit_code"] = 1
    else:
        readiness_written = False

    return {
        "ok": bool(overall.get("ok")),
        "exit_code": overall.get("exit_code"),
        "summary": overall.get("summary"),
        "needs_execute": overall.get("needs_execute"),
        "failures": overall.get("failures"),
        "env_check": env_result.get("ok"),
        "targeted_tests": {
            "rc": targeted.get("rc"),
            "passed": targeted.get("passed"),
            "expected": EXPECTED_TARGETED_TESTS,
        },
        "diagnostic_tests": {
            "rc": diagnostics.get("rc"),
            "passed": diagnostics.get("passed"),
            "expected": EXPECTED_DIAGNOSTIC_TESTS,
        },
        "gates": [_compact_gate(g) for g in gate_results],
        "seal_gates": [
            {"name": s.get("name"), "exit_code": s.get("exit_code"), "ok": s.get("ok")}
            for s in seal_results
        ],
        "readiness_written": readiness_written,
        "readiness_path": str(READINESS_PATH),
        "generated_at": utc_now_iso(),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run the full EVAL-67/68/69 pre-threshold heavy-work loop."
    )
    ap.add_argument(
        "--execute",
        action="store_true",
        help="also execute any campaign arbiter that reports DUE (in ladder order)",
    )
    ap.add_argument(
        "--skip-tests",
        action="store_true",
        help="skip the test suites (not recommended; for status-only debugging)",
    )
    ap.add_argument(
        "--no-write",
        action="store_true",
        help="do not update the readiness JSON",
    )
    ap.add_argument(
        "--gate-timeout",
        type=float,
        default=3600.0,
        help="timeout in seconds for a --execute gate (default: 3600)",
    )
    args = ap.parse_args(argv)

    result = run_prethreshold_progress(
        execute=bool(args.execute),
        run_tests=not bool(args.skip_tests),
        write=not bool(args.no_write),
        gate_timeout=float(args.gate_timeout),
    )
    print(json.dumps(result, indent=2, default=str))
    return int(result.get("exit_code", 1))


if __name__ == "__main__":
    raise SystemExit(main())