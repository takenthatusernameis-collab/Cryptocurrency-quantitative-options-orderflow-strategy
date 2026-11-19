"""Unit tests for EVAL-116 phase-B gate (SEALED/DUE/FAILED arbiter)."""

from __future__ import annotations

import scripts.eval116_phaseb_gate as g116


def test_ids_are_eval116():
    assert g116.TASK_ID.startswith("INIT-")
    assert "EVAL116-CROSS-SECTIONAL-SKEW-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD" in g116.TASK_ID
    assert g116.TASK_LABEL == "EVAL116-CROSS-SECTIONAL-SKEW-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD"
    assert g116.PREREG_GLOB.startswith("EVAL_116_")
    assert g116.COMBINED_GLOB.startswith("EVAL_116_")
    assert g116.BLOCKED_GLOB.startswith("EVAL_116_")


def test_exit_codes():
    assert g116.EXIT_SEALED == 0
    assert g116.EXIT_FAILED == 1
    assert g116.EXIT_DUE == 20


def test_task_floor_stamp_parses():
    stamp = g116.task_floor_stamp(g116.TASK_ID)
    assert stamp == "20261119T025129Z"


def test_detect_seal_shape():
    out = g116.detect_seal(g116.RS_DIR)
    assert set(out) >= {"sealed", "artifacts", "floor_stamp"}
    assert isinstance(out["sealed"], bool)
    assert isinstance(out["artifacts"], list)
    assert out["floor_stamp"] == "20261119T025129Z"


def test_capture_ready_shape():
    cap = g116.capture_ready()
    assert set(cap) >= {"present", "btc", "eth", "capture_dir"}
    assert isinstance(cap["present"], bool)


def test_readiness_keys():
    readiness = {
        "capture": g116.capture_ready(),
        "runnable_now": bool(g116.capture_ready().get("present")),
        "task_id": g116.TASK_ID,
        "task_label": g116.TASK_LABEL,
    }
    assert readiness["task_id"] == g116.TASK_ID
