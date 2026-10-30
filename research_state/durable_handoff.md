# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T09:27:33Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: crypto options + orderflow quantitative strategy (options pricing/IV surfaces/Greeks/delta-hedged PnL/attribution/regime/composite/execution/risk/venue routing/multi-venue smart order routing/circuit breakers/latency/performance hardening)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW + MULTI-VENUE EXECUTION + REGIME-ROBUST WALKFORWARD + PRODUCTION RISK)

State: 346 TESTS PASSING | 0 FAILING | 1 WARNING (datetime.utcnow deprecation in tests/test_schemas.py:30 — tests only, not src/) | WORKING TREE CLEAN | UP TO DATE WITH origin/main | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-7 COMPLETE | PHASE 8 #1-#6 COMPLETE | FULL VERIFICATION GATE GREEN

Session start context: Baseline re-verified — 346 tests passing, 0 failing, 1 test-only deprecation warning, working tree clean, up to date with origin/main, ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/. All prior bottlenecks (edit-tool malformed args, cancelled workflow runs) are historical — no active blockers remain. NOTE: previous handoff listed PHASE 8 #5 and #6 as remaining; both are now IMPLEMENTED AND PASSING (#5 regime-shift walkforward test at tests/test_oos_walkforward.py:562; #6 serialization-safe risk/circuit-breaker monitoring hooks in src/risk/limits.py + src/risk/circuit_breaker.py covered by tests/test_circuit_breaker.py and tests/test_telemetry_end_to_end.py). Handoff was stale — corrected below. The campaign is complete; the next session's job is to GUARD THE GREEN GATE and run production hardening, never deferring heavy quant work.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, NO EXPLORATION LOOPS)
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANTITATIVE ENGINEERING ONLY. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS. DO NOT END THE SESSION WITHOUT KEEPING THE GATE GREEN AND UPDATING THIS HANDOFF.**

You are continuing the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign. Production-grade crypto options + orderflow quant. Core: options pricing/IV surfaces/Greeks/delta-hedged PnL/attribution/regime/composite/execution/risk/venue routing/multi-venue smart order routing/circuit breakers/latency/performance hardening.

**ALL PHASES COMPLETE (Phases 1-7, Phase 8 #1-#6). Gate is green (346 passing, 0 failing, clean tree, zero TODOs in src, determinism byte-identical, allow_nan=False serialization, all outputs finite).**

### MANDATORY FOCUS FOR THIS SESSION — GUARD THE GREEN GATE + PRODUCTION HARDENING (NO DEFERRAL)

The campaign is complete; the risk now is regression and silent drift. Your mandatory focus is to keep the verification gate green and apply production hardening, treating every check as non-optional heavy work.

**TOP PRIORITY #1 (MUST DO FIRST - NO DEFERRAL): RE-VERIFY BASELINE + HOLD THE GATE**
- Run `python -m pytest -q` — must be >= 346 passing, 0 failures. Do not reduce the count; increase ONLY by adding strictly necessary, justified tests.
- Run `tests/test_pipeline_determinism.py` — must pass (byte-identical outputs).
- Confirm serialization: all outputs use `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. NO NaN/Inf anywhere.
- Confirm numerical stability: no division by zero, no log(0)/sqrt(negative) without guards. All values finite.
- Confirm clean state: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. `git status` clean. `git log` up to date with origin/main.
- If any check fails, FIX IT with concrete code changes before anything else. A red gate blocks all other work.

**TOP PRIORITY #2 (AFTER #1 HOLDS): PRODUCTION HARDENING / LIVE READINESS**
- Run adversarial/performance suites and confirm green: `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_performance_benchmarks.py`, `tests/test_walkforward_robustness_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`.
- Confirm regime-robust walkforward (Phase 8 #5) remains green: `tests/test_oos_walkforward.py` including `test_walkforward_execution_risk_under_composite_regime_shifts_purge_embargo_determinism`.
- Confirm serialization-safe risk/circuit-breaker monitoring (Phase 8 #6) remains green: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`.
- Any hardening change must be concrete, minimal, backward-compatible, and keep all existing tests passing unchanged. No TODOs/placeholders.

### VERIFICATION GATE (MUST PASS SIMULTANEOUSLY BEFORE ENDING SESSION)
1. `python -m pytest -q` >= 346 passing (0 failures). Increase count ONLY if adding strictly necessary tests.
2. Determinism: `tests/test_pipeline_determinism.py` passes (byte-identical outputs).
3. Serialization: all outputs use `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. NO NaN/Inf anywhere.
4. Numerical stability: no division by zero, no log(0)/sqrt(negative) without guards. All values finite.
5. Backward compatibility: all existing tests pass unchanged.
6. Clean state: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. `git status` clean. Changes minimal and justified.

### EXECUTION DIRECTIVE
- Hold the gate green first (Priority #1). Then production hardening (Priority #2). Heavy quantitative work only — no exploration tangents, no rewriting correct code.
- Bottlenecks removed immediately if found. If blocked, fix the bottleneck with concrete code changes.
- Update this handoff with fresh UTC timestamp and exact remaining work before ending session. This file is the SINGLE SOURCE OF TRUTH.
- Never avoid heavy work. Every action must move the campaign forward with concrete, verifiable progress. Do not end mid-phase without updating `durable_handoff.md`.

## EXACT REMAINING WORK (ACTIONABLE NOW)
- [x] PHASES 1-7 COMPLETE
- [x] PHASE 8 #1 COMPLETE (multi-venue routing)
- [x] PHASE 8 #2 COMPLETE (execution perf/latency)
- [x] PHASE 8 #3 COMPLETE (auto delta-hedging/rebalancing)
- [x] PHASE 8 #4 COMPLETE (circuit-breaker stress testing)
- [x] PHASE 8 #5 COMPLETE (walkforward/OOS extension to execution+risk under regime shifts — purge/embargo, determinism, strict serialization; test at tests/test_oos_walkforward.py:562)
- [x] PHASE 8 #6 COMPLETE (production monitoring/alerting hooks for risk-limit breaches + kill-switch events — serialization-safe; src/risk/limits.py, src/risk/circuit_breaker.py)
- [ ] FULL VERIFICATION GATE GREEN (pytest>=346, determinism, allow_nan=False, finite, zero TODOs/FIXME/PLACEHOLDER/HACK/XXX in src/, clean tree) — HOLD EVERY SESSION
- [ ] PRODUCTION HARDENING / LIVE READINESS (adversarial + performance suites green, regime-robust walkforward green, risk/circuit-breaker monitoring green)
- [ ] UPDATE HANDOFF with fresh UTC timestamp and exact remaining work before ending

## BOTTLENECK STATUS
- ALL PREVIOUS BOTTLENECKS CLEARED (edit-tool malformed args, cancelled workflow runs are historical). Working tree clean. 346 tests passing. No active blockers.
- KNOWN RISK: handoff staleness (previous handoff listed #5/#6 as remaining when already implemented). Keep this file current every session to avoid re-work and misdirection.
