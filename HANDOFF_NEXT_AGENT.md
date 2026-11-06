# HANDOFF_NEXT_AGENT — Cryptocurrency quantitative options orderflow strategy

Generated: 2026-11-06T17:30:00Z (UTC)
Repo: `Cryptocurrency-quantitative-options-orderflow-strategy`
Branch: `main` (verify with `git status --short`)

## Mission (repo-name priority)
Deliver a **live-trading-ready, paper-gated** crypto **options orderflow** strategy: multi-venue ingestion (Deribit/OKX/Binance) → options/IV/liquidity/GEX + orderflow features → composite/orderflow signals → execution + delta-neutral options hedging → backtest → reconciliation/monitoring. **No live capital.** Every claim must have timestamped artifacts and gates.

## Current state (verified this session)
- Stack present: 44+ `src/` modules, 375 tests, campaigns phase1..phase110+, synthetic/raw data in `data/`.
- **Environment now runnable**: `pydantic`, `pytest`, `mypy` installed into `.venv`. `PYTHONPATH` must be the **project root** (not `src/`).
- Backtest unblocked: `PYTHONPATH=<root> python scripts/run_backtest_synthetic.py` → `total_trades=2`, `equity_final=100000.15976002` (non-flat), finite metrics. Artifact `research_state/BACKTEST_SYNTHETIC_20261106T172843Z.json`.
- `tests/test_backtest_trades_synthetic.py` passes; focused backtest subset `tests/test_backtest*.py` → 35 passed.
- `data/processed/features_latest.json` exists; `build_features.py` materializes features atomically.
- `src/signals/orderflow_signal.py` present (`OrderflowSignalGenerator`, imbalance-thresholded).
- `src/pipelines/build_features.py` present but pipeline scope incomplete for end-to-end readiness.

## Open incidents (do not ignore)
1. **slo_reconciliation_freshness = 0.0 vs 0.99** — **hard blocker for live-trading readiness.** No reconciliation heartbeat/freshness emitted in validation path. Wire freshness emission in E2E/campaign runner; add regression asserting SLO met when reconciliation ran within window. See `research_state/INCIDENT_TRIAGE_20261106T172016Z.md`.
2. **r_drawdown_pct (alert_6863a5540ff6)** — drawdown 0.12 > 0.1 warning, unack/unresolved. Paper decision: acknowledge as expected for synthetic stress; require evidence before live. Next agent must implement explicit ack/resolve handling with evidence artifacts.
3. **mypy noise bottleneck**: `mypy src/` reports 5796 errors across 325 files, dominated by auto-generated `src/risk/phase110_live_execution_*_ultra_deep_*.py` files (missing return types, attr-defined errors). Do not fix phase110 by hand unless in campaign scope. Scope mypy to campaign-relevant modules (`src/signals`, `src/pipelines`, `src/backtest`, `src/features`, `src/execution`) and document phase110 as pre-existing noise with file:line.
4. **Test suite inefficiency**: full `pytest -q` (375 files) times out (>5 min). Run targeted subsets (`test_backtest*.py`, `test_integrated_campaign.py`, `test_live_trading_readiness.py`) for velocity; treat full suite as a nightly gate, not a per-session gate.

## SINGLE INITIAL TASK (durable, do first — no skipping)

### Task A — Prove the unblock in a real test env and lock the gates
1. Env: `. .venv/bin/activate` (already created; deps installed). Confirm `python -c "import pydantic, pytest, mypy"`.
2. Backtest: `PYTHONPATH=<root> python scripts/run_backtest_synthetic.py` → confirm `total_trades > 0`, `equity_final != initial_capital`, finite metrics.
3. Tests: `PYTHONPATH=<root> python -m pytest tests/test_backtest_trades_synthetic.py tests/test_backtest*.py tests/test_integrated_campaign.py tests/test_live_trading_readiness.py -q` (must pass). Do not run the full 375-file suite interactively.
4. mypy scoped: `PYTHONPATH=<root> python -m mypy src/signals src/pipelines src/backtest src/features src/execution` → clean. Document any pre-existing failures in phase110/risk modules with file:line; do not hide them.
5. Keep tree clean; commit-ready evidence only when explicitly asked.

## HEAVY FOCUS CAMPAIGN (future agents cannot avoid)

### CAMPAIGN: `END2END_LIVE_TRADING_READINESS` (paper → live gate)
**Objective:** produce non-flat, reconciled, multi-venue end-to-end evidence that the options+orderflow strategy can trade under controls.

**Scope (all required):**
- **Data/features:** ingest/load BTC,ETH × deribit,okx,binance (recorded/synthetic fallback only if labeled). Materialize processed features to `data/processed/<venue>_<symbol>_<ts>.json|parquet` with schema/version metadata. Compute: cumulative delta, orderflow imbalance, GEX/delta-weighted/OI-volume-weighted GEX, gamma flip, IV surface/skew, liquidity, PCR, max pain.
- **Signals:** use `src/signals/orderflow_signal.py` + `CompositeSignalGenerator`; no hard gate that yields 0 trades on valid directional flow. Thresholds config-driven and tested.
- **Execution/backtest:** event-driven path with fees/slippage/position sizing/risk limits. Add cross-venue orderflow arbitrage signal evaluation (paper) and delta-neutral options hedging leg with real position tracking (PnL attribution separated: directional vs hedge).
- **Reconciliation/monitoring:** emit reconciliation freshness; resolve/ack open incidents with evidence artifacts. `slo_reconciliation_freshness` must be met (`>=0.99`) in campaign report.
- **Pipelines:** complete `src/pipelines/` for reproducible runs; wire `scripts/` entrypoint.

**Artifacts (timestamped, UTC):**
- `research_state/BACKTEST_E2E_<UTC>.json` and/or campaign report with per-venue/symbol metrics.
- `research_state/campaign_checkpoints/END2END_LIVE_TRADING_READINESS_latest.json` + immutable timestamped copy.
- Processed feature files under `data/processed/`.
- Incident resolution evidence under `research_state/`.

**Gates (fail campaign if any unmet):**
- `total_trades > 0` and `equity_final != initial_capital` (not flat) for at least the primary scenario; report per scenario.
- `sharpe_ratio` finite; `max_drawdown < 0.2` unless explicitly justified by paper stress test.
- `slo_reconciliation_freshness` met (`>=0.99`); r_drawdown_pct handled with evidence.
- `pytest` targeted subset green; scoped `mypy` clean.
- Delta-neutral hedge PnL attribution present and reconciled.

## Definition of done (this/next session checkpoint)
- Runnable env proven; targeted tests + scoped mypy status reported with evidence.
- At least one non-flat E2E/campaign backtest artifact committed to `research_state/` with UTC timestamp.
- `HANDOFF_NEXT_AGENT.md` updated with the *next* concrete checkpoint after END2END_LIVE_TRADING_READINESS progress (no vague "continue research").

## Entry points
- Synthetic backtest: `PYTHONPATH=<root> python scripts/run_backtest_synthetic.py`
- Feature build: `PYTHONPATH=<root> python -m src.pipelines.build_features`
- CLI: `python -m src.main --config config/settings.yaml --json` (verify config path/fields)
- Conventions: Python 3.10, pydantic>=2.5, pandas/numpy/pyyaml/scipy; no comments unless asked; UTC ISO-8601 timestamps.
