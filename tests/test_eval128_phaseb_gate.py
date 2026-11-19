"""Unit tests for the EVAL-128 phase-B gate (SEALED / DUE / FAILED arbiter).

Deterministic; no real data, no research_state writes, no network. The gate is
exercised via its pure helpers (detect_seal, task_floor_stamp) and by
inspecting the pre-registered identifiers; the seal-gate shells out to
check_session_sealed.py which is pinned by the sealed campaigns already.
"""

from __future__ import annotations

import sys
from pathlib import Path

import scripts.eval128_phaseb_gate as g128


def test_ids_are_eval128():
    assert "EVAL128" in g128.TASK_ID
    assert g128.TASK_LABEL == "EVAL128-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD"
    assert g128.PREREG_GLOB == "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION_*"
    assert g128.COMBINED_GLOB == "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED_*"
    assert g128.BLOCKED_GLOB == "EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED_*"
    assert g128.EXIT_SEALED == 0
    assert g128.EXIT_FAILED == 1
    assert g128.EXIT_DUE == 20


def test_task_id_has_utc_timestamp_and_floor_stamp():
    stamp = g128.task_floor_stamp(g128.TASK_ID)
    assert stamp == "20261119T161747Z"
    assert len(stamp) == 16  # YYYYMMDDTHHMMSSZ


def test_detect_seal_empty_dir(tmp_path):
    empty = tmp_path / "research_state"
    empty.mkdir()
    out = g128.detect_seal(empty)
    assert out["sealed"] is False
    assert out["artifacts"] == []
    assert out["floor_stamp"] == "20261119T161747Z"


def test_gate_module_has_execute_path():
    assert callable(g128.execute_phaseb)
    assert callable(g128.run_seal_gate_check)
    assert callable(g128.capture_ready)
    assert callable(g128.detect_seal)
