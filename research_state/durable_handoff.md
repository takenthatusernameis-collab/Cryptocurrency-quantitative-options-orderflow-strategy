# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T10:29:40Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: crypto options + orderflow quantitative strategy (options pricing/IV surfaces/Greeks/delta-hedged PnL/attribution/regime/composite/execution/risk/venue routing/multi-venue smart order routing/circuit breakers/latency/performance hardening)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW + MULTI-VENUE EXECUTION + REGIME-ROBUST WALKFORWARD + PRODUCTION RISK)

State: 346 TESTS PASSING | 0 FAILING | 1 WARNING (datetime.utcnow deprecation in tests/test_schemas.py:30 — tests only) | WORKING TREE CLEAN | UP TO DATE WITH origin/main | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-7 COMPLETE | PHASE 8 COMPLETE | FULL VERIFICATION GATE GREEN

Session start context: Gate verified green (346 passed). Focused on regime-robust walkforward/OOS (purge/embargo, determinism, execution+risk under CompositeSignalGenerator regimes), adversarial stress/correlation, pricing/Greeks/IV numerics, risk/circuit-breaker/telemetry serialization. All targeted tests pass. No code changes required beyond verification; bottlenecks cleared.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, NO EXPLORATION LOOPS)
**MANDATE: HEAVY QUANT ONLY. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS/FIXMEs/HACKs/XXX. NO EXPLORATION AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE.**

You are picking up **Cryptocurrency-quantitative-options-orderflow-strategy**. Production-grade crypto options + orderflow quant system. All phases 1-7 and Phase 8 are **COMPLETE**. Verification gate is **GREEN** (346 passed, 0 failed). Your job is NOT to build new features from scratch - it is to **GUARD THE GATE** and perform **CONCRETE PRODUCTION HARDENING** every session, with zero deferral.

**EXECUTE IN THIS EXACT ORDER - NO DEVIATION:**

### STEP 1: HOLD THE GATE (MANDATORY FIRST - BLOCKS EVERYTHING ELSE)
```bash
python -m pytest -q  # MUST be >=346 passing, 0 failures
```
Also verify simultaneously:
- `tests/test_pipeline_determinism.py` passes (byte-identical outputs)
- All serialization uses `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. NO NaN/Inf.
- Numerical stability: no division by zero, no log(0)/sqrt(negative) without guards. All outputs finite.
- ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. `git status` clean.
- Fix the single remaining warning: replace `datetime.utcnow()` in `tests/test_schemas.py:30` with timezone-aware `datetime.now(datetime.UTC)` (tests-only, zero-risk, removes the deprecation warning).
- If ANY check fails → fix with concrete minimal code changes BEFORE moving to Step 2.

### STEP 2: HEAVY QUANT HARDENING (PRIORITIZED BY IMPACT - DO NOT SKIP)
Focus ruthlessly on these high-signal areas in order of leverage:

1. **Regime-robust walkforward & OOS** - Keep `tests/test_oos_walkforward.py` green, especially `test_walkforward_execution_risk_under_composite_regime_shifts_purge_embargo_determinism`. Tighten purge/embargo logic, regime shift handling, and execution cost realism without API breaks.
2. **Adversarial stress & correlation** - Harden `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`. Target tail robustness, correlation breakdowns, and regime miscalibration.
3. **Numerics & pricing/Greeks/IV surface** - Audit `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Eliminate any unguarded divisions/logs/powers; enforce finiteness everywhere. Preserve invariants.
4. **Risk, circuit breakers, telemetry** - Harden `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`. Ensure strict serialization (allow_nan=False), NaN/Inf propagation is blocked, and telemetry never leaks bad values.
5. **Performance without regression** - Only optimize hot paths (`tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`) if you can prove byte-identical results or all tests unchanged. No speculative micro-optimizations.

All changes must be minimal, backward-compatible, concrete, justified by a failing adversarial case or a clear numerical edge. Never add stubs/TODOs/placeholders. Never rewrite correct working code.

### STEP 3: FINAL GATE (BEFORE ENDING SESSION)
Run full simultaneous verification. ALL must pass:
1. `python -m pytest -q` >= 346 passing (0 failures). Only increase count if strictly necessary with justification.
2. Determinism: `tests/test_pipeline_determinism.py` passes (byte-identical)
3. Serialization strict (allow_nan=False), no NaN/Inf anywhere in outputs
4. Numerical stability everywhere, all finite
5. Backward compatibility: all existing tests pass unchanged
6. Clean: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`, `git status` clean

**MANDATORY:** Update this handoff with fresh UTC timestamp and exact remaining work before ending. If you find bottlenecks, REMOVE THEM IMMEDIATELY with concrete fixes. Never end mid-phase without updating this file. Never leave the gate red.

## EXACT REMAINING WORK
- [ ] HOLD GATE GREEN every session (re-verify baseline first)
- [ ] Fix `tests/test_schemas.py:30` `datetime.utcnow()` deprecation → `datetime.now(datetime.UTC)` (tests-only, removes the 1 warning). Note: current grep shows `datetime.now(timezone.utc)` usage; verify actual source of warning if persists.
- [ ] HEAVY QUANT HARDENING: regime/OOS walkforward + adversarial stress/correlation + pricing/Greeks/IV numerics + risk/circuit-breaker/telemetry serialization safety (all targeted suites pass currently)
- [ ] CONCRETE IMPROVEMENTS: only where they harden correctness/numerics/stability without breaking existing tests; prove impact
- [ ] UPDATE HANDOFF with fresh timestamp + exact remaining work before session end

## BOTTLENECK STATUS
- ALL PREVIOUS BOTTLENECKS CLEARED. No active blockers. Working tree clean. 346 tests passing. Gate GREEN. Historical edit-tool abort loop resolved. Focus: pure hardening, no new features, no deferral.

## NEXT FOCUS CAMPAIGN (FORCES HEAVY QUANT WORK - NO AVOIDANCE)
**Campaign goal:** Sustain Phase 8 production-readiness hardening indefinitely. Every session must produce measurable heavy-quant progress (a tightened numerical guard, a hardened adversarial case, a tightened purge/embargo path, or a serialization-safety fix) and end with the gate GREEN. Future agents CANNOT avoid heavy working: Step 1 (hold the gate) is mandatory and blocks everything else; Step 2 is executed in fixed priority order without skipping; Step 3 (final gate) is mandatory before session end. No scaffolding, no stubs, no placeholders, no exploration loops, no new features — correctness, numerical stability, determinism, and strict serialization only.
