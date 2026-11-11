from src.hedging.phase213_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase213AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase213AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase213_paper_only_and_composes():
    import os
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase213AdaptiveToxicityResilientPostAttributionSealConfig(seed=213213, cycles=20)
    assert cfg.paper_only is True
    orch = Phase213AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=20)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE212" in rep["composes"]
    assert "PHASE32" in rep["composes"]
