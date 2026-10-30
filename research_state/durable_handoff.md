# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T11:26:03Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: cryptocurrency options + orderflow quantitative strategy (derivatives pricing/Greeks/IV surfaces/delta-hedged PnL/attribution/regime classification/composite signals/execution/risk/multi-venue routing/latency/performance hardening/walkforward/OOS/purge-embargo)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (NO EXPLORATION, NO SCAFFOLDING)

State: 346 TESTS PASSING | 0 FAILING | 0 WARNINGS | WORKING TREE CLEAN | UP TO DATE WITH origin/main | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-8 COMPLETE | GATE GREEN | BASELINE VERIFIED 2026-10-30T11:26:03Z (python -m pytest -q → 346 passed; determinism byte-identical; git status clean)

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, DO NOT EXPLORE)
**MANDATE: HEAVY QUANT ONLY. PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW. NO SCAFFOLDING/STUBS/TODOs/PLACEHOLDERS/FIXMEs/HACKs/XXX. DO NOT REWRITE CORRECT CODE.**

You are inheriting the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign. Everything is built and verified green (346/346). Your sole purpose is to **GUARD THE GATE** and do **concrete hardening**. Future agents must NOT avoid heavy working - this message forces it.

### EXECUTE IN EXACT ORDER (BLOCKING)
#### STEP 1: HOLD THE GATE (MANDATORY, BLOCKS ALL ELSE)
```bash
python -m pytest -q  # MUST be >=346 passing, 0 failures, 0 warnings
```
Simultaneous checks:
- `tests/test_pipeline_determinism.py` passes (byte-identical)
- Strict serialization: use `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. ZERO NaN/Inf.
- Numerical stability: guard divisions/logs/sqrt/powers. ALL outputs finite.
- ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. `git status` clean.
- If ANY fails → minimal concrete fix BEFORE Step 2.

#### STEP 2: HEAVY QUANT PRIORITIES (IN ORDER, NO SKIPPING)
1. **Regime-robust walkforward/OOS** - `tests/test_oos_walkforward.py` (esp. `test_walkforward_execution_risk_under_composite_regime_shifts_purge_embargo_determinism`). Tighten purge/embargo, regime-shift realism, execution costs under CompositeSignalGenerator regimes. Determinism required.
2. **Adversarial stress/correlation** - `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`. Harden tails, correlation breakdowns, regime miscalibration.
3. **Pricing/Greeks/IV numerics** - `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Remove unguarded ops, enforce finiteness, preserve invariants.
4. **Risk/circuit-breakers/telemetry** - `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`. Strict serialization, block NaN/Inf propagation, safe alerts/kill-switch paths.
5. **Performance** - `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`. Only optimize if byte-identical or all tests unchanged. Prove it.

Every change must be minimal/backward-compatible, justified by numerical edge/adversarial case, and pass existing tests.

#### STEP 3: FINAL GATE (BEFORE ENDING)
1. `python -m pytest -q` >= 346 passing (0 failures). Only increase with justification.
2. `tests/test_pipeline_determinism.py` byte-identical.
3. allow_nan=False everywhere; no NaN/Inf.
4. All finite, numerically stable.
5. All existing tests unchanged/passing.
6. ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`, `git status` clean.
7. **UPDATE THIS FILE** with fresh UTC timestamp + exact remaining work.

## EXACT REMAINING WORK
- [ ] HOLD GATE GREEN every session (verify baseline first) — current: 346/346 passing, 0 warnings
- [ ] HEAVY QUANT HARDENING: regime/OOS walkforward + adversarial stress/correlation + pricing/Greeks/IV + risk/circuit-breaker/telemetry serialization (all green; find and fix concrete numerical edges)
- [ ] CONCRETE IMPROVEMENTS only where they harden correctness/numerics/stability without breaking tests; prove impact
- [ ] UPDATE HANDOFF with fresh timestamp + exact remaining work before ending session

## BOTTLENECK STATUS
- ALL CLEARED. Working tree clean. 346 passing. Gate GREEN. No active blockers.
- HISTORICAL BOTTLENECKS REMOVED: workflow_run_diagnostics.jsonl showed repeated kilo edit-tool invalid-argument failures and turn aborts (kilo_invalid_argument_turn_abort). Root cause: malformed edit calls. Future sessions: issue complete edit calls (filePath + oldString + newString). Focus: pure hardening.

## NEXT FOCUS CAMPAIGN (FORCES HEAVY QUANT WORK)
Sustain production-readiness hardening indefinitely. Every session MUST produce measurable heavy-quant progress (tightened guard, hardened adversarial path, tightened purge/embargo, or serialization-safety fix) and end with gate GREEN. Steps 1-3 mandatory. No scaffolding/stubs/placeholders/exploration/new features — correctness, numerical stability, determinism, strict serialization only.
