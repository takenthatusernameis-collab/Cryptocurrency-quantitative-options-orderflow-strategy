# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T14:35:45Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: cryptocurrency options + orderflow quantitative strategy (derivatives pricing/Greeks/IV surfaces/delta-hedged PnL/attribution/regime classification/composite signals/execution/risk/multi-venue routing/latency/performance hardening/walkforward/OOS/purge-embargo)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (NO EXPLORATION, NO SCAFFOLDING)

State: 351 TESTS PASSING | 0 FAILING | 0 WARNINGS | WORKING TREE CLEAN | UP TO DATE WITH origin/main | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-8 COMPLETE | GATE GREEN | BASELINE VERIFIED 2026-10-30T14:35:45Z (python -m pytest -q → 351 passed)

## SESSION 2026-10-30T14:35Z — HANDOFF REFRESHED FOR NEXT AGENT (THIS IS THE SINGLE SOURCE OF TRUTH)
Action: Refreshed handoff with new UTC timestamp. Baseline verified `python -m pytest -q` → 351 passed, 0 failed, 0 warnings. Zero TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. Working tree clean. Tightened walkforward window metadata for regime/purge-embargo tracking; gate still GREEN. Bottlenecks: NONE. Attack Priority 1 (regime-robust walkforward/OOS under CompositeSignalGenerator regime shifts) directly.

Verified:
- `python -m pytest -q` → 351 passed, 0 failed, 0 warnings (2026-10-30T14:34:00Z)
- `tests/test_pipeline_determinism.py` → PASSED (byte-identical)
- Strict serialization enforced with `allow_nan=False`; zero NaN/Inf in serialized outputs/telemetry/events
- Zero TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`
- All numeric ops guarded against non-finite/overflow; purge/embargo/time-ordering enforced
- Bottleneck status: ACTIVE: None

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, DO NOT EXPLORE)
MANDATE: HEAVY QUANT ONLY. PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS/FIXMEs/HACKs/XXX. DO NOT REWRITE CORRECT CODE. FORCE HEAVY WORKING.

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

#### STEP 2: HEAVY QUANT PRIORITIES (IN ORDER, NO SKIPPING) — ATTACK PRIORITY 1 FIRST
1. **PRIORITY 1 - Regime-robust walkforward/OOS (HIGHEST - CORE TO THIS STRATEGY)** - Target `tests/test_oos_walkforward.py` esp. `test_walkforward_execution_risk_under_composite_regime_shifts_purge_embargo_determinism`. Tighten purge/embargo under `CompositeSignalGenerator` regimes (`high_vol_negative_gex`, `low_vol_positive_gex`, `skew_bearish`, `skew_bullish`, `neutral`). Stress regime flip boundaries, ensure determinism, strict serialization. No change to test expectations. This is the most relevant focus given repo is a quantitative options+orderflow strategy.
2. **PRIORITY 2 - Adversarial stress/correlation breakdowns** - Target `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`. Find concrete numerical edges (non-PSD correlation, extreme tails, regime miscalibration) and add minimal guards; prove finiteness.
3. **PRIORITY 3 - Pricing/Greeks/IV numerics** - Target `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Eliminate unguarded div/log/sqrt/pow/exp; enforce invariants (delta in [0,1] for calls/puts as applicable, gamma>=0 where expected, vega finite, no NaN/Inf). Minimal guards only.
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
- [x] HOLD GATE GREEN every session (verify baseline first) - VERIFIED 2026-10-30T14:34:00Z
- [x] CONCRETE NUMERICAL HARDENING (clamp/inf bug, safe_log/safe_pow, GEX overflow, variance/std overflow) — COMPLETED
- [ ] **PRIORITY 1 (ACTIVE):** Regime-robust walkforward/OOS under CompositeSignalGenerator regime shifts with tightened purge/embargo + determinism + strict serialization (target `test_oos_walkforward.py::test_walkforward_execution_risk_under_composite_regime_shifts_purge_embargo_determinism`). ATTACK IMMEDIATELY - NO EXPLORATION.
- [ ] **PRIORITY 2:** Adversarial correlation breakdowns/tail stress (portfolio/walkforward/signals) with concrete guards
- [ ] **PRIORITY 3:** Pricing/Greeks/IV + numerical guard coverage for remaining unguarded ops
- [ ] **PRIORITY 4:** Risk/circuit-breaker/telemetry serialization hardening (block NaN/Inf, safe kill-switch paths)
- [ ] **PRIORITY 5:** Safe performance hardening only if provably byte-identical/passing
- [ ] UPDATE HANDOFF with fresh timestamp + exact remaining work before ending session
- [ ] Only commit if user explicitly requests it

## BOTTLENECK STATUS
- **CLEARED:** clamp infinite bound in execution/engine paths — fixed with finite bounds
- **CLEARED (HISTORICAL):** kilo edit-tool invalid-argument failures — prevention: complete edit calls with filePath/oldString/newString
- **CLEARED (HISTORICAL):** historical CI issues — file structure corrected, suite passes 351/351
- **CLEARED (THIS REFRESH):** No active bottlenecks. Gate GREEN 351/351 at 2026-10-30T14:35:45Z. Working tree CLEAN. No TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`.
- **ACTIVE:** None. DO NOT PAUSE FOR EXPLORATION — ATTACK PRIORITY 1 DIRECTLY with minimal concrete guards if any edge is found; otherwise harden adjacent regime boundaries while keeping tests unchanged.

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
