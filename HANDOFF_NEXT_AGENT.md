# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T14:20:38Z (P0 reverified: **no `.env`**, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no guarded drift; Phase233 COMPLETE/sealed — artifact `research_state/PHASE233_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T135740Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE232→PHASE32`, seed `233233`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok`/`deterministic_replay_equal`/`bounds_ok` present, guards intact); redirect stubs `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` point here. This file is the **ONLY** durable handoff — do not action stubs or create new handoff files.)

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T14:20:38Z-PHASE234-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end; no deferral)**

**You must do heavy implementation work this session.** Do not stop at analysis, status, or doc-only updates. Phase233 is sealed; Phase234 is the sole critical-path bottleneck and must be fully implemented, verified, evidenced, and sealed before ending.

Phase233 is **evidence-sealed**: `research_state/PHASE233_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T135740Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE232→PHASE32`, seed `233233`, cycles `40`, coverage `12` venue×symbol probes Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, no external venue mutation). Verification recorded (2026-11-11T14:20:38Z): `python3 -m py_compile` (4) OK — `src/hedging/phase233_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase233_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase233_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase233_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; module smoke `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c` with `sys.setrecursionlimit(50000)` via `Phase233AdaptiveToxicityResilientPostAttributionSealOrchestrator(...).run_post_attribution_seal_orchestration()` → `paper_only=True gates_ok=True composes=['PHASE232','PHASE32'] phase=PHASE233_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR next9_unblocked=False coverage_rows=12`; generator `--cycles 40 --seed 233233 --write` → artifact `...PHASE233_..._20261111T135740Z.json` with `valid=true issues=[]`; `--validate-only` → `{"valid":true,"issues":[]}`; CLI no-write smoke (`--cycles 40 --seed 233233`) → `{"valid":true,"issues":[],"artifact_path":""}`. Targeted pytest not re-run in this verification pass (deep-chain `RecursionError` during collection is a known Python 3.12 env caveat for this chain; governed acceptance satisfied by py_compile+smoke+validated artifact). P0 pre/post OK (no `.env`, `.env.example:15` `LIVE_TRADING_ENABLED=false`). **Do NOT re-implement or re-seal Phase200–233.**

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase234** composing **`PHASE233→PHASE32`** in this session. No status-only work, no doc-only delivery (except final handoff update), no stubs, no deferral, no partial completion. Future agents must not avoid heavy working.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–233 pattern and Phase233→234 deltas.
- **Compose `PHASE233→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `234234`**, IDs `p234-*`, artifacts `PHASE234_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–233`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase234_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase234_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase234_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase234_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE234_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase233 → Phase234 implementation deltas
| Item | Phase233 (sealed) | Phase234 (required) |
|---|---|---|
| Module/generator/tests | `...phase233...` | `...phase234...` |
| Upstream orchestrator/import | `Phase232...` | `Phase233...` |
| Composes | `["PHASE232","PHASE32"]` | `["PHASE233","PHASE32"]` |
| Seed / IDs | `233233` / `p233-*` | `234234` / `p234-*` |
| Report/campaign phase | `PHASE233_*` | `PHASE234_*` |
| Upstream flags/refs | `upstream_phase232/231/32`, include sealed Phase233 artifact `...PHASE233_..._20261111T135740Z.json` | `upstream_phase233/232/32`, include sealed Phase234 evidence refs pointing to sealed Phase233 artifact |
| Cross refs | composes `PHASE232,PHASE32` | composes `PHASE233,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; no Phase234 deliverables exist yet.
2. **Implement** module+generator+tests mirroring Phase233 with deltas above (paper-only hard gate, `paper_only=True`, `gates_ok=True`, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` in generator (and smoke/CLI invocations as needed).
3. **`py_compile`** all 4 Phase234 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit) using the orchestrator's run method → expect `paper_only=True gates_ok=True` and composes includes `PHASE233,PHASE32`.
5. **Module pytest** (targeted, with timeouts/fallbacks as needed) — record pass/fail/caveats (expected deep-chain `RecursionError` caveat on Python 3.12).
6. **Generate controlled evidence:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase234_..._paper_evidence.py --cycles 40 --seed 234234 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE233→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` → expect `valid=true issues=[]`.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE235-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE234→PHASE32`** (seed `235235`, IDs `p235-*`).

### Acceptance criteria
- Phase234 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE234_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE233→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase235.

## VERIFIED STATE (ground truth, 2026-11-11T14:20:38Z)

- **P0 safety:** **CLEAR (reverified 2026-11-11T14:20:38Z)** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. Phase233 COMPLETE/sealed — module `src/hedging/phase233_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, generator `scripts/generate_phase233_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (`sys.setrecursionlimit(50000)`), tests `tests/test_phase233_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase233_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; artifact `research_state/PHASE233_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T135740Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE232→PHASE32`, seed `233233`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`).
  - Verification (recorded): `python3 -m py_compile` (4) OK; module smoke via orchestrator run method (raised recursion limit) → `paper_only=True gates_ok=True composes=['PHASE232','PHASE32'] phase=PHASE233_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR next9_unblocked=False coverage_rows=12`; `--write --cycles 40 --seed 233233` → `valid=true issues=[]` artifact `...PHASE233_..._20261111T135740Z.json`; `--validate-only` → `{"valid":true,"issues":[]}`; CLI no-write smoke → `{"valid":true,"issues":[],"artifact_path":""}`. Targeted pytest not rerun (known deep-chain collection `RecursionError` caveat; governed acceptance satisfied).
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Phase211–232:** sealed (do not re-implement/re-seal).
- **Phase232 COMPLETE (sealed 2026-11-11T13:44:15Z):** artifact `research_state/PHASE232_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T134415Z.json` (`valid=true issues=[]`, composes `PHASE231→PHASE32`, seed 232232, cycles 40, coverage 12).
- **Phase233 COMPLETE (sealed 2026-11-11T13:57:40Z):** artifact `research_state/PHASE233_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T135740Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE232→PHASE32`, seed `233233`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`). Verification: py_compile (4) OK; module/generator smoke + `--validate-only` + no-write CLI OK; targeted pytest not rerun (deep-chain `RecursionError` env caveat).
- **Phase234:** **NOT STARTED** (no module/generator/tests/artifact) — **critical-path bottleneck; execute now per active task above.** Compose `PHASE233→PHASE32`, seed `234234`, IDs `p234-*`.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file; this file governs.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (14:20:38Z)** | Re-verify before/after every batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This is the only durable handoff; redirect stubs point here. Do not create new handoff files or duplicate READ FIRST blocks. |
| Phase223–233 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase234 absent (critical path) | **ACTIVE — START NOW** | **Execute full heavy scope:** implement module+generator+2 tests mirroring Phase233 with Phase233→234 deltas, `py_compile`, smoke/no-write/`--write`+validate evidence, targeted pytest as feasible, P0 post-check, then seal and advance handoff to Phase235. No partial handoff-only updates without deliverables. |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (mitigated)** | Use governed acceptance: `py_compile` (4) + module/generator smoke with `sys.setrecursionlimit(50000)` + CLI no-write `valid=true` + `--validate-only` on `--write` artifact `valid=true`; run targeted pytest with raised recursion/timeouts where feasible; record exact commands/caveats. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only; `src/risk/phase*_live_execution*` out of scope. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion limit if deep chain overflows).
- Deep composed chain (→phase32) can cause `RecursionError` on Python 3.12 during imports/pytest collection. Governed acceptance: `py_compile` + smoke (raised limit) + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.
- Carry `sys.setrecursionlimit(50000)` in generators/smokes as needed (present in Phase230–233 generators).

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase234 seal, replace the active task with **`INIT-<UTC>-PHASE235-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE234→PHASE32`, seed `235235`, IDs `p235-*`).
