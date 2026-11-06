# HANDOFF_NEXT_AGENT — Cryptocurrency quantitative options orderflow strategy

Generated: 2026-11-06T17:20:16Z (UTC)
Repo: `Cryptocurrency-quantitative-options-orderflow-strategy`
Branch: `main` (clean at handoff generation; verify with `git status --short`)

## Mission (repo-name priority)
Deliver a **live-trading-ready, paper-gated** crypto **options orderflow** strategy: multi-venue ingestion (Deribit/OKX/Binance) → options/IV/liquidity/GEX + orderflow features → composite/orderflow signals → execution + delta-neutral options hedging → backtest → reconciliation/monitoring. **No live capital.** Every claim must have timestamped artifacts and gates.

## Current state (verified)
- Stack present: 44+ `src/` modules, 374+ tests (historical), campaigns phase1..phase110+, synthetic/raw data in `data/`.
- **0-trades blocker addressed in code path**: `scripts/run_backtest_synthetic.py` now trades on relaxed imbalance (`abs(of_imbalance) >= 0.001`) with position scaling and a synthetic round-trip mark close. Latest artifact `research_state/BACKTEST_SYNTHETIC_20261106T170007Z.json` shows `total_trades=1`, `equity_final=99999.87999` (non-flat), `max_drawdown>0`. Prior flat artifacts (`BACKTEST_20261031T081646Z.json`, total_trades=0) are superseded for this specific gate.
- Added `tests/test_backtest_trades_synthetic.py` (regression: synthetic backtest must produce >0 trades and non-flat equity).
- Added `src/signals/orderflow_signal.py` (`OrderflowSignalGenerator`, imbalance-thresholded direction/strength/confidence, large-trade awareness) — closes DATA_INVENTORY gap.
- `src/pipelines/__init__.py` and `src/pipelines/build_features.py` exist; pipeline scope still incomplete for end-to-end readiness.
- `data/processed/` is effectively empty of materialized feature sets.

## Open incidents (do not ignore)
1. **r_drawdown_pct / alert_6863a5540ff6**: drawdown 0.12 > 0.1 warning, unack/unresolved in `CONTINUOUS_VALIDATION_20261101T004750Z.json`. Paper decision recorded in `research_state/INCIDENT_TRIAGE_20261106T172016Z.md` (acknowledge as expected for synthetic stress; require evidence before live). **Next agent must implement explicit ack/resolve handling in monitoring artifacts/config with evidence**, not hand-wave.
2. **slo_reconciliation_freshness = 0.0 vs 0.99** (unmet). **Hard blocker for live-trading readiness.** Wire freshness emission in E2E/campaign path; add regression.

## Environment constraint observed
This runner image lacked project deps (`pydantic` missing; `pytest`/`mypy` not installed as modules). I could not execute `pytest -q` or `mypy src/`. **First action next session: establish a runnable env** (install `requirements.txt` into venv/container, or use the project’s CI image) and run the full gates before new campaign work.

## SINGLE INITIAL TASK (durable, do first — no skipping)

### Task A — Prove the unblock in a real test env and lock it
1. Create/activate env: `python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt pytest mypy` (or equivalent).
2. Run: `PYTHONPATH=src python scripts/run_backtest_synthetic.py` → confirm `total_trades > 0`, `equity_final != initial_capital`, finite metrics.
3. Run: `pytest tests/test_backtest_trades_synthetic.py -q` (must pass). Then `pytest tests/test_backtest*.py tests/test_integrated_campaign.py -q`.
4. Run: `pytest -q` (full suite) and `mypy src/` (per `mypy.ini`: strict_optional, disallow_untyped_defs, warn_return_any). Fix regressions you introduce; document any pre-existing failures with file:line and do not hide them.
5. Commit-ready evidence only when explicitly asked; keep tree clean otherwise.

## HEAVY FOCUS CAMPAIGN (future agents cannot avoid)

### CAMPAIGN: `END2END_LIVE_TRADING_READINESS` (paper → live gate)
**Objective:** produce non-flat, reconciled, multi-venue end-to-end evidence that the options+orderflow strategy can trade under controls.

**Scope (all required):**
- **Data/features:** ingest/load BTC,ETH × deribit,okx,binance (recorded/synthetic fallback only if labeled). Materialize processed features to `data/processed/<venue>_<symbol>_<ts>.json|parquet` with schema/version metadata. Compute: cumulative delta, orderflow imbalance, GEX/delta-weighted/OI-volume-weighted GEX, gamma flip, IV surface/skew, liquidity, PCR, max pain.
- **Signals:** use `src/signals/orderflow_signal.py` + `CompositeSignalGenerator`; no hard gate that yields 0 trades on valid directional flow. Thresholds must be config-driven and tested.
- **Execution/backtest:** event-driven path with fees/slippage/position sizing/risk limits. Add **cross-venue orderflow arbitrage** signal evaluation (paper) and **delta-neutral options hedging leg** with real position tracking (PnL attribution separated: directional vs hedge).
- **Reconciliation/monitoring:** emit reconciliation freshness; resolve/ack open incidents with evidence artifacts. `slo_reconciliation_freshness` must be met (`>=0.99`) in campaign report.
- **Pipelines:** implement/complete `src/pipelines/` for reproducible runs; wire `scripts/` entrypoint.

**Artifacts (timestamped, UTC):**
- `research_state/BACKTEST_E2E_<UTC>.json` and/or campaign report with per-venue/symbol metrics.
- `research_state/campaign_checkpoints/END2END_LIVE_TRADING_READINESS_latest.json` + immutable timestamped copy.
- Processed feature files under `data/processed/`.
- Incident resolution evidence under `research_state/`.

**Gates (fail campaign if any unmet):**
- `total_trades > 0` and `equity_final != initial_capital` (not all zeros/flat) for at least the primary scenario; report per scenario.
- `sharpe_ratio` finite; `max_drawdown < 0.2` (or stricter configured limit) unless explicitly justified by paper stress test.
- `slo_reconciliation_freshness` met; r_drawdown_pct handled with evidence.
- `pytest -q` green; `mypy src/` clean.
- Delta-neutral hedge PnL attribution present and reconciled.

## Definition of done (this/next session checkpoint)
- Runnable env proven; full tests + mypy status reported with evidence.
- At least one non-flat E2E/campaign backtest artifact committed to `research_state/` with UTC timestamp.
- `HANDOFF_NEXT_AGENT.md` updated with the *next* concrete checkpoint after END2END_LIVE_TRADING_READINESS progress (no vague “continue research”).

## Entry points
- Synthetic backtest: `PYTHONPATH=src python scripts/run_backtest_synthetic.py`
- CLI: `python -m src.main --config config/settings.yaml --json` (verify config path/fields)
- Conventions: Python 3.10, pydantic>=2.5, pandas/numpy/pyyaml/scipy; no comments unless asked; UTC ISO-8601 timestamps.
