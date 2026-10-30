# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T07:47:23Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: crypto options + orderflow quantitative strategy (options pricing/IV surfaces/Greeks/delta-hedged PnL/attribution/regime/composite/execution/risk/venue routing)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW + MULTI-VENUE EXECUTION + REGIME-ROBUST WALKFORWARD)

State: 345 TESTS PASSING | 0 FAILING | 1 WARNING (datetime.utcnow deprecation in tests/test_schemas.py:30 — tests only, not src/) | WORKING TREE CLEAN | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-7 COMPLETE | PHASE 8 #1+#2+#3+#4 COMPLETE | PHASE 8 REMAINING: #5+#6 (HEAVY QUANT MANDATORY)

Session start context: Bottleneck removed (typing imports in src/backtest/engine.py). All gates green. Focus shifted to regime-robust execution/risk walkforward + production monitoring.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, NO EXPLORATION LOOPS)
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANTITATIVE ENGINEERING ONLY. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS.**

You are continuing the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign. Production-grade crypto options + orderflow quantitative strategy. Core: options pricing/IV surfaces/Greeks/delta-hedged PnL/attribution/regime/composite/execution/risk/venue routing.

**Phases 1-7 COMPLETE. Phase 8 #1 (multi-venue routing), #2 (execution perf/latency), #3 (auto delta-hedging/rebalancing), #4 (circuit-breaker stress testing) COMPLETE.**

**MANDATORY FOCUS (HEAVY QUANT): PHASE 8 - PRODUCTION EXECUTION & RISK - LIVE READINESS & PERFORMANCE HARDENING**

### TOP PRIORITY #1 (MUST DO FIRST - NO DEFERRAL)
**WALKFORWARD/OOS EXTENSION TO EXECUTION+RISK UNDER REGIME SHIFTS (PURGE/EMBARGO, DETERMINISM, STRICT SERIALIZATION)**

Extend walkforward/OOS coverage to the full execution+risk path under explicit regime shifts. Requirements:
- Extend `tests/test_oos_walkforward.py` or add a tightly focused adversarial test that exercises `WalkForwardBacktest` with execution+risk integration under regime shifts (use `CompositeSignalGenerator` regime states: high_vol_negative_gex/low_vol_positive_gex/skew_bearish/skew_bullish/neutral; create regime-shifting price/signal sequences).
- Enforce strict purge/embargo (no train/test overlap), strict time-ordering/no-lookahead, byte-identical determinism via `verify_determinism` or equivalent (seeded RNG), `allow_nan=False` serialization via `serialize_metrics_strict`/`WalkForwardResults.serialize_oos()`, all metrics finite.
- Verify execution engine + RiskManager + CircuitBreaker paths under regime shifts without stubs/placeholders. No changes to passing tests unless fixing a real bug with justification.
- This is HEAVY QUANT: implement/extend concrete logic, not comments/docs-only.

### TOP PRIORITY #2 (AFTER #1 OR IN PARALLEL IF CLEAN)
**PRODUCTION MONITORING/ALERTING HOOKS FOR RISK-LIMIT BREACHES AND KILL-SWITCH EVENTS (SERIALIZATION-SAFE)**

Add structured, serialization-safe monitoring/alerting hooks for risk-limit breaches and circuit-breaker kill-switch events. Requirements:
- Hook into `src/risk/limits.py` (RiskManager) and `src/risk/circuit_breaker.py` (CircuitBreaker) with deterministic, serializable event payloads (`allow_nan=False`).
- Emit/record events in a form consumable by telemetry without NaN/Inf; integrate cleanly with existing telemetry patterns.
- Add/extend focused tests if necessary (minimal, justified). No TODOs/placeholders.

### VERIFICATION GATE (MUST PASS SIMULTANEOUSLY BEFORE ENDING SESSION)
1. `python -m pytest -q` >= 345 passing (0 failures). Increase count ONLY if adding strictly necessary tests.
2. Determinism: `tests/test_pipeline_determinism.py` passes (byte-identical outputs).
3. Serialization: all outputs use `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. NO NaN/Inf anywhere.
4. Numerical stability: no division by zero, no log(0)/sqrt(negative) without guards. All values finite.
5. Backward compatibility: all existing tests pass unchanged.
6. Clean state: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. `git status` clean. Changes minimal and justified.

### EXECUTION DIRECTIVE
- START WITH #1. Do heavy quantitative engineering. No exploration tangents. No rewriting correct code.
- Bottlenecks removed immediately if found. If blocked, fix the bottleneck with concrete code changes.
- Update this handoff with fresh UTC timestamp and exact remaining work before ending session. This file is the SINGLE SOURCE OF TRUTH.

## EXACT REMAINING WORK (ACTIONABLE NOW)
- [x] PHASES 1-7 COMPLETE
- [x] PHASE 8 #1 COMPLETE (multi-venue routing)
- [x] PHASE 8 #2 COMPLETE (execution perf/latency)
- [x] PHASE 8 #3 COMPLETE (auto delta-hedging/rebalancing)
- [x] PHASE 8 #4 COMPLETE (circuit-breaker stress testing)
- [ ] PHASE 8 #5 - Walkforward/OOS extension to execution+risk path under regime shifts with purge/embargo, determinism, strict serialization (extend `tests/test_oos_walkforward.py` or add adversarial test exercising regime-shifting sequences)
- [ ] PHASE 8 #6 - Production monitoring/alerting hooks for risk-limit breaches and kill-switch events (serialization-safe)
- [ ] FULL VERIFICATION GATE (pytest>=345, determinism, allow_nan=False, finite, zero TODO/FIXME/PLACEHOLDER/HACK/XXX in src/, clean tree)
- [ ] UPDATE HANDOFF with fresh UTC timestamp and exact remaining work before ending

## BOTTLENECK STATUS
- ALL PREVIOUS BOTTLENECKS CLEARED. Working tree clean. 345 tests passing.
- NO KNOWN BLOCKERS. Heavy quant work required on #5 first.
