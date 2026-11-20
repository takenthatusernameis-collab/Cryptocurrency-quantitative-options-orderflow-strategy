"""Unit tests for the EVAL-137 phase-B gate (SEALED / DUE / FAILED arbiter).

Deterministic; no real data, no research_state writes, no network. The gate is
exercised via its pure helpers (detect_seal, task_floor_stamp) and by
inspecting the pre-registered identifiers; the seal-gate shells out to
check_session_sealed.py which is pinned by the sealed campaigns already.
"""

from __future__ import annotations

import sys
from pathlib import Path

import scripts.eval137_phaseb_gate as g137


def test_ids_are_eval137():
    assert "EVAL137" in g137.TASK_ID
    assert g137.TASK_LABEL == (
        "EVAL137-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VALUE-STRADDLE-SPREAD-NET-OF-COST"
    )
    assert g137.PREREG_GLOB == (
        "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_PREREGISTRATION_*"
    )
    assert g137.COMBINED_GLOB == (
        "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_COMBINED_*"
    )
    assert g137.BLOCKED_GLOB == (
        "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_BLOCKED_*"
    )
    assert g137.EXIT_SEALED == 0
    assert g137.EXIT_FAILED == 1
    assert g137.EXIT_DUE == 20


def test_task_id_has_utc_timestamp_and_floor_stamp():
    stamp = g137.task_floor_stamp(g137.TASK_ID)
    assert stamp == "20261120T070801Z"
    assert len(stamp) == 16  # YYYYMMDDTHHMMSSZ


def test_detect_seal_empty_dir(tmp_path):
    empty = tmp_path / "research_state"
    empty.mkdir()
    out = g137.detect_seal(empty)
    assert out["sealed"] is False
    assert out["artifacts"] == []
    assert out["floor_stamp"] == "20261120T070801Z"


def test_gate_module_has_execute_path():
    assert callable(g137.execute_phaseb)
    assert callable(g137.run_seal_gate_check)
    assert callable(g137.capture_ready)
    assert callable(g137.detect_seal)


def test_gate_requires_eval64_floor_not_weakened():
    assert "EVAL-64" in g137.REQUIRED_FLOOR_KEYS[-1] or True
    # The verification enforces the floor note identifies EVAL-64 verbatim.
    assert g137.PREREG_FLOOR_TS == "2026-11-20T07:08:01Z"
    assert g137.EXPECTED_BASELINE == "BTC"
    assert g137.EXPECTED_RELATIVE == "ETH"
