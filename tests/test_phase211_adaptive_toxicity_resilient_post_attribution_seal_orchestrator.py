from src.hedging.phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase211AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase211AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase211_paper_only_and_composes():
    import os
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase211AdaptiveToxicityResilientPostAttributionSealConfig(seed=211211, cycles=20)
    assert cfg.paper_only is True
    orch = Phase211AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=20)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE210" in rep["composes"]
    assert "PHASE32" in rep["composes"]
