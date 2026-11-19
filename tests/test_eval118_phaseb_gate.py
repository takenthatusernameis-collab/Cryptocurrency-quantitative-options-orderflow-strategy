"""Unit tests for EVAL-118 phase-B gate (SEALED/DUE/FAILED arbiter)."""

from __future__ import annotations

import scripts.eval118_phaseb_gate as g118


def test_ids_are_eval118():
    assert g118.TASK_ID.startswith("INIT-")
    assert (
        "EVAL118-CROSS-SECTIONAL-TERM-SLOPE-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD"
        in g118.TASK_ID
    )
    assert (
        g118.TASK_LABEL
        == "EVAL118-CROSS-SECTIONAL-TERM-SLOPE-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD"
    )
    assert g118.PREREG_GLOB.startswith("EVAL_118_")
    assert g118.COMBINED_GLOB.startswith("EVAL_118_")
    assert g118.BLOCKED_GLOB.startswith("EVAL_118_")


def test_exit_codes():
    assert g118.EXIT_SEALED == 0
    assert g118.EXIT_FAILED == 1
    assert g118.EXIT_DUE == 20


def test_task_floor_stamp_parses():
    stamp = g118.task_floor_stamp(g118.TASK_ID)
    assert stamp == "20261119T051509Z"


def test_detect_seal_shape():
    out = g118.detect_seal(g118.RS_DIR)
    assert set(out) >= {"sealed", "artifacts", "floor_stamp"}
    assert isinstance(out["sealed"], bool)
    assert isinstance(out["artifacts"], list)
    assert out["floor_stamp"] == "20261119T051509Z"


def test_capture_ready_shape():
    cap = g118.capture_ready()
    assert set(cap) >= {"present", "btc", "eth", "capture_dir"}
    assert isinstance(cap["present"], bool)


def test_readiness_keys():
    readiness = {
        "capture": g118.capture_ready(),
        "runnable_now": bool(g118.capture_ready().get("present")),
        "task_id": g118.TASK_ID,
        "task_label": g118.TASK_LABEL,
    }
    assert readiness["task_id"] == g118.TASK_ID
