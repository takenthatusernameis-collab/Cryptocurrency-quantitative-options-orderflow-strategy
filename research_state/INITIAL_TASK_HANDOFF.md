# INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
Timestamp (UTC): 2026-10-31T16:52:52Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

**SINGLE SOURCE OF TRUTH:** research_state/durable_handoff.md

This file points to the authoritative handoff. Read durable_handoff.md for full timestamped initial task message, bottlenecks, objectives, acceptance criteria, and execution rules. Priorities inferred from repo name (crypto options + orderflow); A) CRYPTO OPTIONS PRICING/GREEKS/IV is highest (already green).

## Initial Task Message
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant. Phases 1-4b + Phase 5 (regime OOS + portfolio scaling + hedging robustness) COMPLETE. **CURRENT STATE (2026-10-31T16:52:52Z): 385 tests passing, 0 failing, 0 warnings. Gate GREEN. Bottlenecks: NONE.** Read durable_handoff.md for exact requirements.

## Immediate Objectives
1. **HOLD GATE:** `python -m pytest -q` (>=385 passing, 0 failures). `tests/test_campaign_resume.py` must pass.
2. **PRIORITY 1 (HIGHEST REMAINING - ATTACK NOW):** Campaign resume hardening + atomic checkpoint orchestration. `src/campaign/` is empty, no `scripts/run_campaign.py`, `tests/test_campaign_resume.py` is minimal. Build atomic checkpoint/resume orchestration + tests + `research_state/CAMPAIGN_RESUME_*.json` artifact + RESULTS_SUMMARY section. Read durable_handoff.md for exact requirements.
3. Continue P3-P5 (telemetry hardening, options adversarial audit) as defined in durable_handoff.md.
4. Full simultaneous verification pass before ending; update durable_handoff.md with fresh UTC timestamp + changes + remaining work.

## Next Focus Campaign
**Campaign Goal:** Harden the campaign lifecycle and telemetry with production-grade numerical safety. Every session MUST produce measurable heavy-quant progress and end with gate GREEN.

**MANDATE:** Heavy quant only. Correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade. Complete end-to-end. Bottlenecks removed immediately. Determinism preserved. Minimal backward-compatible changes. Verify after every change. Read durable_handoff.md first.

### Phase 1 (CLOSED)
Regime-robust walkforward/OOS under CompositeSignalGenerator regime shifts with tightened purge/embargo + determinism + strict serialization.

### Phase 2 (CLOSED)
Adversarial correlation/tail/cross-asset stress under portfolio walkforward/signals/routing — concrete numerical edges hunted and guarded.

### Phase 3 (CLOSED)
Crypto options pricing/Greeks/IV + numerical guard coverage hardened and verified green.

### Phase 4 (CLOSED)
Risk/circuit-breaker/orderflow/telemetry serialization hardening; `allow_nan=False` enforced.

### Phase 5 (ATTACK NOW - HIGHEST REMAINING)
Campaign resume hardening: atomic checkpoints, resumability, `scripts/run_campaign.py` state tracking, strengthened `tests/test_campaign_resume.py`, CAMPAIGN_RESUME artifact. Then telemetry/serialization hardening and options adversarial audit.
