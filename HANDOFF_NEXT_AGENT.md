# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T15:51:43Z (P0 reverified pre/post: **no `.env`**, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no guarded drift; Phase233–239 sealed; **Phase239 COMPLETE/sealed** — artifact `research_state/PHASE239_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T155143Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE238→PHASE32`, seed `239239`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, gates_ok/`deterministic_replay_equal`/`bounds_ok` true, refs sealed Phase238 artifact `...PHASE238_..._20261111T153925Z.json`); redirect stubs `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` point here. This file is the **ONLY** durable handoff — do not action stubs or create new handoff files.)

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T15:51:43Z-PHASE240-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end; no deferral)**

**You must do heavy implementation work this session.** Do not stop at analysis, status, or doc-only updates. Phase239 is sealed; Phase240 is the sole critical-path bottleneck and must be fully implemented, verified, evidenced, and sealed before ending.

Phase239 is **evidence-sealed**: `research_state/PHASE239_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T155143Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE238→PHASE32`, seed `239239`, cycles `40`, coverage `12` venue×symbol probes Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, gates_ok/`deterministic_replay_equal`/`bounds_ok` true, refs sealed Phase238 `...PHASE238_..._20261111T153925Z.json`).

Phase238 is **evidence-sealed** (prior): `research_state/PHASE238_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T153925Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE237→PHASE32`, seed `238238`, cycles `40`, coverage `12`). **Do NOT re-implement or re-seal Phase200–239.**

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase240** composing **`PHASE239→PHASE32`** in this session. No status-only work, no doc-only delivery (except final handoff update), no stubs, no deferral, no partial completion. Future agents must not avoid heavy working.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–239 pattern and Phase239→240 deltas.
- **Compose `PHASE239→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `240240`**, IDs `p240-*`, artifacts `PHASE240_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–239`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase240_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase240_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase240_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase240_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE240_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase239 → Phase240 implementation deltas
| Item | Phase239 (sealed) | Phase240 (required) |
|---|---|---|
| Module/generator/tests | `...phase239...` | `...phase240...` |
| Upstream orchestrator/import | `Phase238...` | `Phase239...` |
| Composes | `["PHASE238","PHASE32"]` | `["PHASE239","PHASE32"]` |
| Seed / IDs | `239239` / `p239-*` | `240240` / `p240-*` |
| Report/campaign phase | `PHASE239_*` | `PHASE240_*` |
| Upstream flags/refs | `upstream_phase238/237/32`, refs sealed Phase238 `...PHASE238_..._20261111T153925Z.json` | `upstream_phase239/238/32`, refs sealed Phase239 `...PHASE239_..._20261111T155143Z.json` |
| Cross refs | composes `PHASE238,PHASE32` | composes `PHASE239,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; no Phase240 deliverables exist yet.
2. **Implement** module+generator+tests mirroring Phase239 with deltas above (paper-only hard gate, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` in generator/smokes as needed.
3. **`py_compile`** all 4 Phase240 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit) → expect `paper_only=True gates_ok=True` and composes includes `PHASE239,PHASE32`.
5. **Module pytest** (targeted) — record pass/fail/caveats (deep-chain `RecursionError` caveat possible).
6. **Generate controlled evidence:** `--cycles 40 --seed 240240 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE239→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` → expect `valid=true issues=[]`.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE241-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE240→PHASE32`** (seed `241241`, IDs `p241-*`).

### Acceptance criteria
- Phase240 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE240_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE239→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase241.

## VERIFIED STATE (ground truth, 2026-11-11T15:51:43Z)

- **P0 safety:** **CLEAR (pre/post 2026-11-11T15:51:43Z)** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- **Phase232 COMPLETE (sealed 2026-11-11T13:44:15Z):** artifact `research_state/PHASE232_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T134415Z.json` (`valid=true issues=[]`, composes `PHASE231→PHASE32`, seed 232232, cycles 40, coverage 12).
- **Phase233 COMPLETE (sealed 2026-11-11T13:57:40Z):** artifact `research_state/PHASE233_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T135740Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE232→PHASE32`, seed `233233`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`).
- **Phase234 COMPLETE (sealed 2026-11-11T14:29:15Z):** artifact `research_state/PHASE234_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T142915Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE233→PHASE32`, seed `234234`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`).
- **Phase235 COMPLETE (sealed 2026-11-11T14:42:13Z):** artifact `research_state/PHASE235_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T144213Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE234→PHASE32`, seed `235235`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`).
- **Phase236 COMPLETE (sealed 2026-11-11T15:24:28Z):** artifact `research_state/PHASE236_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T152428Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE235→PHASE32`, seed `236236`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`).
- **Phase237 COMPLETE (sealed 2026-11-11T15:30:35Z):** artifact `research_state/PHASE237_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T153035Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE236→PHASE32`, seed `237237`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`).
- **Phase238 COMPLETE (sealed 2026-11-11T15:39:51Z):** artifact `research_state/PHASE238_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T153925Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE237→PHASE32`, seed `238238`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, gates_ok/`deterministic_replay_equal`/`bounds_ok` true, refs `...PHASE237_..._20261111T153035Z.json`). Verification recorded (2026-11-11T15:39:51Z): P0 pre `env_exists=no`, `.env.example:15` `LIVE_TRADING_ENABLED=false`; `python3 -m py_compile` (4) OK — `src/hedging/phase238_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase238_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase238_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase238_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; module smoke `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c` with `sys.setrecursionlimit(50000)` → `paper_only=True gates_ok=True composes=['PHASE237','PHASE32'] phase=PHASE238_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR n_seal_attestations=1`; `--write --cycles 40 --seed 238238` → `valid=true issues=[]` artifact `...PHASE238_..._20261111T153925Z.json`; `--validate-only` → `{"valid":true,"issues":[]}`; CLI no-write smoke → `{"valid":true,"issues":[],"artifact_path":""}`. Targeted pytest collection hit known deep-chain `RecursionError` on Python 3.12 env (`maximum recursion depth exceeded` during `_pytest.assertion.rewrite` over composed hedging chain) — governed acceptance satisfied by py_compile+smoke+validated artifact; record if retried with raised limits. P0 post OK.
- **Phase239 COMPLETE (sealed 2026-11-11T15:51:43Z):** artifact `research_state/PHASE239_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T155143Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE238→PHASE32`, seed `239239`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, gates_ok/`deterministic_replay_equal`/`bounds_ok` true, refs `...PHASE238_..._20261111T153925Z.json`). Verification recorded (2026-11-11T15:51:43Z): P0 pre `env_exists=no`, `.env.example:15` `LIVE_TRADING_ENABLED=false`; `python3 -m py_compile` (4) OK — `src/hedging/phase239_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase239_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase239_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase239_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; module smoke `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c` with `sys.setrecursionlimit(50000)` → `paper_only=True gates_ok=True composes=['PHASE238','PHASE32'] phase=PHASE239_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR n_seal_attestations=2`; `--write --cycles 40 --seed 239239` (PHASE_QUICK_VERIFY=1) → `valid=true issues=[]` artifact `...PHASE239_..._20261111T155143Z.json`; `--validate-only` → `{"valid":true,"issues":[]}`; CLI no-write smoke → `{"valid":true,"issues":[],"artifact_path":""}`; pytest 5/5 passed with `sys.setrecursionlimit(50000)`. P0 post OK.
- **Phase240:** **NOT STARTED** (no module/generator/tests/artifact) — **critical-path bottleneck; execute now per active task above.** Compose `PHASE239→PHASE32`, seed `240240`, IDs `p240-*`.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file; this file governs.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (15:51:43Z pre/post)** | Re-verify before/after every batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This is the only durable handoff; redirect stubs point here. Do not create new handoff files or duplicate READ FIRST blocks. |
| Phase223–238 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase239 sealed | **CLEARED** | Implemented+verified+evidenced+sealed Phase239 end-to-end (artifact `...PHASE239_..._20261111T155143Z.json`, `valid=true issues=[]`). Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase240 absent (critical path) | **ACTIVE — START NOW** | **Execute full heavy scope:** implement module+generator+2 tests mirroring Phase239 with Phase239→240 deltas, `py_compile`, smoke/no-write/`--write`+validate evidence, targeted pytest as feasible, P0 post-check, then seal and advance handoff to Phase241. No partial handoff-only updates without deliverables. |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (mitigated)** | Use governed acceptance: `py_compile` (4) + module/generator smoke with `sys.setrecursionlimit(50000)` + CLI no-write `valid=true` + `--validate-only` on `--write` artifact `valid=true`; run targeted pytest with raised recursion/timeouts where feasible; record exact commands/caveats. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only; `src/risk/phase*_live_execution*` out of scope. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion limit if deep chain overflows).
- Deep composed chain (→phase32) can cause `RecursionError` on Python 3.12 during imports/pytest collection. Governed acceptance: `py_compile` + smoke (raised limit) + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.
- Carry `sys.setrecursionlimit(50000)` in generators/smokes as needed (present in Phase230–239 generators).

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase239 seal, replace the active task with **`INIT-<UTC>-PHASE240-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE239→PHASE32`, seed `240240`, IDs `p240-*`).
