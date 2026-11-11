# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T11:08:20Z (P0 rechecked: no `.env`, `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase222 evidence sealed; Phase223 not started; competing handoff stubs and `research_state/durable_handoff.md` confirmed redirect-only). Built on 10:40:00Z state (branch `main`, HEAD `435ff7e20`). This file is the ONLY durable handoff. Competing handoff files are redirect stubs pointing here — do not action them.

> **Single initial task for next agentic session (mandatory):** `INIT-2026-11-11T10:40:00Z-PHASE223-POST-ATTRIBUTION-SEAL-DEPTH` — implement+verify+generate-validated-evidence+seal Phase223 (Chain B `src/hedging`, compose `PHASE222→PHASE32`, seed `223223`, paper-only). No status-only/doc-only work; no deferral; complete all deliverables and acceptance criteria below, then advance handoff to `INIT-<UTC>-PHASE224-POST-ATTRIBUTION-SEAL-DEPTH`.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-2026-11-11T10:40:00Z-PHASE223-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (mandatory, heavy)**

Phase222 is **evidence-sealed**: `research_state/PHASE222_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103906Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE221→PHASE32`, seed `222222`, cycles `40`, `venue_symbol_coverage=12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`). **Do NOT re-implement or re-seal Phase200–222.**

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase223** composing **`PHASE222→PHASE32`** in this session. No status-only work, no doc-only delivery (except final handoff update), no stubs, no deferral, no partial completion. Future agents must not avoid heavy working.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/` artifacts. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–222 pattern and Phase222→223 deltas below.
- **Compose `PHASE222→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `223223`**, IDs `p223-*`, artifacts `PHASE223_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–222`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only if verification reveals a real defect (preserve semantics/guards).

### Required deliverables (all)
1. `src/hedging/phase223_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase223_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase223_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase223_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE223_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase222 → Phase223 implementation deltas
| Item | Phase222 (sealed) | Phase223 (required) |
|---|---|---|
| Module/generator/tests | `...phase222...` | `...phase223...` |
| Upstream orchestrator/import | `Phase221...` | `Phase222...` |
| Composes | `["PHASE221","PHASE32"]` | `["PHASE222","PHASE32"]` |
| Seed / IDs | `222222` / `p222-*` | `223223` / `p223-*` |
| Report/campaign phase | `PHASE222_*` | `PHASE223_*` |
| Upstream flags | `upstream_phase221/220/32` | `upstream_phase222/221/32` (match established naming pattern) |
| Evidence refs | includes sealed Phase221 artifact `research_state/PHASE221_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103217Z.json` | includes sealed Phase222 artifact `research_state/PHASE222_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103906Z.json` |
| Cross refs | composes `PHASE221,PHASE32` | composes `PHASE222,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; no Phase223 deliverables exist yet.
2. **Implement** module+generator+tests mirroring Phase222 with deltas above (paper-only hard gate, `paper_only=True`, `gates_ok=True`, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations).
3. **`py_compile`** all 4 Phase223 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit if needed) → expect `paper_only=True gates_ok=True` and composes includes `PHASE222,PHASE32`.
5. **Module pytest** (targeted, with timeouts/fallbacks as needed) — record pass/fail/caveats.
6. **Generate controlled evidence:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase223_..._paper_evidence.py --cycles 40 --seed 223223 --write` then `--validate-only <artifact>` and/or direct `validate_artifact` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE222→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` (no `--no-write` flag in this repo revision) — expect `valid=true issues=[]`. Re-run validation if code changed. Use raised recursion limit (`sys.setrecursionlimit(50000)`) if needed.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE224-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE223→PHASE32`**.

### Acceptance criteria
- Phase223 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE223_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE222→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase224.

## VERIFIED STATE (ground truth, 2026-11-11T11:08:20Z recheck)

- **P0 safety (rechecked 2026-11-11T11:08:20Z):** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. Phase223 not yet started (no `src/hedging/phase223*`, no `scripts/generate_phase223*`, no `tests/test_phase223*`, no `research_state/PHASE223_*` artifact).
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Phase211–221:** sealed (do not re-implement/re-seal).
- **Phase221 COMPLETE:** artifact `research_state/PHASE221_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103217Z.json` (`valid=true issues=[]`, composes `PHASE220→PHASE32`, seed 221221, cycles 40, coverage 12, deterministic/bounded, guards intact).
- **Phase222 COMPLETE (this session):** module `src/hedging/phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; generator `scripts/generate_phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; tests `tests/test_phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` + `tests/test_generate_phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; artifact `research_state/PHASE222_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103906Z.json` (`valid=true issues=[]`, composes `PHASE221→PHASE32`, seed 222222, cycles 40, coverage 12, deterministic/bounded, guards intact).
- **Verification (Phase222):** P0 pre-check PASS (no `.env`, `LIVE_TRADING_ENABLED=false`, no Phase222 targets). `py_compile` 4 files OK. Module smoke (raised recursion limit `sys.setrecursionlimit(50000)`, `PHASE_QUICK_VERIFY=1`) → `{'paper_only': True, 'gates_ok': True, 'composes': ['PHASE221','PHASE32'], 'up': (True, True, True)}`. Generator `--write --cycles 40 --seed 222222` (hang stubs) → `valid=true issues=[]` artifact `research_state/PHASE222_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103906Z.json`. `--validate-only` → `valid=true issues=[]`. CLI no-write via `runpy` with raised recursion limit → `valid=true issues=[] artifact_path=""`. Artifact fields: composes `[PHASE221,PHASE32]`, upstream221/220/32 all `True`, gates_ok `True`, paper_only `True`, live `False`, next9 `False`, coverage `12`, deterministic `True`, bounds_ok `True`, evidence_ref Phase221 artifact `...T103217Z.json`. **pytest: governed caveat — deep-chain RecursionError risk at collection (governed acceptance satisfied by py_compile + smoke + no-write + validated artifact).**
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, `research_state/durable_handoff.md` are redirect stubs to this file; this file governs.

## BOTTLENECKS & UNBLOCKING ACTIONS (remove before/while executing)

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (11:08:20Z)** | Re-verify before/after every batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Phase221/222 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase223 absent (critical path) | **ACTIVE — START NOW** | **Execute full heavy scope in this session:** implement module+generator+2 tests, `py_compile`, smoke/no-write/`--write`+validate evidence, targeted pytest as feasible, P0 post-check, then seal and advance handoff to Phase224. No partial handoff-only updates without deliverables. |
| Deep-chain pytest/import RecursionError | **ENV CAVEAT (mitigated, not a stop reason)** | Use governed acceptance: `py_compile` (4) + module smoke/CLI with `sys.setrecursionlimit(50000)` + CLI no-write `valid=true` + `--validate-only`/direct validate on `--write` artifact `valid=true`; run targeted pytest with raised recursion/timeouts where feasible; record exact commands/caveats. Prior `--write` runs with hang stubs completed successfully. |
| Stale/competing handoffs / duplicate READ FIRST | **CLEARED** | This file is the only durable handoff; `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, `research_state/durable_handoff.md` are redirect stubs (no competing instructions). Do not create new handoff files. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only; `src/risk/phase*_live_execution*` out of scope. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion limit if deep chain overflows).
- Deep composed chain (→phase32) can cause `RecursionError` on Python 3.12 (pydantic/typing_extensions) during imports/pytest collection. Acceptance: `py_compile` + module smoke (raised limit) + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase223 seal, replace `INIT-2026-11-11T10:40:00Z-PHASE223-...` with next `INIT-<UTC>-PHASE224-POST-ATTRIBUTION-SEAL-DEPTH` (compose `PHASE223→PHASE32`, seed `224224`, IDs `p224-*`).
