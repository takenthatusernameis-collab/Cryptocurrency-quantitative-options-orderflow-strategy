TIMESTAMP: 2026-11-04T00:47:40Z
REPO: Cryptocurrency-quantitative-options-orderflow-strategy
PRIORITY: P0 - CRYPTO OPTIONS ORDERFLOW CRITICAL PATH
MODE: HEAVY IMPLEMENTATION (NO DOC-ONLY WORK)

# OBJECTIVE (NON-NEGOTIABLE)
Wire cryptocurrency options + orderflow end-to-end: orderflow microstructure -> features/signals -> greeks-aware sizing -> execution/SOR with risk guards -> telemetry/attribution. Treat `pytest` as gate. Eliminate every bottleneck preventing significant progress.

# CURRENT STATE (INFERRED)
- 337 src modules, 197 test files, 2799 tests collected
- Pipeline integration tests pass (3/3). Adversarial stress tests pass (25/25).
- Large phase-based test suite suggests many integration seams may be partially wired or need hardening
- Heavy artifacts in `research_state/` indicate prior campaign work

# BLOCKERS TO ELIMINATE IMMEDIATELY
1. **Full test health** - Run full suite in background/strategically; fix all failures with root-cause fixes (imports/config/cascades first). Never xfail/skip.
2. **Orderflow->Options wiring gaps** - Ensure CVD/OFI/footprint/liquidations flow into signals that actually reach options execution paths (dealer gamma/flow references).
3. **Execution/risk enforcement** - Verify pre-trade risk, guards, circuit breakers, kill-switch paths are enforced (no bypass) on any execution path touched by tests.
4. **Integration seams** - Close gaps surfaced by high-phase/pipeline/integration tests; wire unimplemented stubs that block tested behavior.

# MANDATORY EXECUTION SEQUENCE (HEAVY)

## STEP 1: RAPID MAP (5-10 min)
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
ls src/orderflow src/signals src/options src/execution src/risk src/integration src/flow 2>&1 | head -40
cat config/settings.yaml 2>&1 | head -80
cat requirements.txt
```

## STEP 2: UNBLOCK TESTS (BLOCKING)
```bash
python -m pytest -q 2>&1 | tail -60
```
- Triage first failures (imports/config/deps). Fix cascades. Re-run after each batch.
- If deps missing, install from requirements.txt immediately.
- Do not proceed until failures are understood and being fixed.

## STEP 3: WIRE CRITICAL CRYPTO OPTIONS ORDERFLOW PATH (HEAVY)
Prioritize wiring in this exact order:
1. **Orderflow ingestion/features** (`src/orderflow/`, `src/features/orderflow*`, `src/ingestion/*`) - ensure trades/liquidations/footprint/CVD/OFI normalized and consumed
2. **Signals** (`src/signals/`, `src/alpha/`, `src/flow/`) - flow orderflow features into composite signals with clear interfaces
3. **Options + greeks** (`src/options/`, `src/features/gamma_exposure*`, `src/features/iv*`) - greeks-aware sizing, gamma exposure, IV surface integrated
4. **Execution/SOR + risk** (`src/execution/`, `src/risk/`, `src/portfolio/`) - route through SOR with pre-trade checks, guards/circuit breakers/kill switches enforced
5. **Integration/orchestration/telemetry/attribution** (`src/integration/`, `src/orchestration/`, `src/telemetry/`, `src/attribution/`) - close seams, ensure observability on executed paths

## STEP 4: HARD GATE - FULL GREEN
```bash
python -m pytest -q 2>&1 | tail -40
python -m pytest tests/test_pipeline_integration.py -v 2>&1 | tail -10
```
ALL tests must pass. If any failures remain, return to STEP 2. No stopping while red.

# IF ALREADY GREEN (FORCE HEAVY CAMPAIGN)
Do NOT declare done. Execute deep integration hardening:
1. Trace `tests/test_pipeline_integration.py` and every import it touches - harden all seams
2. Sweep high-phase tests (phase 50+): identify unintegrated modules and wire them to exercised paths
3. Strengthen crypto options orderflow integration (dealer gamma positioning/flow, liquidity, pin risk where tested)
4. Stress adversarial paths: `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py` - keep green, add guards if brittle
5. Run full suite repeatedly until stable under all collected tests

# SUCCESS CRITERIA
- [ ] `python -m pytest -q` exits 0 with no failures/errors
- [ ] Concrete wiring: orderflow -> signals -> greeks-aware sizing -> execution/SOR with enforced risk guards
- [ ] No unimplemented stubs blocking tested paths; integration seams closed
- [ ] Changes minimal, idiomatic to codebase, tests updated only if fixing to match correct behavior

# RULES
- HEAVY WORK ONLY. Code > commentary/docs.
- REMOVE BOTTLENECKS. Implement missing pieces if they block tested behavior.
- TEST-DRIVEN. Let tests dictate exact wiring/fixes.
- NO COSMETIC SCOPE CREEP. Fix what blocks progress.
- NO SKIPPING FAILING TESTS.
- LEAVE NO OBVIOUS SEAM UNWIRED IF TESTS IMPLY IT.

START NOW: STEP 1 + STEP 2 immediately. Do not summarize - act.
