from src.alpha.phase62_execution_alpha_synthesis_engine import (
    Phase62ExecutionAlphaSynthesisEngine,
    Phase62ExecutionAlphaSynthesisConfig,
)


def test_phase62_execution_alpha_synthesis_basic():
    cfg = Phase62ExecutionAlphaSynthesisConfig(seed=62060, cycles=40)
    e = Phase62ExecutionAlphaSynthesisEngine(cfg)
    rep = e.synthesize_alpha(cycles=40)
    assert rep["phase"] == "PHASE62_EXECUTION_ALPHA_SYNTHESIS_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_synth"], int)
    assert isinstance(rep["avg_fused_alpha"], float)
    assert isinstance(rep["avg_position_scale"], float)


def test_phase62_execution_alpha_synthesis_artifacts(tmp_path):
    e = Phase62ExecutionAlphaSynthesisEngine(Phase62ExecutionAlphaSynthesisConfig(seed=62160, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase62_execution_alpha_synthesis_finite_and_paper_only():
    e = Phase62ExecutionAlphaSynthesisEngine(Phase62ExecutionAlphaSynthesisConfig(seed=62260, cycles=30))
    rep = e.synthesize_alpha(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_regime_weights"], int)
    assert isinstance(rep["n_sizing"], int)
    assert isinstance(rep["n_fused_alpha"], int)
