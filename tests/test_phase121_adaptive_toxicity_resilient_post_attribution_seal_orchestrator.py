from __future__ import annotations

import os

from src.hedging.phase121_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase121AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase121AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase121_smoke_paper_only_gates_ok_compose() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    orch = Phase121AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase121AdaptiveToxicityResilientPostAttributionSealConfig(seed=121121, paper_only=True)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=16)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert isinstance(rep.get("composes"), list)
    assert "PHASE120" in rep["composes"]
    assert "PHASE32" in rep["composes"]
    assert rep["phase"] == "PHASE121_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"