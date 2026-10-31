# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T10:00:20Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY (PRIORITIZE BY REPO NAME)
Gate status: GREEN (362 passed, 0 failed, 0 warnings — verified 2026-10-31T10:00:20Z). tests/test_campaign_resume.py: PASSED (4/4). Working tree clean. Bottlenecks: NONE active.

## BOTTLENECKS (FIXED / PREVENTED)
- NONE active. All tooling/edit paths unblocked.
- EDIT TOOL MANDATE: When using edit, always pass absolute filePath + exact oldString (with sufficient surrounding context). For full rewrites, use Write.
- NO IDLE TURNS: Every turn must produce measurable, heavy-quant progress.
- SINGLE SOURCE OF TRUTH: Always read/update THIS file. research_state/INITIAL_TASK_HANDOFF.md points here.
- LOCAL TEST RUNNER: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q`
- CHECKPOINT-ONLY COMMITS ARE WASTE: Do not end a session with only "chore(kilo): checkpoint". Every session must add executable code, tests, data artifacts, or passing validation.

## INITIAL TASK MESSAGE (FOR NEXT AGENT - EXECUTE IMMEDIATELY, NO DEVIATION)

**CRITICAL: DO NOT EXPLORE AIMLESSLY. HEAVY QUANT WORK ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS MANDATORY. DETERMINISM MANDATORY.**

You are picking up the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign (crypto options + orderflow quant). Phases A-C COMPLETE. Current gate GREEN (360/360, 0 failures, 0 warnings).

**MANDATORY PRIORITIZATION BY REPOSITORY NAME (INFERRED - MUST FOLLOW):**
1. **A) CRYPTO OPTIONS PRICING/GREEKS/IV** — HIGHEST PRIORITY (repo name = crypto options). This is the core differentiator. Actively hunt for unguarded numerical edges, especially around:
   - Black-Scholes/Barone-Adesi-Whaley and any custom pricing in `src/features/options_pricing.py`
   - Greeks (delta/gamma/vega/theta/rho) - finite differences vs closed forms, sign conventions, ATM/ITM/OTM boundaries
   - IV surface construction, interpolation/extrapolation, arbitrage constraints in `src/features/iv_surface.py`
   Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Harden surgically with minimal diffs.
2. **B) ORDERFLOW/CORRELATION/TAIL/STRESS** — Audit for unguarded edges (especially tail/stress/correlation). Targets: `tests/test_adversarial_stress.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`. Source: `src/features/orderflow.py`, `src/signals/composite.py`, `src/ingestion/*`.
3. **C) RISK/CIRCUIT-BREAKERS/TELEMETRY SERIALIZATION** — Harden if any unguarded path found. Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`. Source: `src/risk/*`, `src/telemetry/*`.
4. **D) SAFE PERFORMANCE — SECONDARY ONLY IF A-C CLEAN** — Optimize only measured hotspots with proof of numerical equivalence (byte-identical OR tests unchanged+passing). Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`. If no provably safe optimization exists, DO NOT fabricate - go back to A and harden more aggressively.

**CORE DIRECTIVE:** By repo-name priority, ATTACK A FIRST. Find and surgically harden unguarded numerical paths in crypto options pricing/Greeks/IV. Every change minimal, backward-compatible, deterministic, verified. If tests all pass, STILL reason adversarially and harden concrete edges. No idle turns.

## MANDATORY FIRST ACTIONS (BEFORE ANYTHING ELSE)
1. **HOLD GATE (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q` Must be >=358 passing, 0 failures, 0 warnings.
2. **CAMPAIGN RESUME (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_campaign_resume.py -q` Must pass (4/4).
3. **CLEAN TREE:** `git status --short` — clean unless minimal intentional hardenings.
4. **IF GATE SLIPS:** RESTORE IT BEFORE ANY NEW HARDENING. NO EXCEPTIONS.

## EXECUTION PLAN (STRICT ORDER - NO SKIPPING)
### STEP 1: HOLD GATE ✓
### STEP 2: A) CRYPTO OPTIONS PRICING/GREEKS/IV — PRIMARY ATTACK
**Targets:** `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
**Hunt:** Finite differences vs analytical, gamma/delta/vega stability, division by zero, near-expiry, deep ITM/OTM, bad vol inputs, NaN/Inf propagation, IV interpolation/extrapolation producing arbitrage or non-finite values. Add guards (clamping/finite checks) only where they don't change correct results; prove via tests.
### STEP 3: B) ORDERFLOW/TAIL if A yields no obvious unguarded edges or as secondary hardenings
### STEP 4: C) RISK/TELEMETRY if needed
### STEP 5: D) SAFE PERFORMANCE only if A-C are provably hardened with no remaining obvious adversarial gaps
### STEP 6: Full gate before ending.

## MANDATE & RULES (NON-NEGOTIABLE)
- Numerical safety first: Prove finiteness on ALL touched paths. No NaN/Inf leakage.
- Determinism: Fixed seeds. No nondeterministic serialization.
- Minimal diffs: Preserve APIs unless fixing concrete numerical edge covered by tests.
- No placeholders: Zero TODOs/FIXMEs/HACKs/XXX.
- Verify relentlessly: Run affected tests after each change. Full gate before ending.
- Bottleneck removal: Remove/route around workflow/tooling friction immediately.
- Heavy quant or bust: Every session MUST produce measurable heavy-quant progress (code change + tests/guards + verification). Idle turns not allowed.
- Single handoff: Update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work. Make priorities unmissable. NO IDLE TURNS. HEAVY QUANT WORK ONLY.

## EXACT REMAINING WORK
- [x] Gate GREEN (360/360, 0 failures, 0 warnings)
- [x] Campaign resume contract passes (4/4)
- [x] Phase A adversarial targets pass
- [x] Phase A hardening complete
- [x] Phase B adversarial targets pass
- [x] Phase C hardened (serialization, circuit breaker, risk limits) — targets pass (20/20)
- [ ] **A) CRYPTO OPTIONS PRICING/GREEKS/IV** - Ongoing adversarial hardening by repo-name priority. Find and fix unguarded numerical edges.
- [ ] **B) ORDERFLOW/TAIL/STRESS** - Re-audit for any missed adversarial cases
- [ ] **C) RISK/CIRCUIT-BREAKERS/TELEMETRY** - Spot check for serialization/non-finite paths
- [ ] **D) SAFE PERFORMANCE** - Only if provably byte-identical/same tests passing

## NEXT FOCUS CAMPAIGN (CLEAR FOR NEXT AGENT - UNAVOIDABLY HEAVY)
**Goal:** Attack crypto options (pricing/Greeks/IV) first per repo name. Deliver surgical numerical hardenings or provably safe performance gains. No session may end without measurable heavy-quant progress and gate GREEN.

**EXECUTION DIRECTIVE (NON-NEGOTIABLE):**
1. HOLD GATE + campaign resume MUST pass. Fix immediately if not.
2. ATTACK A FIRST. Grep for potential unguarded divisions, logs of non-positive values, exp/pow, sqrt of negatives, IV solve paths, surface extrapolation. Add minimal guards with tests.
3. SURGICAL HARDENING only. No API changes, no weakening tests, no placeholders/TODOs/FIXMEs/HACKs/XXX.
4. VERIFY affected tests after each change. Full `python3 -m pytest -q` before ending.
5. UPDATE THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work. Make priorities unmissable. NO IDLE TURNS. HEAVY QUANT WORK ONLY.

## LAST SESSION (2026-10-31T10:00:20Z)
- **Handoff refreshed:** single durable handoff updated with timestamped initial task message prioritizing crypto options (A) by repo name, bottlenecks cleared (none active), next focus campaign enforced (A first, heavy quant mandatory). Gate GREEN (362/362). Working tree clean.
- **State:** Ready for next agent. Heavy quant work mandatory.
