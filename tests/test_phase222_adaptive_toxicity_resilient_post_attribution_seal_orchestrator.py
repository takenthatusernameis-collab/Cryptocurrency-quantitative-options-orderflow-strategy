import os
os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.hedging.phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase222AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase222AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase222_paper_only_guard():
    try:
        Phase222AdaptiveToxicityResilientPostAttributionSealConfig(paper_only=False)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_phase222_runs_paper_only():
    cfg = Phase222AdaptiveToxicityResilientPostAttributionSealConfig(seed=222222, cycles=8, paper_only=True)
    orch = Phase222AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=8)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["composes"] == ["PHASE221", "PHASE32"]
    assert rep["phase"] == "PHASE222_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"
    assert rep["n_seal_attestations"] > 0
    assert rep["n_hedging_seal_attestations"] > 0
    assert rep["upstream_phase221"] is True


def test_phase222_deterministic_quick():
    cfg = Phase222AdaptiveToxicityResilientPostAttributionSealConfig(seed=222222, cycles=6, paper_only=True)
    r1 = Phase222AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg).run_post_attribution_seal_orchestration(cycles=6)
    r2 = Phase222AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg).run_post_attribution_seal_orchestration(cycles=6)
    for k in ("avg_cross_venue_ok", "avg_seal_pass_rate", "n_seal_attestations", "n_hedging_seal_attestations"):
        assert r1[k] == r2[k]
