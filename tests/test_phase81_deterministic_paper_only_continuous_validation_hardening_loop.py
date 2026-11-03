import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.monitoring.phase81_deterministic_paper_only_continuous_validation_hardening_loop import (
    Phase81DeterministicPaperOnlyContinuousValidationHardeningLoop,
    Phase81DeterministicPaperOnlyContinuousValidationHardeningConfig,
)


def test_phase81_deterministic_paper_only_continuous_validation_hardening_loop_smoke():
    eng = Phase81DeterministicPaperOnlyContinuousValidationHardeningLoop(
        Phase81DeterministicPaperOnlyContinuousValidationHardeningConfig(seed=81088, cycles=50)
    )
    rep = eng.run_deterministic_paper_only_continuous_validation_hardening(cycles=50)
    assert rep["phase"] == "PHASE81_DETERMINISTIC_PAPER_ONLY_CONTINUOUS_VALIDATION_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["validation_pass_rate_ok"] is True
    assert rep["gates"]["regression_guards_ok"] is True
    assert rep["gates"]["simulation_fidelity_ok"] is True
    assert rep["gates"]["strict_paper_gating_ok"] is True
