from src.hedging.phase214_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase214AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase214AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase214_paper_only_and_composes():
    import os
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase214AdaptiveToxicityResilientPostAttributionSealConfig(seed=214214, cycles=20)
    assert cfg.paper_only is True
    orch = Phase214AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=20)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE213" in rep["composes"]
    assert "PHASE32" in rep["composes"]
