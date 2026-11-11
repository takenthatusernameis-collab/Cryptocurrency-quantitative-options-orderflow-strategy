# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B (`src/hedging`) adaptive post-attribution seal orchestrator campaign is the active paper-only engineering track.
**Handoff refreshed (verified):** 2026-11-11T23:47:50Z (UTC). **This file is the ONLY durable handoff.** `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs (re-synced 23:47:50Z) — do not action stubs or create new handoff files.
**P0 re-verified (23:47:50Z):** no `.env` (absent); `.env.example:15` `LIVE_TRADING_ENABLED=false`. No venue/config/credential mutation. Prior bottleneck (missing `pydantic`/`numpy`/`pandas`/`scipy`) is **cleared** in current env (imports OK; pip reports pydantic 2.14.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1).

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T23:47:50Z-PHASE255-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute end-to-end; no deferral, no stubs, no partial completion).**

**Objective (Phase255):** implement, verify, generate validated evidence, and seal **Phase255 adaptive-toxicity-resilient post-attribution seal orchestrator** (Chain B, `src/hedging`) composing **`PHASE254→PHASE32`** (12 coverage rows: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), seed `255255`, IDs `p255-*`. No stubs, no deferral, no partial completion.

**Predecessor sealed (do NOT re-implement/re-seal):** `INIT-2026-11-11T23:37:00Z-PHASE254-POST-ATTRIBUTION-SEAL-DEPTH` — **COMPLETE/SEALED** (verified 2026-11-11T23:47:50Z). Artifact: `research_state/PHASE254_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T234145Z.json` (`validation.valid=true`, `issues=[]`, seed `254254`, cycles `40`, `campaign.composes=["PHASE253","PHASE32"]`, `campaign.gates_ok=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `seal_surface.bounds_ok=true`, 12 venue×symbol coverage; generator `--validate-only` → `{"valid":true,"issues":[]}`). Deliverables present and `py_compile`-clean: `src/hedging/phase254_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase254_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase254_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase254_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.

Phases 79/80/110–254 are **evidence-sealed** in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-implement/re-seal.

### Phase255 implementation/verification scope (heavy — must complete)
1. **Additive deliverables (mirror Phase254 pattern exactly):**
   - Module: `src/hedging/phase255_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - Generator: `scripts/generate_phase255_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   - Tests: `tests/test_phase255_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase255_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
2. **Compose `PHASE254→PHASE32`**. Seed `255255`, IDs `p255-*`, artifacts `PHASE255_*`. Upstream refs must include sealed Phase254 artifact above; flags `upstream_phase254/253/32` as appropriate per pattern.
3. **Verification (record exact results/caveats):** `python3 -m py_compile` (4 files); module smoke with `PHASE_QUICK_VERIFY=1 PYTHONPATH=. sys.setrecursionlimit(200000)` → expect `paper_only=True gates_ok=True composes ['PHASE254','PHASE32']`; module + generator pytest (targeted/governed, `PHASE_QUICK_VERIFY=1`, bounded timeouts/recursion as needed); generate controlled evidence `--cycles 40 --seed 255255 --write` then `--validate-only <artifact>` → `valid=true issues=[]`, deterministic/bounded, 12-coverage, guards intact; CLI no-write smoke (no `--write`; use `runpy`+raised recursion if needed) → `valid=true issues=[]`.
4. **Seal & advance handoff:** record exact artifact path/commands/caveats, re-verify P0, mark Phase255 sealed in this file, and replace active task with **`INIT-<UTC>-PHASE256-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE255→PHASE32`** (seed `256256`, IDs `p256-*`).

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** No stubs, no deferral, no partial completion.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Do not refactor sealed phases `phase79/80/110–254`.

### Acceptance criteria
- Phase255 module/generator/tests exist and syntactically valid.
- Validated `research_state/PHASE255_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), deterministic/bounded, composes `PHASE254→PHASE32`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`.
- Verification evidence recorded (smokes, validate-only, CLI no-write, pytests) or explicit bounded governed caveats.
- P0 intact; handoff advanced to Phase256 only after seal.

## VERIFIED STATE (ground truth, 2026-11-11T23:47:50Z)

- **P0 safety:** **CLEAR** — `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`. No venue/config/credential mutation.
- **Phase233–254 COMPLETE (sealed):** post-attribution seal phases evidenced in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-seal. Phase254 artifact: `research_state/PHASE254_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T234145Z.json` (`valid=true`, seed `254254`, composes `PHASE253→PHASE32`, gates_ok, 12 coverage).
- **Phase255:** **NOT STARTED** — no `src/hedging/phase255*`, `scripts/generate_phase255*`, `tests/*phase255*`, or `research_state/PHASE255_*` artifacts present (active mandatory task above).
- **Runtime deps (prior blocker):** **CLEAR** — `pydantic/numpy/pandas/scipy/yaml/pytest` import OK in current Python env.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (23:47:50Z)** | Re-verify before/after batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Missing runtime deps (`pydantic`,`numpy`,`pandas`,`scipy`) | **CLEARED (23:47:50Z)** | None; deps importable. If a future env regresses, provision deps per `docs/PAPER_RUNBOOK.md`/`requirements.txt` without weakening guards. |
| Phase254 artifact/verification | **CLEARED/SEALED** | Phase254 evidence validated (`PHASE254_..._20261111T234145Z.json`). Do not re-seal. |
| Phase255 not implemented/sealed | **BLOCKING — ACTIVE** | Execute `INIT-2026-11-11T23:47:50Z-PHASE255-POST-ATTRIBUTION-SEAL-DEPTH` end-to-end (implement→verify→evidence→seal→advance). |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (expected)** | Use `PHASE_QUICK_VERIFY=1`, `sys.setrecursionlimit` (≥50k/200k as needed), targeted tests, governed acceptance; record exact caveats. |
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
- After Phase255 seal, replace active task with **`INIT-<UTC>-PHASE256-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE255→PHASE32`, seed `256256`, IDs `p256-*`).
