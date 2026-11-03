import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.monitoring.phase80_deterministic_paper_only_continuous_validation_hardening_loop import (
    Phase80DeterministicPaperOnlyContinuousValidationHardeningLoop,
    Phase80DeterministicPaperOnlyContinuousValidationHardeningConfig,
)


def test_phase80_deterministic_paper_only_continuous_validation_hardening_loop_smoke():
    eng = Phase80DeterministicPaperOnlyContinuousValidationHardeningLoop(
        Phase80DeterministicPaperOnlyContinuousValidationHardeningConfig(seed=80091, cycles=40)
    )
    rep = eng.run_deterministic_paper_only_continuous_validation_hardening(cycles=40)
    assert rep["phase"] == "PHASE80_DETERMINISTIC_PAPER_ONLY_CONTINUOUS_VALIDATION_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["strict_paper_gating"] is True
    assert rep["gates"]["paper_only_enforced"] is True
    assert rep["gates"]["live_disabled"] is True
    assert rep["gates"]["deterministic_validation_ok"] is True
    assert rep["gates"]["regression_guard_strict_ok"] is True
    assert rep["gates"]["simulation_fidelity_ok"] is True
