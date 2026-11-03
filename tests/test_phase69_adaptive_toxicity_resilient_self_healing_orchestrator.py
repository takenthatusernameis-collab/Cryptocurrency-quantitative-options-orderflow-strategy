from src.hedging.phase69_adaptive_toxicity_resilient_self_healing_orchestrator import (
    Phase69AdaptiveToxicityResilientSelfHealingOrchestrator,
    Phase69AdaptiveToxicityResilientSelfHealingConfig,
)


def test_phase69_self_healing_orchestrator_deterministic():
    orch = Phase69AdaptiveToxicityResilientSelfHealingOrchestrator(
        Phase69AdaptiveToxicityResilientSelfHealingConfig(seed=69061, cycles=40)
    )
    rep = orch.run_self_healing_orchestration(cycles=40)
    assert rep["phase"] == "PHASE69_ADAPTIVE_TOXICITY_RESILIENT_SELF_HEALING_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["n_hedging_self_heals"] > 0
    arts = orch.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
