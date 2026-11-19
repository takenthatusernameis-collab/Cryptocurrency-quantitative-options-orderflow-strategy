"""Unit tests for the EVAL-125 phase-B gate (SEALED / DUE / FAILED arbiter).

Deterministic; no real data, no research_state writes, no network. The gate is
exercised via its pure helpers (detect_seal, task_floor_stamp) and by
inspecting the pre-registered identifiers; the seal-gate shells out to
check_session_sealed.py which is pinned by the sealed campaigns already.
"""

from __future__ import annotations

import sys
from pathlib import Path

import scripts.eval125_phaseb_gate as g125


def test_ids_are_eval125():
    assert "EVAL125" in g125.TASK_ID
    assert g125.TASK_LABEL == "EVAL125-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD"
    assert g125.PREREG_GLOB == "EVAL_125_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_PREREGISTRATION_*"
    assert g125.COMBINED_GLOB == "EVAL_125_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_COMBINED_*"
    assert g125.BLOCKED_GLOB == "EVAL_125_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_BLOCKED_*"
    assert g125.EXIT_SEALED == 0
    assert g125.EXIT_FAILED == 1
    assert g125.EXIT_DUE == 20


def test_task_id_has_utc_timestamp_and_floor_stamp():
    stamp = g125.task_floor_stamp(g125.TASK_ID)
    assert stamp == "20261119T133002Z"
    assert len(stamp) == 16  # YYYYMMDDTHHMMSSZ


def test_detect_seal_empty_dir(tmp_path):
    empty = tmp_path / "research_state"
    empty.mkdir()
    out = g125.detect_seal(empty)
    assert out["sealed"] is False
    assert out["artifacts"] == []
    assert out["floor_stamp"] == "20261119T133002Z"


def test_gate_module_has_execute_path():
    assert callable(g125.execute_phaseb)
    assert callable(g125.run_seal_gate_check)
    assert callable(g125.capture_ready)
    assert callable(g125.detect_seal)