# INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
Timestamp (UTC): 2026-10-30T15:17:00Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

**SINGLE SOURCE OF TRUTH:** `research_state/durable_handoff.md`

This file points to the authoritative handoff. Read `durable_handoff.md` for full timestamped initial task message, bottlenecks, objectives, acceptance criteria, and execution rules.

## Initial Task Message
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant. Phases 1-8 COMPLETE. **CURRENT STATE (2026-10-30T15:17Z): 351 tests passing, gate GREEN.** See `durable_handoff.md` for exact requirements and the latest bottleneck resolution.

## Immediate Objectives
1. Re-verify baseline: `python -m pytest -q` (>=351 passing, 0 failures). `git status` shows intentional hardening changes.
2. **HEAVY QUANT PRIORITY #2 (PRIORITY 1 CLOSED):** Adversarial correlation/tail-stress hardening under regime shifts. Target `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`. Find concrete numerical edges (non-PSD correlation, extreme tails, regime miscalibration) and add minimal guards; prove finiteness. See `durable_handoff.md` for exact requirements.
3. **PRIORITY #3-5:** Pricing/Greeks/IV numerics, risk/circuit-breaker/telemetry serialization hardening, and safe performance hardening (only if byte-identical/passing).
4. Full simultaneous verification pass: pytest >=351 passing, determinism byte-identical, allow_nan=False serialization, finite outputs, zero TODO/FIXME/PLACEHOLDER/HACK/XXX in src/, working tree clean.
5. Do NOT end mid-phase without updating `durable_handoff.md` with fresh UTC timestamp and exact remaining work.

## Next Focus Campaign
**Campaign Goal:** Harden the system against adversarial regime/correlation/tail cases with production-grade numerical safety. Every session MUST produce measurable heavy-quant progress (concrete guard tightened, adversarial path hardened, purge/embargo tightened, serialization-safety fix, or invariant enforced) and end with gate GREEN.

Phases:
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - COMPLETE
- Phase 6: Advanced Integration & Production Hardening - COMPLETE
- Phase 7: Production Execution & Risk Management - COMPLETE (CLOSED)
- Phase 8: Production Execution & Risk - Live Readiness & Performance Hardening - regime boundary consistency, non-finite PnL guard, regime-shift coverage auditability, mark_to_market_all equity guard COMPLETE; adversarial/serialization hardening CONTINUES

**MANDATORY GATE:** All acceptance criteria in `durable_handoff.md` must pass simultaneously. Session must not end mid-phase without updating handoff.

**MANDATE:** Heavy quant only. Correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade. Complete end-to-end. Bottlenecks removed immediately. Determinism preserved. Minimal backward-compatible changes. Verify after every change. Read `durable_handoff.md` first.
