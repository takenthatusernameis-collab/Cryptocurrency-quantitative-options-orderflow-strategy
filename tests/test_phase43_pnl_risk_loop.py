from src.integration.phase43_pnl_risk_loop import Phase43PnlRiskLoop, Loop43Config


def test_phase43_loop_integration_paper_only():
    cfg = Loop43Config(seed=43, cycles=12, paper_only=True, modes="paper")
    loop = Phase43PnlRiskLoop(cfg)
    rep = loop.run()
    assert rep["phase"] == "PHASE43_PNL_RISK_LOOP"
    assert rep["paper_only"] is True
    assert rep["modes"] == "paper"
    assert "attribution_campaign" in rep
    assert rep["attribution_campaign"]["gates_ok"] is True


def test_phase43_loop_composes_phases():
    cfg = Loop43Config(seed=143, cycles=8, paper_only=True, modes="paper")
    loop = Phase43PnlRiskLoop(cfg)
    rep = loop.run()
    assert "PHASE39_KILL_SWITCHES" in rep["integrated_with"]
    assert "PHASE40_RECONCILIATION" in rep["integrated_with"]
    assert "PHASE41_SETTLEMENT" in rep["integrated_with"]
    assert "PHASE42_RISK_HEDGE" in rep["integrated_with"]
