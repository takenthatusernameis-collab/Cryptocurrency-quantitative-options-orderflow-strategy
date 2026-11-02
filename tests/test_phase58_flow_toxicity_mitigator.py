from src.orderflow.phase58_flow_toxicity_mitigator import Phase58FlowToxicityMitigator, Phase58FlowToxicityMitigatorConfig


def test_phase58_flow_toxicity_mitigator_basic():
    cfg = Phase58FlowToxicityMitigatorConfig(seed=58058, cycles=40)
    m = Phase58FlowToxicityMitigator(cfg)
    rep = m.mitigate(cycles=40)
    assert rep["phase"] == "PHASE58_FLOW_TOXICITY_MITIGATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["avg_vpin"], float)
    assert isinstance(rep["n_quarantined"], int)


def test_phase58_flow_toxicity_mitigator_artifacts(tmp_path):
    m = Phase58FlowToxicityMitigator(Phase58FlowToxicityMitigatorConfig(seed=58158, cycles=20))
    rep = m.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")
