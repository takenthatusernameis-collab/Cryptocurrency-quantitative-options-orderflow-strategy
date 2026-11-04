TIMESTAMP: 2026-11-04T00:23:34Z
REPO: Cryptocurrency-quantitative-options-orderflow-strategy
PRIORITY: P0 - EXECUTION CRITICAL PATH
MODE: HEAVY IMPLEMENTATION (NO DOC-ONLY WORK)

# OBJECTIVE (DO NOT DEVIATE)
Make the strategy executable end-to-end with orderflow-driven signals wired into options execution, risk controls, and attribution. Treat passing tests as the gate to completion - remove every blocking bottleneck.

# INFERRED CONTEXT (BASED ON REPO STRUCTURE)
- Large test suite (phases 10..84) indicates a multi-phase campaign; integration gaps are the likely failure mode.
- Core surfaces present: `src/`, `tests/`, `research_state/`, `config/`, `scripts/`.
- Focus must be on wiring (orderflow -> signals -> sizing/greeks -> SOR/execution -> risk/telemetry), not re-documenting.

# BOTTLENECKS TO REMOVE FIRST (BLOCKING)
1. Test health: unknown pass/fail state. If red, fix until green. Do not skip.
2. Import/dependency/config: resolve any import errors, missing config, or env issues blocking tests.
3. Integration seams: connect orderflow microstructure to signal generation and options execution paths.
4. Production hardening seams: if phase tests reference guards/circuit breakers/attestation, wire them or fix them.

# HEAVY INITIAL TASK (MUST EXECUTE IN THIS ORDER)
## STEP 1: INVENTORY (5-10 min, but do it)
- Map `src/` by modules: orderflow, signals, options/pricing/greeks, execution/SOR, risk, portfolio, telemetry, config.
- Read top-level config (`config/`, `requirements.txt`, `mypy.ini`) to understand deps.
- Skim 2-3 failing phase tests if any to see exact contracts expected.

## STEP 2: UNBLOCK TESTS (BLOCKING - HEAVY)
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
pytest -q 2>&1 | tail -80
```
- Fix ALL failures. No "skip", no xfail without fixing root cause. If environment issue, fix deps/config.
- After each fix batch, re-run to verify.

## STEP 3: WIRE CRITICAL PATH (HEAVY IMPLEMENTATION)
- Ensure orderflow ingestion -> features/signals are consumed by options strategy logic.
- Ensure signals -> position sizing/greeks-aware sizing flows to execution/SOR with risk checks.
- Ensure risk/guards/circuit breakers are enforced (no bypass).
- Ensure telemetry/attribution hooks exist for executed paths.
- Make minimal, correct changes to satisfy tests and close seams.

## STEP 4: VERIFY END-TO-END (HARD GATE)
```bash
pytest -q 2>&1 | tail -40
```
- All tests must pass. If any remain, return to STEP 2.
- Optionally run a quick integration smoke if present in `scripts/` or `tests/test_pipeline_integration.py`.

# SUCCESS CRITERIA
- [ ] `pytest -q` passes with no errors/failures (blocking)
- [ ] Orderflow -> signals -> execution critical path is concretely wired (no unimplemented stubs blocking tested paths)
- [ ] Risk/guards enforced on execution paths touched
- [ ] Changes are minimal, correct, and consistent with existing codebase style

# NEXT FOCUS CAMPAIGN (IF ALREADY GREEN - FORCE HEAVY WORK)
If tests already pass, DO NOT stop. Run a deep integration pass:
1. Trace `tests/test_pipeline_integration.py` and harden seams it exercises.
2. Review phase tests for unintegrated components and wire them.
3. Add/strengthen integration between orderflow microstructure and options execution (dealer gamma/flow where referenced).
4. Stress test critical paths against adversarial tests (`tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`) and fix failures.
5. Re-run full suite until stable.

# RULES FOR THIS SESSION
- HEAVY WORK ONLY. Prioritize code changes over summaries/docs.
- REMOVE BOTTLENECKS. If blocked by missing piece, implement it.
- TEST-DRIVEN UNBLOCKING. Let tests tell you what to wire/fix.
- NO SCOPE CREEP TO PURELY COSMETIC. Fix what blocks progress.
- LEAVE NO OBVIOUS SEAM UNWIRED IF TESTS IMPLY IT.

START NOW: Run STEP 1 + STEP 2 immediately.
