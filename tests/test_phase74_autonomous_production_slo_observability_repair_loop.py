from src.integration.phase74_autonomous_production_slo_observability_repair_loop import (
    Phase74AutonomousProductionSloObservabilityRepairLoop,
    Phase74AutonomousProductionSloObservabilityRepairLoopConfig,
)


def test_phase74_autonomous_production_slo_observability_repair_loop_smoke():
    eng = Phase74AutonomousProductionSloObservabilityRepairLoop(Phase74AutonomousProductionSloObservabilityRepairLoopConfig(seed=7474, cycles=40))
    rep = eng.run_slo_observability_repair_loop(cycles=40)
    assert rep["phase"] == "PHASE74_AUTONOMOUS_PRODUCTION_SLO_OBSERVABILITY_REPAIR_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
