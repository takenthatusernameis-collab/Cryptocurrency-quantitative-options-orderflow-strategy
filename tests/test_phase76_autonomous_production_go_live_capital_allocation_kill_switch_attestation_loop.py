from src.integration.phase76_autonomous_production_go_live_capital_allocation_kill_switch_attestation_loop import (
    Phase76AutonomousProductionGoLiveCapitalAllocationKillSwitchAttestationLoop,
    Phase76AutonomousProductionGoLiveCapitalAllocationKillSwitchAttestationConfig,
)


def test_phase76_autonomous_production_go_live_capital_allocation_kill_switch_attestation_loop_smoke():
    eng = Phase76AutonomousProductionGoLiveCapitalAllocationKillSwitchAttestationLoop(
        Phase76AutonomousProductionGoLiveCapitalAllocationKillSwitchAttestationConfig(seed=7672, cycles=40)
    )
    rep = eng.run_capital_allocation_kill_switch_attestation_loop(cycles=40)
    assert rep["phase"] == "PHASE76_AUTONOMOUS_PRODUCTION_GO_LIVE_CAPITAL_ALLOCATION_KILL_SWITCH_ATTESTATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
