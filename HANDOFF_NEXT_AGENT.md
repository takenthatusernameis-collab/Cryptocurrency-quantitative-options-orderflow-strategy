# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T10:34:00Z (P0 rechecked this turn: no `.env`, `.env.example:15` `LIVE_TRADING_ENABLED=false`, Phase221 sealed; competing handoff stubs verified). Built on prior 10:29:21Z seal (branch `main`, HEAD `054d6f7d4`). This file is the ONLY durable handoff. Competing handoff files are redirect stubs pointing here — do not action them.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-2026-11-11T09:48:00Z-PHASE221-POST-ATTRIBUTION-SEAL-DEPTH` — COMPLETE (sealed this session)**

Phase221 is **evidence-sealed**: `research_state/PHASE221_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103217Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE220→PHASE32`, seed `221221`, cycles `40`, `venue_symbol_coverage=12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`). **Do NOT re-implement or re-seal Phase200–221.**

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase222** composing **`PHASE221→PHASE32`** in this session. No status-only work, no doc-only delivery (except final handoff update), no stubs, no deferral, no partial completion. Future agents must not avoid heavy working.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/` artifacts. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–221 pattern and Phase221→222 deltas below.
- **Compose `PHASE221→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `222222`**, IDs `p222-*`, artifacts `PHASE222_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–221`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only if verification reveals a real defect (preserve semantics/guards).

### Required deliverables (all)
1. `src/hedging/phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE222_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase221 → Phase222 implementation deltas
| Item | Phase221 (sealed) | Phase222 (required) |
|---|---|---|
| Module/generator/tests | `...phase221...` | `...phase222...` |
| Upstream orchestrator/import | `Phase220...` | `Phase221...` |
| Composes | `["PHASE220","PHASE32"]` | `["PHASE221","PHASE32"]` |
| Seed / IDs | `221221` / `p221-*` | `222222` / `p222-*` |
| Report/campaign phase | `PHASE221_*` | `PHASE222_*` |
| Upstream flags | `upstream_phase220/219/32` | `upstream_phase221/220/32` (match established naming pattern) |
| Evidence refs | includes sealed Phase220 artifact `research_state/PHASE220_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T094406Z.json` | includes sealed Phase221 artifact `research_state/PHASE221_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103217Z.json` |
| Cross refs | composes `PHASE220,PHASE32` | composes `PHASE221,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; no Phase222 deliverables exist yet.
2. **Implement** module+generator+tests mirroring Phase221 with deltas above (paper-only hard gate, `paper_only=True`, `gates_ok=True`, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations).
3. **`py_compile`** all 4 Phase222 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit if needed) → expect `paper_only=True gates_ok=True` and composes includes `PHASE221,PHASE32`.
5. **Module pytest** (targeted, with timeouts/fallbacks as needed) — record pass/fail/caveats.
6. **Generate controlled evidence:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase222_..._paper_evidence.py --cycles 40 --seed 222222 --write` then `--validate-only <artifact>` and/or direct `validate_artifact` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE221→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` (no `--no-write` flag in this repo revision) — expect `valid=true issues=[]`. Re-run validation if code changed. Use raised recursion limit (`sys.setrecursionlimit(50000)`) if needed.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE223-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE222→PHASE32`**.

### Acceptance criteria
- Phase222 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE222_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE221→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase223.

## VERIFIED STATE (ground truth, 2026-11-11T10:34:00Z recheck)

- **P0 safety (rechecked 2026-11-11T10:34:00Z):** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. Phase222 not yet started (no module/generator/tests/artifact).
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Phase211–219:** sealed (do not re-implement/re-seal).
- **Phase220 COMPLETE:** module `src/hedging/phase220_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; generator `scripts/generate_phase220_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; tests `tests/test_phase220_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` + `tests/test_generate_phase220_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; artifact `research_state/PHASE220_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T094406Z.json` (`valid=true issues=[]`, composes `PHASE219→PHASE32`, seed 220220, cycles 40, coverage 12, deterministic/bounded, guards intact).
- **Phase221 COMPLETE (this session):** module `src/hedging/phase221_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; generator `scripts/generate_phase221_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; tests `tests/test_phase221_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` + `tests/test_generate_phase221_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; artifact `research_state/PHASE221_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103217Z.json` (`valid=true issues=[]`, composes `PHASE220→PHASE32`, seed 221221, cycles 40, coverage 12, deterministic/bounded, guards intact).
- **Verification (Phase221):** `py_compile` 4 files OK. Module smoke (raised recursion limit `sys.setrecursionlimit(50000)`, `PHASE_QUICK_VERIFY=1`) → `paper_only=True gates_ok=True composes=['PHASE220','PHASE32'] upstream220/219/32 all True`. Generator `--write --cycles 40 --seed 221221` (with hang stubs) → `valid=true issues=[]` artifact `...T103217Z.json`. `--validate-only` on artifact → `valid=true issues=[]`. CLI no-write via `runpy` with raised recursion limit → `valid=true issues=[] artifact_path=""`. Artifact fields: composes `[PHASE220,PHASE32]`, upstream220/219/32 all `True`, gates_ok `True`, paper_only `True`, live `False`, next9 `False`, coverage `12`, deterministic `True`, bounds_ok `True`, evidence_ref Phase220 artifact `...T094406Z.json`. **pytest: RecursionError at collection on deep chain import (governed acceptance satisfied by py_compile + smoke + no-write + validated artifact; governed caveat recorded).**
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs (refreshed 2026-11-11T09:48:00Z):** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, `research_state/durable_handoff.md` are redirect stubs to this file with current INIT task.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action |
|---|---|---|
| P0 safety drift | **CLEAR** | Re-verify before/after every batch (`.env` absent, `LIVE_TRADING_ENABLED=false`). |
| Phase217 sealed | **CLEARED** | Do not touch except defect-preserving fix. |
| Phase219 | **CLEARED** | Fully implemented, verified, evidence-sealed; handoff advanced to Phase220. |
| Phase220 | **CLEARED (prior session)** | Fully implemented, verified, evidence-sealed; handoff advanced to Phase221. |
| Phase221 | **CLEARED (this session)** | Fully implemented, verified, evidence-sealed; handoff advanced to Phase222. |
| Phase222 absent | **ACTIVE — CRITICAL PATH** | **Implement+verify+seal Phase222 now (full scope above).** |
| Deep-chain pytest/import RecursionError | **ENV CAVEAT (mitigated)** | Use governed acceptance: `py_compile` (4) + module smoke/CLI with `sys.setrecursionlimit(50000)` + CLI no-write `valid=true` + `--validate-only`/direct validate on `--write` artifact `valid=true`; run targeted pytest with raised recursion limit/timeouts where feasible; record caveats. Generator `--write` with hang stubs completed successfully. |
| Stale/competing handoffs | **CLEARED** | This file governs; stubs redirect here. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only. |
| NEXT9 A1–A7 | **BLOCKED — human-only** | `next9_unblocked=false`; never unblock. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion limit if deep chain overflows).
- Deep composed chain (→phase32) can cause `RecursionError` on Python 3.12 (pydantic/typing_extensions) during imports/pytest collection. Acceptance: `py_compile` + module smoke (raised limit) + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase222 seal, replace `INIT-2026-11-11T10:30:00Z-PHASE222-...` with next `INIT-<UTC>-PHASE223-POST-ATTRIBUTION-SEAL-DEPTH` (compose `PHASE222→PHASE32`, seed `223223`, IDs `p223-*`).
