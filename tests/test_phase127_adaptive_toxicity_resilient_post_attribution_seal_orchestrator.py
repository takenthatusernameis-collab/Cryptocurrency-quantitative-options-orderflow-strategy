from __future__ import annotations

import os

from src.hedging.phase127_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase127AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase127AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase127_smoke_paper_only_gates_ok_compose() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    orch = Phase127AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase127AdaptiveToxicityResilientPostAttributionSealConfig(seed=127127, paper_only=True)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=16)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert isinstance(rep.get("composes"), list)
    assert "PHASE126" in rep["composes"]
    assert "PHASE32" in rep["composes"]
    assert rep["phase"] == "PHASE127_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"