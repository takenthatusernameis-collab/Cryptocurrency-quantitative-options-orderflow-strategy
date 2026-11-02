from src.hedging.phase49_orderflow_driven_delta_hedge import Phase49OrderflowDrivenDeltaHedge, Phase49HedgeConfig


def test_p49_delta_hedge_paper_only_and_structure():
    eng = Phase49OrderflowDrivenDeltaHedge(Phase49HedgeConfig(seed=49049, paper_only=True))
    rep = eng.run_campaign(cycles=10)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts("research_state")
    assert arts["json"].endswith(".json")
    assert arts["report"]["phase"] == "PHASE49_ORDERFLOW_DRIVEN_DELTA_HEDGE"


def test_p49_delta_hedge_toxicity_adjusted():
    eng = Phase49OrderflowDrivenDeltaHedge(Phase49HedgeConfig(seed=7, paper_only=True))
    eng.update_greeks({"BTC": {"delta": 0.3, "gamma": 0.02, "vega": 0.4, "theta": -0.05, "vanna": 0.01, "charm": -0.002, "net_notional": 1000000.0}})
    eng.assess_toxicity()
    acts = eng.rebalance()
    assert isinstance(acts, list)
    for a in acts:
        assert a.paper_only is True
        assert a.hedge_ratio >= 0.0
