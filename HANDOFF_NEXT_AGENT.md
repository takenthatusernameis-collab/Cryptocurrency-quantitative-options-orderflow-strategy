# HANDOFF_NEXT_AGENT — Cryptocurrency quantitative options orderflow strategy (SINGLE DURABLE HANDOFF)

Generated: **2026-11-07T01:28:49Z (UTC)**
Repo: `Cryptocurrency-quantitative-options-orderflow-strategy`
Branch: `main` (verify `git status --short --branch`; workspace shows untracked `.venv/` only)
Workspace: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
Current session status: NEXT8 (review-only live-enablement proposal) is PENDING — no `LIVE_ENABLEMENT_PROPOSAL_*` artifact exists; all prerequisite checkpoints verified present at 2026-11-07T01:28:49Z.

## Priority (from repo name)
**Crypto options orderflow (multi-venue) + execution/hedging + reconciliation gates.** All work serves: Deribit/OKX/Binance × BTC/ETH ingestion/features (cumulative delta, orderflow imbalance, GEX/gamma flip, IV/skew, liquidity, PCR/max pain) → composite/orderflow signals → event-driven execution/backtest (fees/slippage/risk limits) → delta-neutral options hedging with directional vs hedge PnL attribution → reconciliation/monitoring. **Paper-gated only. No live capital. No `LIVE_TRADING_ENABLED=true`.** Every claim needs timestamped, non-empty artifacts and passing gates.

## Verified state (ground truth, 2026-11-07T01:01:01Z)
- Stack: 44+ `src/` modules, 375+ tests, phase campaigns; additive evidence in `research_state/`.
- **Environment proven:** `.venv/` runnable. `. .venv/bin/activate && PYTHONPATH=. python -c "import pydantic,pytest,pandas,numpy,yaml,scipy,mypy; print('deps ok')"` → `deps ok`.
- **END2END_LIVE_TRADING_READINESS — completed:** `research_state/campaign_checkpoints/END2END_LIVE_TRADING_READINESS_latest.json` (+ immutable `..._20261106T211035Z.json`).
- **PAPER_TRADING_PRE_LIVE_READINESS — completed:** `research_state/campaign_checkpoints/PAPER_TRADING_PRE_LIVE_READINESS_latest.json` (+ immutable `..._20261106T232349Z.json`).
- **CONTINUOUS_VALIDATION_AND_MONITORING — completed:** strict 5/5, 0 failed, paper-only, `live_trading_enabled=false`, `slo_reconciliation_freshness target_gte 0.99 met=true` with measurements `[1,1,1,1,1]`. `research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json` (+ immutable `..._20261107T001342Z.json`).
- **PAPER_RUNBOOK_DRILL_AND_GO_NO_GO (NEXT7) — completed 2026-11-07T01:01:01Z:**
  - **3 paper campaign runs, all critical passed, 0 failed (18/18):** `research_state/PAPER_TRADING_CAMPAIGN_20261107T002933Z_run1.json`, `...002937Z_run2.json`, `...002941Z_run3.json` (indexed; each `summary.all_critical_passed==true`, `failed==0`).
  - **Incident injection/ack drill (reconciliation + drawdown/risk + circuit-breaker signal), all passed:** `research_state/INCIDENT_DRILL_20261107T010035Z.json` — critical position mismatch auto-halt detected+acked+resolved; drawdown `RiskManager` kill-switch (`drawdown_pct_limit_breached`, 15% > 10%) detected+acked+resolved; circuit breaker failure-path exercised/reviewed. Paper-only, controlled.
  - **Operator runbook:** `docs/PAPER_RUNBOOK.md` (env, CLI, artifact locations, thresholds, incident ack steps, explicit no-live guardrails).
  - **GO/NO-GO report (cites all prerequisites):** `research_state/GO_NO_GO_REPORT_20261107T010101Z.json` — recommendation **“GO for continued paper operations / NO-GO for live capital enablement”**; `all_gates_passed=true`.
  - **Checkpoint:** `research_state/campaign_checkpoints/PAPER_RUNBOOK_DRILL_AND_GO_NO_GO_latest.json` + immutable `..._20261107T010101Z.json`.
- **Guardrail state:** `LIVE_TRADING_ENABLED` remains `false`; no live capital authorized.

## Bottlenecks / risks (address before/during NEXT8)
1. **No human-reviewed live-enablement proposal exists:** live capital remains blocked; NEXT8 is review-only (no enablement code/config).
2. **Paper campaign JSON schema nuance:** indexed run files expose `summary.all_critical_passed/failed` (canonical); some top-level/report fields may be null — NEXT8/ops should consume `summary.*` and checkpoint evidence, not ad-hoc top-level fields.
3. **Pre-existing scoped mypy debt:** 40 errors in 13 files under `src/monitoring src/telemetry src/validation` (phase74/79/80 hardening) — unchanged; do not mass-refactor phase79/80/110 mega-files.
4. **`research_state/` is large:** additive timestamped artifacts only; no destructive cleanup.

## SINGLE INITIAL TASK (durable — do first, no skipping)
**Task ID:** `NEXT8-20261107T010101Z-LIVE-ENABLEMENT-PROPOSAL-REVIEW-ONLY`
**Priority:** P0 (campaign gate `LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY`)
**Mode:** **review-only, paper-gated. No live capital. No `LIVE_TRADING_ENABLED=true`. No code/config that enables live trading.**

### Steps (concrete, verifiable)
1. **Confirm prerequisites (cite, do not re-run heavy campaigns unless missing):** END2END, PAPER_TRADING_PRE_LIVE_READINESS, CONTINUOUS_VALIDATION_AND_MONITORING, PAPER_RUNBOOK_DRILL_AND_GO_NO_GO latest+immutable checkpoints; `docs/PAPER_RUNBOOK.md`; `GO_NO_GO_REPORT_20261107T010101Z.json`; 3 indexed paper runs; `INCIDENT_DRILL_20261107T010035Z.json`.
2. **Produce review-only proposal:** write `research_state/LIVE_ENABLEMENT_PROPOSAL_<UTC>.md` and/or `.json` summarizing: all paper gates passed, residual risks (schema nuance, pre-existing mypy debt, operational/venue/credential risks), required operator controls, kill-switch/limits/circuit-breaker posture, venue credential boundaries (secrets never committed; least privilege; paper vs live separation), reconciliation/drawdown monitoring cadence, and rollback/disable procedure.
3. **Explicit approval checklist (human gate):** include a checklist requiring explicit human approval before any future live-enablement campaign; state **live remains disabled** and **`LIVE_TRADING_ENABLED` must not be set true** by this task.
4. **No enablement changes:** verify no diff enables live trading (no `LIVE_TRADING_ENABLED=true`, no live mode defaults changed for production paths). If any code/doc changes are made, run targeted tests for touched scope and scoped mypy with **no new errors**.
5. **Checkpoint:** write `research_state/campaign_checkpoints/LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY_latest.json` + immutable timestamped copy with gate booleans, artifact paths, and `live_trading_enabled:false`.
6. **Handoff update:** replace this file with completion status, exact artifacts, blockers, and the next concrete checkpoint (which must remain non-enabling unless a separately defined, explicitly approved campaign exists).

## Gates (FAIL if any unmet)
- Proposal cites all prerequisite checkpoints/artifacts listed above.
- Proposal states residual risks, operator controls, kill-switch/limits, credential boundaries, monitoring/rollback.
- Explicit human-approval checklist present; **live remains NO-GO/disabled**.
- No code/config enables live trading; `LIVE_TRADING_ENABLED != true`.
- `LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY` checkpoint latest + immutable.
- Any touched code: targeted tests green, scoped mypy no new errors.

## HEAVY FOCUS CAMPAIGN (future agents cannot avoid)
**Campaign:** `LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY` — produce an **operator-grade, review-only live-enablement proposal** that binds every paper gate to explicit controls and human approval. After completion, **do not enable live trading**. The next step, if ever taken, must be a **separately defined, explicitly human-approved live-enablement campaign** with its own gates/checkpoints and zero ambiguity.

## Definition of done (for NEXT8)
- [ ] Prerequisites cited with paths/timestamps.
- [ ] `LIVE_ENABLEMENT_PROPOSAL_<UTC>.md`/`.json` written.
- [ ] Residual risks + controls + kill-switch/limits + credential boundaries + rollback documented.
- [ ] Explicit human approval checklist; live remains disabled.
- [ ] No live-enabling diff; `LIVE_TRADING_ENABLED != true`.
- [ ] `LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY` checkpoint latest + immutable.
- [ ] Handoff updated with concrete next checkpoint.

## Next concrete checkpoint (after NEXT8 completes)
**NEXT9-<UTC>-HUMAN-APPROVED-LIVE-ENABLEMENT-CAMPAIGN (BLOCKED pending explicit human approval):** only if explicit human approval is recorded in artifacts, define narrow, venue-scoped, limit-capped live-enablement gates with kill-switch drills, credential verification, and rollback proof. **Until then, no implementation; live remains disabled.**

## Entry points / conventions
- `. .venv/bin/activate && PYTHONPATH=<root> python ...`
- `python scripts/run_continuous_validation.py --iterations 5 --strict --symbols BTC,ETH --seed 42`
- `python scripts/run_paper_trading_campaign.py --mode paper --strict-gates`
- Python 3.10, pydantic>=2.5, pandas/numpy/pyyaml/scipy; UTC ISO-8601; no comments unless asked; do not refactor phase79/80/110 mega-files.
