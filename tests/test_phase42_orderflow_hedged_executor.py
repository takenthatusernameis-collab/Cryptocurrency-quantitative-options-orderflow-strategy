from src.hedging.phase42_orderflow_hedged_executor import Phase42OrderflowHedgedExecutor, HedgedExecutorConfig42


def test_phase42_orderflow_hedging_paper_only_and_sizing():
    h = Phase42OrderflowHedgedExecutor(HedgedExecutorConfig42(seed=44, cycles=6))
    plan = h.plan_hedge(1, portfolio_delta_usd=200000.0, portfolio_gamma_usd=80000.0)
    assert plan.paper_only is True
    assert isinstance(plan.execution_ok, bool)
    assert plan.hedge_budget_utilization >= 0.0
    assert plan.avg_slippage_est_bps >= 0.0


def test_phase42_orderflow_campaign_deterministic():
    h = Phase42OrderflowHedgedExecutor(HedgedExecutorConfig42(seed=55, cycles=12))
    rep = h.run_campaign(12)
    assert rep["phase"] == "PHASE42_ORDERFLOW_HEDGED_EXECUTOR"
    assert rep["paper_only"] is True
    assert rep["execution_ok_all"] in (True, False)


def test_phase42_orderflow_reports(tmp_path):
    h = Phase42OrderflowHedgedExecutor(HedgedExecutorConfig42(seed=9, cycles=4))
    res = h.generate_reports(str(tmp_path))
    assert "json" in res
