# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T21:32:56Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE BY REPO NAME -> crypto options pricing/Greeks/IV + orderflow features). THIS IS THE ONLY SOURCE OF TRUTH FOR NEXT AGENT SESSION.

Gate status: GREEN (434 passed, 0 failed, 2 skipped — verified 2026-10-31T21:32:56Z via `python -m pytest tests/ -q`). Working tree clean.

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
**PRIORITIZE BY REPO NAME. LEAVE MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK. REMOVE BOTTLENECKS. BUILD NEXT FOCUS CAMPAIGN SO HEAVY WORK IS UNAVOIDABLE.**

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
- Timestamp: 2026-10-31T19:47:22Z
- **THIS IS THE SINGLE DURABLE HANDOFF. READ IT FIRST.** All prior phases complete - compose/integrate, don't redo.
- **IMMEDIATE FOCUS (MANDATORY):** Phase 6 — Full End-to-End Integrated Campaign (CRYPTO OPTIONS + ORDERFLOW). Build the COMPLETE integrated pipeline wiring crypto options + orderflow stack together with campaign orchestration, checkpointing, validation, and comprehensive artifacts. This is HEAVY implementation - do real engineering work.
- **REMOVE BOTTLENECKS:** Fix anything blocking integration (imports, wiring, serialization) as you go. Do not stop at stubs.
- **FAIL-FORWARD:** Extend existing APIs if needed to make full integration work cleanly.
- **SHIP:** Every deliverable above (modules/CLI/tests/artifacts/RESULTS_SUMMARY) must be produced in this session.
- **NEVER AVOID HEAVY WORK.** If something is complex, implement it properly.
- Verify gate at start and end. Keep all tests green.
- **BEFORE ENDING:** Update THIS FILE (durable_handoff.md) with fresh UTC timestamp, exact files changed, concrete rationale, verification commands+results, and updated remaining work (or confirm Phase 6 complete per success criteria). Also ensure research_state/RESULTS_SUMMARY.md is updated.



## NEXT FOCUS CAMPAIGN (PHASE 7): Production Execution, Real-Time Risk & Orderflow Microstructure Hardening (CRYPTO OPTIONS + ORDERFLOW)
Timestamp (UTC): 2026-10-31T21:36:30Z
Repo domain: CRYPTO OPTIONS + ORDERFLOW QUANT. HEAVY PRODUCTION IMPLEMENTATION ONLY. NO PLACEHOLDERS.

State: Phase 6 COMPLETE. Gate GREEN (434 passed, 2 skipped, 0 failed). Integrated pipeline operational with artifacts/resume/checkpoints.

### OBJECTIVE
Harden the integrated crypto options+orderflow system for production execution: realistic execution (fees/slippage/latency, order routing, partial fills), hard real-time risk controls integrated end-to-end, orderflow microstructure robustness (gamma walls, liquidity sweeps, footprint/signed flow) with adversarial validation, latency-aware delta/gamma hedging, and production telemetry/monitoring. Must be fully tested, deterministic, serializable, and ship artifacts.

### MANDATORY DELIVERABLES
1) **Execution Engine** (`src/execution/engine.py` new or extend): Production-grade execution simulator/routing for crypto options + spot hedges. Include fees (maker/taker), slippage models (linear/impact), latency (order->fill), partial fills, queue position, rejects, idempotent order IDs. Deterministic seeded behavior.
2) **Risk Integration Layer** (`src/risk/execution_integration.py` new): Wire RiskManager/CircuitBreaker/KillSwitch into execution path with pre-trade checks, post-trade limits, kill-switch propagation, block/hold/flatten logic. Enforce no-trade on breach, full audit trail.
3) **Orderflow Microstructure Hardening** (`src/features/orderflow_microstructure.py` extend/new): Harden features (signed volume, footprint imbalance, gamma walls, liquidity sweeps, OFI, trade aggressor) with NaN/Inf guards, regime-aware normalization, lookahead-free, crypto-realistic distributions. Add adversarial tests.
4) **Latency-Aware Hedging** (`src/backtest/options_hedging.py` extend): Support latency-delayed rebalances, stale greeks detection, partial-hedge on latency, hedge slippage/fees, attribution including execution cost. Deterministic.
5) **Production Telemetry & Monitoring** (`src/telemetry/monitor.py` new + `scripts/run_production_campaign.py`): Real-time-style metrics (PnL, drawdown, greeks, gamma exposure, VaR/ES, heat, limits utilization), alerts, structured logging, artifact emission. CLI with run/resume/status/abort.
6) **Comprehensive Tests** (`tests/test_production_execution_risk.py`, `tests/test_orderflow_microstructure.py`): >=25 substantive tests covering execution, risk wiring, microstructure adversarial, latency hedging, determinism, strict serialization, no-lookahead.
7) **Artifacts**: Emit to `research_state/` `PRODUCTION_CAMPAIGN_{TS}.json`, `RISK_AUDIT_{TS}.json`, `MICROSTRUCTURE_ADVERSARIAL_{TS}.json`, update `RESULTS_SUMMARY.md` with Phase 7 section.

### IMMEDIATE FIRST ACTIONS
```bash
python -m pytest tests/ -q  # confirm GREEN
ls src/execution/ src/risk/ src/features/ src/telemetry/ 2>&1 | head -20
grep -rn "RiskManager\|CircuitBreaker" src 2>&1 | head -10
grep -rn "orderflow" src/features 2>&1 | head -15
```

### HARD CONSTRAINTS
- Production-grade, no stubs/placeholders/TODOs
- Deterministic, purge/embargo where applicable, train-only where applicable, no-lookahead
- Strict serialization allow_nan=False everywhere
- Fail-forward, extend existing APIs
- Wire risk controls into execution (hard enforcement)
- Ship modules/CLI/tests/artifacts/RESULTS_SUMMARY every session
- Single handoff: update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification, remaining work

### SUCCESS CRITERIA
- [ ] Gate GREEN: `python -m pytest tests/ -q` (>=434 passing, 0 failures)
- [ ] Execution engine + risk integration implemented and wired
- [ ] Microstructure hardened with adversarial tests passing
- [ ] Latency-aware hedging implemented with execution costs
- [ ] Production CLI working (run/resume/status/abort)
- [ ] New tests >=25 passing
- [ ] Artifacts emitted to research_state/
- [ ] RESULTS_SUMMARY.md updated with Phase 7
- [ ] Determinism + strict serialization verified end-to-end

### INITIAL TASK MESSAGE (EXECUTE IMMEDIATELY)
Timestamp: 2026-10-31T21:36:30Z
THIS IS THE SINGLE DURABLE HANDOFF. READ FIRST.
IMMEDIATE FOCUS: Phase 7 — Production Execution, Real-Time Risk & Orderflow Microstructure Hardening (CRYPTO OPTIONS + ORDERFLOW). Heavy implementation required.
REMOVE BOTTLENECKS. WIRE RISK INTO EXECUTION. HARDEN MICROSTRUCTURE. SHIP EVERYTHING.

BEFORE ENDING: Update THIS FILE with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.
