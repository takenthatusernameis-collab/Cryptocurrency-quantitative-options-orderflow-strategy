from __future__ import annotations

import os

import pytest

os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.hedging.phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (  # noqa: E402
    Phase202AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase202AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase202_paper_only_hard_gate() -> None:
    with pytest.raises(ValueError):
        Phase202AdaptiveToxicityResilientPostAttributionSealConfig(paper_only=False)


def test_phase202_run_seal_orchestration_paper_only() -> None:
    orch = Phase202AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase202AdaptiveToxicityResilientPostAttributionSealConfig(seed=202202, cycles=20)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=20)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE201" in rep["composes"]
    assert "PHASE32" in rep["composes"]
    assert rep["live_trading_enabled"] is False
    assert rep["next9_unblocked"] is False
    assert rep["n_seal_attestations"] > 0
    assert rep["n_hedging_seal_attestations"] > 0
    assert rep["deterministic"] is True
    assert rep["bounds_ok"] is True
