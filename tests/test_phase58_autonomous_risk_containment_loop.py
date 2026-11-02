from src.integration.phase58_autonomous_risk_containment_loop import Phase58AutonomousRiskContainmentLoop, Phase58AutonomousRiskContainmentConfig


def test_phase58_autonomous_risk_containment_loop_basic():
    cfg = Phase58AutonomousRiskContainmentConfig(seed=58060, cycles=40)
    loop = Phase58AutonomousRiskContainmentLoop(cfg)
    rep = loop.run_containment(cycles=40)
    assert rep["phase"] == "PHASE58_AUTONOMOUS_RISK_CONTAINMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["composed_phases"] == "17-57"
    assert isinstance(rep["pretrade_pass_rate"], float)
    assert isinstance(rep["posttrade_pass_rate"], float)


def test_phase58_autonomous_risk_containment_loop_artifacts(tmp_path):
    loop = Phase58AutonomousRiskContainmentLoop(Phase58AutonomousRiskContainmentConfig(seed=58160, cycles=20))
    rep = loop.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")
