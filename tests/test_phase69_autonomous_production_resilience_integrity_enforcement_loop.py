from src.integration.phase69_autonomous_production_resilience_integrity_enforcement_loop import (
    Phase69AutonomousProductionResilienceIntegrityEnforcementLoop,
    Phase69AutonomousProductionResilienceIntegrityEnforcementLoopConfig,
)


def test_phase69_integrity_enforcement_deterministic():
    loop = Phase69AutonomousProductionResilienceIntegrityEnforcementLoop(
        Phase69AutonomousProductionResilienceIntegrityEnforcementLoopConfig(seed=69062, cycles=40)
    )
    rep = loop.run_integrity_enforcement(cycles=40)
    assert rep["phase"] == "PHASE69_AUTONOMOUS_PRODUCTION_RESILIENCE_INTEGRITY_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["n_integrity_checks"] > 0
    arts = loop.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
