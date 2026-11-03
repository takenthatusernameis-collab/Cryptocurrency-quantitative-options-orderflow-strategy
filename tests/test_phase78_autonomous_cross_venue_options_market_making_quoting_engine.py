import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.mm.phase78_autonomous_cross_venue_options_market_making_quoting_engine import (
    Phase78AutonomousCrossVenueOptionsMarketMakingQuotingEngine,
    Phase78AutonomousCrossVenueOptionsMarketMakingQuotingEngineConfig,
)


def test_phase78_autonomous_cross_venue_options_market_making_quoting_engine_smoke():
    eng = Phase78AutonomousCrossVenueOptionsMarketMakingQuotingEngine(
        Phase78AutonomousCrossVenueOptionsMarketMakingQuotingEngineConfig(seed=7801, cycles=40)
    )
    rep = eng.run_autonomous_cross_venue_mm_quoting(cycles=40)
    assert rep["phase"] == "PHASE78_AUTONOMOUS_CROSS_VENUE_OPTIONS_MARKET_MAKING_QUOTING_ENGINE"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["quotes_authorized_ok"] is True
