# INITIAL_TASK_HANDOFF - Cryptocurrency quantitative options orderflow strategy

Generated: 2026-11-06T17:19:03Z
Repo: Cryptocurrency-quantitative-options-orderflow-strategy
Branch: main

## Initial task (single durable handoff - do NOT skip)

Task 1 (BLOCKER, do first): Unblock the backtest so it actually trades.
- Read src/backtest/engine.py, src/signals/composite.py, src/campaign/integrated.py, scripts/run_backtest_synthetic.py.
- Reproduce: PYTHONPATH=src python scripts/run_backtest_synthetic.py -> total_trades == 0.
- Relax entry threshold (abs(of_imbalance) > 0.001 or abs(cum_delta) > 0); keep risk guards.
- Re-run until total_trades > 0 and equity_final != initial_capital; assert sharpe_ratio and max_drawdown finite.
- Add tests/test_backtest_trades_synthetic.py asserting total_trades > 0.
- Run pytest tests/test_backtest*.py -q and pytest tests/test_integrated_campaign.py -q; all pass.
- Run mypy src/ and pytest -q (full suite) before proceeding.

Then Task 2: clear open incidents (drawdown alert r_drawdown_pct; slo_reconciliation_freshness).
Then Task 3: CAMPAIGN_PHASE_END2END_LIVE_TRADING_READINESS (paper->live gate), gates total_trades>0, sharpe finite>0, max_drawdown<0.2, reconciliation_freshness met, tests+mypy clean; output must not be flat equity.

Definition of done: pytest -q green, mypy src/ clean, one backtest report total_trades>0 committed to research_state/ with UTC timestamp, HANDOFF_NEXT_AGENT.md updated.
