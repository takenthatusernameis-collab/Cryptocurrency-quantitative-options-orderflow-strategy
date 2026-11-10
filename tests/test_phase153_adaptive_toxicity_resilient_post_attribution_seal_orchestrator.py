from __future__ import annotations

import os

from src.hedging.phase153_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase153AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase153AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase153_smoke_paper_only_gates_ok_compose() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    orch = Phase153AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase153AdaptiveToxicityResilientPostAttributionSealConfig(seed=153153, paper_only=True)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=16)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert isinstance(rep.get("composes"), list)
    assert "PHASE152" in rep["composes"]
    assert "PHASE32" in rep["composes"]
    assert rep["phase"] == "PHASE153_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"


def test_phase153_config_rejects_live() -> None:
    try:
        Phase153AdaptiveToxicityResilientPostAttributionSealConfig(seed=153153, paper_only=False)
        raise AssertionError("expected ValueError for paper_only=False")
    except ValueError:
        pass