from __future__ import annotations

import os

from src.hedging.phase119_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase119AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase119AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase119_smoke_paper_only_gates_ok_compose() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    orch = Phase119AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase119AdaptiveToxicityResilientPostAttributionSealConfig(seed=119119, paper_only=True)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=16)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert isinstance(rep.get("composes"), list)
    assert "PHASE118" in rep["composes"]
    assert "PHASE32" in rep["composes"]
    assert rep["phase"] == "PHASE119_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"
