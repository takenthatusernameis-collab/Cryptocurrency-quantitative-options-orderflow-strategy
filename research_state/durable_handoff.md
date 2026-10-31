# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T17:52:29Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (prioritize by repo name -> crypto options pricing/Greeks/IV + orderflow features)

Gate status: GREEN (393 passed, 0 failed, 0 warnings — verified 2026-10-31T17:52:29Z via `python -m pytest tests/ -q`). Working tree clean, branch `main` up to date with `origin/main`.

COMPLETED (DO NOT REDO):
- Phases 1-4b: data/loaders, features (orderflow/gamma/IV/liquidity/vol/pricing), time-series + walk-forward/OOS with purge/embargo, portfolio walk-forward, options hedging integrated.
- Phase 5 Regime OOS: COMPLETE (artifacts + module + tests).
- Phase 5 Portfolio Scaling: COMPLETE (engine.py allocation weights/turnover cap; tests/test_portfolio_scaling.py 14 tests; PORTFOLIO_SCALING_*.json artifacts; RESULTS_SUMMARY section). Gate was 380.
- Phase 5 Hedging Robustness: COMPLETE (options_hedging.py PnL decomposition delta/gamma/vega/theta/residual, sum_attribution==total_pnl; tests/test_options_hedging.py extended; HEDGING_ROBUSTNESS_*.json artifact; RESULTS_SUMMARY section).
- Priority A (crypto options pricing/Greeks/IV): VERIFIED GREEN + hardened (safe_divide/safe_sqrt/safe_log/validate_finite guards, arbitrage guards, strict serialization; adversarial tests pass).

BOTTLENECKS REMOVED (THIS SESSION):
- [x] Portfolio scaling was a silent no-op in engine.py -> FIXED (allocation weights + turnover cap actually applied, train-only/no-lookahead, deterministic).
- [x] Stale root HANDOFF_NEXT_AGENT.md listed portfolio scaling as the current initial task though it is DONE -> this file (durable_handoff.md) is the SINGLE SOURCE OF TRUTH; root handoff is retired. Do NOT re-run portfolio scaling as the opening task.
- [x] Priority A already green -> not blocking. Move to the next unimplemented heavy item.
- No active bottlenecks. Next agent starts from a clean green baseline (385/385).

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION - EXECUTE IMMEDIATELY, NO DEVIATION)

**BY REPO NAME - CRYPTO OPTIONS + ORDERFLOW IS THE DOMAIN. HEAVY QUANT IMPLEMENTATION ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY. SHIP CODE/TESTS/ARTIFACTS EVERY SESSION.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign.
STATE: Phases 1-4b + Phase 5 (regime OOS + portfolio scaling + hedging robustness) complete. Priority A green. Gate GREEN (385/385). Bottlenecks: none. Previous agent left clean, verified state.

### MANDATORY INITIAL TASK: Campaign resume hardening + atomic checkpoint orchestration (PRIORITY 1 NOW — portfolio scaling and hedging are DONE)
Repo = crypto options+orderflow; a production strategy is only as good as its campaign lifecycle. Campaign orchestration is MISSING: `src/campaign/` is empty, there is no `scripts/run_campaign.py`, and `tests/test_campaign_resume.py` is minimal (only asserts the handoff file exists — zero coverage of checkpoint/resume/atomicity/state tracking). Implement and validate:

1) Add `scripts/run_campaign.py` (and/or a `src/campaign/` module) with: campaign state tracking (started/in-progress/completed/failed), atomic checkpoints (write-to-temp-then-rename so no partial writes), resume-from-checkpoint (skip completed windows/steps, replay failed steps), deterministic seeding, CLI verbs (`run`, `resume`, `status`, `abort`), and strict JSON serialization (`allow_nan=False`) of all state artifacts.
2) Strengthen `tests/test_campaign_resume.py`: atomic checkpoint integrity (no partial/torn writes), resume skips completed work (idempotent), resume re-runs failed steps, valid state transitions, CLI run/resume/status/abort behavior, determinism (same input -> identical state artifact), strict serialization `allow_nan=False`, corruption recovery (truncated/missing checkpoint -> safe restart or clear error).
3) Produce `research_state/CAMPAIGN_RESUME_{YYYYMMDDTHHMMSSZ}.json` covering a run -> checkpoint -> interrupt -> resume -> complete cycle, with state transitions, checkpoint counts, resume skip/replay evidence, and timing.
4) Update `research_state/RESULTS_SUMMARY.md` with a 'Phase 5: Campaign Resume Hardening' section.
5) Gate: `python -m pytest tests/ -q` green (>=385 passed, 0 failures). Fail-forward: extend APIs if awkward; fix bugs found. Do not skip implementation for discussion.

## NEXT FOCUS CAMPAIGN (EXECUTE AFTER/WHILE DOING THE INITIAL TASK)
### Phase 5: Production hardening, validation rigor, campaign automation (FORCE HEAVY IMPLEMENTATION)
1. **Campaign resume hardening** — ACTIVE NOW = current initial task above. `src/campaign/` empty + no `run_campaign.py` + `test_campaign_resume.py` minimal = a real gap. Build atomic checkpoint/resume orchestration + tests + artifact.
2. **Telemetry/serialization** — harden non-finite/NaN/Inf guards across production code paths (engine, hedging, features), ensure JSON-serializable artifacts under all regimes (`tests/test_nonfinite_result_serialization.py` exists; extend guards).
3. **A) Crypto options pricing/Greeks/IV adversarial audit** — VERIFIED GREEN + hardened. Remaining: write explicit adversarial audit (findings + verdict) for `src/features/options_pricing.py` + `src/features/iv_surface.py`. Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`.
4. **Portfolio scaling** — DONE (do not redo).
5. **Hedging robustness** — DONE (do not redo).

## IMMEDIATE FIRST ACTIONS
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q   # must be 385 passing, 0 failures

# 2) Confirm campaign orchestration gap
ls -la src/campaign/ scripts/run_campaign.py 2>&1
grep -rn "checkpoint\|resume\|atomic" tests/test_campaign_resume.py src/ scripts/ 2>&1 | head -20

# 3) Run campaign + telemetry + hedging + portfolio tests
python -m pytest tests/test_campaign_resume.py tests/test_nonfinite_result_serialization.py tests/test_options_hedging.py tests/test_portfolio_scaling.py -q

# 4) Implement campaign resume hardening per initial task; write CAMPAIGN_RESUME_*.json artifact; update RESULTS_SUMMARY.md
```

## HARD CONSTRAINTS
- **Heavy implementation required**: code/tests/artifacts, not just analysis/reports.
- **No checkpoint spam**: commit only when adding executable code/tests/data/artifacts or passing validation.
- **Deterministic & reproducible**: headless, `research_state/` artifacts, explicit configs.
- **Fail-forward**: extend APIs if awkward; fix bugs found.
- **Ship every session**: new code/tests/artifacts or concrete fixes with passing tests.
- **Don't redo completed phases**: 1-4b done + regime OOS done + portfolio scaling done + hedging robustness done + Priority A green - build on them.
- **Single handoff**: update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.

## SUCCESS CRITERIA (MUST HIT BEFORE NEXT HANDOFF)
- [ ] Gate GREEN: `python -m pytest tests/ -q` (>=385 passing, 0 failures)
- [ ] Campaign resume: `scripts/run_campaign.py` (and/or `src/campaign/`) with atomic checkpoints, run/resume/status/abort CLI, state tracking, strict JSON serialization.
- [ ] Campaign resume tests strengthened and passing (atomicity, idempotent resume, failed-step replay, state transitions, determinism, serialization, corruption recovery).
- [ ] `research_state/CAMPAIGN_RESUME_*.json` artifact with run->checkpoint->interrupt->resume->complete cycle evidence.
- [ ] `research_state/RESULTS_SUMMARY.md` updated with Phase 5: Campaign Resume Hardening section.
- [ ] Then continue campaign: telemetry/serialization hardening, options adversarial audit.

## NEXT AGENT INSTRUCTION (CLEAR, TIMESTAMPED, NON-DEFERRABLE)
**EXECUTE NOW - NO QUESTIONS - NO DELAY**
- Timestamp: 2026-10-31T16:52:52Z
- Read this file first. Do NOT re-run portfolio scaling or hedging robustness (DONE) or treat Priority A as blocking (already green).
- Start on the Campaign resume hardening initial task immediately. Produce code/guards/tests/artifacts every turn.
- Verify gate at start and end. Keep >=385 green.
- Update this handoff before finishing with concrete evidence.