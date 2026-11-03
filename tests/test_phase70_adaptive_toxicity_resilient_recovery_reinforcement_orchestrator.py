from src.hedging.phase70_adaptive_toxicity_resilient_recovery_reinforcement_orchestrator import (
    Phase70AdaptiveToxicityResilientRecoveryReinforcementOrchestrator,
    Phase70AdaptiveToxicityResilientRecoveryReinforcementConfig,
)


def test_phase70_recovery_reinforcement_orchestrator_smoke():
    orch = Phase70AdaptiveToxicityResilientRecoveryReinforcementOrchestrator(
        Phase70AdaptiveToxicityResilientRecoveryReinforcementConfig(seed=7071, cycles=40)
    )
    rep = orch.run_recovery_reinforcement_orchestration(cycles=40)
    assert rep["phase"] == "PHASE70_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_REINFORCEMENT_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["recovery_reinforce_pass_rate"] >= 0.0
    arts = orch.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
