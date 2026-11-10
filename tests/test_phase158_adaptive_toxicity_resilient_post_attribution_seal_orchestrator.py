from __future__ import annotations

import os

from src.hedging.phase158_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase158AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase158AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase158_smoke_paper_only_gates_ok_compose() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    orch = Phase158AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase158AdaptiveToxicityResilientPostAttributionSealConfig(seed=158158, paper_only=True)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=16)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert isinstance(rep.get("composes"), list)
    assert "PHASE157" in rep["composes"]
    assert "PHASE32" in rep["composes"]
    assert rep["phase"] == "PHASE158_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"


def test_phase158_config_rejects_live() -> None:
    try:
        Phase158AdaptiveToxicityResilientPostAttributionSealConfig(seed=158158, paper_only=False)
        raise AssertionError("expected ValueError for paper_only=False")
    except ValueError:
        pass