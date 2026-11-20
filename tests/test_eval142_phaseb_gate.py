"""Unit tests for the EVAL-142 phase-B gate (SEALED / DUE / FAILED arbiter).

Deterministic; no real data, no research_state writes, no network. The gate is
exercised via its pure helpers (detect_seal, task_floor_stamp) and by
inspecting the pre-registered identifiers; the seal-gate shells out to
check_session_sealed.py which is pinned by the sealed campaigns already.
"""

from __future__ import annotations

import sys
from pathlib import Path

import scripts.eval142_phaseb_gate as g142


def test_ids_are_eval142():
    assert "EVAL142" in g142.TASK_ID
    assert g142.TASK_LABEL == "EVAL142-CROSS-ASSET-TERM-RATIO-SPILLOVER-RISK-REVERSAL-NET-OF-COST"
    assert g142.PREREG_GLOB == "EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_PREREGISTRATION_*"
    assert g142.COMBINED_GLOB == "EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_COMBINED_*"
    assert g142.BLOCKED_GLOB == "EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_BLOCKED_*"
    assert g142.CAPTURE_DIR.name == "eval68"
    assert g142.EXIT_SEALED == 0
    assert g142.EXIT_FAILED == 1
    assert g142.EXIT_DUE == 20


def test_task_id_has_utc_timestamp_and_floor_stamp():
    stamp = g142.task_floor_stamp(g142.TASK_ID)
    assert stamp == "20261120T135159Z"
    assert len(stamp) == 16  # YYYYMMDDTHHMMSSZ


def test_detect_seal_empty_dir(tmp_path):
    empty = tmp_path / "research_state"
    empty.mkdir()
    out = g142.detect_seal(empty)
    assert out["sealed"] is False
    assert out["artifacts"] == []
    assert out["floor_stamp"] == "20261120T135159Z"


def test_gate_module_has_execute_path():
    assert callable(g142.execute_phaseb)
    assert callable(g142.run_seal_gate_check)
    assert callable(g142.capture_ready)
    assert callable(g142.detect_seal)
