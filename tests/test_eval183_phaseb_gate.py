"""Unit tests for the EVAL-183 Phase-B gate (deterministic completion arbiter).

The gate has three honest outcomes — SEALED (0), DUE (20), FAILED (1) — and,
unlike EVAL-67/68/69, no NOT_DUE phase: the EVAL-183 inputs are on disk, so the
honest pre-execution state is DUE (heavy work required now).

No real data, no network, no research_state writes (temp dirs only).
"""

from __future__ import annotations

import scripts.eval183_phaseb_gate as gate


def test_ids_and_globs_are_eval183():
    assert gate.TASK_ID.startswith("INIT-")
    assert "EVAL183" in gate.TASK_ID
    assert gate.TASK_ID.endswith(
        "EVAL183-CROSS-ASSET-OFLOW-TOX-ATM-IV-INTERACTION-SPILLOVER-FORWARD-CVAR"
    )
    assert gate.TASK_LABEL == (
        "EVAL183-CROSS-ASSET-OFLOW-TOX-ATM-IV-INTERACTION-SPILLOVER-FORWARD-CVAR"
    )
    assert gate.PREREG_GLOB.startswith("EVAL_183_")
    assert gate.COMBINED_GLOB.startswith("EVAL_183_")
    assert gate.BLOCKED_GLOB.startswith("EVAL_183_")
    assert "OFLOW_TOX_ATM_IV_INTERACTION" in gate.COMBINED_GLOB
    assert "FORWARD_CVAR" in gate.COMBINED_GLOB


def test_task_floor_stamp_parses_iso():
    assert gate.task_floor_stamp(gate.TASK_ID) == "20261122T023000Z"


def test_detect_seal_missing(tmp_path):
    res = gate.detect_seal(tmp_path)
    assert res["sealed"] is False
    assert res["artifacts"] == []


def test_detect_seal_hit(tmp_path):
    name = f"{gate.COMBINED_GLOB.rstrip('*')}20261122T023000Z.json"
    (tmp_path / name).write_text("{}")
    res = gate.detect_seal(tmp_path)
    assert res["sealed"] is True
    assert any("COMBINED" in a["name"] for a in res["artifacts"])


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
