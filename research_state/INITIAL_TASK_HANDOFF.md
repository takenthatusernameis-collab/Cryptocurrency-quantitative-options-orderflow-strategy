# INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
Timestamp (UTC): 2026-10-30T06:46:34Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

**SINGLE SOURCE OF TRUTH:** `research_state/durable_handoff.md`

This file points to the authoritative handoff. Read `durable_handoff.md` for full timestamped initial task message, bottlenecks, objectives, acceptance criteria, and execution rules.

## Initial Task Message
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant. Phases 1-7 COMPLETE. **NEXT MANDATORY FOCUS: PHASE 8 - PRODUCTION EXECUTION & RISK - LIVE READINESS & PERFORMANCE HARDENING (HEAVY QUANT).** See `durable_handoff.md`.

## Immediate Objectives
1. Re-verify baseline: `python -m pytest -q` (>=322 passing, 0 failures). `git status` clean.
2. **HEAVY QUANT PRIORITY:** Execute one unfinished Phase 8 item (execution performance benchmarks/latency profiling, multi-venue smart order routing, automated delta-hedging/rebalancing, circuit-breaker stress testing, walkforward/OOS execution+risk extension, or production monitoring/alerting hooks). Heavy quantitative engineering only.
3. Full simultaneous verification pass: pytest >=322 passing, determinism byte-identical, allow_nan=False serialization, finite outputs, zero TODO/FIXME/PLACEHOLDER/HACK/XXX in src/, working tree clean.
4. Do NOT end mid-phase without updating `durable_handoff.md` with fresh UTC timestamp and exact remaining work.

## Next Focus Campaign
**Campaign Goal:** Complete Phase 8 - Production Execution & Risk - Live Readiness & Performance Hardening with FULL simultaneous verification. Heavy quantitative engineering only - no scaffolding/stubs/TODOs/placeholders.

Phases:
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - COMPLETE
- Phase 6: Advanced Integration & Production Hardening - COMPLETE
- Phase 7: Production Execution & Risk Management - COMPLETE (CLOSED)
- Phase 8: Production Execution & Risk - Live Readiness & Performance Hardening - **NEXT (MANDATORY HEAVY WORK)**

**MANDATORY GATE:** All acceptance criteria in `durable_handoff.md` must pass simultaneously. Session must not end mid-phase without updating handoff.

**MANDATE:** Heavy quant only. Correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade. Complete end-to-end. Bottlenecks removed immediately. Determinism preserved. Minimal backward-compatible changes. Verify after every change. Read `durable_handoff.md` first.
