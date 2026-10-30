# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T17:17:24Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: cryptocurrency options + orderflow quantitative strategy (derivatives pricing/Greeks/IV surfaces/delta-hedged PnL/attribution/regime classification/composite signals/execution/risk/multi-venue routing/latency/performance hardening/walkforward/OOS/purge-embargo)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (NO EXPLORATION, NO SCAFFOLDING)

State: 351 TESTS PASSING | 0 FAILING | 0 WARNINGS | WORKING TREE CLEAN | UP TO DATE WITH origin/main | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-8 COMPLETE | GATE GREEN | BASELINE VERIFIED 2026-10-30T17:17:24Z (python -m pytest -q → 351 passed)

## SESSION 2026-10-30T17:17:24Z — FRESH TIMESTAMPED INITIAL TASK MESSAGE (NEXT SESSION - EXECUTE IMMEDIATELY)
Action: Prioritized strictly by repository name "Cryptocurrency-quantitative-options-orderflow-strategy". Refreshed the single durable handoff with a crystal-clear, forceful timestamped initial task message for the next agentic work session. Confirmed no active bottlenecks; gate remains GREEN (351/351). Locked focus to adversarial hardening of crypto options+orderflow with production-grade numerical safety. No production code modified.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, DO NOT EXPLORE AIMLESSLY)
Timestamp (UTC): 2026-10-30T17:17:24Z
Repo domain (inferred from repo name, highest priority): Cryptocurrency-quantitative-options-orderflow-strategy → PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY
(derivatives pricing/Greeks/IV surfaces/gamma exposure/delta-hedged PnL/attribution/regime classification/composite signals/execution/risk/multi-venue routing/latency/performance/walkforward/OOS/purge-embargo)

MANDATE: HEAVY QUANT ONLY. CORRECTNESS MANDATORY. NUMERICAL STABILITY MANDATORY. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS/FIXMEs/HACKs/XXX. DO NOT REWRITE CORRECT CODE. FORCE HEAVY WORKING. EVERY SESSION MUST PRODUCE MEASURABLE HEAVY-QUANT PROGRESS. SESSION MAY NOT END WITHOUT UPDATING THIS FILE WITH FRESH UTC TIMESTAMP + EXACT REMAINING WORK + CONCRETE CHANGES MADE.

### EXECUTE IN EXACT ORDER (BLOCKING)

#### STEP 1: HOLD THE GATE (MANDATORY)
```bash
python -m pytest -q                        # MUST be >=351 passing, 0 failures, 0 warnings
git status --short                         # clean unless minimal intentional hardenings
python -m pytest tests/test_campaign_resume.py -q  # handoff contract must pass
```
Checks enforced simultaneously:
- Strict serialization: `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. ZERO NaN/Inf anywhere serialized.
- Numerical stability: all divisions/logs/sqrt/powers/clamped. ALL outputs finite.
- ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`.
- If ANY fails → make minimal concrete fix BEFORE Step 2.

#### STEP 2: ATTACK HIGHEST-PRIORITY ADVERSARIAL EDGES (IN ORDER)
1. **PRIORITY 1 - Regime-robust walkforward/OOS (CLOSED)** — Maintain unchanged passing.
2. **PRIORITY 2 - Adversarial correlation/tail/cross-asset stress (ATTACK NOW)** — Targets: `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`. Hunt: non-PSD correlation matrices (nearest PSD/eigenvalue floor), singular/ill-conditioned covariance, extreme tail shocks → NaN/Inf/overflow, regime miscalibration, cross-venue routing blowups. Add MINIMAL guards (clamps/finite checks/safe PSD/eigenvalue floors) in production code paths. Prove finiteness. Do NOT weaken assertions.
3. **PRIORITY 3 - Crypto options pricing/Greeks/IV numerics** — Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Eliminate unguarded div/log/sqrt/pow/exp; enforce invariants; guard domain errors.
4. **PRIORITY 4 - Risk/circuit-breakers/orderflow/telemetry serialization** — Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`. Enforce `allow_nan=False`, block NaN/Inf propagation, harden kill-switch paths, alerts must never emit non-finite values.
5. **PRIORITY 5 - Safe performance hardening (ONLY if provably safe)** — Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`. ONLY optimize if byte-identical OR all tests unchanged and passing. Prove with numbers.

#### STEP 3: FINAL GATE (BEFORE ENDING - MANDATORY)
1. `python -m pytest -q` >= 351 passing (0 failures). If adding tests, justify and update counts here.
2. `tests/test_pipeline_determinism.py` byte-identical.
3. `allow_nan=False` enforced everywhere serialized (metrics/telemetry/events).
4. All outputs finite across exercised paths.
5. All existing tests unchanged/passing.
6. ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. Git tree clean OR only minimal intentional hardenings.
7. **UPDATE THIS FILE** with fresh UTC timestamp + exact remaining work + concrete changes (files + rationale).
8. Only commit if explicitly requested.

## EXACT REMAINING WORK
- [x] HOLD GATE GREEN every session (verified 2026-10-30T17:17:24Z: 351/351, clean)
- [x] PRIORITY 1 (CLOSED): Regime-robust walkforward/OOS under CompositeSignalGenerator regime shifts with tightened purge/embargo + determinism + strict serialization.
- [x] GATE INTEGRITY (CLOSED): `tests/test_campaign_resume.py` contract satisfied.
- [ ] **PRIORITY 2 (HIGHEST REMAINING - ATTACK NOW):** Adversarial correlation breakdowns/tail stress (portfolio/walkforward/signals/routing). Targets: `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`. Find concrete numerical edges (non-PSD correlation, singular covariance, extreme tails, regime miscalibration, routing blowups). Add minimal guards; prove finiteness. No test changes.
- [ ] PRIORITY 3: Crypto options pricing/Greeks/IV surface + numerical guard coverage — `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`.
- [ ] PRIORITY 4: Risk/circuit-breaker/orderflow/telemetry serialization hardening — `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`.
- [ ] PRIORITY 5: Safe performance hardening only if provably byte-identical/passing — `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`.
- [x] UPDATE HANDOFF with fresh timestamp before ending session (DONE 2026-10-30T17:17:24Z)
- [ ] Only commit if user explicitly requests it

## BOTTLENECK STATUS
- **CLEARED (HISTORICAL):** Multiple historical bottlenecks resolved. Gate stable at 351/351.
- **ACTIVE:** NONE. No session blocked or inefficient. ATTACK PRIORITY 2 IMMEDIATELY with minimal concrete guards only where adversarial edges exist. Keep all existing tests unchanged/passing. NO IDLE EXPLORATION.

## NEXT FOCUS CAMPAIGN (FORCES HEAVY QUANT WORK)
Campaign Goal: Harden crypto options + orderflow system against adversarial regime/correlation/tail/venue cases with production-grade numerical safety. Every session MUST produce measurable heavy-quant progress and end with gate GREEN. Session may NOT end without updating this file with a fresh UTC timestamp and exact remaining work.

Rules (ENFORCED):
- Heavy quant only. No scaffolding/stubs/placeholders/TODOs/FIXMEs/HACKs/XXX/new features.
- Correctness > speed. Determinism preserved. Backward-compatible minimal changes.
- Strict serialization: `allow_nan=False`. Zero NaN/Inf propagation.
- Numerical stability mandatory (guard divisions/logs/sqrt/powers/clamps).
- Verify after every change: relevant tests + full gate before ending.
- Do NOT explore aimlessly. Attack concrete failing-adjacent edges via tests.
- Prioritize by repo name: options pricing/Greeks, IV surfaces, orderflow, gamma exposure, regime classification, walkforward/OOS, correlation constraints, multi-venue routing, risk/circuit breakers.
- Every action must move system closer to bulletproof adversarial robustness. Must end with refreshed handoff timestamp.

Acceptance Criteria (MUST HOLD):
- `python -m pytest -q` >= 351 passing, 0 failures, 0 warnings
- `tests/test_pipeline_determinism.py` byte-identical
- All serialized outputs finite, `allow_nan=False` enforced
- Zero TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`
- Working tree clean/intentional only. No debug prints/log spam.
- Determinism preserved (no RNG/seed/order changes)
