# INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
Timestamp (UTC): 2026-10-29T18:57:00Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

**SINGLE SOURCE OF TRUTH:** `research_state/durable_handoff.md`

This file is the initial task message / index. The authoritative, single durable handoff for this campaign is `research_state/durable_handoff.md`. Do not maintain a second divergent copy — read `durable_handoff.md` for the full timestamped initial task message, immediate objectives, concrete targets, acceptance criteria, execution rules, and the next focus campaign. This file mirrors only the required section headers so the campaign-resume contract is satisfied; all detail lives in `durable_handoff.md`.

## Initial Task Message
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Phases 1-4 complete and hardened. **NEXT MANDATORY FOCUS: PHASE 5 - PIPELINE INTEGRATION & END-TO-END CAMPAIGN VERIFICATION.** See `research_state/durable_handoff.md` for the exact baseline, remaining files, and acceptance criteria.

## Immediate Objectives
1. Re-verify baseline: `python -m pytest -q` >=320 passing. `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean. `git status` clean of modifications.
2. PHASE 5 - Pipeline Integration (HEAVY): extend `src/signals/composite.py` and `src/backtest/engine.py` to consume IV surface/Greeks features (backward compatible); add end-to-end determinism test under `tests/`.
3. Full verification pass; hardening; update this handoff + `durable_handoff.md` if stopping mid-campaign.
See `research_state/durable_handoff.md` for exact file paths and next steps.

## Next Focus Campaign
**Campaign Goal:** Complete Phase 5 integration with full end-to-end verification. IV surface/Greeks must actually drive signals and backtest attribution; pipeline must be deterministically verifiable run-to-run. Future agents MUST do heavy quantitative engineering - integration must be complete and adversarially verified. No scaffolding, no placeholders.

Phases:
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - IN PROGRESS (IMMEDIATE FOCUS - HEAVY WORK)
  - Done: `src/main.py` wiring (IV surface, Greeks, serialization)
  - Remaining: `src/signals/composite.py` feature consumption hardening; `src/backtest/engine.py` options-aware inputs; end-to-end determinism test

**Mandatory gate before declaring Phase 5 complete:** All acceptance criteria in `research_state/durable_handoff.md` must pass simultaneously. A session may not end mid-Phase-5 without updating `durable_handoff.md` with exact remaining work.

## MANDATE
Heavy quantitative engineering only. Mathematical correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade only. Complete end-to-end. Do not stop at scaffolding. Bottlenecks removed immediately. Determinism preserved. Keep changes minimal and backward compatible. Verify after every change. See `research_state/durable_handoff.md` for the full execution rules.

**Do not explore aimlessly. Do not rewrite existing correct code. Heavy quant work only. Phase 5 - Pipeline Integration & End-to-End Campaign Verification is the immediate mandatory focus.**
