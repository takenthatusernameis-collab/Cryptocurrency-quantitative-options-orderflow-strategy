"""Unit tests for the EVAL-124 phase-B gate (SEALED / DUE / FAILED arbiter).

Deterministic; no real data, no research_state writes, no network. The gate is
exercised via its pure helpers (detect_seal, task_floor_stamp) and by
inspecting the pre-registered identifiers; the seal-gate shells out to
check_session_sealed.py which is pinned by the sealed campaigns already.
"""

from __future__ import annotations

import sys
from pathlib import Path

import scripts.eval124_phaseb_gate as g124


def test_ids_are_eval124():
    assert "EVAL124" in g124.TASK_ID
    assert g124.TASK_LABEL == "EVAL124-CROSS-ASSET-TERM-SLOPE-SPILLOVER-RISK-REVERSAL-NET-OF-COST"
    assert g124.PREREG_GLOB == "EVAL_124_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_PREREGISTRATION_*"
    assert g124.COMBINED_GLOB == "EVAL_124_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_COMBINED_*"
    assert g124.BLOCKED_GLOB == "EVAL_124_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_BLOCKED_*"
    assert g124.CAPTURE_DIR.name == "eval61"
    assert g124.EXIT_SEALED == 0
    assert g124.EXIT_FAILED == 1
    assert g124.EXIT_DUE == 20


def test_task_id_has_utc_timestamp_and_floor_stamp():
    stamp = g124.task_floor_stamp(g124.TASK_ID)
    assert stamp == "20261119T103411Z"
    assert len(stamp) == 16  # YYYYMMDDTHHMMSSZ


def test_detect_seal_empty_dir(tmp_path):
    empty = tmp_path / "research_state"
    empty.mkdir()
    out = g124.detect_seal(empty)
    assert out["sealed"] is False
    assert out["artifacts"] == []
    assert out["floor_stamp"] == "20261119T103411Z"


def test_gate_module_has_execute_path():
    assert callable(g124.execute_phaseb)
    assert callable(g124.run_seal_gate_check)
    assert callable(g124.capture_ready)
    assert callable(g124.detect_seal)
