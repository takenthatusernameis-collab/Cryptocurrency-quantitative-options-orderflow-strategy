# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo:** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy. Active track: **Chain B** (`src/hedging`) adaptive post-attribution seal orchestrator campaign (paper-only, additive, deterministic, bounded, guarded).
**Handoff verified/refreshed:** 2026-11-12T01:47:00Z (UTC). **This file is the ONLY durable handoff.** `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs — do not action stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped)

**`INIT-2026-11-12T01:41:45Z-PHASE258-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute end-to-end now; no deferral, no stubs, no partial completion).**

**Objective:** implement, verify, generate validated evidence, and seal **Phase258 adaptive-toxicity-resilient post-attribution seal orchestrator** (Chain B, `src/hedging`) composing **`PHASE257→PHASE32`** (12 coverage rows: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), seed `258258`, IDs `p258-*`, artifacts `PHASE258_*`.

**Predecessor sealed (do NOT re-implement/re-seal):** Phase257 — `research_state/PHASE257_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T013932Z.json` (`validation.valid=true`, `issues=[]`, seed `257257`, cycles `40`, composes `PHASE256→PHASE32`, `campaign.gates_ok=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, 12 coverage). Deliverables present: `src/hedging/phase257_*`, `scripts/generate_phase257_*`, `tests/test_phase257_*`, `tests/test_generate_phase257_*`.

### Phase258 implementation/verification scope (heavy — must complete)
1. **Additive deliverables (mirror Phase257 exactly):**
   - `src/hedging/phase258_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `scripts/generate_phase258_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   - `tests/test_phase258_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `tests/test_generate_phase258_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
2. **Compose `PHASE257→PHASE32`**. Seed `258258`, IDs `p258-*`. Upstream refs must include sealed Phase257 artifact above; flags `upstream_phase257/256/32` as appropriate per pattern.
3. **Verification (record exact results/caveats):**
   - `python3 -m py_compile` on 4 files (clean).
   - Module smoke: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. sys.setrecursionlimit(200000)` → expect `paper_only=True gates_ok=True composes ['PHASE257','PHASE32']`.
   - Module + generator pytest (targeted/governed, `PHASE_QUICK_VERIFY=1`, bounded timeouts/recursion as needed) — record pass counts/caveats.
   - Generate controlled evidence: `--cycles 40 --seed 258258 --write` then `--validate-only <artifact>` → `valid=true issues=[]`, deterministic/bounded, 12-coverage, guards intact.
   - CLI no-write smoke (no `--write`; generator does **not** accept `--no-write`): `runpy` + raised recursion if needed → `valid=true issues=[]`.
4. **Seal & advance handoff:** record exact artifact path/commands/caveats, re-verify P0, mark Phase258 sealed here, and replace active task with **`INIT-<UTC>-PHASE259-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE258→PHASE32`** (seed `259259`, IDs `p259-*`).

### Acceptance criteria
- Phase258 module/generator/tests exist and syntactically valid.
- Validated `research_state/PHASE258_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), deterministic/bounded, composes `PHASE257→PHASE32`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`.
- Verification evidence recorded (smokes, validate-only, CLI no-write, pytests) or explicit bounded governed caveats.
- P0 intact; handoff advanced to Phase259 only after seal.

## VERIFIED STATE (ground truth, 2026-11-12T01:47:00Z)

- **P0 safety:** **CLEAR** — `.env` **absent**; `.env.example:15` `LIVE_TRADING_ENABLED=false`. No venue/config/credential mutation performed or permitted.
- **Runtime deps:** **OK** — `pydantic/numpy/pandas/scipy/yaml/pytest` importable (Python 3.12.3).
- **Phase79/80/110–257:** **evidence-sealed** in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-implement/re-seal.
- **Phase258:** **NOT STARTED / ACTIVE** — no `src/hedging/phase258*`, `scripts/generate_phase258*`, `tests/*phase258*`, or `research_state/PHASE258_*` present (verified 2026-11-12T01:47:00Z). Execute active task.
- **Chain A:** `src/risk/phase*_live_execution*` out of scope (Chain B only).
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Competing handoffs:** stubs redirect here (cleared).

## BOTTLENECKS & UNBLOCKING (reconciled 2026-11-12T01:47:00Z)

| Bottleneck | Status | Unblock action |
|---|---|---|
| P0 safety drift | **CLEAR** | Re-verify before/after batch: `.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`, no venue/config/credential mutation. |
| Missing runtime deps | **CLEARED** | Imports OK now. If env regresses, provision per `requirements.txt`/docs without weakening guards. |
| Phase257 not sealed | **CLEARED** | Sealed artifact validated; do not re-seal. |
| **Phase258 not implemented/sealed** | **BLOCKING — ACTIVE** | **Execute `INIT-2026-11-12T01:41:45Z-PHASE258-POST-ATTRIBUTION-SEAL-DEPTH` end-to-end now.** |
| Deep-chain `RecursionError`/pytest slowness (→phase32) | **EXPECTED CAVEAT** | Use `PHASE_QUICK_VERIFY=1`, raise `sys.setrecursionlimit` (≥50k/200k), targeted tests, governed acceptance; record caveats. Generator CLI has no `--no-write` (run without `--write` / `runpy`). |
| Competing/stale handoffs | **CLEARED** | Keep this file single source; no duplicates. |
| NEXT9 A1–A7 | **BLOCKED — human-only** | Never unblock/mutate. |

## SCOPE & HARD GUARDS (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. No Chain A substitution.
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** No stubs, no deferral, no partial completion.
- **NO live trading. NO `.env` creation. NO venue/config/credential mutation. NO NEXT9 unblock.** Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Do not refactor sealed phases `phase79/80/110–257`.

## HANDOFF DISCIPLINE
- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- Final responses must not ask follow-up questions.
- After Phase258 seal, set active task to **`INIT-<UTC>-PHASE259-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE258→PHASE32`, seed `259259`, IDs `p259-*`).
