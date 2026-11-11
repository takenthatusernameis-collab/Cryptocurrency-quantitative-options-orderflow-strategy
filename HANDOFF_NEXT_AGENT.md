# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B (`src/hedging`) adaptive post-attribution seal orchestrator campaign is the active paper-only engineering track.
**Handoff refreshed (verified):** 2026-11-11T23:37:00Z (UTC). **This file is the ONLY durable handoff.** `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs (re-synced 23:37:00Z) — do not action stubs or create new handoff files.
**P0 re-verified (23:37:00Z):** no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. **New bottleneck:** runtime missing deps (`pydantic`, `numpy`, `pandas`, `scipy` absent) — Phase254 evidence/seal blocked at import boundary.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T23:37:00Z-PHASE254-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute end-to-end; no deferral, no stubs, no partial completion).**

**Status:** Phase254 deliverables **implemented** (4 files) and `py_compile` **OK** (23:37Z). **NOT SEALED:** validated artifact/evidence generation, smokes, and pytest blocked by environment missing required deps (`pydantic`/`numpy`/`pandas`/`scipy`) causing deep-chain `ModuleNotFoundError` on import; Phase254 artifact absent.

**Predecessor sealed (do NOT re-implement/re-seal):** `INIT-2026-11-11T22:45:41Z-PHASE253-POST-ATTRIBUTION-SEAL-DEPTH` — COMPLETE/SEALED (2026-11-11T22:45:41Z). Artifact: `research_state/PHASE253_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T224306Z.json` (`validation.valid=true`, `issues=[]`, seed `253253`, cycles `40`, paper-only, `live_trading_enabled=false`, `next9_unblocked=false`, composes `PHASE252→PHASE32`).

Phase252 is **evidence-sealed** (do NOT re-implement/re-seal Phase79/80/110–253): `research_state/PHASE252_..._20261111T222557Z.json` (`valid=true`).

**Objective (Phase254):** complete verification, generate validated evidence, and seal Phase254 composing **`PHASE253→PHASE32`** (12 coverage rows: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), seed `254254`, IDs `p254-*`. No stubs, no deferral, no partial completion. Then advance this handoff to **`INIT-<UTC>-PHASE255-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE254→PHASE32`** (seed `255255`, IDs `p255-*`).

### Phase254 implementation (done, 23:37Z)
| Item | Value |
|---|---|
| Module | `src/hedging/phase254_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator | `scripts/generate_phase254_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Tests | `tests/test_phase254_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase254_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Composes | `PHASE253→PHASE32` |
| Seed / IDs | `254254` / `p254-*` |
| Upstream flags/refs | `upstream_phase253/252/32`, refs sealed Phase253 artifact `...PHASE253_...T224306Z.json` |
| `py_compile` (4) | **OK** — `python3 -m py_compile ...` (23:37Z) |

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase253 pattern exactly.
- **Compose `PHASE253→PHASE32`**. Seed `254254`, IDs `p254-*`, artifacts `PHASE254_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–253`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`.

### Required to seal (remaining, heavy — must complete)
1. **Unblock env deps (bottleneck):** ensure `pydantic`, `numpy`, `pandas`, `scipy` (and test deps as required) are installed/available in the active Python env (see `docs/PAPER_RUNBOOK.md` venv/dep check). Do not weaken guards.
2. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` with `sys.setrecursionlimit(200000)` → expect `paper_only=True gates_ok=True composes ['PHASE253','PHASE32']`.
3. **Module pytest** (targeted) — record pass/fail/caveats.
4. **Generate controlled evidence:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase254_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py --cycles 40 --seed 254254 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE253→PHASE32`, guards intact. **Record exact artifact path.**
5. **CLI no-write smoke:** run generator without `--write` (use `runpy`+raised recursion if needed) → expect `valid=true issues=[]`.
6. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
7. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
8. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats, mark Phase254 sealed, and advance next task to **`INIT-<UTC>-PHASE255-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE254→PHASE32`** (seed `255255`, IDs `p255-*`).

### Acceptance criteria
- Phase254 module/generator/tests exist and syntactically valid. ✅ (23:37Z)
- Validated `research_state/PHASE254_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE253→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`. ❌ **BLOCKED (deps)**
- Verification evidence recorded (or explicit bounded caveats per governed acceptance). ❌ **BLOCKED (deps)**
- P0 intact; handoff advanced to Phase255 only after seal.

## VERIFIED STATE (ground truth, 2026-11-11T23:37:00Z)

- **P0 safety:** **CLEAR** — no `.env` (absent, 23:37Z); `.env.example:15` `LIVE_TRADING_ENABLED=false`. No venue/config/credential mutation.
- **Phase233–253 COMPLETE (sealed):** post-attribution seal phases evidenced in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-seal. Phase253: `...PHASE253_...T224306Z.json`.
- **Phase254 IN PROGRESS (active, not sealed):** 4 deliverables present in `src/hedging/phase254*`, `scripts/generate_phase254*`, `tests/*phase254*` (verified 23:37Z); `py_compile` 4/4 OK. `research_state/PHASE254_*` artifact **absent**. Smokes/generator/validate/tests **blocked** by missing runtime deps: `pydantic` MISSING, `numpy` MISSING, `pandas` MISSING, `scipy` MISSING (Python 3.12 env check 23:37Z); `yaml` OK. Commands attempted: module smoke and generator `--write` → `ModuleNotFoundError: No module named 'pydantic'` during deep-chain import (`src/data/schemas.py`).
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` redirect stubs to this file.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (23:37Z)** | Re-verify before/after batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Missing runtime deps (`pydantic`,`numpy`,`pandas`,`scipy`) | **BLOCKING — ACTIVE** | Provision/activate env with required deps (e.g. `.venv` per `docs/PAPER_RUNBOOK.md`, `pip install -r requirements.txt` or equivalent) so Phase254 import chain loads; then complete verification/evidence/seal. Do not bypass guards. |
| Phase254 artifact/verification | **BLOCKED by deps** | After deps fixed: module smoke, module+generator pytest (governed), `--write`+`--validate-only`, CLI no-write; record exact results and seal. |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (expected)** | Use `PHASE_QUICK_VERIFY=1`, `sys.setrecursionlimit` (200k), governed acceptance; record caveats. |
| Competing/stale handoff files | **CLEARED** | Stubs redirect here. Do not create duplicates. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion if needed).
- Deep composed chain (→phase32) can raise `RecursionError`/hang on Python 3.12 during imports/pytest collection without `PHASE_QUICK_VERIFY=1`. Use governed acceptance and record exact outcomes.
- Carry `sys.setrecursionlimit(50000)` (or higher) in generators/smokes as needed.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase254 seal, replace active task with **`INIT-<UTC>-PHASE255-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE254→PHASE32`, seed `255255`, IDs `p255-*`).
