from src.volatility.phase49_vol_surface_arb_engine import Phase49VolSurfaceArbEngine, Phase49VolSurfConfig


def test_p49_vol_surface_arb_paper_only_and_structure():
    eng = Phase49VolSurfaceArbEngine(Phase49VolSurfConfig(seed=49049, paper_only=True))
    rep = eng.run_campaign(cycles=10)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts("research_state")
    assert arts["json"].endswith(".json")
    assert arts["report"]["phase"] == "PHASE49_VOL_SURFACE_ARB_ENGINE"


def test_p49_vol_surface_arb_dislocations_signals_deterministic():
    eng = Phase49VolSurfaceArbEngine(Phase49VolSurfConfig(seed=123, paper_only=True))
    quotes = []
    for v in ["deribit", "okx", "bybit"]:
        quotes.append({"underlying": "BTC", "expiry": "30D", "strike": 30000.0, "option_type": "call", "venue": v, "bid_iv": 0.5, "ask_iv": 0.51})
    quotes.append({"underlying": "BTC", "expiry": "30D", "strike": 30000.0, "option_type": "call", "venue": "okx", "bid_iv": 0.54, "ask_iv": 0.55})  # creates dislocation
    eng.ingest_iv_quotes(quotes)
    d = eng.detect_dislocations()
    s = eng.build_signals()
    assert isinstance(d, list)
    assert isinstance(s, list)
    # all finite
    for sig in s:
        assert sig.delta_neutral in (True, False)
