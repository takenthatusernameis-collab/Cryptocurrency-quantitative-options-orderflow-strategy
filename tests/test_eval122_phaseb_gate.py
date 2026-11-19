"""Unit tests for the EVAL-122 Phase-B gate (deterministic completion arbiter).

The gate has three honest outcomes — SEALED (0), DUE (20), FAILED (1) — and,
unlike EVAL-67/68/69, no NOT_DUE phase: the EVAL-122 inputs are on disk, so the
honest pre-execution state is DUE (heavy work required now).

No real data, no network, no research_state writes (temp dirs only).
"""

from __future__ import annotations

import scripts.eval122_phaseb_gate as gate


def test_ids_and_globs_are_eval122():
    assert gate.TASK_ID.startswith("INIT-")
    assert "EVAL122" in gate.TASK_ID
    assert gate.TASK_ID.endswith("EVAL122-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-SKEWNESS")
    assert gate.TASK_LABEL == "EVAL122-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-SKEWNESS"
    assert gate.PREREG_GLOB.startswith("EVAL_122_")
    assert gate.COMBINED_GLOB.startswith("EVAL_122_")
    assert gate.BLOCKED_GLOB.startswith("EVAL_122_")
    assert "TERM_SLOPE" in gate.COMBINED_GLOB
    assert "SPILLOVER" in gate.COMBINED_GLOB
    assert "FORWARD_RETURN_SKEWNESS" in gate.COMBINED_GLOB


def test_task_floor_stamp_parses_iso():
    assert gate.task_floor_stamp(gate.TASK_ID) == "20261119T081800Z"


def test_detect_seal_missing(tmp_path):
    res = gate.detect_seal(tmp_path)
    assert res["sealed"] is False
    assert res["artifacts"] == []


def test_detect_seal_hit(tmp_path):
    name = f"{gate.COMBINED_GLOB.rstrip('*')}20261119T090000Z.json"
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
