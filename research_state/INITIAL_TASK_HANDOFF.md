# INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
Timestamp (UTC): 2026-10-30T15:13:15Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

**SINGLE SOURCE OF TRUTH:** `research_state/durable_handoff.md`

This file points to the authoritative handoff. Read `durable_handoff.md` for full timestamped initial task message, bottlenecks, objectives, acceptance criteria, and execution rules.

## Initial Task Message
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant. Phases 1-8 COMPLETE. **CURRENT STATE (2026-10-30T13:38Z): 351 tests passing, gate GREEN.** See `durable_handoff.md` for exact requirements and the latest bottleneck resolution.

## Immediate Objectives
1. Re-verify baseline: `python -m pytest -q` (>=351 passing, 0 failures). `git status` shows intentional hardening changes.
2. **HEAVY QUANT PRIORITY #1:** Extend walkforward/OOS to full execution+risk path under regime shifts (purge/embargo, determinism, strict serialization). Exercise with CompositeSignalGenerator regimes (`high_vol_negative_gex`, `low_vol_positive_gex`, `skew_bearish`, `skew_bullish`, `neutral`). See `durable_handoff.md` for exact requirements.
3. **PRIORITY #2:** Add serialization-safe production monitoring/alerting hooks for risk-limit breaches and kill-switch events (RiskManager/CircuitBreaker + telemetry).
4. Full simultaneous verification pass: pytest >=351 passing, determinism byte-identical, allow_nan=False serialization, finite outputs, zero TODO/FIXME/PLACEHOLDER/HACK/XXX in src/, working tree clean.
5. Do NOT end mid-phase without updating `durable_handoff.md` with fresh UTC timestamp and exact remaining work.

## Next Focus Campaign
**Campaign Goal:** Complete Phase 8 remaining hardening with FULL simultaneous verification. Heavy quantitative engineering only - no scaffolding/stubs/TODOs/placeholders.

Phases:
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - COMPLETE
- Phase 6: Advanced Integration & Production Hardening - COMPLETE
- Phase 7: Production Execution & Risk Management - COMPLETE (CLOSED)
- Phase 8: Production Execution & Risk - Live Readiness & Performance Hardening - clamp/log/pow/variance hardening COMPLETE; adversarial/serialization hardening CONTINUES

**MANDATORY GATE:** All acceptance criteria in `durable_handoff.md` must pass simultaneously. Session must not end mid-phase without updating handoff.

**MANDATE:** Heavy quant only. Correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade. Complete end-to-end. Bottlenecks removed immediately. Determinism preserved. Minimal backward-compatible changes. Verify after every change. Read `durable_handoff.md` first.
