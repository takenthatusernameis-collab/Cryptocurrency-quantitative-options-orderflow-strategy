# HANDOFF_NEXT_AGENT — Cryptocurrency quantitative options orderflow strategy (SINGLE DURABLE HANDOFF)

Generated: **2026-11-06T23:25:09Z (UTC)**
Repo: `Cryptocurrency-quantitative-options-orderflow-strategy`
Branch: `main` (verify `git status --short`)
Workspace: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`

## Priority (from repo name)
**Crypto options orderflow (multi-venue) + execution/hedging + reconciliation gates.** All work serves: Deribit/OKX/Binance × BTC/ETH ingestion/features (cumulative delta, orderflow imbalance, GEX/gamma flip, IV/skew, liquidity, PCR/max pain) → composite/orderflow signals → event-driven execution/backtest (fees/slippage/risk limits) → delta-neutral options hedging with directional vs hedge PnL attribution → reconciliation/monitoring. **Paper-gated only. No live capital. No `LIVE_TRADING_ENABLED=true`.** Every claim needs timestamped, non-empty artifacts and passing gates.

## Verified state (ground truth, rechecked 2026-11-06T23:25:09Z)
- Stack: 44+ `src/` modules, 375 tests, phase campaigns; data in `data/`, evidence in `research_state/`.
- **Environment bottleneck (active):** no `.venv/` in workspace; `python3 -m pip show` shows `PyYAML` system but **`pydantic/pandas/numpy/scipy/pytest/mypy` not found** by `pip show` in current environment; prior handoff claimed `.venv` deps — **reconfirm env before running campaigns/tests**. `PYTHONPATH` must be project root.
- **Multi-venue features present (6):** `data/processed/{deribit,okx,binance}_{btc,eth}_20261106T210539Z.json` + `features_20261106T210539Z.json`/`features_latest.json`.
- **END2END_LIVE_TRADING_READINESS — completed:** `research_state/campaign_checkpoints/END2END_LIVE_TRADING_READINESS_latest.json` (+ immutable `END2END_LIVE_TRADING_READINESS_20261106T211035Z.json`) gates true. Evidence: `E2E_READINESS_20261106T210244Z.json` (freshness 0.999982, `slo_met=true`), `E2E_READINESS_MULTI_VENUE_20261106T210745Z.json` (0.999981, `slo_met=true`), `BACKTEST_E2E_20261106T210846Z.json` (15 trades, `equity_final!=100000`, Sharpe 2.8 finite, max_dd 0.012<0.2), `BACKTEST_E2E_MULTI_20261106T210846Z.json` (multi_venue, non-flat), `HEDGE_ATTRIBUTION_20261106T210937Z.json` (directional_pnl=1245.67, hedge_pnl=-892.34, net_pnl=353.33, `reconciled=true`), incidents acked (`RECONCILIATION_FRESHNESS_FIX_20261106T192549Z.json`, `DRAWDOWN_ACK_20261106T192549Z.json`).
- **PAPER_TRADING_PRE_LIVE_READINESS — evidence passed; checkpoint restored:** `PAPER_TRADING_CAMPAIGN_20261106T222609Z.json` / `RECONCILIATION_AUDIT_20261106T222609Z.json` / `PRE_LIVE_GATE_REPORT_20261106T222609Z.json` are non-empty; gate report `READY FOR PAPER TRADING`, 18/18 passed, `failed=0`, `all/critical_passed=true`. Missing checkpoint files added this session: `campaign_checkpoints/PAPER_TRADING_PRE_LIVE_READINESS_20261106T232349Z.json` + `_latest.json` (paper, `LIVE_TRADING_ENABLED=false`).
- **CONTINUOUS_VALIDATION — NOT campaign-complete:** only `CONTINUOUS_VALIDATION_20261101T004750Z.json` exists (old, `seed=42`, 1-run Phase 9 artifact). It shows `slo_reconciliation_freshness` **`met=false`, `num_measurements=0`** in that run — **stale/unreconciled for this SLI**. No 5/5-iteration `CONTINUOUS_VALIDATION_<recent UTC>.json`, no `CONTINUOUS_VALIDATION_AND_MONITORING_latest.json`. NEXT6 gate remains **open**.
- **Script interface mismatch (bottleneck):** `scripts/run_continuous_validation.py` CLI is `--symbols/--seed` only (no `--mode/--iterations/--strict` claimed by prior handoff). `scripts/run_paper_trading_campaign.py` CLI is `--mode/--gates-only/--strict-gates` (matches). Both require `PYTHONPATH=<root>` and deps (paper script imports `pydantic` transitively). Do **not** fail the campaign by inventing flags; use actual CLI and add iteration/strict orchestration if missing.
- **SLO wiring reality:** `src/monitoring/slo.py` defines `slo_reconciliation_freshness` (target 0.99, gte, 60s). `continuous_monitor.record_reconciliation()` computes/emits freshness SLI (`src/monitoring/continuous_monitor.py:226+`), but `run_continuous_validation.py` records latency/error/uptime/fill_rate only and **does not record reconciliation freshness** — explains `met=false, num_measurements=0` in old artifact. Fix/wire evidence path is part of NEXT6 heavy work.
- **Mypy/pre-existing noise:** prior scoped mypy reported 130 errors across 36 files, all pre-existing phase79/80 noise; touched-module runs in this campaign found no new errors introduced. Do not mass-refactor phase79/80/phase110 mega-files.

## Bottlenecks — clear in this order (significant progress blocked until done)
1. **Environment not runnable in-place:** create/activate `.venv` (or use system env with deps) and prove `import pydantic, pytest, mypy, pandas, numpy, yaml, scipy` + `PYTHONPATH=<root>`. Record exact env evidence in the first new artifact.
2. **Continuous validation lacks iteration/strict gates and reconciliation SLI recording:** `run_continuous_validation.py` runs once and never records `reconciliation_freshness`. NEXT6 cannot pass by rerunning the same broken shape. Add a paper-only iteration loop (`--iterations N`, default 5; `--strict`) and record genuine reconciliation freshness SLI (>=0.99, met) each iteration using the existing SLO/monitor reconciliation path; fail non-zero on unmet gates in `--strict`.
3. **CONTINUOUS_VALIDATION_AND_MONITORING checkpoint missing:** no `_latest.json` + immutable timestamped copy with gates/evidence.

## SINGLE INITIAL TASK (durable — do first, no skipping)
**Task ID:** `NEXT6-20261106T232509Z-CONTINUOUS-VALIDATION-RECON-SLO-HARDENING`
**Priority:** P0 (campaign gate `CONTINUOUS_VALIDATION_AND_MONITORING`)
**Mode:** **paper-only, no live capital, `LIVE_TRADING_ENABLED != true`, `TRADING_MODE=paper`**

### Steps (concrete, verifiable)
1. **Env sanity + guard (must produce evidence):** ensure deps available; run `. .venv/bin/activate` if created (or document exact interpreter). `python -c "import pydantic, pytest, mypy, pandas, numpy, yaml, scipy; print('ok')"`. Assert no live trading: config/secrets must not enable live (`LIVE_TRADING_ENABLED` false/unset for paper). Save env note in first artifact.
2. **Fix/wire continuous validation for the gate it claims:** extend `scripts/run_continuous_validation.py` (and/or `src/validation/continuous.py` / SLI recording) to support paper iterations and strictness consistent with NEXT6: run N iterations (target 5), each producing checks; **record `reconciliation_freshness` SLI** via the real reconciliation/SLO path so `slo_reconciliation_freshness >= 0.99` is `met=true` with measurements > 0 (not synthetic pass without measurement). Preserve existing useful behavior; keep changes scoped. Update CLI help truthfully.
3. **Run continuous validation (paper):** `PYTHONPATH=<root> python scripts/run_continuous_validation.py --iterations 5 --strict` (or the implemented equivalent; if flags differ, document and keep `--strict` semantics). Require **5/5 iterations passed, 0 failed, reconciliation freshness met >=0.99**.
4. **Re-run paper trading campaign:** `PYTHONPATH=<root> python scripts/run_paper_trading_campaign.py --mode paper --strict-gates` (and full run if gates-only was used first) → `all_critical_passed==true`, `failed==0`, recommendation READY.
5. **Targeted tests + scoped mypy:** run focused set covering touched code: at minimum `tests/test_reconciliation_freshness.py`, `tests/test_backtest_*.py`, `tests/test_integrated_campaign.py`, `tests/test_live_trading_readiness.py` plus any new/affected validation/monitoring tests. Scoped mypy on touched modules (`src/monitoring/`, `src/telemetry/`, `src/risk/`, `src/execution/`, `src/validation/`, `scripts/run_continuous_validation.py`) — **no new errors**; document pre-existing with `file:line`.
6. **Emit non-empty UTC artifacts:** `research_state/CONTINUOUS_VALIDATION_<UTC>.json` (includes per-iteration results, 5/5, reconciliation SLI met + measurements), `research_state/PAPER_TRADING_CAMPAIGN_<UTC>.json`, `research_state/RECONCILIATION_AUDIT_<UTC>.json`, `research_state/PRE_LIVE_GATE_REPORT_<UTC>.json`, and `research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json` + immutable `CONTINUOUS_VALIDATION_AND_MONITORING_<UTC>.json`.
7. **Checkpoint handoff:** update this file with completion status, exact artifact paths, gate results, any remaining blockers, and the **next concrete checkpoint** (specific files/tasks/gates). Do not write "continue research".

## Gates (FAIL if any unmet — empty/null/synthetic-without-measurement = fail)
- `all_critical_passed == true`, `failed == 0` (paper/pre-live)
- continuous validation **5/5 iterations passed, 0 failed** in `--strict` mode
- `slo_reconciliation_freshness >= 0.99` **met=true with measurements > 0** in the new continuous validation artifact
- targeted tests green; scoped mypy clean or pre-existing noise documented (no new errors)
- required artifacts non-empty with UTC timestamps
- `LIVE_TRADING_ENABLED != true`, paper-only

## HEAVY FOCUS CAMPAIGN (future agents cannot avoid)
**Campaign:** `CONTINUOUS_VALIDATION_AND_MONITORING` (Phase 9 hardening) — must produce **repeated, reconciled, paper-only** evidence that options+orderflow multi-venue operations sustain SLOs/risk/telemetry/order lifecycle. After this gate, the next heavy campaign is **`PAPER_RUNBOOK_DRILL_AND_GO_NO_GO`**: 3+ scheduled paper campaign runs over distinct UTC windows (or deterministic seeded runs with runbook evidence), incident injection/ack drill tied to reconciliation/drawdown/risk, operator runbook in `docs/` or `research_state/`, and a timestamped GO/NO-GO report that cites every prerequisite artifact — still **no live capital**. Do not start live enablement.

## Definition of done (for NEXT6)
- [ ] Env proven (imports OK) with evidence.
- [ ] Continuous validation CLI/logic supports iterations+strict and records real reconciliation freshness SLI.
- [ ] `CONTINUOUS_VALIDATION_<UTC>.json`: 5/5, 0 failed, recon freshness met w/ measurements.
- [ ] Fresh paper trading/reconciliation/pre-live artifacts all critical passed.
- [ ] Targeted tests green; scoped mypy no new errors.
- [ ] `CONTINUOUS_VALIDATION_AND_MONITORING_latest.json` + immutable checkpoint.
- [ ] Handoff updated with concrete next checkpoint.

## Next concrete checkpoint (after NEXT6 completes)
**NEXT7-<UTC>-PAPER-RUNBOOK-DRILL-AND-GO-NO-GO:** produce `research_state/RUNBOOK_DRILL_<UTC>.json`, 3x `research_state/PAPER_TRADING_CAMPAIGN_<UTC>_run{1..3}.json` (or clearly indexed), incident drill/ack evidence, `research_state/GO_NO_GO_REPORT_<UTC>.json` referencing all prerequisite gate artifacts/checkpoints; gate = all paper critical gates pass, recon SLO met, incidents acked, runbook present, recommendation explicit (GO for continued paper / NO-GO for live). Paper-only.

## Entry points / conventions
- `PYTHONPATH=<root> python scripts/run_continuous_validation.py ...` (verify actual CLI flags first)
- `PYTHONPATH=<root> python scripts/run_paper_trading_campaign.py --mode paper --strict-gates`
- `PYTHONPATH=<root> python scripts/run_integrated_campaign.py run ...`
- Python 3.10, pydantic>=2.5, pandas/numpy/pyyaml/scipy; UTC ISO-8601; no comments unless asked; do not refactor phase79/80/110 mega-files.
