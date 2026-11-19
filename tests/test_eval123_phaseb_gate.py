"""Unit tests for EVAL-123 phase-B gate (SEALED/DUE/FAILED arbiter)."""

from __future__ import annotations

import scripts.eval123_phaseb_gate as g123


def test_ids_are_eval123():
    assert g123.TASK_ID.startswith("INIT-")
    assert "EVAL123-CROSS-SECTIONAL-SKEW-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD" in g123.TASK_ID
    assert g123.TASK_LABEL == "EVAL123-CROSS-SECTIONAL-SKEW-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD"
    assert g123.PREREG_GLOB.startswith("EVAL_123_")
    assert g123.COMBINED_GLOB.startswith("EVAL_123_")
    assert g123.BLOCKED_GLOB.startswith("EVAL_123_")


def test_exit_codes():
    assert g123.EXIT_SEALED == 0
    assert g123.EXIT_FAILED == 1
    assert g123.EXIT_DUE == 20


def test_task_floor_stamp_parses():
    stamp = g123.task_floor_stamp(g123.TASK_ID)
    assert stamp == "20261119T091632Z"


def test_detect_seal_shape():
    out = g123.detect_seal(g123.RS_DIR)
    assert set(out) >= {"sealed", "artifacts", "floor_stamp"}
    assert isinstance(out["sealed"], bool)
    assert isinstance(out["artifacts"], list)
    assert out["floor_stamp"] == "20261119T091632Z"


def test_capture_ready_shape():
    cap = g123.capture_ready()
    assert set(cap) >= {"present", "btc", "eth", "capture_dir"}
    assert isinstance(cap["present"], bool)


def test_readiness_keys():
    readiness = {
        "capture": g123.capture_ready(),
        "runnable_now": bool(g123.capture_ready().get("present")),
        "task_id": g123.TASK_ID,
        "task_label": g123.TASK_LABEL,
    }
    assert readiness["task_id"] == g123.TASK_ID
