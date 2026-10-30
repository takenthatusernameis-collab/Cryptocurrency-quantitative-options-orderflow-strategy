# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T17:21:05Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: cryptocurrency options + orderflow quantitative strategy (derivatives pricing/Greeks/IV surfaces/delta-hedged PnL/attribution/regime classification/composite signals/execution/risk/multi-venue routing/latency/performance hardening/walkforward/OOS/purge-embargo/correlation/stress)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (NO EXPLORATION, NO SCAFFOLDING)

State: 351 TESTS PASSING | 0 FAILING | 0 WARNINGS | WORKING TREE CLEAN | UP TO DATE WITH origin/main | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-8 COMPLETE | GATE GREEN | BASELINE VERIFIED 2026-10-30T17:21:05Z (python -m pytest -q → 351 passed)

## SESSION 2026-10-30T17:21:05Z — FRESH TIMESTAMPED INITIAL TASK MESSAGE (NEXT SESSION - EXECUTE IMMEDIATELY)
Action: Re-prioritized strictly by repository name "Cryptocurrency-quantitative-options-orderflow-strategy". Confirmed gate GREEN (351/351), all Priority 2 adversarial tests passing (58/58). No active bottlenecks. Focus remains on adversarial hardening across remaining priority areas.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, DO NOT EXPLORE AIMLESSLY)
Timestamp (UTC): 2026-10-30T17:21:05Z
Repo domain (inferred from repo name, highest priority): Cryptocurrency-quantitative-options-orderflow-strategy → PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY

MANDATE: HEAVY QUANT ONLY. CORRECTNESS MANDATORY. NUMERICAL STABILITY MANDATORY. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS/FIXMEs/HACKs/XXX. DO NOT REWRITE CORRECT CODE. FORCE HEAVY WORKING. EVERY SESSION MUST PRODUCE MEASURABLE HEAVY-QUANT PROGRESS. SESSION MAY NOT END WITHOUT UPDATING THIS FILE WITH FRESH UTC TIMESTAMP + EXACT REMAINING WORK + CONCRETE CHANGES MADE (FILES + RATIONALE).

### EXECUTE IN EXACT ORDER (BLOCKING)

#### STEP 1: HOLD THE GATE (MANDATORY)
```bash
python -m pytest -q                        # MUST be >=351 passing, 0 failures, 0 warnings
git status --short                         # clean unless minimal intentional hardenings
python -m pytest tests/test_campaign_resume.py -q  # handoff contract must pass
```

#### STEP 2: ATTACK HIGHEST-PRIORITY ADVERSARIAL EDGES (IN ORDER)
1. **PRIORITY 1 - Regime-robust walkforward/OOS (CLOSED)** — Maintain unchanged passing.
2. **PRIORITY 2 - Adversarial correlation/tail/cross-asset stress (PASSING)** — All tests pass (58/58). Continue to scan for any remaining edge cases; add minimal guards only if found.
3. **PRIORITY 3 - Crypto options pricing/Greeks/IV numerics** — Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Eliminate unguarded div/log/sqrt/pow/exp; enforce invariants.
4. **PRIORITY 4 - Risk/circuit-breakers/orderflow/telemetry serialization** — Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`. Enforce `allow_nan=False`, block NaN/Inf propagation.
5. **PRIORITY 5 - Safe performance hardening (ONLY if provably safe)** — Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`.

#### STEP 3: FINAL GATE (BEFORE ENDING - MANDATORY)
All gates as specified, and UPDATE THIS FILE with fresh UTC timestamp + exact remaining work + concrete changes.

## EXACT REMAINING WORK
- [x] HOLD GATE GREEN every session (verified 2026-10-30T17:21:05Z: 351/351, clean)
- [x] PRIORITY 1 (CLOSED): Regime-robust walkforward/OOS
- [x] PRIORITY 2 (PASSING): Adversarial correlation/tail/cross-asset stress (58/58 tests passing)
- [ ] PRIORITY 3: Crypto options pricing/Greeks/IV surface + numerical guard coverage
- [ ] PRIORITY 4: Risk/circuit-breaker/orderflow/telemetry serialization hardening
- [ ] PRIORITY 5: Safe performance hardening only if provably byte-identical/passing

## BOTTLENECK STATUS
- **ACTIVE:** NONE. Gate stable at 351/351, clean tree. All Priority 2 adversarial tests pass. Attack remaining priorities with minimal concrete guards only where needed. NO IDLE EXPLORATION.

## NEXT FOCUS CAMPAIGN
Continue adversarial hardening of crypto options + orderflow system. Focus on remaining priority areas while keeping all tests green.
