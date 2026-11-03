from src.integration.phase68_autonomous_production_hardening_enforcement_loop import (
    Phase68AutonomousProductionHardeningEnforcementLoop,
    Phase68AutonomousProductionHardeningEnforcementLoopConfig,
)


def test_phase68_hardening_enforcement_deterministic():
    loop = Phase68AutonomousProductionHardeningEnforcementLoop(
        Phase68AutonomousProductionHardeningEnforcementLoopConfig(seed=68062, cycles=40)
    )
    rep = loop.run_hardening_enforcement(cycles=40)
    assert rep["phase"] == "PHASE68_AUTONOMOUS_PRODUCTION_HARDENING_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["n_hardening_checks"] > 0
    arts = loop.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
