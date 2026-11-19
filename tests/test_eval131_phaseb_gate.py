"""Unit tests for the EVAL-131 phase-B gate (SEALED / DUE / FAILED arbiter).

Deterministic; no real data, no research_state writes, no network. The gate is
exercised via its pure helpers (detect_seal, task_floor_stamp) and by
inspecting the pre-registered identifiers; the seal-gate shells out to
check_session_sealed.py which is pinned by the sealed campaigns already.
"""

from __future__ import annotations

import sys
from pathlib import Path

import scripts.eval131_phaseb_gate as g131


def test_ids_are_eval131():
    assert "EVAL131" in g131.TASK_ID
    assert g131.TASK_LABEL == "EVAL131-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-RETURN-TAIL-ASYMMETRY-SPREAD"
    assert g131.PREREG_GLOB == "EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION_*"
    assert g131.COMBINED_GLOB == "EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_COMBINED_*"
    assert g131.BLOCKED_GLOB == "EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_BLOCKED_*"
    assert g131.EXIT_SEALED == 0
    assert g131.EXIT_FAILED == 1
    assert g131.EXIT_DUE == 20


def test_task_id_has_utc_timestamp_and_floor_stamp():
    stamp = g131.task_floor_stamp(g131.TASK_ID)
    assert stamp == "20261119T181500Z"
    assert len(stamp) == 16  # YYYYMMDDTHHMMSSZ


def test_detect_seal_empty_dir(tmp_path):
    empty = tmp_path / "research_state"
    empty.mkdir()
    out = g131.detect_seal(empty)
    assert out["sealed"] is False
    assert out["artifacts"] == []
    assert out["floor_stamp"] == "20261119T181500Z"


def test_gate_module_has_execute_path():
    assert callable(g131.execute_phaseb)
    assert callable(g131.run_seal_gate_check)
    assert callable(g131.capture_ready)
    assert callable(g131.detect_seal)