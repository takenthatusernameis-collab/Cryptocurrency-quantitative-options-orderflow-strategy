from src.marketmaking.phase50_toxicity_aware_options_mm import Phase50ToxicityAwareOptionsMM, Phase50MMConfig


def test_p50_toxicity_aware_options_mm_paper_only_and_structure():
    eng = Phase50ToxicityAwareOptionsMM(Phase50MMConfig(seed=50050, paper_only=True))
    rep = eng.run_campaign(cycles=30)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts("research_state")
    assert arts["json"].endswith(".json")
    assert arts["report"]["phase"] == "PHASE50_TOXICITY_AWARE_OPTIONS_MM"


def test_p50_toxicity_aware_options_mm_quotes_deterministic():
    eng = Phase50ToxicityAwareOptionsMM(Phase50MMConfig(seed=123, paper_only=True))
    quotes = eng.generate_quotes(mid_price=100.0, cycles=30)
    assert isinstance(quotes, list)
    assert len(quotes) > 0
    for q in quotes:
        assert q["paper_only"] is True
        assert q["ask"] >= q["bid"] - 1e-12
        assert isinstance(q["spread_bps"], float)
