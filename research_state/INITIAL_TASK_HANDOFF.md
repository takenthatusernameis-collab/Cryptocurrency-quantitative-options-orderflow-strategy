# INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
Timestamp (UTC): 2026-10-29T20:06:45Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

**SINGLE SOURCE OF TRUTH:** `research_state/durable_handoff.md`

This file is the initial task message / index. The authoritative, single durable handoff for this campaign is `research_state/durable_handoff.md`. Do not maintain a second divergent copy — read `durable_handoff.md` for the full timestamped initial task message, immediate objectives, concrete targets, acceptance criteria, execution rules, and the next focus campaign. This file mirrors only the required section headers so the campaign-resume contract is satisfied; all detail lives in `durable_handoff.md`.

## Initial Task Message
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. This is production-grade crypto options + orderflow quant. Phases 1-4 complete and hardened. **NEXT MANDATORY FOCUS: PHASE 5 - PIPELINE INTEGRATION & END-TO-END CAMPAIGN VERIFICATION.** See `research_state/durable_handoff.md` for exact baseline, integration gaps, heavy quant tasks, and acceptance criteria.

## Immediate Objectives
1. Re-verify baseline: `python -m pytest -q` >=321 passing. `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean. `git status` shows only intentional Phase-5 edits.
2. **HEAVY QUANT:** Phase 5 verification gate — confirm IV/Greeks drive signal components (`components["iv_greeks"]` non-zero when inputs present), `backtest.iv_surfaces`/`options_hedging` populated when inputs provided, end-to-end determinism (byte-identical JSON run-to-run), and `allow_nan=False` serialization with NO NaN/Inf.
3. Full simultaneous verification pass: pytest + mypy + determinism + finite serialization + backward compatibility.
4. Declare Phase 5 complete ONLY when all acceptance criteria in `research_state/durable_handoff.md` pass simultaneously. Update handoff if stopping mid-campaign.

## Next Focus Campaign
**Campaign Goal:** Complete Phase 5 integration with full end-to-end verification. IV surface/Greeks MUST drive signals and backtest attribution. Pipeline MUST be deterministically verifiable run-to-run. Future agents MUST do heavy quantitative engineering - no scaffolding, no placeholders.

Phases:
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - **IN PROGRESS (MANDATORY HEAVY WORK)**
  - Done: `src/main.py` wiring verified; `src/signals/composite.py` IV/Greeks deepened (iv_greeks component); `src/backtest/engine.py` options_data_ref declared field; iv_surfaces/options_hedging populated
  - Remaining (VERIFICATION GATE): simultaneous pytest >=321 + mypy clean + determinism + finite serialization + backward compatibility

**Mandatory gate before declaring Phase 5 complete:** All acceptance criteria in `research_state/durable_handoff.md` must pass simultaneously. A session may not end mid-Phase-5 without updating `durable_handoff.md` with exact remaining work and fresh UTC timestamp.

## MANDATE
Heavy quantitative engineering only. Mathematical correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade only. Complete end-to-end. Do not stop at scaffolding. Bottlenecks removed immediately. Determinism preserved. Keep changes minimal and backward compatible. Verify after every change. See `research_state/durable_handoff.md` for full execution rules.

**Do not explore aimlessly. Do not rewrite existing correct code. Heavy quant work only. Phase 5 - Pipeline Integration & End-to-End Campaign Verification is the immediate mandatory focus.**
