# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T09:34:41Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: crypto options + orderflow quantitative strategy (options pricing/IV surfaces/Greeks/delta-hedged PnL/attribution/regime/composite/execution/risk/venue routing/multi-venue smart order routing/circuit breakers/latency/performance hardening)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW + MULTI-VENUE EXECUTION + REGIME-ROBUST WALKFORWARD + PRODUCTION RISK)

State: 346 TESTS PASSING | 0 FAILING | 1 WARNING (datetime.utcnow deprecation in tests/test_schemas.py:30 — tests only, not src/) | WORKING TREE CLEAN | UP TO DATE WITH origin/main | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-7 COMPLETE | PHASE 8 #1-#6 COMPLETE | FULL VERIFICATION GATE GREEN

Session start context: Baseline re-verified — 346 tests passing, 0 failing, 1 test-only deprecation warning, working tree clean, up to date with origin/main, ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/. All prior bottlenecks (edit-tool malformed args, cancelled workflow runs) are historical — no active blockers remain. Campaign is complete; gate is green. Next session must GUARD THE GREEN GATE and do HEAVY PRODUCTION HARDENING with zero deferral.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, NO EXPLORATION LOOPS)
**MANDATE: HEAVY QUANT ONLY. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS/FIXMEs/HACKs/XXX. NO EXPLORATION AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE.**

You are picking up **Cryptocurrency-quantitative-options-orderflow-strategy**. Production-grade crypto options + orderflow quant system. All phases 1-7 and Phase 8 #1-#6 are **COMPLETE**. Verification gate is **GREEN** (346 passed, 0 failed). Your job is NOT to build new features from scratch - it is to **GUARD THE GATE** and perform **CONCRETE PRODUCTION HARDENING**.

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
- If ANY check fails → fix with concrete minimal code changes BEFORE moving to Step 2.

### STEP 2: PRODUCTION HARDENING (HEAVY QUANT WORK - DO NOT SKIP)
Run and keep green these adversarial/performance/regime/risk suites:
- `tests/test_adversarial_stress.py`
- `tests/test_backtest_stress_adversarial.py`
- `tests/test_performance_benchmarks.py`
- `tests/test_walkforward_robustness_adversarial.py`
- `tests/test_portfolio_walkforward_correlation_adversarial.py`
- `tests/test_oos_walkforward.py` (must include `test_walkforward_execution_risk_under_composite_regime_shifts_purge_embargo_determinism` passing)
- `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`

Look for concrete hardening opportunities:
- **Numerical robustness**: improve guards in pricing/Greeks/surfaces/attribution under extreme regimes without changing API contracts or breaking tests
- **Determinism**: ensure all RNG paths seeded; serialization paths strictly allow_nan=False
- **Execution/risk**: tighten validation, add explicit finite checks, improve error messages with concrete types
- **Performance**: only optimize hot paths if it preserves byte-identical results or all tests unchanged
- **Serialization safety**: audit any new/changed paths to use strict serializers

All changes must be minimal, backward-compatible, concrete, justified. Never add stubs/TODOs/placeholders. Never rewrite correct working code.

### STEP 3: FINAL GATE (BEFORE ENDING SESSION)
Run full simultaneous verification. ALL must pass:
1. `python -m pytest -q` >= 346 passing (0 failures). Only increase count if strictly necessary with justification.
2. Determinism: `tests/test_pipeline_determinism.py` passes
3. Serialization strict (allow_nan=False), no NaN/Inf anywhere
4. Numerical stability everywhere, all finite
5. Backward compatibility: all existing tests pass unchanged
6. Clean: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`, `git status` clean

**MANDATORY:** Update this handoff with fresh UTC timestamp and exact remaining work before ending. If you find bottlenecks, REMOVE THEM IMMEDIATELY with concrete fixes. Never end mid-phase without updating this file.

## EXACT REMAINING WORK
- [ ] HOLD GATE GREEN every session (re-verify baseline first)
- [ ] PRODUCTION HARDENING: adversarial + performance + regime-robust walkforward + risk/circuit-breaker serialization safety all green
- [ ] CONCRETE IMPROVEMENTS: only where they harden correctness/numerics/stability without breaking existing tests
- [ ] UPDATE HANDOFF with fresh timestamp + exact remaining work before session end

## BOTTLENECK STATUS
- ALL PREVIOUS BOTTLENECKS CLEARED. No active blockers. Working tree clean. 346 tests passing. Gate GREEN.
