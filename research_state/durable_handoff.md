# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T16:23:28Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: cryptocurrency options + orderflow quantitative strategy (derivatives pricing/Greeks/IV surfaces/delta-hedged PnL/attribution/regime classification/composite signals/execution/risk/multi-venue routing/latency/performance hardening/walkforward/OOS/purge-embargo)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (NO EXPLORATION, NO SCAFFOLDING)

State: 351 TESTS PASSING | 0 FAILING | 0 WARNINGS | WORKING TREE CLEAN | UP TO DATE WITH origin/main | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-8 COMPLETE | GATE GREEN | BASELINE VERIFIED 2026-10-30T16:21:16Z (python -m pytest -q → 351 passed)

## SESSION 2026-10-30T16:23:28Z — FRESH TIMESTAMPED INITIAL TASK MESSAGE (NEXT SESSION - EXECUTE IMMEDIATELY)
Action: Prioritized strictly by repo name "Cryptocurrency-quantitative-options-orderflow-strategy". Refreshed single durable handoff with fresh UTC timestamp and a concrete, forceful initial task message for the next agentic session. Removed/confirmed no active bottlenecks (gate GREEN). Locked next focus campaign to the most adversarial remaining areas in crypto options+orderflow (correlation/tail stress, IV/Greeks numerical stability, risk/serialization hardening). No production code touched. Gate remains GREEN 351/351.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, DO NOT EXPLORE)
Timestamp (UTC): 2026-10-30T16:23:28Z
Repo domain (prioritized from repository name): Cryptocurrency-quantitative-options-orderflow-strategy → production-grade crypto OPTIONS + ORDERFLOW quantitative strategy (derivatives pricing/Greeks/IV surfaces/delta-hedged PnL/attribution/regime classification/composite signals/execution/risk/multi-venue routing/latency/performance hardening/walkforward/OOS/purge-embargo).
MANDATE: HEAVY QUANT ONLY. PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS/FIXMEs/HACKs/XXX. DO NOT REWRITE CORRECT CODE. FORCE HEAVY WORKING. SESSION MAY NOT END WITHOUT UPDATING THIS FILE WITH A FRESH UTC TIMESTAMP AND EXACT REMAINING WORK. Every action must move the system closer to bulletproof adversarial robustness.

### EXECUTE IN EXACT ORDER (BLOCKING)

#### STEP 1: HOLD THE GATE (MANDATORY, BLOCKS ALL ELSE)
```bash
python -m pytest -q  # MUST be >=351 passing, 0 failures, 0 warnings
git status --short   # should be clean unless making minimal intentional hardenings
tests/test_campaign_resume.py  # handoff contract must pass
```
Simultaneous checks:
- Strict serialization: use `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. ZERO NaN/Inf anywhere in serialized outputs/telemetry/events.
- Numerical stability: audit divisions/logs/sqrt/powers/clamp bounds. ALL outputs finite.
- ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`.
- Bottlenecks: none active — all historical blockers cleared. Do NOT reintroduce exploration/stubbing/placeholders.
- If ANY fails → minimal concrete fix BEFORE Step 2.

#### STEP 2: HEAVY QUANT PRIORITIES (IN ORDER, NO SKIPPING) — CRYPTO OPTIONS + ORDERFLOW FOCUSED
1. **PRIORITY 1 - Regime-robust walkforward/OOS (CLOSED)** - Done. Keep passing unchanged.
2. **PRIORITY 2 - Adversarial correlation/tail/cross-asset stress (HIGHEST REMAINING - ATTACK NOW)** - Target `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`. Hunt concrete numerical edges: non-PSD correlation matrices (nearest PSD/eigenvalue floor), singular/ill-conditioned covariance, extreme tail shocks causing NaN/Inf/overflow, regime miscalibration producing unstable weights/signals, cross-venue routing blowups. Add minimal guards (clamps/finite checks/safe PSD projection or eigenvalue floors) in actual production code paths. Prove finiteness everywhere. Do NOT weaken assertions.
3. **PRIORITY 3 - Crypto options pricing/Greeks/IV surface numerics** - Target `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Eliminate unguarded div/log/sqrt/pow/exp; enforce invariants (delta in valid ranges where applicable, gamma>=0 where expected, vega finite, no arbitrage violations that produce NaN/Inf). Minimal guards only.
4. **PRIORITY 4 - Risk/circuit-breakers/orderflow/telemetry serialization** - Target `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`. Harden serialization to `allow_nan=False`, block NaN/Inf propagation, safe kill-switch/risk-limit breach paths, orderflow extreme values. Alerts cannot emit non-finite values.
5. **PRIORITY 5 - Performance/vectorization hardening (only if safe)** - Target `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`. ONLY optimize if byte-identical OR all tests remain unchanged and passing. Prove with numbers.

Every change must be minimal/backward-compatible, justified by concrete numerical/adversarial edge, pass all existing tests unchanged.

#### STEP 3: FINAL GATE (BEFORE ENDING SESSION - MANDATORY)
1. `python -m pytest -q` >= 351 passing (0 failures). If adding tests, justify and update counts in handoff.
2. `tests/test_pipeline_determinism.py` byte-identical.
3. `allow_nan=False` enforced everywhere serialized (metrics/telemetry/events).
4. All outputs finite across exercised paths.
5. All existing tests unchanged/passing.
6. ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`, `git status` clean OR only intentional hardening changes remain.
7. **UPDATE THIS FILE** (`research_state/durable_handoff.md`) with fresh UTC timestamp + exact remaining work + concrete changes made (files + rationale).
8. Only commit if user explicitly requests it.

## EXACT REMAINING WORK
- [x] HOLD GATE GREEN every session (verify baseline first) - VERIFIED 2026-10-30T16:23:28Z (351/351, clean tree)
- [x] PRIORITY 1 (CLOSED): Regime-robust walkforward/OOS under CompositeSignalGenerator regime shifts with tightened purge/embargo + determinism + strict serialization.
- [x] GATE INTEGRITY (CLOSED 2026-10-30T15:28:23Z): `tests/test_campaign_resume.py` handoff-contract failures cleared. Gate 351/351.
- [ ] **PRIORITY 2 (HIGHEST REMAINING - ATTACK NOW):** Adversarial correlation breakdowns/tail stress (portfolio/walkforward/signals/routing). Target `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`. Find concrete numerical edges (non-PSD correlation matrices, extreme tails, regime miscalibration, singular covariance, overflow/underflow, venue routing failures) and add minimal guards; prove finiteness. No test changes.
- [ ] PRIORITY 3: Crypto options pricing/Greeks/IV surface + numerical guard coverage — Target `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`.
- [ ] PRIORITY 4: Risk/circuit-breaker/orderflow/telemetry serialization hardening — Target `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`.
- [ ] PRIORITY 5: Safe performance hardening only if provably byte-identical/passing — Target `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`.
- [x] UPDATE HANDOFF with fresh timestamp + exact remaining work + concrete changes before ending session — DONE 2026-10-30T16:23:28Z
- [ ] Only commit if user explicitly requests it

## BOTTLENECK STATUS
- **CLEARED:** clamp infinite bound in execution/engine paths — fixed with finite bounds
- **CLEARED (HISTORICAL):** kilo edit-tool invalid-argument failures — prevention: complete edit calls with filePath/oldString/newString
- **CLEARED (HISTORICAL):** historical CI issues — file structure corrected, suite passes 351/351
- **CLEARED (2026-10-30T15:28:23Z):** gate-integrity blocker — `tests/test_campaign_resume.py` failures from trimmed handoff pointer file; restored required sections + Phase 1-5 markers. Gate GREEN 351/351.
- **ACTIVE:** None. All bottlenecks removed — no session is blocked or inefficient. ATTACK PRIORITY 2 DIRECTLY (adversarial correlation/tail/cross-asset stress) with minimal concrete guards only where adversarial edges exist; keep all existing tests unchanged/passing. NO IDLE EXPLORATION.

## NEXT FOCUS CAMPAIGN (FORCES HEAVY QUANT WORK)
Campaign Goal: Harden crypto options + orderflow system against adversarial regime/correlation/tail/venue cases with production-grade numerical safety. Every session MUST produce measurable heavy-quant progress (concrete guard tightened, adversarial path hardened, purge/embargo tightened, serialization-safety fix, or invariant enforced) and end with gate GREEN. A session may NOT end without updating `research_state/durable_handoff.md` with a fresh UTC timestamp and exact remaining work.

Rules (ENFORCED):
- Heavy quant only. No scaffolding/stubs/placeholders/TODOs/FIXMEs/HACKs/XXX/new features.
- Correctness > speed. Determinism preserved. Backward-compatible minimal changes.
- Strict serialization: `allow_nan=False`. Zero NaN/Inf propagation.
- Numerical stability mandatory (guard divisions/logs/sqrt/powers/clamp).
- Verify after every change: run relevant tests + full gate before ending.
- Do NOT explore aimlessly. Attack concrete failing-adjacent edges via tests.
- Prioritize by repo name: options pricing/Greeks, IV surfaces, orderflow, gamma exposure, regime classification, walkforward/OOS, correlation constraints, multi-venue routing, risk/circuit breakers.
- Every action must move the system closer to bulletproof adversarial robustness. Session may not end without measurable progress and a refreshed handoff timestamp.

Acceptance Criteria (MUST HOLD SIMULTANEOUSLY):
- `python -m pytest -q` >= 351 passing, 0 failures, 0 warnings
- `tests/test_pipeline_determinism.py` byte-identical
- All serialized outputs finite, `allow_nan=False` enforced
- Zero TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`
- Working tree clean/intentional only. No debug prints/log spam.
- Determinism preserved (no RNG/seed/order changes)
