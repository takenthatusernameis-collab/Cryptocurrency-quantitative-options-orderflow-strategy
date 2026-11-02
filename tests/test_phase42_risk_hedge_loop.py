from src.integration.phase42_risk_hedge_loop import Phase42RiskHedgeLoop, Loop42Config


def test_phase42_loop_integration_paper_only():
    cfg = Loop42Config(seed=42, cycles=12, paper_only=True, modes="paper")
    loop = Phase42RiskHedgeLoop(cfg)
    rep = loop.run()
    assert rep["phase"] == "PHASE42_RISK_HEDGE_LOOP"
    assert rep["paper_only"] is True
    assert rep["modes"] == "paper"
    assert rep["gates_ok"] in (True, False)


def test_phase42_loop_composes_phases():
    cfg = Loop42Config(seed=99, cycles=8, paper_only=True, modes="paper")
    loop = Phase42RiskHedgeLoop(cfg)
    rep = loop.run()
    assert "PHASE39_KILL_SWITCHES" in rep["integrated_with"]
    assert "PHASE40_RECONCILIATION" in rep["integrated_with"]
    assert "PHASE41_SETTLEMENT" in rep["integrated_with"]
