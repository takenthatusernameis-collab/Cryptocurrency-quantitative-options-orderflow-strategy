from src.execution.phase51_latency_aware_options_sor import (
    Phase51LatencyAwareOptionsSOR,
    Phase51SORConfig,
)


def test_p51_sor_paper_only_and_gates():
    eng = Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=51052, paper_only=True))
    rep = eng.run_campaign(cycles=40)
    assert rep["paper_only"] is True
    assert rep["phase"] == "PHASE51_LATENCY_AWARE_OPTIONS_SOR"
    assert rep["gates_ok"] is True
    assert rep["n_routes"] == 40


def test_p51_sor_deterministic():
    def strip(rep):
        rep = dict(rep)
        for d in rep.get("routes", []):
            d.pop("timestamp", None)
        for t in rep.get("tcas", []):
            t.pop("timestamp", None)
        return rep

    a = strip(Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=4242, paper_only=True)).run_campaign(cycles=30))
    b = strip(Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=4242, paper_only=True)).run_campaign(cycles=30))
    assert a == b


def test_p51_sor_routing_decisions_finite():
    eng = Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=3, paper_only=True))
    rep = eng.run_campaign(cycles=25)
    for d in rep["routes"]:
        assert d["latency_ms"] >= 0
        assert 0.0 <= d["fill_probability"] <= 1.0
        assert d["toxicity_penalty_bps"] >= 0
        assert d["slippage_bps"] >= 0
        assert d["expected_cost_bps"] >= 0
        assert d["paper_only"] is True


def test_p51_sor_toxicity_aware_penalty():
    eng = Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=11, paper_only=True, toxicity_penalty_bps=20.0))
    rep = eng.run_campaign(cycles=20)
    for d in rep["routes"]:
        assert d["toxicity_penalty_bps"] <= 20.0 + 1e-9


def test_p51_sor_slicing_and_tca():
    eng = Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=22, paper_only=True, max_slices=8))
    rep = eng.run_campaign(cycles=20)
    assert rep["n_sliced"] >= 0
    for t in rep["tcas"]:
        assert t["implementation_shortfall_bps"] >= 0
        assert t["slippage_bps"] >= 0
        assert t["paper_only"] is True


def test_p51_sor_finite_and_json_serializable():
    import json

    eng = Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=7, paper_only=True))
    rep = eng.run_campaign(cycles=20)
    json.dumps(rep, allow_nan=False)
    arts = eng.generate_artifacts("research_state")
    assert arts["json"].endswith(".json")
    assert arts["md"].endswith(".md")
    assert arts["report"]["phase"] == "PHASE51_LATENCY_AWARE_OPTIONS_SOR"


def test_p51_sor_rejects_live_path():
    try:
        Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=1, paper_only=False))
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
