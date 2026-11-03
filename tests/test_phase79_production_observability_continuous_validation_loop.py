import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.monitoring.phase79_production_observability_continuous_validation_loop import (
    Phase79ProductionObservabilityContinuousValidationLoop,
    Phase79ProductionObservabilityContinuousValidationConfig,
)


def test_phase79_production_observability_continuous_validation_loop_smoke():
    eng = Phase79ProductionObservabilityContinuousValidationLoop(
        Phase79ProductionObservabilityContinuousValidationConfig(seed=7901, cycles=40)
    )
    rep = eng.run_production_observability_continuous_validation(cycles=40)
    assert rep["phase"] == "PHASE79_PRODUCTION_OBSERVABILITY_CONTINUOUS_VALIDATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["slo_observability_enforced"] is True
    assert rep["gates"]["continuous_validation_passed"] is True
    assert rep["gates"]["risk_ok"] is True
    assert rep["counts"]["slo_evals"] > 0
    assert rep["counts"]["observability_enforcements"] > 0
    assert rep["counts"]["validations"] > 0
