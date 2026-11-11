from src.hedging.phase208_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase208AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase208AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase208_paper_only_and_composes():
    import os
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase208AdaptiveToxicityResilientPostAttributionSealConfig(seed=208208, cycles=20)
    assert cfg.paper_only is True
    orch = Phase208AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=20)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE207" in rep["composes"]
    assert "PHASE32" in rep["composes"]
