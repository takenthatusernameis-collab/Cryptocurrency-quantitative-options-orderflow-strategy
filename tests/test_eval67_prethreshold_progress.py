from __future__ import annotations

import json
from pathlib import Path

import scripts.eval67_prethreshold_progress as progress


def _gate(name, exit_code, phase, *, classification=None):
    return {
        "name": name,
        "execute": False,
        "exit_code": exit_code,
        "phase": phase,
        "classification": classification or progress.classify_gate(
            {"exit_code": exit_code, "phase": phase}
        ),
        "duration_seconds": 0.1,
        "payload": {
            "phase": phase,
            "exit_code": exit_code,
            "disjointness": {"overlap_seconds": 1.0, "disjoint": False},
        },
        "tail": "ok",
    }


def _good_tests(count):
    return {"rc": 0, "passed": count, "duration_seconds": 0.1, "tail": "ok"}


def test_parse_pytest_passed_reads_summary():
    assert progress._parse_pytest_passed("124 passed in 242.54s") == 124
    assert progress._parse_pytest_passed("1 failed, 2 passed in 1s") == 2
    assert progress._parse_pytest_passed("no tests ran") is None


def test_classify_gate_maps_contract_exit_codes():
    assert progress.classify_gate({"exit_code": 0, "phase": "SEALED"}) == "ok"
    assert progress.classify_gate({"exit_code": 10, "phase": "NOT_DUE"}) == "ok"
    assert progress.classify_gate({"exit_code": 10, "phase": "WAIT_EVAL67"}) == "ok"
    assert progress.classify_gate({"exit_code": 10, "phase": "WAIT_EVAL68"}) == "ok"
    assert progress.classify_gate({"exit_code": 20, "phase": "DUE"}) == "needs_execute"
    assert progress.classify_gate({"exit_code": 1, "phase": "FAILED"}) == "failed"


def test_classify_unknown_gate_is_failure():
    assert progress.classify_gate({"exit_code": 7, "phase": "MATADOR"}) == "failed"
    assert progress.classify_gate({}) == "failed"


def test_overall_status_accepts_prethreshold_carry():
    gates = [
        _gate("EVAL-67", 10, "NOT_DUE"),
        _gate("EVAL-68", 10, "WAIT_EVAL67"),
        _gate("EVAL-69", 10, "WAIT_EVAL68"),
    ]
    overall = progress._overall_status(
        env_result={"ok": True},
        targeted=_good_tests(progress.EXPECTED_TARGETED_TESTS),
        diagnostics=_good_tests(progress.EXPECTED_DIAGNOSTIC_TESTS),
        gate_results=gates,
        execute_requested=False,
    )
    assert overall["ok"] is True
    assert overall["exit_code"] == 0
    assert overall["needs_execute"] == []


def test_overall_status_due_without_execute_requires_execute():
    gates = [
        _gate("EVAL-67", 20, "DUE"),
        _gate("EVAL-68", 10, "WAIT_EVAL67"),
        _gate("EVAL-69", 10, "WAIT_EVAL68"),
    ]
    overall = progress._overall_status(
        env_result={"ok": True},
        targeted=_good_tests(progress.EXPECTED_TARGETED_TESTS),
        diagnostics=_good_tests(progress.EXPECTED_DIAGNOSTIC_TESTS),
        gate_results=gates,
        execute_requested=False,
    )
    assert overall["ok"] is False
    assert overall["exit_code"] == 20
    assert overall["needs_execute"] == ["EVAL-67"]


def test_overall_status_failed_gate_is_failure():
    gates = [
        _gate("EVAL-67", 1, "FAILED"),
        _gate("EVAL-68", 10, "WAIT_EVAL67"),
        _gate("EVAL-69", 10, "WAIT_EVAL68"),
    ]
    overall = progress._overall_status(
        env_result={"ok": True},
        targeted=_good_tests(progress.EXPECTED_TARGETED_TESTS),
        diagnostics=_good_tests(progress.EXPECTED_DIAGNOSTIC_TESTS),
        gate_results=gates,
        execute_requested=True,
    )
    assert overall["ok"] is False
    assert overall["exit_code"] == 1
    assert any("gate:EVAL-67" in f for f in overall["failures"])


def test_overall_status_rejects_failed_seal_gate():
    gates = [
        _gate("EVAL-67", 0, "SEALED"),
        _gate("EVAL-68", 10, "WAIT_EVAL67"),
        _gate("EVAL-69", 10, "WAIT_EVAL68"),
    ]
    overall = progress._overall_status(
        env_result={"ok": True},
        targeted=_good_tests(progress.EXPECTED_TARGETED_TESTS),
        diagnostics=_good_tests(progress.EXPECTED_DIAGNOSTIC_TESTS),
        gate_results=gates,
        seal_results=[
            {"name": "EVAL-67", "exit_code": 1, "expected_exit": 0, "ok": False}
        ],
        execute_requested=True,
    )
    assert overall["ok"] is False
    assert overall["exit_code"] == 1
    assert any("seal_gate:EVAL-67" in f for f in overall["failures"])


def test_pytest_result_builds_expected_command(monkeypatch):
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = list(cmd)
        return {
            "command": list(cmd),
            "rc": 0,
            "stdout": "3 passed in 0.1s",
            "stderr": "",
            "output": "3 passed in 0.1s",
            "duration_seconds": 0.0,
        }

    monkeypatch.setattr(progress, "_run", fake_run)
    res = progress._pytest_result(("tests/a.py", "tests/b.py"))
    assert res["rc"] == 0
    assert res["passed"] == 3
    assert captured["cmd"][1:] == ["-m", "pytest", "-q", "tests/a.py", "tests/b.py"]


def test_run_gate_parses_json_payload(monkeypatch):
    payload = {"phase": "NOT_DUE", "exit_code": 10}
    monkeypatch.setattr(
        progress,
        "_run",
        lambda cmd, **kwargs: {
            "rc": 10,
            "stdout": json.dumps(payload),
            "stderr": "",
            "output": json.dumps(payload),
            "duration_seconds": 0.0,
        },
    )
    spec = {"name": "EVAL-67", "script": Path("scripts/eval67_phaseb_gate.py")}
    result = progress.run_gate(spec, execute=False, timeout=1.0)
    assert result["exit_code"] == 10
    assert result["phase"] == "NOT_DUE"
    assert result["payload"] == payload


def test_update_readiness_preserves_existing_blocks_and_writes_evidence(tmp_path, monkeypatch):
    path = tmp_path / "EVAL_67_PREWINDOW_READINESS.json"
    monkeypatch.setattr(progress, "READINESS_PATH", path)
    path.write_text(
        json.dumps(
            {
                "schema_version": 3,
                "eval68": {"task_id": "keep-68", "prereg_present": True},
                "eval69": {"task_id": "keep-69", "prereg_present": True},
            }
        )
    )
    gates = [
        _gate("EVAL-67", 10, "NOT_DUE"),
        _gate("EVAL-68", 10, "WAIT_EVAL67"),
        _gate("EVAL-69", 10, "WAIT_EVAL68"),
    ]
    overall = {"ok": True, "exit_code": 0, "needs_execute": [], "failures": []}
    data = progress.update_readiness(
        env_result={"ok": True},
        targeted=_good_tests(progress.EXPECTED_TARGETED_TESTS),
        diagnostics=_good_tests(progress.EXPECTED_DIAGNOSTIC_TESTS),
        gate_results=gates,
        seal_results=[
            {"name": "EVAL-66", "exit_code": 0, "ok": True},
            {"name": "EVAL-67", "exit_code": 1, "ok": True},
            {"name": "EVAL-68", "exit_code": 1, "ok": True},
            {"name": "EVAL-69", "exit_code": 1, "ok": True},
        ],
        overall=overall,
        execute_requested=False,
    )
    assert data["gate_phase"] == "NOT_DUE"
    assert data["gate_exit"] == 10
    assert data["tests_passed"] == progress.EXPECTED_TARGETED_TESTS
    assert data["diagnostics_passed"] == progress.EXPECTED_DIAGNOSTIC_TESTS
    assert data["eval68"]["task_id"] == "keep-68"
    assert data["eval69"]["task_id"] == "keep-69"
    assert "EVAL-67=NOT_DUE" in data["notes"]
    assert data["orchestrator"]["script"] == "scripts/eval67_prethreshold_progress.py"
    progress.write_readiness(data)
    on_disk = json.loads(path.read_text())
    assert on_disk["gate_phase"] == "NOT_DUE"