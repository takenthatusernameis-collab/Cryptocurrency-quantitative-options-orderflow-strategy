import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.monitoring.phase82_deterministic_paper_only_continuous_validation_observability_hardening_loop import (
    Phase82DeterministicPaperOnlyContinuousValidationObservabilityHardeningLoop,
    Phase82DeterministicPaperOnlyContinuousValidationObservabilityHardeningConfig,
)


def test_phase82_deterministic_paper_only_continuous_validation_observability_hardening_loop_smoke():
    eng = Phase82DeterministicPaperOnlyContinuousValidationObservabilityHardeningLoop(
        Phase82DeterministicPaperOnlyContinuousValidationObservabilityHardeningConfig(seed=82011, cycles=50)
    )
    rep = eng.run_deterministic_paper_only_continuous_validation_observability_hardening(cycles=50)
    assert rep["phase"] == "PHASE82_DETERMINISTIC_PAPER_ONLY_CONTINUOUS_VALIDATION_OBSERVABILITY_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["validation_pass_rate_ok"] is True
    assert rep["gates"]["regression_guards_ok"] is True
    assert rep["gates"]["simulation_fidelity_ok"] is True
    assert rep["gates"]["observability_slo_ok"] is True
    assert rep["gates"]["strict_paper_gating_ok"] is True
