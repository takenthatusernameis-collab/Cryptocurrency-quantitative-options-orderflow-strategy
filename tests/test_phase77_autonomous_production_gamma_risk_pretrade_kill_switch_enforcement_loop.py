from src.integration.phase77_autonomous_production_gamma_risk_pretrade_kill_switch_enforcement_loop import (
    Phase77AutonomousProductionGammaRiskPretradeKillSwitchEnforcementLoop,
    Phase77AutonomousProductionGammaRiskPretradeKillSwitchEnforcementLoopConfig,
)


def test_phase77_autonomous_production_gamma_risk_pretrade_kill_switch_enforcement_loop_smoke():
    eng = Phase77AutonomousProductionGammaRiskPretradeKillSwitchEnforcementLoop(
        Phase77AutonomousProductionGammaRiskPretradeKillSwitchEnforcementLoopConfig(seed=7703, cycles=40)
    )
    rep = eng.run_gamma_risk_pretrade_kill_switch_loop(cycles=40)
    assert rep["phase"] == "PHASE77_AUTONOMOUS_PRODUCTION_GAMMA_RISK_PRETRADE_KILL_SWITCH_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
