from src.integration.phase59_autonomous_execution_hardening_loop import Phase59AutonomousExecutionHardeningLoop, Phase59AutonomousExecutionHardeningConfig


def test_phase59_autonomous_execution_hardening_basic():
    cfg = Phase59AutonomousExecutionHardeningConfig(seed=59061, cycles=40)
    l = Phase59AutonomousExecutionHardeningLoop(cfg)
    rep = l.run_hardening(cycles=40)
    assert rep["phase"] == "PHASE59_AUTONOMOUS_EXECUTION_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_failovers"], int)
    assert isinstance(rep["posttrade_pass_rate"], float)


def test_phase59_autonomous_execution_hardening_artifacts(tmp_path):
    l = Phase59AutonomousExecutionHardeningLoop(Phase59AutonomousExecutionHardeningConfig(seed=59161, cycles=20))
    rep = l.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase59_autonomous_execution_hardening_composition_and_paper_only():
    l = Phase59AutonomousExecutionHardeningLoop(Phase59AutonomousExecutionHardeningConfig(seed=59261, cycles=30))
    rep = l.run_hardening(cycles=30)
    assert rep["paper_only"] is True
    assert rep["composed_phases"] == "17-58"
    assert isinstance(rep["n_containments"], int)
    assert isinstance(rep["n_rollbacks"], int)
