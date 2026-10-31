# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T18:56:47Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (prioritize by repo name -> crypto options pricing/Greeks/IV + orderflow features)

Gate status: GREEN (405 passed, 0 failed, 2 skipped — verified 2026-10-31T18:56:47Z via `python -m pytest tests/ -q`). Working tree clean.

COMPLETED (DO NOT REDO):
- Phases 1-4b: data/loaders, features (orderflow/gamma/IV/liquidity/vol/pricing), time-series + walk-forward/OOS with purge/embargo, portfolio walk-forward, options hedging integrated.
- Phase 5 Regime OOS: COMPLETE (artifacts + module + tests).
- Phase 5 Portfolio Scaling: COMPLETE (engine.py allocation weights/turnover cap; tests/test_portfolio_scaling.py 14 tests; PORTFOLIO_SCALING_*.json artifacts).
- Phase 5 Hedging Robustness: COMPLETE (options_hedging.py PnL decomposition delta/gamma/vega/theta/residual; tests/test_options_hedging.py extended; HEDGING_ROBUSTNESS_*.json artifact).
- Phase 5 Campaign Resume Hardening: COMPLETE (`src/campaign/core.py` atomic checkpoints + state tracking + resume; `scripts/run_campaign.py` CLI run/resume/status/abort; `tests/test_campaign_resume.py` strengthened; research_state/CAMPAIGN_RESUME_20261031T175208Z.json).
- Phase 5 Telemetry/Serialization hardening: COMPLETE (profit_factor inf source fix in `src/backtest/engine.py`; tests aligned; gate restored GREEN).
- Phase 5 Options Pricing/Greeks/IV Adversarial Audit: COMPLETE (audit + adversarial tests pass; `research_state/OPTIONS_ADVERSARIAL_AUDIT_20261031T185310Z.json`; RESULTS_SUMMARY updated). All functions verified finite/deterministic/strict-serializable under extremes.

BOTTLENECKS REMOVED (THIS SESSION): None. Clean green baseline (405/405). All prior bottlenecks eliminated.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION - EXECUTE IMMEDIATELY, NO DEVIATION)

**BY REPO NAME - CRYPTO OPTIONS + ORDERFLOW IS THE DOMAIN. HEAVY QUANT IMPLEMENTATION ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY. SHIP CODE/TESTS/ARTIFACTS EVERY SESSION.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign.
STATE: All Phase 1-5 core items complete. Gate GREEN (405 passed, 0 failed). Clean baseline. Previous agent verified full adversarial audit of options pricing/Greeks/IV.

### MANDATORY INITIAL TASK: Phase 6 — Full End-to-End Integrated Campaign (CRYPTO OPTIONS + ORDERFLOW)
Repo = crypto options+orderflow. Build a production-grade integrated campaign that wires EVERYTHING together into one deterministic, resumable, fully-validated pipeline that exercises the full stack under crypto-realistic conditions. This is HEAVY implementation - no analysis-only work.

Implement and validate:

1) **Integrated Campaign Orchestrator Extension** (`src/campaign/integrated.py` new module): Create `IntegratedCampaign` that composes in order with strict no-lookahead: (a) data ingestion/validation, (b) feature engineering (orderflow/gamma/IV/liquidity/vol/pricing), (c) regime classification, (d) walk-forward/OOS with purge/embargo, (e) portfolio construction with allocation modes + turnover caps, (f) options hedging with PnL attribution/reconciliation, (g) strict serialization + artifact emission. All steps checkpointed atomically via existing CampaignOrchestrator.

2) **Crypto-Realistic Integrated Scenario** (`scripts/run_integrated_campaign.py` new CLI): Deterministic end-to-end run producing comprehensive artifacts. Must use crypto-realistic parameters (BTC/ETH style), multi-expiry options chains, orderflow signals, gamma exposure, IV surface construction/calibration, regime stratification. Support `run/resume/status` consistent with existing campaign CLI.

3) **Comprehensive Validation Suite** (`tests/test_integrated_campaign.py` new): Tests must cover full pipeline integration, no-lookahead enforcement across components, purge/embargo propagation, portfolio+hedging composition, strict serialization (`allow_nan=False`) for ALL artifacts, determinism (byte-identical reruns), checkpoint/resume mid-pipeline, atomicity on interruption simulation, finite-guard enforcement end-to-end. Minimum 15 substantive tests.

4) **Production Artifacts**: Emit timestamped integrated artifacts to `research_state/` including:
   - `INTEGRATED_CAMPAIGN_{YYYYMMDDTHHMMSSZ}.json` (full pipeline results with per-step metrics)
   - `INTEGRATED_CAMPAIGN_SUMMARY_{YYYYMMDDTHHMMSSZ}.json` (executive summary with all key metrics)
   - `INTEGRATED_CAMPAIGN_REGIMES_{YYYYMMDDTHHMMSSZ}.json` (regime-stratified integrated results)

5) **Documentation**: Update `research_state/RESULTS_SUMMARY.md` with a 'Phase 6: Full End-to-End Integrated Campaign (Crypto Options + Orderflow)' section with concrete metrics from the run.

## IMMEDIATE FIRST ACTIONS
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q   # must be 405 passing, 0 failures

# 2) Review existing campaign/orchestrator patterns
cat src/campaign/core.py | head -80
cat scripts/run_campaign.py | head -60

# 3) Understand full stack to integrate
ls src/backtest/ src/features/ src/portfolio/ 2>&1 | head -15

# 4) BUILD THE INTEGRATED CAMPAIGN - HEAVY IMPLEMENTATION REQUIRED
# Create src/campaign/integrated.py, scripts/run_integrated_campaign.py, tests/test_integrated_campaign.py
# Run full integrated campaign, produce artifacts, update RESULTS_SUMMARY.md
```

## HARD CONSTRAINTS
- **Heavy implementation required**: Full integrated pipeline wiring all components - substantial code, not just stubs.
- **No placeholders/TODOs/FIXMEs**: Production-grade, complete implementations.
- **Deterministic & reproducible**: Fixed seeds, purge/embargo enforced, no lookahead, strict serialization.
- **Fail-forward**: Extend existing APIs if needed; fix any integration issues found.
- **Ship every session**: New modules + CLI + tests + artifacts + RESULTS_SUMMARY update.
- **Don't redo completed phases**: All prior work is done - compose and integrate, don't reimplement from scratch.
- **Single handoff**: Update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.

## SUCCESS CRITERIA (MUST HIT BEFORE NEXT HANDOFF)
- [ ] Gate GREEN: `python -m pytest tests/ -q` (>=405 passing, 0 failures; new tests all passing)
- [ ] `src/campaign/integrated.py` implemented with full pipeline composition
- [ ] `scripts/run_integrated_campaign.py` CLI working (run/resume/status)
- [ ] `tests/test_integrated_campaign.py` with >=15 tests all passing
- [ ] Integrated artifacts emitted to `research_state/` (INTEGRATED_CAMPAIGN_*.json, summaries, regimes)
- [ ] `research_state/RESULTS_SUMMARY.md` updated with Phase 6 section
- [ ] Determinism verified (rerun produces identical key metrics)
- [ ] Full pipeline exercises: data/features/regimes/walkforward/portfolio/hedging with purge/embargo + strict serialization

## NEXT AGENT INSTRUCTION (CLEAR, TIMESTAMPED, NON-DEFERRABLE)
**EXECUTE NOW - NO QUESTIONS - NO DELAY**
- Timestamp: 2026-10-31T18:56:47Z
- Read this file first. All prior phases complete - compose/integrate, don't redo.
- **START IMMEDIATELY** on Phase 6 Full End-to-End Integrated Campaign. This is heavy implementation - build the full integrated pipeline wiring crypto options + orderflow stack together with campaign orchestration, checkpointing, validation, and comprehensive artifacts.
- Verify gate at start and end. Keep all tests green.
- Update this handoff before finishing with concrete evidence (files, commands, results, next focus).
