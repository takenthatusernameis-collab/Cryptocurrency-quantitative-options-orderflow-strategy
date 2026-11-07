# HANDOFF_NEXT_AGENT — Cryptocurrency quantitative options orderflow strategy (SINGLE DURABLE HANDOFF)

Generated: **2026-11-07T00:14:30Z (UTC)**
Repo: `Cryptocurrency-quantitative-options-orderflow-strategy`
Branch: `main` (verify `git status --short --branch`)
Workspace: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`

## Priority (from repo name)
**Crypto options orderflow (multi-venue) + execution/hedging + reconciliation gates.** All work serves: Deribit/OKX/Binance × BTC/ETH ingestion/features (cumulative delta, orderflow imbalance, GEX/gamma flip, IV/skew, liquidity, PCR/max pain) → composite/orderflow signals → event-driven execution/backtest (fees/slippage/risk limits) → delta-neutral options hedging with directional vs hedge PnL attribution → reconciliation/monitoring. **Paper-gated only. No live capital. No `LIVE_TRADING_ENABLED=true`.** Every claim needs timestamped, non-empty artifacts and passing gates.

## Verified state (ground truth, rechecked 2026-11-07T00:14:30Z)
- Stack: 44+ `src/` modules, 375+ tests, phase campaigns; data in `data/`, evidence in `research_state/`.
- **Environment:** `.venv/` exists and is runnable in this workspace. Verified: `. .venv/bin/activate && PYTHONPATH=. python -c "import pydantic,pytest,pandas,numpy,yaml,scipy,mypy; print('deps ok')"` → `deps ok`. System `python3` may lack pytest; always use `.venv` + `PYTHONPATH=<root>`.
- **Multi-venue features present (6):** `data/processed/{deribit,okx,binance}_{btc,eth}_20261106T210539Z.json` + `features_20261106T210539Z.json`/`features_latest.json`.
- **END2END_LIVE_TRADING_READINESS — completed:** `research_state/campaign_checkpoints/END2END_LIVE_TRADING_READINESS_latest.json` (+ immutable `END2END_LIVE_TRADING_READINESS_20261106T211035Z.json`) gates true (freshness/SLO, non-flat/multi-venue backtest, hedge attribution reconciled, incidents acked).
- **PAPER_TRADING_PRE_LIVE_READINESS — completed:** prior checkpoint present; fresh strict run this session passed. `research_state/PAPER_TRADING_CAMPAIGN_20261107T001344Z.json`, `research_state/RECONCILIATION_AUDIT_20261107T001344Z.json`, `research_state/PRE_LIVE_GATE_REPORT_20261107T001344Z.json` — **18/18 gates passed, 0 failed, all critical passed, recommendation READY FOR PAPER TRADING, `--mode paper --strict-gates` exit 0**.
- **CONTINUOUS_VALIDATION_AND_MONITORING — completed (NEXT6 done this session):** `scripts/run_continuous_validation.py` now supports `--iterations N` and `--strict` (paper-only, `LIVE_TRADING_ENABLED=false`) and records reconciliation freshness via the real `ContinuousMonitor.record_reconciliation()`/SLO path (no synthetic pass without measurement). Run: `PYTHONPATH=. python scripts/run_continuous_validation.py --iterations 5 --strict --symbols BTC,ETH --seed 42` → **status complete, 5/5 iterations passed, 0 failed, `slo_reconciliation_freshness` target_gte 0.99 met=true, measurements_per_iteration `[1,1,1,1,1]`**. Artifacts: `research_state/CONTINUOUS_VALIDATION_20261107T001342Z.json`, `OBSERVABILITY_REPORT_20261107T001342Z.json`, `ALERT_AUDIT_20261107T001342Z.json`, `HEALTH_SLO_REPORT_20261107T001342Z.json`, `RESILIENCE_AUDIT_20261107T001342Z.json`. Checkpoints: `research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json` + immutable `CONTINUOUS_VALIDATION_AND_MONITORING_20261107T001342Z.json`.
- **Targeted tests (touched gate coverage):** `tests/test_reconciliation_freshness.py`, `tests/test_backtest_trades_synthetic.py`, `tests/test_integrated_campaign.py`, `tests/test_live_trading_readiness.py` → **71 passed**.
- **Scoped mypy:** `scripts/run_continuous_validation.py` — **Success: no issues found**. Broader scoped run (`src/monitoring src/telemetry src/validation`) reports **40 pre-existing errors in 13 files** (phase74/79/80 hardening modules; e.g. `phase79_production_observability_continuous_validation_loop.py`, `phase80_deterministic_paper_only_continuous_validation_hardening_loop.py`, `phase74_continuous_slo_observability_enforcement_engine.py`) — **no new errors introduced by this session**. Do not mass-refactor phase79/80/110.

## Bottlenecks — clear before NEXT7 (significant progress blocked until done)
1. **No repeatable paper runbook/drill evidence across windows:** NEXT7 requires 3+ paper campaign runs over distinct UTC windows (or deterministic seeded/indexed runs with runbook evidence) — not yet present.
2. **No incident injection/ack drill tied to reconciliation/drawdown/risk with runbook:** prior E2E incidents were acked, but no fresh operator drill + GO/NO-GO report citing all prerequisite gates/checkpoints.
3. **No `docs/` or `research_state/` runbook + GO/NO-GO report:** required for NEXT7 completion.
4. **Guardrail:** `research_state/` is huge; avoid destructive cleanup. Emit additive, timestamped artifacts/checkpoints only. Keep `LIVE_TRADING_ENABLED != true`.

## SINGLE INITIAL TASK (durable — do first, no skipping)
**Task ID:** `NEXT7-20261107T001430Z-PAPER-RUNBOOK-DRILL-AND-GO-NO-GO`
**Priority:** P0 (campaign gate `PAPER_RUNBOOK_DRILL_AND_GO_NO_GO`)
**Mode:** **paper-only, no live capital, `LIVE_TRADING_ENABLED != true`, `TRADING_MODE=paper`**

### Steps (concrete, verifiable)
1. **Env sanity (must produce evidence):** `. .venv/bin/activate && PYTHONPATH=. python -c "import pydantic,pytest,pandas,numpy,yaml,scipy,mypy; print('deps ok')"`; record exact command/result in runbook or artifact metadata.
2. **Produce 3+ paper campaign runs with distinct evidence:** run `PYTHONPATH=. python scripts/run_paper_trading_campaign.py --mode paper --strict-gates` three times (or deterministic indexed runs) producing **3 clearly indexed, non-empty artifacts** (e.g. `PAPER_TRADING_CAMPAIGN_<UTC>_run1.json` … `_run3.json` or indexed copies with timestamps) — **each must show `all_critical_passed==true`, `failed==0`**. Cite latest CV checkpoint (`CONTINUOUS_VALIDATION_AND_MONITORING_latest.json`).
3. **Incident injection/ack drill (paper, reconciliation/drawdown/risk):** exercise at least reconciliation-freshness/mismatch and drawdown/risk gate paths in a controlled paper drill (use existing monitor/risk/campaign hooks or deterministic simulation; do not enable live). Emit `research_state/INCIDENT_DRILL_<UTC>.json` (or split drill artifacts) showing injected condition, detection, and **ack/resolution evidence** with timestamps.
4. **Operator runbook:** write `docs/PAPER_RUNBOOK.md` or `research_state/PAPER_RUNBOOK_<UTC>.md` covering: env activation, exact CLI commands, artifact locations, gate thresholds (paper critical, recon freshness >=0.99 met w/ measurements, CV 5/5 strict), incident response/ack steps, and explicit **no live capital / `LIVE_TRADING_ENABLED` must remain false**.
5. **GO/NO-GO report:** emit `research_state/GO_NO_GO_REPORT_<UTC>.json` referencing **every prerequisite artifact/checkpoint** (END2END, PAPER_TRADING_PRE_LIVE, CONTINUOUS_VALIDATION_AND_MONITORING checkpoints; latest E2E readiness/backtest/hedge; 3 paper runs; incident drill; runbook). Recommendation must be explicit: **GO for continued paper operations / NO-GO for live capital enablement** (live remains blocked unless separately gated by future explicit campaign).
6. **Checkpoint:** write `research_state/campaign_checkpoints/PAPER_RUNBOOK_DRILL_AND_GO_NO_GO_latest.json` + immutable timestamped copy with all gate booleans/evidence paths.
7. **Handoff update:** replace this file with completion status, exact artifacts, any blockers, and the next concrete checkpoint. Do not write "continue research".

## Gates (FAIL if any unmet)
- 3+ paper campaign run artifacts, each `all_critical_passed==true`, `failed==0`
- `slo_reconciliation_freshness >= 0.99` met with measurements in latest CV evidence
- incident injection/ack drill evidence present (reconciliation/drawdown/risk)
- operator runbook present
- `GO_NO_GO_REPORT` cites all prerequisites; recommendation explicit; **live = NO-GO unless/until separate campaign**
- `PAPER_RUNBOOK_DRILL_AND_GO_NO_GO` checkpoint latest + immutable
- `LIVE_TRADING_ENABLED != true`, paper-only
- targeted tests green if code changed; scoped mypy no new errors

## HEAVY FOCUS CAMPAIGN (future agents cannot avoid)
**Campaign:** `PAPER_RUNBOOK_DRILL_AND_GO_NO_GO` — produce **repeatable, operator-grade paper evidence**: 3+ strict paper runs, reconciliation/drawdown/risk incident drill with ack, runbook, and a GO/NO-GO report that ties every prior gate together. After this, only a **separately defined, explicitly approved live-enablement campaign** may be considered — **do not start live enablement, do not flip `LIVE_TRADING_ENABLED`**.

## Definition of done (for NEXT7)
- [ ] Env proven (imports OK) with evidence.
- [ ] 3+ indexed paper campaign artifacts, all critical passed.
- [ ] Latest CV recon SLO >=0.99 met w/ measurements cited.
- [ ] Incident injection/ack drill artifact(s) for reconciliation/drawdown/risk.
- [ ] Runbook written (`docs/PAPER_RUNBOOK.md` or `research_state/PAPER_RUNBOOK_<UTC>.md`).
- [ ] `GO_NO_GO_REPORT_<UTC>.json` cites prerequisites; explicit recommendation.
- [ ] `PAPER_RUNBOOK_DRILL_AND_GO_NO_GO_latest.json` + immutable checkpoint.
- [ ] Handoff updated with concrete next checkpoint.

## Next concrete checkpoint (after NEXT7 completes)
**NEXT8-<UTC>-LIVE-ENABLEMENT-PROPOSAL-REVIEW-ONLY:** produce `research_state/LIVE_ENABLEMENT_PROPOSAL_<UTC>.md`/`.json` summarizing all paper gates, residual risks, required operator controls, kill-switch/limits, venue credential boundaries, and an explicit **review-only** approval checklist. **No code/config that enables live trading. No `LIVE_TRADING_ENABLED=true`.** Gate = proposal cites all prerequisite artifacts/checkpoints and states live remains disabled pending explicit human approval.

## Entry points / conventions
- `. .venv/bin/activate && PYTHONPATH=<root> python ...` (use `.venv`; root = repo root)
- `python scripts/run_continuous_validation.py --iterations 5 --strict --symbols BTC,ETH --seed 42`
- `python scripts/run_paper_trading_campaign.py --mode paper --strict-gates`
- `python scripts/run_integrated_campaign.py run ...`
- Python 3.10, pydantic>=2.5, pandas/numpy/pyyaml/scipy; UTC ISO-8601; no comments unless asked; do not refactor phase79/80/110 mega-files.
