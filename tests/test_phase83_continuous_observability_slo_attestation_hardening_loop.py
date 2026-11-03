import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.monitoring.phase83_continuous_observability_slo_attestation_hardening_loop import (
    Phase83ContinuousObservabilitySLOAttestationLoop,
    Phase83ContinuousObservabilitySLOAttestationConfig,
)


def test_phase83_continuous_observability_slo_attestation_smoke():
    eng = Phase83ContinuousObservabilitySLOAttestationLoop(
        Phase83ContinuousObservabilitySLOAttestationConfig(seed=83054, cycles=40)
    )
    rep = eng.run_continuous_observability_slo_attestation(cycles=40)
    assert rep["phase"] == "PHASE83_CONTINUOUS_OBSERVABILITY_SLO_ATTESTATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["validation_pass_rate_ok"] is True
    assert rep["gates"]["observability_slo_ok"] is True
    assert rep["gates"]["slo_attestation_ok"] is True
    assert rep["gates"]["strict_paper_gating_ok"] is True
    assert rep["gates"]["kill_switch_ok"] is True
