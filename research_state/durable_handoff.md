# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T22:37:00Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE BY REPO NAME -> crypto options pricing/Greeks/IV + orderflow features/microstructure). THIS IS THE ONLY SOURCE OF TRUTH FOR NEXT AGENT SESSION.

Gate status: GREEN (434 passed, 2 skipped, 0 failed) — verified 2026-10-31T22:37:00Z via `python -m pytest tests/ -q`. Working tree clean.

COMPLETED (DO NOT REDO):
- Phases 1-4b: data/loaders, features (orderflow/gamma/IV/liquidity/vol/pricing), time-series + walk-forward/OOS with purge/embargo, portfolio walk-forward, options hedging integrated.
- Phase 5 Regime OOS: COMPLETE.
- Phase 5 Portfolio Scaling: COMPLETE (engine.py allocation weights/turnover cap; tests/test_portfolio_scaling.py).
- Phase 5 Hedging Robustness: COMPLETE (PnL decomposition delta/gamma/vega/theta/residual).
- Phase 5 Campaign Resume Hardening: COMPLETE (atomic checkpoints/resume/status/abort).
- Phase 5 Telemetry/Serialization hardening: COMPLETE.
- Phase 5 Options Pricing/Greeks/IV Adversarial Audit: COMPLETE (all finite/deterministic/strict-serializable).
- Phase 6 Full End-to-End Integrated Campaign (Crypto Options + Orderflow): COMPLETE (integrated.py, run_integrated_campaign.py, tests/test_integrated_campaign.py, artifacts emitted, RESULTS_SUMMARY updated).

BOTTLENECKS REMOVED: None. Clean green baseline. All prior bottlenecks eliminated. No blockers. Focus on heavy production hardening.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION - EXECUTE IMMEDIATELY, NO DEVIATION)
BY REPO NAME - CRYPTO OPTIONS + ORDERFLOW IS THE DOMAIN. HEAVY QUANT IMPLEMENTATION ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY. SHIP CODE/TESTS/ARTIFACTS EVERY SESSION.
PRIORITIZE BY REPO NAME. LEAVE MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK. REMOVE BOTTLENECKS. BUILD NEXT FOCUS CAMPAIGN SO HEAVY WORK IS UNAVOIDABLE.

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign.
STATE: Phase 6 COMPLETE. Gate GREEN (434 passed, 2 skipped, 0 failed). Integrated pipeline operational. Clean baseline.

### MANDATORY INITIAL TASK: Phase 7 — Production Execution, Real-Time Risk & Orderflow Microstructure Hardening (CRYPTO OPTIONS + ORDERFLOW)
Repo = crypto options+orderflow. Harden the integrated system for production execution with realistic fills/fees/slippage/latency, hard real-time risk controls wired end-to-end, orderflow microstructure robustness (gamma walls/liquidity sweeps/footprint/signed flow) with adversarial validation, latency-aware delta/gamma hedging with execution costs, and production telemetry/monitoring. This is HEAVY implementation - no analysis-only work.

Implement and validate:

1) **Execution Engine** (`src/execution/engine.py` new): Production-grade execution simulator/routing for crypto options + spot hedges. Fees (maker/taker), slippage models (linear/impact), latency (order->fill), partial fills, queue position, rejects, idempotent order IDs. Deterministic seeded behavior.
2) **Risk Integration Layer** (`src/risk/execution_integration.py` new): Wire RiskManager/CircuitBreaker/KillSwitch into execution path with pre-trade checks, post-trade limits, kill-switch propagation, block/hold/flatten logic. Enforce no-trade on breach, full audit trail.
3) **Orderflow Microstructure Hardening** (`src/features/orderflow_microstructure.py` new/extend): Harden features (signed volume, footprint imbalance, gamma walls, liquidity sweeps, OFI, trade aggressor) with NaN/Inf guards, regime-aware normalization, lookahead-free, crypto-realistic distributions. Add adversarial coverage.
4) **Latency-Aware Hedging** (`src/backtest/options_hedging.py` extend): Support latency-delayed rebalances, stale greeks detection, partial-hedge on latency, hedge slippage/fees, attribution including execution cost. Deterministic.
5) **Production Telemetry & Monitoring** (`src/telemetry/monitor.py` new + `scripts/run_production_campaign.py` new): Real-time-style metrics (PnL, drawdown, greeks, gamma exposure, VaR/ES, heat, limits utilization), alerts, structured logging, artifact emission. CLI with run/resume/status/abort.
6) **Comprehensive Tests** (`tests/test_production_execution_risk.py`, `tests/test_orderflow_microstructure.py` new): >=25 substantive tests covering execution, risk wiring, microstructure adversarial, latency hedging, determinism, strict serialization (`allow_nan=False`), no-lookahead.
7) **Artifacts**: Emit timestamped artifacts to `research_state/` including `PRODUCTION_CAMPAIGN_{YYYYMMDDTHHMMSSZ}.json`, `RISK_AUDIT_{YYYYMMDDTHHMMSSZ}.json`, `MICROSTRUCTURE_ADVERSARIAL_{YYYYMMDDTHHMMSSZ}.json`. Update `research_state/RESULTS_SUMMARY.md` with 'Phase 7: Production Execution, Real-Time Risk & Orderflow Microstructure Hardening (Crypto Options + Orderflow)' section.

## IMMEDIATE FIRST ACTIONS
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q  # must be 434 passing, 2 skipped, 0 failures

# 2) Review existing patterns to extend (don't reinvent)
cat src/campaign/core.py | head -60
cat scripts/run_campaign.py | head -40
grep -rn "RiskManager\|CircuitBreaker\|KillSwitch" src 2>&1 | head -15
ls src/execution/ src/risk/ src/features/ src/telemetry/ 2>&1 | head -30

# 3) BUILD PHASE 7 - HEAVY IMPLEMENTATION REQUIRED
# Create/extend: src/execution/engine.py, src/risk/execution_integration.py,
# src/features/orderflow_microstructure.py (or extend), src/backtest/options_hedging.py (extend),
# src/telemetry/monitor.py, scripts/run_production_campaign.py,
# tests/test_production_execution_risk.py, tests/test_orderflow_microstructure.py
# Run production campaign, produce artifacts, update RESULTS_SUMMARY.md
```

## HARD CONSTRAINTS
- **Heavy implementation required**: Full production wiring - substantial code, not just stubs.
- **No placeholders/TODOs/FIXMEs/HACKs/XXX**: Production-grade, complete implementations.
- **Deterministic & reproducible**: Fixed seeds, purge/embargo where applicable, train-only where applicable, no-lookahead.
- **Strict serialization**: `allow_nan=False` everywhere for artifacts.
- **Fail-forward**: Extend existing APIs if needed; fix integration issues.
- **Wire risk controls into execution**: Hard enforcement (block/hold/flatten on breach).
- **Ship every session**: New/extended modules + CLI + tests + artifacts + RESULTS_SUMMARY update.
- **Don't redo completed phases**: Compose and integrate, don't reimplement from scratch.
- **Single handoff**: Update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.

## SUCCESS CRITERIA (MUST HIT BEFORE NEXT HANDOFF)
- [ ] Gate GREEN: `python -m pytest tests/ -q` (>=434 passing, 0 failures; new tests all passing)
- [ ] Execution engine + risk integration implemented and wired end-to-end
- [ ] Orderflow microstructure hardened with adversarial tests passing
- [ ] Latency-aware hedging extended with execution costs/attribution
- [ ] Production CLI working (run/resume/status/abort)
- [ ] New tests >=25 passing (test_production_execution_risk.py + test_orderflow_microstructure.py)
- [ ] Artifacts emitted to `research_state/` (PRODUCTION_CAMPAIGN_*.json, RISK_AUDIT_*.json, MICROSTRUCTURE_ADVERSARIAL_*.json)
- [ ] `research_state/RESULTS_SUMMARY.md` updated with Phase 7 section
- [ ] Determinism verified (reruns produce identical key metrics)
- [ ] Full pipeline exercises execution+risk+microstructure+latency hedging with strict serialization

## NEXT AGENT INSTRUCTION (CLEAR, TIMESTAMPED, NON-DEFERRABLE)
Timestamp: 2026-10-31T22:37:00Z
**THIS IS THE SINGLE DURABLE HANDOFF. READ IT FIRST.** All prior phases complete - compose/integrate/harden, don't redo.
**IMMEDIATE FOCUS (MANDATORY):** Phase 7 — Production Execution, Real-Time Risk & Orderflow Microstructure Hardening (CRYPTO OPTIONS + ORDERFLOW). Build COMPLETE production-grade hardening with execution, risk wiring, microstructure, latency hedging, telemetry, and validation. This is HEAVY implementation - do real engineering work.
**REMOVE BOTTLENECKS:** Fix anything blocking integration (imports, wiring, serialization) as you go. Do not stop at stubs.
**FAIL-FORWARD:** Extend existing APIs if needed to make full integration work cleanly.
**WIRE RISK INTO EXECUTION:** Hard enforcement required.
**SHIP:** Every deliverable above (modules/CLI/tests/artifacts/RESULTS_SUMMARY) must be produced in this session.
**NEVER AVOID HEAVY WORK.** If something is complex, implement it properly.
Verify gate at start and end. Keep all tests green.
**BEFORE ENDING:** Update THIS FILE (research_state/durable_handoff.md) with fresh UTC timestamp, exact files changed, concrete rationale, verification commands+results, and updated remaining work (or confirm Phase 7 complete per success criteria). Also ensure research_state/RESULTS_SUMMARY.md is updated.
