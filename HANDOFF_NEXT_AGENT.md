# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)
Repo: `Cryptocurrency-quantitative-options-orderflow-strategy`
Branch: `main` (working tree clean of tracked changes; untracked `.venv/` ignored)
Workspace: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
Session time (UTC): **2026-11-07T02:52:30Z**
Status: **PAPER-OPS READY (gates green). NEXT9 HUMAN-APPROVED LIVE ENABLEMENT: BLOCKED.** `LIVE_TRADING_ENABLED=false` (verified `src/config/secrets.py:69` default false, `.env.example:15`). `git diff --stat` empty. **No live capital. No live-enabling code/config. No implementation before recorded A1–A7 approvals.**

## TIMESTAMPED INITIAL TASK MESSAGE — HEAVY CAMPAIGN (MANDATORY)
**ID:** `INIT-20261107T025230Z-PAPER-OPS-CONTINUITY-NEXT9-BLOCKED-HEAVY`
**To:** next agentic work session
**Mode:** paper-only. `LIVE_TRADING_ENABLED=false`. No live capital.

**Execute now (no skipping, no status-only turns):**
1. **P0 Guardrails (every session, first):** Confirm `git diff --stat` clean of live-enabling changes; `LIVE_TRADING_ENABLED` default false; `.env.example` keeps `LIVE_TRADING_ENABLED=false`; no secrets committed. Refuse any request that would enable live capital without recorded A1–A7 approvals + approved NEXT9 campaign. **Record check in any additive artifact you produce.**
2. **P0 CV freshness before material decisions:** If latest strict CV is >~2h stale or you need material evidence, run fresh strict CV:
   `. .venv/bin/activate && PYTHONPATH=. python scripts/run_continuous_validation.py --iterations 5 --strict --symbols BTC,ETH --seed 42`
   Require: 5/5, 0 failed, `slo_reconciliation_freshness target_gte 0.99 met=true` with measurements `[1,1,1,1,1]`, paper-only, live not enabled. Write/cite additive timestamped artifacts + latest checkpoint.
3. **P0 Paper evidence integrity:** When consuming paper runs use `summary.all_critical_passed/failed` + campaign checkpoints (schema nuance R1: some top-level fields may be null). If integrity doubtful, run **3 paper campaign passes**:
   `. .venv/bin/activate && PYTHONPATH=. python scripts/run_paper_trading_campaign.py --mode paper --strict-gates`
   Cite fresh additive artifacts; require 18/18 critical, 0 failed per pass (or explain with evidence).
4. **P1 Heavy quality/maintenance (must produce tangible output):** Pick at least one substantial paper-safe improvement with tests/artifacts — e.g. tighten reconciliation/freshness alert evidence, improve deterministic paper-campaign/runbook automation, add targeted regression tests for CV/paper/pre-live gate edge cases, or reduce a specific operational risk (R3–R7) with evidence. **Do not** mass-refactor `phase79/80/110` mega-files. Run targeted tests for touched scope. Baseline scoped mypy (pre-existing, unchanged): **40 errors / 13 files** under `src/monitoring src/telemetry src/validation` — **introduce NO new scoped mypy errors**.
5. **P0 NEXT9 remains blocked until human action:** A1–A7 **NOT recorded/approved**. If explicit A1–A7 approvals are provided, record them in **additive timestamped artifacts** (approver identity, UTC timestamps, venue/symbol scope, notional/position/delta/drawdown/rate/slippage limits, A3 canary, A4 rehearsal evidence, A5 credential controls confirmation, A6 rollback owner, A7 live-disabled-until-approved decision) and update/cite proposal state. **Do not implement live enablement before approvals recorded.** After approvals only: narrowly scoped, venue-limited, canary-capped, kill-switch/circuit-breaker/reconciliation-halt/rollback-proven, non-enabling credential-verified, separately defined NEXT9 campaign with latest+immutable checkpoints.

**Definition of done (minimum):** ≥1 additive timestamped paper-ops/CV/risk-reduction artifact **and** targeted tests for any touched code **and** guardrails verified **and** this handoff updated with artifacts/blockers. Never claim NEXT9 unblocked without recorded A1–A7 approvals.

## Bottlenecks (fixed/controlled)
- **CV-latest pointer stale vs freshest immutable (fixed 2026-11-07T02:52Z):** `CONTINUOUS_VALIDATION_AND_MONITORING_latest.json` now points to `20261107T023732Z` (5/5, 0 failed, recon freshness `slo_reconciliation_freshness target_gte 0.99 met=true`, measurements `[1,1,1,1,1]`, paper-only). Prior `001342Z` retained.
- **P0 human approvals missing:** A1–A7 unapproved — NEXT9 blocked. Cannot be removed by agent; record only when explicitly provided.
- **R1 schema nuance:** consume `summary.*` + checkpoints.
- **R2 pre-existing scoped mypy debt:** 40/13 monitoring/telemetry/validation; no new errors.
- **R3–R7:** venue/ops, credentials, execution/slippage, drift, human-process — require evidence/rehearsal in any approved NEXT9.
- **Historical CI diagnostics noise:** `research_state/workflow_run_diagnostics.jsonl` has old run signals; not paper-gate/live evidence.

## Verified ground truth (cite these)
- **Continuity refresh (latest):** `research_state/campaign_checkpoints/PAPER_OPERATIONS_CONTINUITY_REFRESH_latest.json` = `..._20261107T023814Z.json` (completed, paper-only, `live_trading_enabled:false`, `next9_unblocked:false`, A1–A7 not approved).
- **Strict CV (fresh):** `research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json` = `..._20261107T023732Z.json` (5/5, 0 failed, recon freshness met w/ measurements). Raw: `OBSERVABILITY_REPORT_20261107T023732Z.json`, `ALERT_AUDIT_20261107T023732Z.json`, `HEALTH_SLO_REPORT_20261107T023732Z.json`, `RESILIENCE_AUDIT_20261107T023732Z.json`, `CONTINUOUS_VALIDATION_20261107T023732Z.json`.
- **Paper campaign (fresh):** `PAPER_TRADING_CAMPAIGN_20261107T023814Z.json` (18/18 critical, 0 failed, `summary.all_critical_passed=true`), `RECONCILIATION_AUDIT_20261107T023814Z.json`, `PRE_LIVE_GATE_REPORT_20261107T023814Z.json`.
- **NEXT8 review-only:** `research_state/campaign_checkpoints/LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY_latest.json` = `..._20261107T014236Z.json`; proposal `research_state/LIVE_ENABLEMENT_PROPOSAL_20261107T014236Z.{md,json}`; decision `NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL`; A1–A7 unapproved.
- **GO/NO-GO:** `research_state/GO_NO_GO_REPORT_20261107T010101Z.json` — GO continued paper ops / NO-GO live capital.
- **Runbook / drill:** `docs/PAPER_RUNBOOK.md`; `research_state/INCIDENT_DRILL_20261107T010035Z.json`.
- **Prerequisite checkpoints:** END2END `..._20261106T211035Z`; PAPER_PRE_LIVE `..._20261106T232349Z`; PAPER_RUNBOOK_DRILL_GO_NO_GO `..._20261107T010101Z`.

## Entry points / conventions
- Activate: `. .venv/bin/activate && PYTHONPATH=<repo> python ...`
- Strict CV: `python scripts/run_continuous_validation.py --iterations 5 --strict --symbols BTC,ETH --seed 42`
- Paper campaign: `python scripts/run_paper_trading_campaign.py --mode paper --strict-gates`
- Python 3.10/3.12 env present; pydantic/pandas/numpy/pyyaml/scipy. UTC ISO-8601. Additive timestamped artifacts only. No comments unless asked. No refactor of phase79/80/110 mega-files.
- Repo priority (paper-gated): crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **No live capital.**

## Next agent: start by executing P0 guardrails + P0 CV freshness check, then complete P1 heavy tangible work + additive artifact + handoff update.
