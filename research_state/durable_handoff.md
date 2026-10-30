# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T16:14:44Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: cryptocurrency options + orderflow quantitative strategy (derivatives pricing/Greeks/IV surfaces/delta-hedged PnL/attribution/regime classification/composite signals/execution/risk/multi-venue routing/latency/performance hardening/walkforward/OOS/purge-embargo)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (NO EXPLORATION, NO SCAFFOLDING)

State: 351 TESTS PASSING | 0 FAILING | 0 WARNINGS | WORKING TREE CLEAN | UP TO DATE WITH origin/main | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-8 COMPLETE | GATE GREEN | BASELINE VERIFIED 2026-10-30 (python -m pytest -q → 351 passed)

## SESSION 2026-10-30T16:14:44Z — HANDOFF REFRESH FOR NEXT AGENTIC WORK SESSION
Action: Refreshed single durable handoff with fresh timestamped initial task message, cleared all bottlenecks (none active), and locked the next focus campaign to Priority 2 adversarial correlation/tail-stress hardening so future agents cannot avoid heavy quant work. No production code touched. Gate remains GREEN 351/351.

CONCRETE CHANGES THIS SESSION (minimal, all 351 tests unchanged):
1. `research_state/durable_handoff.md` — Refreshed timestamp, initial task message, bottleneck status, and next focus campaign enforcement. Pointer to `research_state/INITIAL_TASK_HANDOFF.md` preserved as the short pointer; this file remains the single source of truth.

Verified:
- `python -m pytest -q` → 351 passed, 0 failed, 0 warnings
- `tests/test_campaign_resume.py` → all 4 tests PASSED (handoff contract intact)
- Strict serialization enforced with `allow_nan=False`; zero NaN/Inf in serialized outputs/telemetry/events
- Zero TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`
- Bottleneck status: ACTIVE: None (all historical blockers cleared)

## SESSION 2026-10-30T15:28:23Z — GATE RECOVERY + HANDOFF REFRESH (HISTORICAL)
Action: Re-verified baseline. Fixed `research_state/INITIAL_TASK_HANDOFF.md` pointer file to include required sections ("Initial Task Message", "Immediate Objectives", "Next Focus Campaign", "MANDATE") and Phase 1-5 markers required by `tests/test_campaign_resume.py`. Gate recovered: 351 passed, 0 failed, 0 warnings.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, DO NOT EXPLORE)
Timestamp (UTC): 2026-10-30T16:14:44Z
MANDATE: HEAVY QUANT ONLY. PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS/FIXMEs/HACKs/XXX. DO NOT REWRITE CORRECT CODE. FORCE HEAVY WORKING. SESSION MAY NOT END WITHOUT UPDATING THIS FILE WITH A FRESH UTC TIMESTAMP AND EXACT REMAINING WORK.

### EXECUTE IN EXACT ORDER (BLOCKING)

#### STEP 1: HOLD THE GATE (MANDATORY, BLOCKS ALL ELSE)
```bash
python -m pytest -q  # MUST be >=351 passing, 0 failures, 0 warnings
git status --short   # should be clean unless making minimal intentional hardenings
```
Simultaneous checks:
- Strict serialization: use `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. ZERO NaN/Inf anywhere in serialized outputs/telemetry/events.
- Numerical stability: audit divisions/logs/sqrt/powers/clamp bounds. ALL outputs finite.
- ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`.
- If ANY fails → minimal concrete fix BEFORE Step 2.

#### STEP 2: HEAVY QUANT PRIORITIES (IN ORDER, NO SKIPPING)
1. **PRIORITY 1 - Regime-robust walkforward/OOS (CLOSED)** - Done. Keep passing unchanged.
2. **PRIORITY 2 - Adversarial stress/correlation breakdowns/tail stress (HIGHEST REMAINING - ATTACK NOW)** - Target `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`. Hunt concrete numerical edges: non-PSD correlation matrices (nearest PSD/eigenvalue floor), singular/ill-conditioned covariance, extreme tail shocks causing NaN/Inf/overflow, regime miscalibration producing unstable weights/signals. Add minimal guards (clamps/finite checks/safe PSD projection or eigenvalue floors) in the actual production code paths used by these tests. Prove finiteness everywhere. Do NOT weaken assertions.
3. **PRIORITY 3 - Pricing/Greeks/IV numerics** - Target `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Eliminate unguarded div/log/sqrt/pow/exp; enforce invariants (delta in valid ranges where applicable, gamma>=0 where expected, vega finite, no NaN/Inf). Minimal guards only.
4. **PRIORITY 4 - Risk/circuit-breakers/telemetry serialization** - Target `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`. Harden serialization to `allow_nan=False`, block NaN/Inf propagation, safe kill-switch/risk-limit breach paths. Alerts cannot emit non-finite values.
5. **PRIORITY 5 - Performance hardening (only if safe)** - Target `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`. ONLY optimize if byte-identical OR all tests remain unchanged and passing. Prove with numbers.

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
- [x] HOLD GATE GREEN every session (verify baseline first) - VERIFIED 2026-10-30T16:14:44Z
- [x] PRIORITY 1 (CLOSED): Regime-robust walkforward/OOS under CompositeSignalGenerator regime shifts with tightened purge/embargo + determinism + strict serialization.
- [x] GATE INTEGRITY (CLOSED 2026-10-30T15:28:23Z): `tests/test_campaign_resume.py` handoff-contract failures cleared. Gate 351/351.
- [ ] **PRIORITY 2 (HIGHEST REMAINING - ATTACK NOW):** Adversarial correlation breakdowns/tail stress (portfolio/walkforward/signals) with concrete guards. Target `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`. Find concrete numerical edges (non-PSD correlation matrices, extreme tails, regime miscalibration, singular covariance, overflow/underflow) and add minimal guards; prove finiteness. No test changes.
- [ ] PRIORITY 3: Pricing/Greeks/IV + numerical guard coverage for remaining unguarded ops — Target `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`.
- [ ] PRIORITY 4: Risk/circuit-breaker/telemetry serialization hardening — Target `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`.
- [ ] PRIORITY 5: Safe performance hardening only if provably byte-identical/passing — Target `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`.
- [x] UPDATE HANDOFF with fresh timestamp + exact remaining work + concrete changes before ending session — DONE 2026-10-30T16:14:44Z
- [ ] Only commit if user explicitly requests it

## BOTTLENECK STATUS
- **CLEARED:** clamp infinite bound in execution/engine paths — fixed with finite bounds
- **CLEARED (HISTORICAL):** kilo edit-tool invalid-argument failures — prevention: complete edit calls with filePath/oldString/newString
- **CLEARED (HISTORICAL):** historical CI issues — file structure corrected, suite passes 351/351
- **CLEARED (2026-10-30T15:28:23Z):** gate-integrity blocker — `tests/test_campaign_resume.py` failures from trimmed handoff pointer file; restored required sections + Phase 1-5 markers. Gate GREEN 351/351.
- **ACTIVE:** None. All bottlenecks removed. ATTACK PRIORITY 2 DIRECTLY (adversarial correlation/tail stress) with minimal concrete guards only where adversarial edges exist; keep all existing tests unchanged/passing.

## NEXT FOCUS CAMPAIGN (FORCES HEAVY QUANT WORK)
Campaign Goal: Harden the system against adversarial regime/correlation/tail cases with production-grade numerical safety. Every session MUST produce measurable heavy-quant progress (concrete guard tightened, adversarial path hardened, purge/embargo tightened, serialization-safety fix, or invariant enforced) and end with gate GREEN.

Rules (ENFORCED):
- Heavy quant only. No scaffolding/stubs/placeholders/TODOs/FIXMEs/HACKs/XXX/new features.
- Correctness > speed. Determinism preserved. Backward-compatible minimal changes.
- Strict serialization: `allow_nan=False`. Zero NaN/Inf propagation.
- Numerical stability mandatory (guard divisions/logs/sqrt/powers/clamp).
- Verify after every change: run relevant tests + full gate before ending.
- Do NOT explore aimlessly. Attack concrete failing-adjacent edges via tests.
- Update handoff every session with timestamp + remaining work.
- A session may NOT end mid-priority without updating `research_state/durable_handoff.md` with fresh UTC timestamp and exact remaining work.

Acceptance Criteria (MUST HOLD SIMULTANEOUSLY):
- `python -m pytest -q` >= 351 passing, 0 failures, 0 warnings
- `tests/test_pipeline_determinism.py` byte-identical
- All serialized outputs finite, `allow_nan=False` enforced
- Zero TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`
- Working tree clean/intentional only. No debug prints/log spam.
- Determinism preserved (no RNG/seed/order changes)
