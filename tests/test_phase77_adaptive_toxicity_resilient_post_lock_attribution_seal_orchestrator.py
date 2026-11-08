from __future__ import annotations

from src.hedging.phase77_adaptive_toxicity_resilient_post_lock_attribution_seal_orchestrator import (
    Phase77AdaptiveToxicityResilientPostLockAttributionSealConfig,
    Phase77AdaptiveToxicityResilientPostLockAttributionSealOrchestrator,
)


def test_phase77_post_lock_attribution_seal_orchestrator_smoke() -> None:
    cfg = Phase77AdaptiveToxicityResilientPostLockAttributionSealConfig(seed=77077, paper_only=True, cycles=8)
    orch = Phase77AdaptiveToxicityResilientPostLockAttributionSealOrchestrator(cfg)
    rep = orch.run_post_lock_attribution_seal_orchestration(cycles=8)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["phase"] == "PHASE77_ADAPTIVE_TOXICITY_RESILIENT_POST_LOCK_ATTRIBUTION_SEAL_ORCHESTRATOR"
    assert rep["cycles"] == 8
    assert rep["n_venue_seals"] > 0
    assert rep["n_hedging_seals"] > 0
    assert "composes" in rep
