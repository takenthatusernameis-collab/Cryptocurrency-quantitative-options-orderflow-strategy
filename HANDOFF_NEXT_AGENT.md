# HANDOFF_NEXT_AGENT — Cryptocurrency quantitative options orderflow strategy

Generated: 2026-11-06T19:25:49Z (UTC)
Repo: `Cryptocurrency-quantitative-options-orderflow-strategy`
Branch: `main` (verify with `git status --short`)
Priority basis: Repo name => **Crypto options orderflow (multi-venue) + execution/hedging + reconciliation gates**. All other work must serve this campaign until gates pass.

## Mission (repo-name priority)
Deliver a **live-trading-ready, paper-gated** crypto **options orderflow** strategy: multi-venue ingestion (Deribit/OKX/Binance) → options/IV/liquidity/GEX + orderflow features → composite/orderflow signals → execution + delta-neutral options hedging → backtest → reconciliation/monitoring. **No live capital.** Every claim must have timestamped artifacts and gates.

## Verified current state (this session)
- Stack: 44+ `src/` modules, 375 tests, campaigns phase1..phase110+, synthetic/raw data in `data/`.
- Env runnable: `pydantic`, `pytest`, `mypy` installed in `.venv`. `PYTHONPATH` must be **project root** (not `src/`).
- Env sanity proven: `import pydantic, pytest, mypy, pandas, numpy, yaml, scipy` OK.
- Backtest unblocked: `PYTHONPATH=<root> python scripts/run_backtest_synthetic.py` → `total_trades=2`, `equity_final=100000.15976002` (non-flat). Artifact: `research_state/BACKTEST_SYNTHETIC_20261106T191907Z.json`.
- Targeted tests green: `tests/test_backtest_trades_synthetic.py`, `tests/test_backtest*.py`, `tests/test_integrated_campaign.py`, `tests/test_live_trading_readiness.py` → **102 passed**; plus `tests/test_reconciliation_freshness.py` → **105 passed total**.
- Features: `data/processed/features_latest.json` exists; `src/pipelines/build_features.py` materializes atomically.
- Signals: `src/signals/orderflow_signal.py` present (`OrderflowSignalGenerator`).
- **RECONCILIATION FRESHNESS FIXED (INIT blocker cleared):** `rec_freshness` no longer hardcoded `1.0` at `src/monitoring/continuous_monitor.py:249`; now real age-vs-60s-window freshness emitted + recorded as `SLIType.RECONCILIATION_FRESHNESS` so `slo_reconciliation_freshness >= 0.99` is genuinely evaluated (`met=true`, `current_value=0.9999786615371704`). Wired into E2E path via `scripts/run_integrated_campaign.py run`. Regression coverage: `tests/test_reconciliation_freshness.py` (3 tests).
- Evidence artifacts: `research_state/RECONCILIATION_FRESHNESS_FIX_20261106T192549Z.json`, `research_state/DRAWDOWN_ACK_20261106T192549Z.json`.

## Bottlenecks removed/mitigated (do not reintroduce)
1. **Mypy noise**: scoped mypy to campaign modules → 130 errors across 36 files, all pre-existing `phase79`/`phase80` monitoring noise files. Documented as pre-existing noise with `file:line` — **do not mass-fix**. This change introduced no new mypy errors.
2. **Test suite inefficiency**: full `pytest -q` (375 files) can timeout (>5 min). Run targeted subsets for velocity; full suite = nightly gate only.
3. **Reconciliation freshness gap**: **RESOLVED.** `rec_freshness` now computed from real last-reconciliation age vs the 60s window and recorded as an SLI; `slo_reconciliation_freshness >= 0.99` genuinely met. See `research_state/RECONCILIATION_FRESHNESS_FIX_20261106T192549Z.json`.

## SINGLE INITIAL TASK (durable — do first, no skipping)

**Task ID:** `INIT-20261106T190441Z-FIX-RECONCILIATION-FRESHNESS` — **COMPLETE** (2026-11-06T19:25:49Z)
**Status:** All steps done; reconciliation freshness blocker cleared, drawdown alert acknowledged with evidence, 105 targeted tests green.

**NEXT TASK (do second, no skipping):**

**Task ID:** `NEXT-20261106T192549Z-E2E-LIVE-TRADING-READINESS`
**Priority:** P0 (campaign gate `END2END_LIVE_TRADING_READINESS`)
**Time budget:** Complete this campaign before any new feature scope.

### Steps (concrete, verifiable)
1. **Env sanity (reconfirm)**
   - `. .venv/bin/activate`
   - `python -c "import pydantic, pytest, mypy, pandas, numpy, yaml, scipy; print('ok')"`
2. **Run E2E integrated campaign (paper) and capture reconciliation freshness**
   - `PYTHONPATH=<root> python scripts/run_integrated_campaign.py run --campaign-id e2e_readiness_1 --seed 42 --n-points 500 --train-window 120 --test-window 40 --step-size 40`
   - Confirm `reconciliation.slo.met == true` and `reconciliation.freshness >= 0.99` in JSON output.
   - Save output to `research_state/E2E_READINESS_20261106T<UTC>.json`.
3. **Non-flat backtest evidence per scenario**
   - `PYTHONPATH=<root> python scripts/run_backtest_synthetic.py` → confirm `total_trades > 0`, `equity_final != initial_capital`, `sharpe_ratio` finite, `max_drawdown < 0.2`. Save artifact `research_state/BACKTEST_E2E_<UTC>.json`.
4. **Scoped mypy (document noise only)**
   - `PYTHONPATH=<root> python -m mypy src/signals src/pipelines src/backtest src/features src/execution src/risk/reconciliation* src/monitoring* src/validation* 2>&1 | tail -40`
   - All failures pre-existing phase79/80 noise; document `file:line`, do not expand scope.
5. **Targeted tests green** (must pass): same 5 files as step 1 above (105 passed).
6. **Delta-neutral hedge PnL attribution**
   - Confirm `options_hedging_total_pnl` present and separate directional vs hedge PnL attribution in campaign output. Save `research_state/HEDGE_ATTRIBUTION_<UTC>.json`.
7. **Checkpoint**
   - Update `HANDOFF_NEXT_AGENT.md` with **next concrete checkpoint** (specific files/tasks/gates) + new artifacts with UTC timestamps. Do not say "continue research".

## HEAVY FOCUS CAMPAIGN (future agents cannot avoid doing heavy work)

**Campaign:** `END2END_LIVE_TRADING_READINESS`
**Objective:** Produce non-flat, reconciled, multi-venue end-to-end evidence that the options+orderflow strategy can trade under controls (paper-gated). No live capital.

### Scope (all required)
- **Data/features:** Ingest/load BTC,ETH × Deribit/OKX/Binance (recorded/synthetic only if labeled). Materialize to `data/processed/<venue>_<symbol>_<ts>.json|parquet` with schema/version/venue/symbol/timestamp metadata. Compute: cumulative delta, orderflow imbalance, GEX/delta-weighted/OI-volume-weighted GEX, gamma flip, IV surface/skew, liquidity, PCR, max pain.
- **Signals:** Use `src/signals/orderflow_signal.py` + `CompositeSignalGenerator`. Remove/configure any hard gate yielding 0 trades on valid directional flow. Thresholds config-driven and unit-tested.
- **Execution/backtest:** Event-driven with fees/slippage/position sizing/risk limits. Evaluate cross-venue orderflow arbitrage (paper). Implement delta-neutral options hedging leg with real position tracking; separate PnL attribution (directional vs hedge).
- **Reconciliation/monitoring:** Emit reconciliation freshness (must satisfy `slo_reconciliation_freshness >= 0.99`). Resolve/ack all open incidents with evidence.
- **Pipelines:** Complete `src/pipelines/` for reproducible runs; wire `scripts/` entrypoint (e.g. `scripts/run_e2e_campaign.py` or extend existing) producing campaign report.

### Required artifacts (timestamped UTC)
- `research_state/BACKTEST_E2E_<UTC>.json` (and/or full campaign report)
- `research_state/campaign_checkpoints/END2END_LIVE_TRADING_READINESS_latest.json` + immutable timestamped copy
- Processed feature files under `data/processed/` with metadata
- Incident resolution evidence under `research_state/` (reconciliation freshness fix, drawdown ack)
- Delta-neutral hedge attribution report (separate directional vs hedge PnL)

### Gates (campaign FAILS if any unmet)
- `total_trades > 0` and `equity_final != initial_capital` (non-flat) for at least primary scenario; report per scenario
- `sharpe_ratio` finite; `max_drawdown < 0.2` unless explicitly justified by paper stress test with evidence
- `slo_reconciliation_freshness >= 0.99` (met)
- Targeted tests green; scoped `mypy` clean (phase79/80 documented as noise)
- Delta-neutral hedge PnL attribution present and reconciled
- All open incidents resolved/acked with evidence artifacts

## Definition of done (checkpoint for next agent)
- [x] Env proven (imports OK).
- [x] Backtest non-flat confirmed with artifact (`BACKTEST_SYNTHETIC_20261106T191907Z.json`).
- [x] Targeted tests + scoped mypy reported with evidence (105 passed; 130 pre-existing phase79/80 mypy noise documented).
- [x] `slo_reconciliation_freshness >= 0.99` achieved with `RECONCILIATION_FRESHNESS_FIX_20261106T192549Z.json`.
- [x] Drawdown alert acked with `DRAWDOWN_ACK_20261106T192549Z.json`.
- [ ] At least one non-flat E2E/campaign artifact in `research_state/` with UTC timestamp (`E2E_READINESS_<UTC>.json` + `BACKTEST_E2E_<UTC>.json`).
- [ ] Delta-neutral hedge PnL attribution present and reconciled (`HEDGE_ATTRIBUTION_<UTC>.json`).
- [ ] `HANDOFF_NEXT_AGENT.md` updated with **next concrete checkpoint** (specific files/tasks/gates), not vague advice.

## Entry points
- Synthetic backtest: `PYTHONPATH=<root> python scripts/run_backtest_synthetic.py`
- Features: `PYTHONPATH=<root> python -m src.pipelines.build_features`
- CLI: `python -m src.main --config config/settings.yaml --json` (verify config path/fields)
- Conventions: Python 3.10, pydantic>=2.5, pandas/numpy/pyyaml/scipy; no comments unless asked; UTC ISO-8601 timestamps.

**Next agent instruction:** Execute Task `NEXT-20261106T192549Z-E2E-LIVE-TRADING-READINESS` in order. Do not run full 375-file pytest suite. Do not refactor phase79/80/phase110 mega-files. Focus on the paper E2E integrated campaign with genuine reconciliation freshness (`>= 0.99`), non-flat backtest evidence, and delta-neutral hedge attribution. Leave the handoff updated with a concrete next checkpoint after completion.
