"""
Tests for Phase 48: Alpha Orchestration Loop.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.integration.phase48_alpha_orchestration_loop import Phase48AlphaOrchestrationLoop


def test_phase48_loop_paper_only_hard_gate():
    try:
        Phase48AlphaOrchestrationLoop(paper_only=False)
        assert False, "should have raised"
    except Exception:
        pass


def test_phase48_loop_init_structure():
    loop = Phase48AlphaOrchestrationLoop(seed=48048, cycles=6, paper_only=True)
    assert loop.paper_only is True
    assert loop.cycles == 6


def test_phase48_loop_run_composition(tmp_path):
    loop = Phase48AlphaOrchestrationLoop(seed=48048, cycles=10, paper_only=True, outdir=str(tmp_path))
    rep = loop.run()
    assert rep["paper_only"] is True
    assert rep["phase"] == "PHASE48_ALPHA_ORCHESTRATION_LOOP"
    # Composes phases
    assert "PHASE48_REGIME_CONDITIONAL_OPTIONS" in " ".join(rep["integrated_with"])
    assert "PHASE47_CROSS_VENUE_ARBITRAGE" in " ".join(rep["integrated_with"])
    assert "PHASE39_KILL_SWITCHES" in " ".join(rep["integrated_with"])


def test_phase48_loop_artifacts(tmp_path):
    loop = Phase48AlphaOrchestrationLoop(seed=48048, cycles=8, paper_only=True, outdir=str(tmp_path))
    rep = loop.run()
    # Check artifacts written
    jfiles = list(Path(tmp_path).glob("phase48_alpha_orchestration_loop*.json"))
    mfiles = list(Path(tmp_path).glob("phase48_alpha_orchestration_loop*.md"))
    assert len(jfiles) >= 1 or len(mfiles) >= 1
    if jfiles:
        data = json.loads(jfiles[0].read_text())
        assert data["paper_only"] is True
