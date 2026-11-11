from src.hedging.phase212_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase212AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase212AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase212_paper_only_and_composes():
    import os
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase212AdaptiveToxicityResilientPostAttributionSealConfig(seed=212212, cycles=20)
    assert cfg.paper_only is True
    orch = Phase212AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=20)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE211" in rep["composes"]
    assert "PHASE32" in rep["composes"]