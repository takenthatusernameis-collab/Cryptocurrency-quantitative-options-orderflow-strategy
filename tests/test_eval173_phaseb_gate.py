"""Unit tests for the EVAL-173 Phase-B gate."""

from __future__ import annotations

import json

import scripts.eval173_phaseb_gate as gate


def test_ids_and_globs_are_eval173_skew_forward_variance():
    assert gate.TASK_ID.startswith("INIT-")
    assert "EVAL173" in gate.TASK_ID
    assert gate.TASK_ID.endswith("EVAL173-SINGLE-ASSET-SKEW-FORWARD-VARIANCE")
    assert gate.TASK_LABEL == "EVAL173-SINGLE-ASSET-SKEW-FORWARD-VARIANCE"
    assert gate.PREREG_GLOB == "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_PREREGISTRATION_*"
    assert gate.COMBINED_GLOB == "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_COMBINED_*"
    assert gate.BLOCKED_GLOB == "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_BLOCKED_*"


def test_task_floor_stamp_parses_iso():
    assert gate.task_floor_stamp(gate.TASK_ID) == "20261121T211700Z"


def test_detect_seal_missing(tmp_path):
    result = gate.detect_seal(tmp_path)
    assert result["sealed"] is False
    assert result["artifacts"] == []


def test_detect_seal_hit(tmp_path):
    name = f"{gate.COMBINED_GLOB.rstrip('*')}20261121T211700Z.json"
    (tmp_path / name).write_text("{}")
    result = gate.detect_seal(tmp_path)
    assert result["sealed"] is True
    assert result["artifacts"][0]["kind"] == "COMBINED"


def test_detect_seal_stale_stamp_is_not_sealed(tmp_path):
    name = f"{gate.COMBINED_GLOB.rstrip('*')}20260101T000000Z.json"
    (tmp_path / name).write_text("{}")
    assert gate.detect_seal(tmp_path)["sealed"] is False


def test_execute_refuses_without_capture(tmp_path):
    result = gate.execute_phaseb(capture_dir=tmp_path / "missing", research_state_dir=tmp_path)
    assert result["ok"] is False
    assert result["step"] == "capture"


def test_main_due_without_execute(tmp_path, capsys):
    rc = gate.main(["--research-state-dir", str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_DUE == 20
    assert payload["phase"] == "DUE"


def test_main_sealed_with_temp_research_state(tmp_path, capsys, monkeypatch):
    name = f"{gate.COMBINED_GLOB.rstrip('*')}20261121T211700Z.json"
    (tmp_path / name).write_text("{}")
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **kwargs: (0, "OK"))
    rc = gate.main(["--research-state-dir", str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_SEALED == 0
    assert payload["phase"] == "SEALED"


def test_main_execute_failure(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(
        gate,
        "execute_phaseb",
        lambda **kwargs: {"ok": False, "step": "seal_gate", "steps": []},
    )
    rc = gate.main(["--execute", "--research-state-dir", str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_FAILED == 1
    assert payload["phase"] == "FAILED"
    assert payload["failed_step"] == "seal_gate"