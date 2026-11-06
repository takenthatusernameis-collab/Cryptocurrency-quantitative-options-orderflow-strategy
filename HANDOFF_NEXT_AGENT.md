# HANDOFF_NEXT_AGENT — Cryptocurrency quantitative options orderflow strategy

Generated: 2026-11-06T19:04:41Z (UTC)
Repo: `Cryptocurrency-quantitative-options-orderflow-strategy`
Branch: `main` (verify with `git status --short`)
Priority basis: Repo name => **Crypto options orderflow (multi-venue) + execution/hedging + reconciliation gates**. All other work must serve this campaign until gates pass.

## Mission (repo-name priority)
Deliver a **live-trading-ready, paper-gated** crypto **options orderflow** strategy: multi-venue ingestion (Deribit/OKX/Binance) → options/IV/liquidity/GEX + orderflow features → composite/orderflow signals → execution + delta-neutral options hedging → backtest → reconciliation/monitoring. **No live capital.** Every claim must have timestamped artifacts and gates.

## Verified current state (this session)
- Stack: 44+ `src/` modules, 375 tests, campaigns phase1..phase110+, synthetic/raw data in `data/`.
- Env runnable: `pydantic`, `pytest`, `mypy` installed in `.venv`. `PYTHONPATH` must be **project root** (not `src/`).
- Env sanity proven: `import pydantic, pytest, mypy, pandas, numpy, yaml, scipy` OK.
- Backtest unblocked: `PYTHONPATH=<root> python scripts/run_backtest_synthetic.py` → `total_trades=2`, `equity_final=100000.15976002` (non-flat). Artifact: `research_state/BACKTEST_SYNTHETIC_20261106T190505Z.json`.
- Targeted tests green: `tests/test_backtest_trades_synthetic.py`, `tests/test_backtest*.py`, `tests/test_integrated_campaign.py`, `tests/test_live_trading_readiness.py` → **102 passed**.
- Features: `data/processed/features_latest.json` exists; `src/pipelines/build_features.py` materializes atomically.
- Signals: `src/signals/orderflow_signal.py` present (`OrderflowSignalGenerator`).

## Bottlenecks removed/mitigated (do not reintroduce)
1. **Mypy noise**: scoped mypy to campaign modules (`src/signals`, `src/pipelines`, `src/backtest`, `src/features`, `src/execution`, `src/risk/reconciliation*`, `src/monitoring*`, `src/validation*`) → 130 errors across 36 files, all in pre-existing `phase79`/`phase80` monitoring noise files (`phase79_production_observability_continuous_validation_loop.py`, `phase80_deterministic_paper_only_continuous_validation_hardening_loop.py`, etc.). Documented as pre-existing noise with `file:line` — **do not mass-fix**.
2. **Test suite inefficiency**: full `pytest -q` (375 files) can timeout (>5 min). Run targeted subsets for velocity; full suite = nightly gate only.
3. **Reconciliation freshness gap**: `slo_reconciliation_freshness` target `0.99` (gte, window 60s) registered in `src/monitoring/slo.py:415-418`, but `rec_freshness` is hardcoded `1.0` at `src/monitoring/continuous_monitor.py:249` — **not wired to real reconciliation runs**. Still a hard blocker until genuinely emitted from the E2E/campaign runner path with regression coverage.

## SINGLE INITIAL TASK (durable — do first, no skipping)

**Task ID:** `INIT-20261106T190441Z-FIX-RECONCILIATION-FRESHNESS`
**Priority:** P0 (blocks live-trading readiness gate `slo_reconciliation_freshness >= 0.99`)
**Time budget:** Complete within this session before expanding scope.

### Steps (concrete, verifiable)
1. **Env sanity (reconfirm)**
   - `. .venv/bin/activate`
   - `python -c "import pydantic, pytest, mypy, pandas, numpy, yaml, scipy; print('ok')"`
2. **Prove backtest path (non-flat) — reconfirm**
   - `PYTHONPATH=<root> python scripts/run_backtest_synthetic.py` → confirm `total_trades > 0`, `equity_final != initial_capital`, finite metrics. Latest artifact: `research_state/BACKTEST_SYNTHETIC_20261106T190505Z.json`.
3. **Targeted tests (must pass)** — reconfirm
   - `PYTHONPATH=<root> python -m pytest tests/test_backtest_trades_synthetic.py tests/test_backtest*.py tests/test_integrated_campaign.py tests/test_live_trading_readiness.py -q` (last run: 102 passed).
4. **Scoped mypy (document noise)** — reconfirm
   - `PYTHONPATH=<root> python -m mypy src/signals src/pipelines src/backtest src/features src/execution src/risk/reconciliation* src/monitoring* src/validation* 2>&1 | tail -40`
   - All failures are pre-existing phase79/80 monitoring noise; document with `file:line`, do not expand scope.
5. **Fix reconciliation freshness (hard blocker)**
   - Locate emission point: `src/monitoring/continuous_monitor.py:249` (`rec_freshness = 1.0` hardcoded).
   - Wire real reconciliation freshness into `monitor_cycle` / E2E campaign runner path used by `tests/test_integrated_campaign.py` so that when reconciliation runs within the 60s window, `slo_reconciliation_freshness >= 0.99` is genuinely emitted (reflect actual last-reconciliation age vs window).
   - Add/ensure regression coverage asserting freshness >= 0.99 when reconciliation ran within window.
   - Produce evidence artifact: `research_state/RECONCILIATION_FRESHNESS_FIX_<UTC>.json` with before/after values, code paths touched (`file:line`), and test results.
6. **Handle drawdown alert (paper-only)**
   - Address `r_drawdown_pct` (alert_6863a5540ff6) with explicit ack/resolve path + evidence artifact `research_state/DRAWDOWN_ACK_<UTC>.json` (scenarios, justification, paper-only confirmation).
7. **Checkpoint**
   - Update `HANDOFF_NEXT_AGENT.md` with **next concrete checkpoint** (do not say "continue research") and list new artifacts with UTC timestamps.

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
- [ ] Env proven (imports OK).
- [ ] Backtest non-flat confirmed with artifact.
- [ ] Targeted tests + scoped mypy reported with evidence.
- [ ] `slo_reconciliation_freshness >= 0.99` achieved with `RECONCILIATION_FRESHNESS_FIX_<UTC>.json`.
- [ ] Drawdown alert acked with `DRAWDOWN_ACK_<UTC>.json`.
- [ ] At least one non-flat E2E/campaign artifact in `research_state/` with UTC timestamp.
- [ ] `HANDOFF_NEXT_AGENT.md` updated with **next concrete checkpoint** (specific files/tasks/gates), not vague advice.

## Entry points
- Synthetic backtest: `PYTHONPATH=<root> python scripts/run_backtest_synthetic.py`
- Features: `PYTHONPATH=<root> python -m src.pipelines.build_features`
- CLI: `python -m src.main --config config/settings.yaml --json` (verify config path/fields)
- Conventions: Python 3.10, pydantic>=2.5, pandas/numpy/pyyaml/scipy; no comments unless asked; UTC ISO-8601 timestamps.

**Next agent instruction:** Execute Task INIT-20261106T190441Z-FIX-RECONCILIATION-FRESHNESS in order. Do not run full 375-file pytest suite. Do not refactor phase79/80/phase110 mega-files. Focus on wiring real reconciliation freshness emission + E2E non-flat evidence + drawdown ack. Leave the handoff updated with a concrete next checkpoint after completion.
