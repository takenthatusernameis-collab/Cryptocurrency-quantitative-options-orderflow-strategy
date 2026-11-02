from src.alpha.phase51_adaptive_orderflow_alpha_fusion import (
    Phase51AdaptiveOrderflowAlphaFusion,
    Phase51AlphaFusionConfig,
)


def test_p51_alpha_fusion_paper_only_and_gates():
    eng = Phase51AdaptiveOrderflowAlphaFusion(Phase51AlphaFusionConfig(seed=51051, paper_only=True))
    rep = eng.run_campaign(cycles=40)
    assert rep["paper_only"] is True
    assert rep["phase"] == "PHASE51_ADAPTIVE_ORDERFLOW_ALPHA_FUSION"
    assert rep["gates_ok"] is True
    assert rep["n_alphas"] == 40
    assert 0 <= rep["n_gate_failures"] <= 40


def test_p51_alpha_fusion_deterministic():
    def strip(rep):
        rep = dict(rep)
        for al in rep.get("alphas", []):
            al.pop("ts", None)
        return rep

    a = strip(Phase51AdaptiveOrderflowAlphaFusion(Phase51AlphaFusionConfig(seed=777, paper_only=True)).run_campaign(cycles=30))
    b = strip(Phase51AdaptiveOrderflowAlphaFusion(Phase51AlphaFusionConfig(seed=777, paper_only=True)).run_campaign(cycles=30))
    assert a == b


def test_p51_alpha_fusion_weight_adaptation_and_decay():
    eng = Phase51AdaptiveOrderflowAlphaFusion(Phase51AlphaFusionConfig(seed=123, paper_only=True))
    rep = eng.run_campaign(cycles=20)
    weights = rep["weight_history"]
    assert set(weights.keys()) <= set(eng.weights.keys())
    for w in weights.values():
        assert isinstance(w, float)
    assert len(rep["selected_features"]) == eng.cfg.selected_features


def test_p51_alpha_fusion_regime_gating():
    eng = Phase51AdaptiveOrderflowAlphaFusion(Phase51AlphaFusionConfig(seed=9, paper_only=True))
    rep = eng.run_campaign(cycles=30)
    regimes = set(rep["regimes"].keys())
    assert regimes <= set(eng.cfg.regimes)
    for al in rep["alphas"]:
        assert al["gate_passed"] in (True, False)
        assert al["paper_only"] is True


def test_p51_alpha_fusion_finite_and_json_serializable():
    import json

    eng = Phase51AdaptiveOrderflowAlphaFusion(Phase51AlphaFusionConfig(seed=5, paper_only=True))
    rep = eng.run_campaign(cycles=25)
    payload = json.dumps(rep, allow_nan=False)
    assert isinstance(payload, str)
    arts = eng.generate_artifacts("research_state")
    assert arts["json"].endswith(".json")
    assert arts["md"].endswith(".md")
    assert arts["report"]["phase"] == "PHASE51_ADAPTIVE_ORDERFLOW_ALPHA_FUSION"


def test_p51_alpha_fusion_rejects_live_path():
    try:
        Phase51AdaptiveOrderflowAlphaFusion(Phase51AlphaFusionConfig(seed=1, paper_only=False))
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
