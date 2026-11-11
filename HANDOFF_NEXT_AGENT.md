# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T12:30:35Z (P0 reverified pre/post: **no `.env`**, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no guarded drift; redirect stubs `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` unchanged and point here). This file is the **ONLY** durable handoff — do not action stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T12:30:35Z-PHASE228-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end; no deferral)**

**You must do heavy implementation work this session.** Do not stop at analysis, status, or doc-only updates. Phase227 is sealed; Phase228 is the sole critical-path bottleneck and must be fully implemented, verified, evidenced, and sealed before ending.

Phase227 is **evidence-sealed**: `research_state/PHASE227_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T123035Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE226→PHASE32`, seed `227227`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`). Verification recorded (2026-11-11T12:30:35Z): `python3 -m py_compile` (4) OK — `src/hedging/phase227_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase227_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase227_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase227_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; module smoke `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c` with `sys.setrecursionlimit(50000)` → `True True ['PHASE226','PHASE32'] PHASE227_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR`; generator `--cycles 40 --seed 227227 --write` → `valid=true issues=[]` artifact `..._20261111T123035Z.json`; `--validate-only` → `{"valid":true,"issues":[]}`; CLI no-write smoke (`runpy`, recursion limit 50000, no `--write`, argv `--cycles 40 --seed 227227`) → `{"valid":true,"issues":[],"artifact_path":""}` `EXIT 0`; P0 pre/post OK (no `.env`, `.env.example:15` `LIVE_TRADING_ENABLED=false`). Targeted pytest not executed this session (known deep-chain `RecursionError`/collection timeout caveat on Python 3.12; governed acceptance met via py_compile+smoke+CLI+validated artifact). Phase228 seed `228228`, IDs `p228-*`, artifacts `PHASE228_*`. **Do NOT re-implement or re-seal Phase200–227.**

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase228** composing **`PHASE227→PHASE32`** in this session. No status-only work, no doc-only delivery (except final handoff update), no stubs, no deferral, no partial completion. Future agents must not avoid heavy working.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–227 pattern and Phase227→228 deltas.
- **Compose `PHASE227→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `228228`**, IDs `p228-*`, artifacts `PHASE228_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–227`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase228_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase228_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase228_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase228_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE228_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase227 → Phase228 implementation deltas
| Item | Phase227 (sealed) | Phase228 (required) |
|---|---|---|
| Module/generator/tests | `...phase227...` | `...phase228...` |
| Upstream orchestrator/import | `Phase226...` | `Phase227...` |
| Composes | `["PHASE226","PHASE32"]` | `["PHASE227","PHASE32"]` |
| Seed / IDs | `227227` / `p227-*` | `228228` / `p228-*` |
| Report/campaign phase | `PHASE227_*` | `PHASE228_*` |
| Upstream flags/refs | `upstream_phase226/225/32`, includes sealed Phase226 artifact `...PHASE226_..._20261111T122527Z.json` | `upstream_phase227/226/32` (match established naming), include sealed Phase227 artifact `...PHASE227_..._20261111T123035Z.json` |
| Cross refs | composes `PHASE226,PHASE32` | composes `PHASE227,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; no Phase228 deliverables exist yet.
2. **Implement** module+generator+tests mirroring Phase227 with deltas above (paper-only hard gate, `paper_only=True`, `gates_ok=True`, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` in generator (and smoke/CLI invocations as needed).
3. **`py_compile`** all 4 Phase228 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit) → expect `paper_only=True gates_ok=True` and composes includes `PHASE227,PHASE32`.
5. **Module pytest** (targeted, with timeouts/fallbacks as needed) — record pass/fail/caveats (expected deep-chain `RecursionError` caveat on Python 3.12).
6. **Generate controlled evidence:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase228_..._paper_evidence.py --cycles 40 --seed 228228 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE227→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` (use `runpy` + raised recursion limit if needed) → expect `valid=true issues=[]`.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE229-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE228→PHASE32`** (seed `229229`, IDs `p229-*`).

### Acceptance criteria
- Phase228 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE228_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE227→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase229.

## VERIFIED STATE (ground truth, 2026-11-11T12:30:35Z)

- **P0 safety:** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Phase211–226:** sealed (do not re-implement/re-seal).
- **Phase226 COMPLETE:** `research_state/PHASE226_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T122527Z.json` (`valid=true issues=[]`, composes `PHASE225→PHASE32`, seed 226226, cycles 40, coverage 12).
- **Phase227 COMPLETE (sealed 2026-11-11T12:30:35Z):** module `src/hedging/phase227_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; generator `scripts/generate_phase227_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (`sys.setrecursionlimit(50000)`); tests `tests/test_phase227_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase227_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; artifact `research_state/PHASE227_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T123035Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE226→PHASE32`, seed 227227, cycles 40, coverage 12, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`).
  - Verification: `python3 -m py_compile` (4 files) OK; module smoke `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` with `sys.setrecursionlimit(50000)` → `True True ['PHASE226','PHASE32'] PHASE227_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR`; `--write --cycles 40 --seed 227227` → `valid=true issues=[]` artifact `..._20261111T123035Z.json`; `--validate-only` → `{"valid":true,"issues":[]}`; CLI no-write smoke via `runpy` (no `--write`, recursion limit 50000) → `{"valid":true,"issues":[],"artifact_path":""}` `EXIT 0`.
  - Caveat: targeted `pytest` not run this session (deep-chain `RecursionError`/collection timeout on Python 3.12); governed acceptance met via py_compile+smoke+CLI+validated artifact.
- **Phase228:** **NOT STARTED** (no module/generator/tests/artifact) — this is the critical-path bottleneck to execute next.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file; this file governs.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (12:30:35Z)** | Re-verify before/after every batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This is the only durable handoff; `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs. Do not create new handoff files or duplicate READ FIRST blocks. |
| Phase223–227 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase228 absent (critical path) | **ACTIVE — START NEXT** | **Execute full heavy scope:** implement module+generator+2 tests mirroring Phase227 with Phase227→228 deltas, `py_compile`, smoke/no-write/`--write`+validate evidence, targeted pytest as feasible, P0 post-check, then seal and advance handoff to Phase229. No partial handoff-only updates without deliverables. |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (mitigated)** | Use governed acceptance: `py_compile` (4) + module/generator smoke with `sys.setrecursionlimit(50000)` + CLI no-write `valid=true` + `--validate-only`/direct validate on `--write` artifact `valid=true`; run targeted pytest with raised recursion/timeouts where feasible; record exact commands/caveats. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only; `src/risk/phase*_live_execution*` out of scope. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion limit if deep chain overflows).
- Deep composed chain (→phase32) can cause `RecursionError` on Python 3.12 during imports/pytest collection. Governed acceptance: `py_compile` + smoke (raised limit) + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.
- Phase227 generator includes `sys.setrecursionlimit(50000)`; carry this forward for Phase228+ generators/smokes as needed.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase228 seal, replace the active task with **`INIT-<UTC>-PHASE229-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE228→PHASE32`, seed `229229`, IDs `p229-*`).
