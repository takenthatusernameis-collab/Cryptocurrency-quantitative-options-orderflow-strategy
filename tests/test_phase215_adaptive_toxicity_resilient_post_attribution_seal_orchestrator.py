from src.hedging.phase215_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase215AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase215AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase215_paper_only_and_composes():
    import os
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase215AdaptiveToxicityResilientPostAttributionSealConfig(seed=215215, cycles=20)
    assert cfg.paper_only is True
    orch = Phase215AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=20)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE214" in rep["composes"]
    assert "PHASE32" in rep["composes"]