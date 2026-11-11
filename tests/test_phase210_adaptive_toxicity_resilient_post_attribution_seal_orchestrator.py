from src.hedging.phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase210AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase210AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase210_paper_only_and_composes():
    import os
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase210AdaptiveToxicityResilientPostAttributionSealConfig(seed=210210, cycles=20)
    assert cfg.paper_only is True
    orch = Phase210AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=20)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE209" in rep["composes"]
    assert "PHASE32" in rep["composes"]
