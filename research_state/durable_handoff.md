# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T07:04:59Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY (PRIORITIZE BY REPO NAME)
Gate status: GREEN (358 passed, 0 failed, 0 warnings — verified 2026-10-31T05:14:27Z via `python3 -m pytest -q`). tests/test_campaign_resume.py: PASSED (4/4). Working tree clean. Bottlenecks removed/prevented.

## BOTTLENECKS (FIXED / PREVENTED)
- NONE active. All tooling/edit paths unblocked.
- EDIT TOOL MANDATE: When using edit, always pass absolute filePath + exact oldString (with sufficient surrounding context). Do NOT call edit with partial/empty args. For full rewrites, use Write. (Prevents the repeated `filePath`/`oldString` missing-argument aborts seen in workflow_run_diagnostics.jsonl.)
- NO IDLE TURNS: Every turn must produce measurable, heavy-quant progress. No exploration for exploration's sake.
- SINGLE SOURCE OF TRUTH: Always read/update THIS file. research_state/INITIAL_TASK_HANDOFF.md points here.
- LOCAL TEST RUNNER: If pytest not installed, use venv: `python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt && .venv/bin/python -m pytest -q`

## INITIAL TASK MESSAGE (FOR NEXT AGENT - EXECUTE IMMEDIATELY, NO DEVIATION)

**CRITICAL: DO NOT EXPLORE AIMLESSLY. HEAVY QUANT WORK ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS MANDATORY. DETERMINISM MANDATORY.**

You are picking up the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign (crypto options + orderflow quant). Phases 1-8 COMPLETE. Current gate is GREEN (358/358, 0 failures, 0 warnings).

**MANDATORY PRIORITIZATION BY REPOSITORY NAME (INFERRED - MUST FOLLOW):**
1. **A) CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST QUANT IMPACT)** — Black-Scholes/Greeks, IV surface/solver, arbitrage/invariants, crypto extreme regimes, strict `allow_nan=False` serialization. Attack unguarded numerical paths first. (Phase A hardening complete; extend adversarial coverage only if gaps found.)
2. **B) ORDERFLOW-INFORMED SIGNALS/CORRELATION/TAIL/PORTFOLIO/WALKFORWARD/ROUTING** — Non-PSD/ill-conditioned covariance, tail risk, regime shifts, weight blowups/concentration, routing failures. (VERIFIED PASSING — attack only if unguarded edges remain after audit.)
3. **C) RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY/SERIALIZATION (STRICT FINITENESS) — CURRENT PRIMARY ATTACK** — Block NaN/Inf propagation, kill-switch paths, `allow_nan=False` at every serialization call site. Adversarially hunt even if tests pass. (Files: `src/telemetry/serialization.py`, `src/risk/circuit_breaker.py`, `src/risk/limits.py`. Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`.)
4. **D) SAFE PERFORMANCE (ONLY IF PROVABLY BYTE-IDENTICAL OR TESTS UNCHANGED+PASSING)** — Optimize only measured hotspots with proof of numerical equivalence. (Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`.)

**CORE DIRECTIVE:** Find and surgically harden unguarded numerical paths under adversarial extremes. Every change minimal, backward-compatible, deterministic, verified. If tests all pass, STILL reason adversarially and harden concrete edges. Every session MUST produce measurable heavy-quant progress and end with gate GREEN.

## MANDATORY FIRST ACTIONS (BEFORE ANYTHING ELSE)
1. **HOLD GATE (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q` Must be >=358 passing, 0 failures, 0 warnings.
2. **CAMPAIGN RESUME (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_campaign_resume.py -q` Must pass (4/4).
3. **CLEAN TREE:** `git status --short` — clean unless minimal intentional hardenings.
4. **IF GATE SLIPS:** RESTORE IT BEFORE ANY NEW HARDENING. NO EXCEPTIONS.

## EXECUTION PLAN (STRICT ORDER - NO SKIPPING)
### STEP 1: HOLD GATE ✓ (current state GREEN)
### STEP 2: A) CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST - HARDENED, VERIFY NO GAPS)
**Targets:** `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
**Files:** `src/features/options_pricing.py`, `src/features/iv_surface.py`
**Status:** Deep adversarial hardening already in place. Only extend if untouched edge regimes remain.
### STEP 3: B) ORDERFLOW/CORRELATION/TAIL/STRESS (VERIFIED PASSING — AUDIT FOR GAPS)
**Targets:** `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`
**Files:** `src/backtest/engine.py`, `src/features/orderflow.py`, `src/execution/routing.py`, `src/signals/composite.py`, `src/risk/limits.py`
**Status:** Adversarial targets verified passing. Audit for any unguarded edge; add minimal guards only if gaps found. Do not weaken assertions.
### STEP 4: C) RISK/CIRCUIT-BREAKERS/TELEMETRY SERIALIZATION (STRICT FINITENESS) — CURRENT PRIMARY ATTACK
**Targets:** `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`
**Files:** `src/telemetry/serialization.py`, `src/risk/circuit_breaker.py`, `src/risk/limits.py`
**Hunt:** Enforce `allow_nan=False` everywhere, block NaN/Inf propagation, kill-switch hardening. Reason adversarially even if tests pass — find concrete unguarded edges (non-finite serialization leakage, kill-switch paths admitting NaN/Inf, missing `allow_nan=False` call sites, numpy scalar leakage, dict/list nesting).
### STEP 5: D) SAFE PERFORMANCE (ONLY IF PROVABLY SAFE)
**Targets:** `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py` — byte-identical or tests unchanged+passing only.

## MANDATE & RULES (NON-NEGOTIABLE)
- Numerical safety first: Prove finiteness on ALL touched paths. No NaN/Inf leakage.
- Determinism: Fixed seeds. No nondeterministic serialization.
- Minimal diffs: Preserve APIs unless fixing concrete numerical edge covered by tests. No rewriting correct code.
- No placeholders: Zero TODOs/FIXMEs/HACKs/XXX.
- Verify relentlessly: Run affected tests after each change. Full gate before ending.
- Campaign discipline: If no failing tests, STILL harden against adversarial extremes by reasoning about crypto options/orderflow.
- Bottleneck removal: Remove/route around workflow/tooling friction immediately.
- Heavy quant or bust: Every session MUST produce measurable heavy-quant progress. Idle turns not allowed.
- Single handoff: Update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.

## EXACT REMAINING WORK
- [x] Gate GREEN (358/358, 0 failures, 0 warnings) — verified 2026-10-31T05:14:27Z
- [x] Campaign resume contract passes (4/4)
- [x] Phase A adversarial targets pass (options_pricing_greeks_adversarial, iv_surface, phase1_gamma_invariants, numerical_guards)
- [x] Phase A hardening complete (options_pricing.py, iv_surface.py)
- [x] Phase B adversarial targets pass (adversarial_stress, backtest_stress_adversarial, portfolio_walkforward_correlation_adversarial, signals_regime_calibration_adversarial, routing_adversarial)
- [x] **C) RISK/CIRCUIT-BREAKERS/SERIALIZATION** - Hardened serialization for numpy scalars/arrays (allow_nan=False), tightened kill-switch drawdown handling (equity<=0), made circuit breaker snapshot/get_status serialization-safe. Targets pass (20/20). Full gate green.
- [ ] **D) SAFE PERFORMANCE** - Byte-identical or tests unchanged+passing only.

## NEXT FOCUS CAMPAIGN (CLEAR FOR NEXT AGENT - UNAVOIDABLY HEAVY)
**Goal:** Continue adversarial hardening across remaining areas; if no obvious gaps in C, proceed to D only if provably safe/byte-identical with passing tests. No session may end without producing measurable heavy-quant progress and gate GREEN.

**EXECUTION DIRECTIVE (NON-NEGOTIABLE):**
1. HOLD GATE + campaign resume MUST pass. Fix immediately if not.
2. ATTACK C FIRST if any unguarded edge remains (re-audit). If clean, move to B/A spot checks for regression; only proceed to D with proof of byte-identical or tests unchanged+passing.
4. SURGICAL HARDENING only. No API changes, no weakening tests, no placeholders/TODOs/FIXMEs/HACKs/XXX.
5. VERIFY affected tests after each change. Full `python3 -m pytest -q` before ending.
6. UPDATE THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work. Make priorities unmissable. NO IDLE TURNS. HEAVY QUANT WORK ONLY.

## LAST SESSION (2026-10-31T07:04:59Z)
- **Phase C hardened:** serialization now robust to numpy scalars/arrays and nested non-finite values; circuit breaker snapshot/get_status serialize safely; RiskManager kill-switch treats equity<=0 as drawdown breach and normalizes non-finite values.
- **Verification:** `tests/test_circuit_breaker.py tests/test_telemetry_end_to_end.py tests/test_nonfinite_result_serialization.py` all passed (20/20); full gate `python3 -m pytest -q` passed (358/358).
- **State:** Working tree clean; bottlenecks prevented; remaining work updated. Ready for next agent to audit remaining areas (focus D only if provably safe).
