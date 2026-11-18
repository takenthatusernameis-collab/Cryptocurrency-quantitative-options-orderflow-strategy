"""Unit tests for the EVAL-111 Phase-B gate (deterministic completion arbiter).

The gate has three honest outcomes — SEALED (0), DUE (20), FAILED (1) — and,
unlike EVAL-67/68/69, no NOT_DUE phase: the EVAL-111 inputs are on disk, so the
honest pre-execution state is DUE (heavy work required now).

No real data, no network, no research_state writes (temp dirs only).
"""

from __future__ import annotations

import json

import scripts.eval111_phaseb_gate as gate


def test_ids_and_globs_are_eval111():
    assert gate.TASK_ID.startswith("INIT-")
    assert "EVAL111" in gate.TASK_ID
    assert gate.TASK_ID.endswith("EVAL111-SINGLE-ASSET-SKEW-FORWARD-RETURN-SKEWNESS")
    assert gate.TASK_LABEL == "EVAL111-SINGLE-ASSET-SKEW-FORWARD-RETURN-SKEWNESS"
    assert gate.PREREG_GLOB.startswith("EVAL_111_")
    assert gate.COMBINED_GLOB.startswith("EVAL_111_")
    assert gate.BLOCKED_GLOB.startswith("EVAL_111_")
    assert "SKEW" in gate.COMBINED_GLOB
    assert "RETURN_SKEWNESS" in gate.COMBINED_GLOB


def test_task_floor_stamp_parses_iso():
    assert gate.task_floor_stamp(gate.TASK_ID) == "20261118T230000Z"


def test_detect_seal_missing(tmp_path):
    res = gate.detect_seal(tmp_path)
    assert res["sealed"] is False
    assert res["artifacts"] == []


def test_detect_seal_hit(tmp_path):
    name = f"{gate.COMBINED_GLOB.rstrip('*')}20261118T235959Z.json"
    (tmp_path / name).write_text("{}")
    res = gate.detect_seal(tmp_path)
    assert res["sealed"] is True
    assert any("COMBINED" in a["name"] for a in res["artifacts"])


def test_detect_seal_blocked_counts(tmp_path):
    name = f"{gate.BLOCKED_GLOB.rstrip('*')}20261118T235959Z.json"
    (tmp_path / name).write_text("{}")
    res = gate.detect_seal(tmp_path)
    assert res["sealed"] is True
    assert any("BLOCKED" in a["name"] for a in res["artifacts"])


def test_detect_seal_stale_stamp_is_not_sealed(tmp_path):
    name = f"{gate.COMBINED_GLOB.rstrip('*')}20260101T000000Z.json"
    (tmp_path / name).write_text("{}")
    res = gate.detect_seal(tmp_path)
    assert res["sealed"] is False


def test_execute_refuses_without_capture(tmp_path):
    missing = tmp_path / "does_not_exist"
    res = gate.execute_phaseb(capture_dir=missing, research_state_dir=tmp_path)
    assert res["ok"] is False
    assert res["step"] == "capture"


def test_main_due_without_execute(tmp_path, capsys):
    rc = gate.main(["--research-state-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_DUE == 20
    assert out["phase"] == "DUE"
    assert out["readiness"]["runnable_now"] is True


def test_main_sealed_is_idempotent_noop(tmp_path, capsys, monkeypatch):
    name = f"{gate.COMBINED_GLOB.rstrip('*')}20261118T235959Z.json"
    (tmp_path / name).write_text("{}")
    monkeypatch.setattr(gate, "run_seal_gate_check", lambda **kw: (0, "ok"))
    rc = gate.main(["--research-state-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_SEALED == 0
    assert out["phase"] == "SEALED"


def test_main_failed_when_seal_gate_fails(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(
        gate, "execute_phaseb",
        lambda **kw: {"ok": False, "step": "seal_gate", "steps": []},
    )
    rc = gate.main(["--execute", "--research-state-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == gate.EXIT_FAILED == 1
    assert out["phase"] == "FAILED"
