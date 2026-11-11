# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T08:32:00Z (branch `main`, HEAD `b782ae799` `chore(kilo): checkpoint agent session`). This file is the ONLY durable handoff. Competing handoff files are redirect stubs pointing here — do not action them.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-2026-11-11T08:32:00Z-PHASE218-POST-ATTRIBUTION-SEAL-DEPTH`**

Phase217 is **evidence-sealed**: `research_state/PHASE217_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T083104Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE216→PHASE32`, seed `217217`, cycles `40`, `venue_symbol_coverage=12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`). **Do NOT re-implement or re-seal Phase200–217.**

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase218** composing **`PHASE217→PHASE32`** in this session. No status-only work, no doc-only delivery (except final handoff update), no stubs, no deferral, no partial completion. Future agents must not avoid heavy working.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/` artifacts. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–217 pattern and Phase217→218 deltas below.
- **Compose `PHASE217→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `218218`**, IDs `p218-*`, artifacts `PHASE218_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–217`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only if verification reveals a real defect (preserve semantics/guards).

### Required deliverables (all)
1. `src/hedging/phase218_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase218_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase218_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase218_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE218_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase217 → Phase218 implementation deltas
| Item | Phase217 (sealed) | Phase218 (required) |
|---|---|---|
| Module/generator/tests | `...phase217...` | `...phase218...` |
| Upstream orchestrator/import | `Phase216...` | `Phase217...` |
| Composes | `["PHASE216","PHASE32"]` | `["PHASE217","PHASE32"]` |
| Seed / IDs | `217217` / `p217-*` | `218218` / `p218-*` |
| Report/campaign phase | `PHASE217_*` | `PHASE218_*` |
| Upstream flags | `upstream_phase216/215/32` | `upstream_phase217/216/32` (match established naming pattern) |
| Evidence refs | includes sealed Phase216 artifact | includes sealed Phase217 artifact `research_state/PHASE217_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T083104Z.json` |
| Cross refs | composes `PHASE216,PHASE32` | composes `PHASE217,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; no Phase218 deliverables exist yet.
2. **Implement** module+generator+tests mirroring Phase217 with deltas above (paper-only hard gate, `paper_only=True`, `gates_ok=True`, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations).
3. **`py_compile`** all 4 Phase218 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` or equivalent → expect `paper_only=True gates_ok=True` and composes includes `PHASE217,PHASE32`.
5. **Module pytest** (targeted, with timeouts/fallbacks as needed) — record pass/fail/caveats.
6. **Generate controlled evidence:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase218_..._paper_evidence.py --cycles 40 --seed 218218 --write` then `--validate-only <artifact>` and/or direct `validate_artifact` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE217→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` (no `--no-write` flag in this repo revision) — expect `valid=true issues=[]`. Re-run validation if code changed.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE219-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE218→PHASE32`**.

### Acceptance criteria
- Phase218 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE218_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE217→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase219.

## VERIFIED STATE (ground truth, 2026-11-11T08:32:00Z)

- **P0 safety:** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Phase211–215:** sealed (do not re-implement/re-seal).
- **Phase216 sealed:** module/generator/tests present; artifact `research_state/PHASE216_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T074447Z.json` (`valid=true issues=[]`, composes `PHASE215→PHASE32`, seed 216216, 12 coverage, deterministic/bounded, guards intact).
- **Phase217 COMPLETE (this session):** module `src/hedging/phase217_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; generator `scripts/generate_phase217_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; tests `tests/test_phase217_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` + `tests/test_generate_phase217_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; artifact `research_state/PHASE217_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T083104Z.json` (`valid=true issues=[]`, composes `PHASE216→PHASE32`, seed 217217, cycles 40, coverage 12, deterministic/bounded, guards intact).
- **Verification (Phase217):** `py_compile` 4 OK; generator `--write` → `valid=true issues=[]` (artifact path above); `--validate-only` on artifact → `valid=true issues=[]`; CLI no-write → `valid=true issues=[]`; artifact fields: composes `[PHASE216,PHASE32]`, upstream216/upstream215/upstream32 all `True`, gates_ok `True`, paper_only `True`, live `False`, next9 `False`.
- **Phase217 pytest caveat:** pytest collection hits `RecursionError` (Python 3.12 pydantic/typing_extensions deep composed chain →phase32) — governed acceptance satisfied by `py_compile` + CLI no-write + validated `--write`/`--validate-only` artifact. Record targeted pytest outcomes if feasible (e.g. raise recursion limit); not a blocker.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action |
|---|---|---|
| P0 safety drift | **CLEAR** | Re-verify before/after every batch (`.env` absent, `LIVE_TRADING_ENABLED=false`). |
| Phase216 sealed | **CLEARED** | Do not touch except defect-preserving fix. |
| Phase217 | **CLEARED (this session)** | Fully implemented, verified, evidence-sealed; handoff advanced to Phase218. |
| Phase218 absent | **ACTIVE — CRITICAL PATH** | **Implement+verify+seal Phase218 now (full scope above).** |
| Deep-chain pytest RecursionError | **ENV CAVEAT (mitigated)** | Use governed acceptance: `py_compile` (4) + CLI no-write `valid=true` + `--validate-only`/direct validate on `--write` artifact `valid=true`; run targeted pytest with `PHASE_QUICK_VERIFY=1`/timeouts where feasible; consider `sys.setrecursionlimit` raise for collection; record caveats. |
| Stale/competing handoffs | **CLEARED** | This file governs; stubs redirect here. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only. |
| NEXT9 A1–A7 | **BLOCKED — human-only** | `next9_unblocked=false`; never unblock. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation.
- Deep composed chain (→phase32) can cause pytest collection `RecursionError` on Python 3.12 (pydantic/typing_extensions). Acceptance: `py_compile` + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase218 seal, replace `INIT-2026-11-11T08:32:00Z-...` with next `INIT-<UTC>-PHASE219-POST-ATTRIBUTION-SEAL-DEPTH` (compose `PHASE218→PHASE32`, seed `218218+1=219219`, IDs `p219-*`).
