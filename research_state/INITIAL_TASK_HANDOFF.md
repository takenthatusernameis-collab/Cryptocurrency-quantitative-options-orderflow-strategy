# INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
Timestamp (UTC): 2026-10-30T16:14:22Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

**SINGLE SOURCE OF TRUTH:** research_state/durable_handoff.md

This file points to the authoritative handoff. Read durable_handoff.md for full timestamped initial task message, bottlenecks, objectives, acceptance criteria, and execution rules.

## Initial Task Message
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant. Phases 1-8 COMPLETE. **CURRENT STATE (2026-10-30T16:14:22Z): 351 tests passing, 0 failing, 0 warnings. Gate GREEN. Bottlenecks: NONE.** Read durable_handoff.md for exact requirements.

## Immediate Objectives
1. **FIX GATE:** Update `research_state/INITIAL_TASK_HANDOFF.md` to include required sections ("Initial Task Message", "Immediate Objectives", "Next Focus Campaign", "MANDATE") and Phase 1-5 markers so `tests/test_campaign_resume.py` passes. This is the ONLY failing blocker.
2. Re-verify baseline: `python -m pytest -q` (>=351 passing, 0 failures). `git status` clean/intentional.
3. **PRIORITY 1: CLOSED.**
4. **PRIORITY 2 (HIGHEST REMAINING):** Adversarial correlation/tail-stress hardening under regime shifts. Target `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`. Find concrete numerical edges (non-PSD correlation, extreme tails, regime miscalibration, singular covariance) and add minimal guards; prove finiteness.
5. Continue with P3-P5 as defined in durable_handoff.md.
6. Full simultaneous verification pass before ending; update durable_handoff.md with fresh UTC timestamp + changes + remaining work.

## Next Focus Campaign
**Campaign Goal:** Harden against adversarial regime/correlation/tail cases with production-grade numerical safety. Every session MUST produce measurable heavy-quant progress and end with gate GREEN.

**MANDATE:** Heavy quant only. Correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade. Complete end-to-end. Bottlenecks removed immediately. Determinism preserved. Minimal backward-compatible changes. Verify after every change. Read durable_handoff.md first.

### Phase 1
Regime-robust walkforward/OOS under CompositeSignalGenerator regime shifts with tightened purge/embargo + determinism + strict serialization. Concrete edges fixed: (a) regime boundary gaps at exact thresholds (inclusive), (b) non-finite PnL breaking portfolio summary serialization, (c) empty regime_shift_coverage/regime_info audit trail populated, (d) non-finite avg_entry_price poisoning mark_to_market_all equity. `test_oos_walkforward.py::test_walkforward_execution_risk_under_composite_regime_shifts_purge_embargo_determinism` passes unchanged. **CLOSED.**

### Phase 2
Adversarial correlation breakdowns/tail stress (portfolio/walkforward/signals) with concrete guards. Target `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`. Find concrete numerical edges (non-PSD correlation matrices, extreme tails, regime miscalibration, singular covariance, overflow/underflow) and add minimal guards; prove finiteness. **ATTACK NOW — HIGHEST REMAINING.**

### Phase 3
Pricing/Greeks/IV + numerical guard coverage for remaining unguarded ops. Target `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Harden Black-Scholes/Greeks/IV (safe_log/safe_sqrt/safe_pow, domain clamps) against adversarial inputs while preserving invariants.

### Phase 4
Risk/circuit-breaker/telemetry serialization hardening (block NaN/Inf, safe kill-switch paths). Target `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`. Enforce `allow_nan=False` and reject/neutralize non-finite propagations.

### Phase 5
Safe performance hardening only if provably byte-identical/passing. Target `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`. ONLY optimize if byte-identical OR all tests remain unchanged and passing. Prove with numbers.