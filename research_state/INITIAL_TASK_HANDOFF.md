# INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
Timestamp (UTC): 2026-10-29T21:04:25Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

**SINGLE SOURCE OF TRUTH:** `research_state/durable_handoff.md`

This file points to the authoritative handoff. Read `durable_handoff.md` for full timestamped initial task message, bottlenecks, objectives, acceptance criteria, and execution rules.

## Initial Task Message
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant. Phases 1-5 complete. **NEXT MANDATORY FOCUS: PHASE 6 - ADVANCED INTEGRATION & PRODUCTION HARDENING (HEAVY QUANT).** See `durable_handoff.md`.

## Immediate Objectives
1. Re-verify baseline: `python -m pytest -q` >=321 passing. `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean. `git status` clean.
2. **HEAVY QUANT PRIORITY:** Harden attribution in `src/backtest/options_hedging.py` (correct discrete decomposition, attribution sums to total_pnl within tolerance), audit numerical stability across options/IV/greeks/backtest, harden serialization (all paths use allow_nan=False), fortify determinism/regime robustness.
3. Full simultaneous verification pass: pytest + mypy + determinism + finite serialization + backward compatibility.
4. Do NOT end mid-Phase-6 without updating `durable_handoff.md` with fresh UTC timestamp and exact remaining work.

## Next Focus Campaign
**Campaign Goal:** Complete Phase 6 with full simultaneous verification. Attribution precision, numerical stability, serialization hardening, determinism fortification, regime robustness, production-grade integration tests. Heavy quantitative engineering only.

Phases:
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - COMPLETE
- Phase 6: Advanced Integration & Production Hardening - **IN PROGRESS (MANDATORY HEAVY WORK)**

**MANDATORY GATE:** All acceptance criteria in `durable_handoff.md` must pass simultaneously. Session must not end mid-Phase-6 without updating handoff.

**MANDATE:** Heavy quant only. Correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade. Complete end-to-end. Bottlenecks removed immediately. Determinism preserved. Minimal backward-compatible changes. Verify after every change. Read `durable_handoff.md` first.
