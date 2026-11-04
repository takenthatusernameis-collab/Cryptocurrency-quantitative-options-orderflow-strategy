TIMESTAMP: 2026-11-04T00:25:37Z
REPO: Cryptocurrency-quantitative-options-orderflow-strategy
PRIORITY: P0 - EXECUTION CRITICAL PATH
MODE: HEAVY IMPLEMENTATION (NO DOC-ONLY WORK)

# OBJECTIVE (DO NOT DEVIATE)
Make the strategy executable end-to-end with orderflow-driven signals wired into options execution, risk controls, and attribution. Treat passing tests as the gate to completion - remove every blocking bottleneck.

# INFERRED CONTEXT (BASED ON REPO STRUCTURE)
- Large test suite (2799 tests collected) across phases 1..84, integration, adversarial/stress - integration gaps are likely failure mode
- Core surfaces: `src/` (orderflow, signals, options/pricing/greeks, execution/SOR, risk, portfolio, telemetry), `tests/`, `research_state/` (extensive artifacts), `config/`, `scripts/`
- Focus on wiring (orderflow -> signals -> sizing/greeks -> SOR/execution -> risk/telemetry/attribution), not re-documenting

# BOTTLENECKS TO REMOVE FIRST (BLOCKING)
1. **Test health** - Run full suite and fix all failures until green. Do not skip/xfail without fixing root cause.
2. **Import/dependency/config** - Resolve import errors, missing config, env issues blocking tests
3. **Integration seams** - Connect orderflow microstructure to signal generation and options execution paths
4. **Production hardening** - Wire guards/circuit breakers/kill switches/attestation where phase tests reference them

# HEAVY INITIAL TASK (MUST EXECUTE IN THIS ORDER)

## STEP 1: INVENTORY (QUICK MAP)
- Map critical modules: `src/orderflow/`, `src/signals/` (or alpha/features), `src/options/`, `src/execution/`, `src/risk/`, `src/portfolio/`, `src/telemetry/`, `src/integration/`, `src/config/`
- Review `config/`, `requirements.txt`, `mypy.ini`
- Note `src/main.py` and pipeline orchestration

## STEP 2: UNBLOCK TESTS (BLOCKING - HEAVY)
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
python -m pytest -q 2>&1 | tail -80
```
- Fix ALL failures. After each fix batch, re-run. If environment issue (deps), install/fix immediately.
- Focus on first failures - often import/config cascade.

## STEP 3: WIRE CRITICAL PATH (HEAVY IMPLEMENTATION)
- **Orderflow ingestion -> features/signals**: Ensure orderflow microstructure consumed by signal generation
- **Signals -> sizing/greeks-aware**: Flow to position sizing with greeks awareness
- **Execution/SOR + risk checks**: Route through SOR with pre-trade risk/guards/circuit breakers enforced (no bypass)
- **Telemetry/attribution**: Ensure hooks exist for executed paths
- **Integration seams**: Close gaps revealed by integration/phase tests

## STEP 4: VERIFY END-TO-END (HARD GATE)
```bash
python -m pytest -q 2>&1 | tail -40
```
- All tests must pass. If any remain, return to STEP 2.
- If pipeline integration tests exist, ensure they pass: `python -m pytest tests/test_pipeline_integration.py -v`

# SUCCESS CRITERIA
- [ ] `python -m pytest -q` passes with no errors/failures (blocking)
- [ ] Orderflow -> signals -> execution critical path concretely wired (no unimplemented stubs blocking tested paths)
- [ ] Risk/guards/circuit breakers enforced on execution paths touched
- [ ] Changes minimal, correct, consistent with existing codebase style

# NEXT FOCUS CAMPAIGN (IF ALREADY GREEN - FORCE HEAVY WORK)
If tests already pass, DO NOT stop. Run deep integration pass:
1. Trace `tests/test_pipeline_integration.py` and harden seams it exercises
2. Review high-phase tests (70+) for unintegrated components and wire them
3. Strengthen integration between orderflow microstructure and options execution (dealer gamma/flow where referenced)
4. Stress test critical paths: `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py` - fix failures
5. Re-run full suite until stable

# RULES FOR THIS SESSION
- HEAVY WORK ONLY. Prioritize code changes over summaries/docs
- REMOVE BOTTLENECKS. If blocked by missing piece, implement it
- TEST-DRIVEN UNBLOCKING. Let tests tell you what to wire/fix
- NO SCOPE CREEP TO PURELY COSMETIC. Fix what blocks progress
- LEAVE NO OBVIOUS SEAM UNWIRED IF TESTS IMPLY IT
- DO NOT SKIP FAILING TESTS

START NOW: Run STEP 1 + STEP 2 immediately.
