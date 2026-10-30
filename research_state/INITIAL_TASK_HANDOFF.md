1: # INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
2: Timestamp (UTC): 2026-10-30T15:24:45Z
3: Project: Cryptocurrency-quantitative-options-orderflow-strategy
4:
5: **SINGLE SOURCE OF TRUTH:** research_state/durable_handoff.md
6:
7: This file points to the authoritative handoff. Read durable_handoff.md for full timestamped initial task message, bottlenecks, objectives, acceptance criteria, and execution rules.
8:
9: ## Initial Task Message (Summary)
10: **DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**
11:
12: You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant. Phases 1-8 COMPLETE. **CURRENT STATE (2026-10-30T15:24:45Z): 351 tests passing, gate GREEN.** Read durable_handoff.md for exact requirements.
13:
14: ## Immediate Focus
15: 1. Re-verify baseline: python -m pytest -q (>=351 passing, 0 failures). git status clean/intentional.
16: 2. **PRIORITY 1: CLOSED.**
17: 3. **PRIORITY 2 (HIGHEST REMAINING):** Adversarial correlation/tail-stress hardening under regime shifts. Target tests/test_adversarial_stress.py, tests/test_backtest_stress_adversarial.py, tests/test_portfolio_walkforward_correlation_adversarial.py, tests/test_signals_regime_calibration_adversarial.py. Find concrete numerical edges (non-PSD correlation, extreme tails, regime miscalibration, singular covariance) and add minimal guards; prove finiteness. See durable_handoff.md for exact requirements.
18: 4. Continue with P3-P5 as defined in durable_handoff.md.
19: 5. Full simultaneous verification pass before ending; update durable_handoff.md with fresh UTC timestamp + changes + remaining work.
20:
21: ## Next Focus Campaign
22: **Campaign Goal:** Harden against adversarial regime/correlation/tail cases with production-grade numerical safety. Every session MUST produce measurable heavy-quant progress and end with gate GREEN.
23:
24: **MANDATORY GATE:** All acceptance criteria in durable_handoff.md must pass simultaneously. Session must not end mid-phase without updating handoff.
25:
26: **MANDATE:** Heavy quant only. Correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade. Complete end-to-end. Bottlenecks removed immediately. Determinism preserved. Minimal backward-compatible changes. Verify after every change. Read durable_handoff.md first.
