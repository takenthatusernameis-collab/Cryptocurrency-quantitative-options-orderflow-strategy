from src.integration.phase71_autonomous_production_certification_enforcement_loop import (
    Phase71AutonomousProductionCertificationEnforcementLoop,
    Phase71AutonomousProductionCertificationEnforcementLoopConfig,
)


def test_phase71_production_certification_enforcement_loop_smoke():
    loop = Phase71AutonomousProductionCertificationEnforcementLoop(
        Phase71AutonomousProductionCertificationEnforcementLoopConfig(seed=7172, cycles=40)
    )
    rep = loop.run_certification_enforcement(cycles=40)
    assert rep["phase"] == "PHASE71_AUTONOMOUS_PRODUCTION_CERTIFICATION_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["production_certification_pass_rate"] >= 0.0
    arts = loop.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
