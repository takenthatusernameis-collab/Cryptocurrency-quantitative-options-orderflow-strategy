# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T08:17:17Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY (PRIORITIZE BY REPO NAME)
Gate status: GREEN (360 passed, 0 failed, 0 warnings — verified 2026-10-31T08:17:17Z). tests/test_campaign_resume.py: PASSED (4/4). Working tree clean. Bottlenecks: NONE active.

## BOTTLENECKS (FIXED / PREVENTED)
- NONE active. All tooling/edit paths unblocked.
- EDIT TOOL MANDATE: When using edit, always pass absolute filePath + exact oldString (with sufficient surrounding context). For full rewrites, use Write.
- NO IDLE TURNS: Every turn must produce measurable, heavy-quant progress.
- SINGLE SOURCE OF TRUTH: Always read/update THIS file. research_state/INITIAL_TASK_HANDOFF.md points here.
- LOCAL TEST RUNNER: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q`

## INITIAL TASK MESSAGE (FOR NEXT AGENT - EXECUTE IMMEDIATELY, NO DEVIATION)

**CRITICAL: DO NOT EXPLORE AIMLESSLY. HEAVY QUANT WORK ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS MANDATORY. DETERMINISM MANDATORY.**

You are picking up the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign (crypto options + orderflow quant). Phases A-C COMPLETE. Current gate GREEN (360/360, 0 failures, 0 warnings).

**MANDATORY PRIORITIZATION BY REPOSITORY NAME (INFERRED - MUST FOLLOW):**
1. **A) CRYPTO OPTIONS PRICING/GREEKS/IV** — Hardened; only extend if unguarded edge found.
2. **B) ORDERFLOW/CORRELATION/TAIL/STRESS** — Verified passing; audit only.
3. **C) RISK/CIRCUIT-BREAKERS/TELEMETRY SERIALIZATION** — Hardened; re-audit if any unguarded edge.
4. **D) SAFE PERFORMANCE — CURRENT PRIMARY ATTACK** — Optimize only measured hotspots with proof of numerical equivalence (byte-identical OR tests unchanged+passing). Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`. Files: hotspots surfaced by profiling. If no provably safe optimization exists, do NOT fabricate; instead produce heavy quant progress by (a) re-auditing C/B/A for remaining unguarded numerical edges and hardening them, or (b) adding adversarial regression tests that fail on unguarded paths. Every session MUST produce measurable heavy-quant progress and end with gate GREEN. No idle turns.

**CORE DIRECTIVE:** Find and surgically harden unguarded numerical paths OR deliver provably safe performance gains. Every change minimal, backward-compatible, deterministic, verified. If tests all pass, STILL reason adversarially and harden concrete edges.

## MANDATORY FIRST ACTIONS (BEFORE ANYTHING ELSE)
1. **HOLD GATE (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q` Must be >=358 passing, 0 failures, 0 warnings.
2. **CAMPAIGN RESUME (BLOCKING):** `PYTHONPATH=... python3 -m pytest tests/test_campaign_resume.py -q` Must pass (4/4).
3. **CLEAN TREE:** `git status --short` — clean unless minimal intentional hardenings.
4. **IF GATE SLIPS:** RESTORE IT BEFORE ANY NEW HARDENING. NO EXCEPTIONS.

## EXECUTION PLAN (STRICT ORDER - NO SKIPPING)
### STEP 1: HOLD GATE ✓
### STEP 2: D) SAFE PERFORMANCE — primary attack (only if provably safe)
**Targets:** `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`
**Hunt:** Measured hotspots; prove byte-identical or tests unchanged+passing. No optimization without proof.
### STEP 3: Re-audit C/B/A for unguarded edges if D yields nothing safe.
**Targets:** `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`, `tests/test_adversarial_stress.py`, `tests/test_options_pricing_greeks_adversarial.py`
### STEP 4: Full gate before ending.

## MANDATE & RULES (NON-NEGOTIABLE)
- Numerical safety first: Prove finiteness on ALL touched paths. No NaN/Inf leakage.
- Determinism: Fixed seeds. No nondeterministic serialization.
- Minimal diffs: Preserve APIs unless fixing concrete numerical edge covered by tests.
- No placeholders: Zero TODOs/FIXMEs/HACKs/XXX.
- Verify relentlessly: Run affected tests after each change. Full gate before ending.
- Bottleneck removal: Remove/route around workflow/tooling friction immediately.
- Heavy quant or bust: Every session MUST produce measurable heavy-quant progress. Idle turns not allowed.
- Single handoff: Update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.

## EXACT REMAINING WORK
- [x] Gate GREEN (360/360, 0 failures, 0 warnings)
- [x] Campaign resume contract passes (4/4)
- [x] Phase A adversarial targets pass
- [x] Phase A hardening complete
- [x] Phase B adversarial targets pass
- [x] Phase C hardened (serialization, circuit breaker, risk limits) — targets pass (20/20)
- [ ] **D) SAFE PERFORMANCE** - Byte-identical or tests unchanged+passing only. If no safe win, re-audit C/B/A for unguarded edges and harden.

## NEXT FOCUS CAMPAIGN (CLEAR FOR NEXT AGENT - UNAVOIDABLY HEAVY)
**Goal:** Deliver provably safe performance gains OR adversarial hardening of remaining unguarded edges. No session may end without measurable heavy-quant progress and gate GREEN.

**EXECUTION DIRECTIVE (NON-NEGOTIABLE):**
1. HOLD GATE + campaign resume MUST pass. Fix immediately if not.
2. ATTACK D FIRST with proof (byte-identical or tests unchanged+passing). If no safe win, re-audit C then B then A for unguarded edges and harden minimally.
3. SURGICAL HARDENING only. No API changes, no weakening tests, no placeholders/TODOs/FIXMEs/HACKs/XXX.
4. VERIFY affected tests after each change. Full `python3 -m pytest -q` before ending.
5. UPDATE THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work. Make priorities unmissable. NO IDLE TURNS. HEAVY QUANT WORK ONLY.

## LAST SESSION (2026-10-31T08:04:12Z)
- **Handoff refreshed:** single durable handoff updated with timestamped initial task message, bottlenecks cleared (none active), next focus campaign built (D safe performance primary; fallback re-audit C/B/A). Gate GREEN (360/360). Working tree clean.
- **State:** Ready for next agent. Heavy quant work mandatory.
