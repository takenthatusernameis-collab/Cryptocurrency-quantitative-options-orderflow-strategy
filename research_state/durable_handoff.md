# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T18:44:47Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (prioritize by repo name -> crypto options pricing/Greeks/IV + orderflow features)

Gate status: GREEN (405 passed, 0 failed, 2 skipped — verified 2026-10-31T18:44:47Z via `python -m pytest tests/ -q`). Working tree clean, branch `main` up to date with `origin/main`.

COMPLETED (DO NOT REDO):
- Phases 1-4b: data/loaders, features (orderflow/gamma/IV/liquidity/vol/pricing), time-series + walk-forward/OOS with purge/embargo, portfolio walk-forward, options hedging integrated.
- Phase 5 Regime OOS: COMPLETE (artifacts + module + tests).
- Phase 5 Portfolio Scaling: COMPLETE (engine.py allocation weights/turnover cap; tests/test_portfolio_scaling.py 14 tests; PORTFOLIO_SCALING_*.json artifacts).
- Phase 5 Hedging Robustness: COMPLETE (options_hedging.py PnL decomposition delta/gamma/vega/theta/residual, sum_attribution==total_pnl; tests/test_options_hedging.py extended; HEDGING_ROBUSTNESS_*.json artifact).
- Phase 5 Campaign Resume Hardening: COMPLETE (`src/campaign/core.py` atomic checkpoints + state tracking + resume; `scripts/run_campaign.py` CLI run/resume/status/abort; `tests/test_campaign_resume.py` strengthened; research_state/CAMPAIGN_RESUME_20261031T175208Z.json; RESULTS_SUMMARY.md section).
- Phase 5 Telemetry/Serialization hardening: COMPLETE THIS SESSION — `src/backtest/engine.py` profit_factor no longer emits `inf` when wins exist with zero losses (now finite total_wins; never collapses to 0); `tests/test_backtest_numeric.py::test_profit_factor_inf_when_no_losses` realigned to assert finite + strict `allow_nan=False` serialization. Gate restored GREEN (was 403 passed / 2 failed on test_artifact_serialization trending+ranging).
- Priority A (crypto options pricing/Greeks/IV): VERIFIED GREEN + hardened (safe_divide/safe_sqrt/safe_log/validate_finite guards, arbitrage guards, strict serialization; adversarial tests pass).

BOTTLENECKS REMOVED (THIS SESSION):
- [x] Gate was RED: `test_artifact_serialization.py::test_real_regime_artifact_is_strict[trending/ranging]` raised SerializationError because regime walk-forward payloads contained non-finite `profit_factor` (Inf when gross_loss==0). Fixed at source in `src/backtest/engine.py` (finite profit_factor) and realigned `tests/test_backtest_numeric.py` (was asserting `isinf`, i.e. demanding non-serializable output). Gate now GREEN (405 passed, 0 failed).
- [x] No active bottlenecks. Next agent starts from a clean green baseline (405/405).

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION - EXECUTE IMMEDIATELY, NO DEVIATION)

**BY REPO NAME - CRYPTO OPTIONS + ORDERFLOW IS THE DOMAIN. HEAVY QUANT IMPLEMENTATION ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY. SHIP CODE/TESTS/ARTIFACTS EVERY SESSION.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign.
STATE: Phases 1-4b + Phase 5 (regime OOS + portfolio scaling + hedging robustness + campaign resume hardening + telemetry/serialization hardening) complete. Priority A green. Gate GREEN (405 passed, 0 failed). Bottlenecks: none. Previous agent left clean, verified state.

### MANDATORY INITIAL TASK: Phase 5 item A — Crypto options pricing/Greeks/IV adversarial audit (PRIORITY 1 NOW)
Repo = crypto options+orderflow. The remaining heavy implementation item is the adversarial audit of the options pricing/Greeks/IV surface. `src/features/options_pricing.py` and `src/features/iv_surface.py` are Priority A (green + hardened) but lack an explicit adversarial audit document with findings + verdict. Implement and validate:

1) Write an explicit adversarial audit for `src/features/options_pricing.py` and `src/features/iv_surface.py`: probe extreme inputs (spot/strike/rate/volatility = 0, inf, nan, negative, deep ITM/OTP, near-expiry, put-call parity, gamma/vanna/charm sign conventions, IV surface arbitrage bounds, calendar butterfly constraints). Record every input that breaks or misbehaves, the root cause, and a verdict (PASS/FIX-NEEDED) per function.
2) Strengthen/extend the adversarial test targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Every adversarial case must assert finite, deterministic, strictly serializable (`allow_nan=False`) outputs; no NaN/Inf may reach any artifact.
3) Produce `research_state/OPTIONS_ADVERSARIAL_AUDIT_{YYYYMMDDTHHMMSSZ}.json` covering: audited functions, adversarial cases tried, failures found, fixes applied, verdict per function, timestamps.
4) Update `research_state/RESULTS_SUMMARY.md` with a 'Phase 5: Options Pricing/Greeks/IV Adversarial Audit' section.
5) Gate: `python -m pytest tests/ -q` green (>=405 passed, 0 failures). Fail-forward: extend APIs if awkward; fix bugs found. Do not skip implementation for discussion.

## NEXT FOCUS CAMPAIGN (EXECUTE AFTER THE INITIAL TASK)
### Phase 5: Production hardening, validation rigor, campaign automation
1. Campaign resume hardening — DONE.
2. Telemetry/serialization hardening — DONE (profit_factor inf source fix).
3. **A) Crypto options pricing/Greeks/IV adversarial audit — ACTIVE NOW** = current initial task above. Build the audit + tests + artifact + RESULTS_SUMMARY section.
4. Portfolio scaling — DONE (do not redo).
5. Hedging robustness — DONE (do not redo).

## IMMEDIATE FIRST ACTIONS
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q   # must be 405 passing, 0 failures

# 2) Confirm adversarial-audit test targets exist
ls tests/test_options_pricing_greeks_adversarial.py tests/test_iv_surface.py tests/test_phase1_gamma_invariants.py tests/test_numerical_guards.py

# 3) Run options/numerical tests
python -m pytest tests/test_options_pricing_greeks_adversarial.py tests/test_iv_surface.py tests/test_phase1_gamma_invariants.py tests/test_numerical_guards.py -q

# 4) Implement the adversarial audit per the initial task; write OPTIONS_ADVERSARIAL_AUDIT_*.json; update RESULTS_SUMMARY.md
```

## HARD CONSTRAINTS
- **Heavy implementation required**: code/tests/artifacts, not just analysis/reports.
- **No checkpoint spam**: commit only when adding executable code/tests/data/artifacts or passing validation.
- **Deterministic & reproducible**: headless, `research_state/` artifacts, explicit configs.
- **Fail-forward**: extend APIs if awkward; fix bugs found.
- **Ship every session**: new code/tests/artifacts or concrete fixes with passing tests.
- **Don't redo completed phases**: 1-4b done + regime OOS done + portfolio scaling done + hedging robustness done + campaign resume done + telemetry/serialization done + Priority A green - build on them.
- **Single handoff**: update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.

## SUCCESS CRITERIA (MUST HIT BEFORE NEXT HANDOFF)
- [ ] Gate GREEN: `python -m pytest tests/ -q` (>=405 passing, 0 failures)
- [ ] Options adversarial audit: explicit findings + verdict for `src/features/options_pricing.py` + `src/features/iv_surface.py`.
- [ ] Adversarial tests strengthened and passing (finite/deterministic/strict-serializable outputs under extreme inputs).
- [ ] `research_state/OPTIONS_ADVERSARIAL_AUDIT_*.json` artifact with cases, failures, fixes, verdicts, timing.
- [ ] `research_state/RESULTS_SUMMARY.md` updated with Phase 5: Options Pricing/Greeks/IV Adversarial Audit section.

## NEXT AGENT INSTRUCTION (CLEAR, TIMESTAMPED, NON-DEFERRABLE)
**EXECUTE NOW - NO QUESTIONS - NO DELAY**
- Timestamp: 2026-10-31T18:44:47Z
- Read this file first. Do NOT re-run portfolio scaling, hedging robustness, campaign resume, or telemetry/serialization hardening (DONE). Do NOT treat Priority A as blocking (already green) — proceed to the adversarial audit.
- Start on the Phase 5 item A adversarial audit immediately. Produce code/tests/artifacts every turn.
- Verify gate at start and end. Keep >=405 green.
- Update this handoff before finishing with concrete evidence.
