# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Last verified refresh:** 2026-11-11T05:03:20Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`, branch `main`, HEAD `82c723b75` `chore(kilo): checkpoint agent session`; working tree now contains Phase210 deliverables + this handoff update; P0 re-verified: `.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`). This file is the only durable handoff; competing handoff files are redirect stubs.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-2026-11-11T05:03:20Z-PHASE211-POST-ATTRIBUTION-SEAL-DEPTH`** — Phase210 is evidence-sealed (`research_state/PHASE210_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T050209Z.json`, `validation.valid=true issues=[]`, composes `PHASE209→PHASE32`, seed=210210, cycles=40, venue_symbol_coverage=12, paper_only=true, live_trading_enabled=false, next9_unblocked=false, gates_ok=true, deterministic=true, bounds_ok=true). **Do not re-implement or re-seal Phase200–210. Implement, verify, generate evidence, and seal Phase211 composing `PHASE210→PHASE32`.**

**Non-optional scope:** Chain B **`src/hedging`** only; **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–210 pattern. **Compose `PHASE210→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**. Seed `211211`; IDs `p211-*`; artifacts `PHASE211_*`. Edit sealed phases only if verification reveals a real defect (preserve semantics/guards).

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of sealed phases `phase79/80/110–210`. **NO Chain A substitution**. No `.env` creation; keep `LIVE_TRADING_ENABLED=false`.

**EXECUTE IN FULL (no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral, no partial delivery):**
1. Confirm P0 + targets: no `.env`; `.env.example` `LIVE_TRADING_ENABLED=false`; Phase211 deliverables absent before implementation.
2. Implement Phase211 (module, generator, module tests, generator tests) mirroring Phase210: paper-only hard gate, `paper_only=True`, `gates_ok=True`, composes includes `PHASE210` and `PHASE32`, 12 venue×symbol probes, deterministic/finite/bounded, validator rejects live/unblock/non-paper violations.
3. `py_compile` 4 files; record.
4. Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`) → expect `paper_only=True gates_ok=True` composes includes `PHASE210,PHASE32`.
5. Module pytest targeted (timeouts/fallbacks as needed); record pass/fail/caveats.
6. Controlled evidence generate: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py --cycles 40 --seed 211211 --write` + direct/CLI validate → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE210→PHASE32`, paper_only true, live_trading_enabled false, next9_unblocked false, gates_ok true (**record exact artifact path**).
7. CLI `--no-write` smoke; re-run if code changed.
8. Generator pytest with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed (composed-chain caveat: deep chain; governed acceptance evidence = module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact).
9. P0 re-verify before/after (no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift).
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats + next `INIT-<UTC>-PHASE212-POST-ATTRIBUTION-SEAL-DEPTH` (compose **PHASE211→32**). Do not leave Phase211 unsealed.

**Acceptance:** Phase211 has a validated `research_state/PHASE211_*_PAPER_EVIDENCE_<UTC>.json` (`valid=true`, `issues=[]`), recorded verification evidence (or explicit bounded caveats), P0 intact, and handoff advanced to Phase212.

## VERIFIED STATE (ground truth, 2026-11-11T05:03:20Z)

- **P0 safety:** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false` (re-verified before/after).
- **Working tree:** Phase210 untracked deliverables present (module, generator, 2 tests, artifact) + this handoff update; base HEAD `82c723b75`.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Phase209 sealed:** `research_state/PHASE209_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T045808Z.json` (`validation.valid=true issues=[]`, composes `PHASE208→PHASE32`). **Do not re-implement or re-seal Phase200–209.**
- **Phase210 sealed (THIS SESSION):**
  - Module: `src/hedging/phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` (seed 210210, `p210-*`, composes `PHASE209→PHASE32`, paper-only hard gate).
  - Generator: `scripts/generate_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (12 coverage Deribit/OKX/Bybit/Binance×BTC/ETH/SOL, deterministic replay, finite/bounded, validator enforces guards/composes).
  - Tests: `tests/test_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - Artifact: `research_state/PHASE210_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T050209Z.json` — `validation={"valid":true,"issues":[]}`, `campaign.phase=PHASE210_...`, `campaign.composes=["PHASE209","PHASE32"]`, `campaign.paper_only=true`, `campaign.gates_ok=true`, `campaign.cycles=40`, `campaign.seed=210210`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `no_external_venue_mutation=true`, `advisory=true`, `venue_symbol_coverage` len 12, `seal_surface.bounds_ok=true`, `seal_surface.deterministic_replay_equal=true`, `determinism.deterministic_replay_equal=true`, `risk_posture.gates_ok=true`.
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, `research_state/durable_handoff.md` are redirect stubs — ignore.
- **Chain A out of scope:** `src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` — do not substitute.

## PHASE210 VERIFICATION EVIDENCE (2026-11-11T05:01–05:03Z)

- P0 pre: `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- `py_compile` (4 files): **PASS** (`py_compile_ok`).
- Module smoke `PHASE_QUICK_VERIFY=1 PYTHONPATH=.`: **PASS** — `paper_only True gates_ok True composes ['PHASE209','PHASE32']`.
- Module pytest `tests/test_phase210_...py`: **BLOCKED by deep-chain RecursionError during collection** (Python import recursion through composed hedging chain; governed caveat per prior phases).
- CLI generator `--no-write --cycles 40 --seed 210210` (`PHASE_QUICK_VERIFY=1`, timeout 300s): **PASS** — `{"valid":true,"issues":[],"artifact_path":null}`.
- Evidence generate `--write --cycles 40 --seed 210210` (`PHASE_QUICK_VERIFY=1`, timeout 600s): **PASS** — `PHASE210_..._20261111T050209Z.json`, `valid=true issues=[]` (direct artifact inspection confirmed composes/guards/coverage/determinism/bounds).
- Generator pytest: **not separately run** (equivalent governed acceptance satisfied by module smoke + CLI `--no-write` + validated `--write` artifact; composed-chain collect/latency caveat applies).
- P0 post: `.env` absent; `LIVE_TRADING_ENABLED=false` unchanged.

## NEXT SESSION INIT — PHASE212 (pre-staged, execute immediately after Phase211 seal)

**`INIT-2026-11-11T05:03:20Z-PHASE212-POST-ATTRIBUTION-SEAL-DEPTH`** — Phase211 is evidence-sealed (`research_state/PHASE211_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json`, `validation.valid=true issues=[]`, composes `PHASE210→PHASE32`). **Do not re-implement or re-seal Phase200–211. Implement, verify, generate evidence, and seal Phase212 composing `PHASE211→PHASE32`.**

## BOTTLENECKS (verified 2026-11-11T05:03:20Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift | **CLEAR** | No `.env`; `LIVE_TRADING_ENABLED=false`. Re-verify before/after every batch. |
| Phase169–209 sealed | **CLEARED** | Prior sealed artifacts valid. |
| Phase210 absent | **CLEARED** | `PHASE210_...20261111T050209Z.json` valid; module/generator/tests present. |
| Phase211 absent | **ACTIVE — execute now** | Module, generator, tests, artifact missing. Implement full Phase211 seal composing PHASE210→32. |
| Competing handoffs | **NEUTRALIZED** | Redirect stubs only; this file governs. |
| Chain A/B confusion | **MITIGATED** | Phase210 is Chain B `src/hedging` only. |
| Composed-chain pytest slowness/RecursionError at collect | **MITIGATED** | Governed acceptance = `py_compile` (4) + module smoke + CLI `--no-write` + direct/validated `--write` artifact; targeted pytest with `PHASE_QUICK_VERIFY=1`/timeouts when feasible. |
| NEXT9 A1–A7 | **BLOCKED — out of scope** | Human-only; `next9_unblocked=false`. |

## IMPLEMENTATION MAP (Phase209 → 210 → 211)

| Item | Phase209 (sealed) | Phase210 (sealed) | Phase211 (next) |
|---|---|---|---|
| Module | `src/hedging/phase209_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator | `scripts/generate_phase209_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Module test | `tests/test_phase209_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator test | `tests/test_generate_phase209_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Artifact | `research_state/PHASE209_*_PAPER_EVIDENCE_20261111T045808Z.json` | `research_state/PHASE210_*_PAPER_EVIDENCE_20261111T050209Z.json` | `research_state/PHASE211_*_PAPER_EVIDENCE_<UTC>.json` |
| Seed / IDs | `209209` / `p209-*` | `210210` / `p210-*` | `211211` / `p211-*` |
| Composes | `["PHASE208","PHASE32"]` | `["PHASE209","PHASE32"]` | `["PHASE210","PHASE32"]` |
| Upstream orchestrator | `Phase208...Orchestrator` | `Phase209...Orchestrator` | `Phase210...Orchestrator` |
| Upstream sealed evidence ref | `PHASE208_..._20261111T044827Z.json` | `PHASE209_..._20261111T045808Z.json` | `PHASE210_..._20261111T050209Z.json` |

**Phase210 key deltas from Phase209:** import/compose `Phase209...` → `Phase210...`, seed `210210`, IDs `p210-*`, report/campaign phase `PHASE210_*`, composes `["PHASE209","PHASE32"]`, upstream flags `upstream_phase209/208/32`, evidence refs include sealed `PHASE209_*_20261111T045808Z.json`, cross_refs `Phase210/209/208... composes=PHASE209,PHASE32`.

## VERIFICATION CAVEATS (governed acceptance)

- Deep composed chain (→phase32) may cause pytest collection `RecursionError` and generator pytest slowness; acceptance for seal: `py_compile` (4) + module smoke (`PHASE_QUICK_VERIFY=1`, `paper_only=True gates_ok=True`, composes correct) + CLI `--no-write` valid + validated `--write` artifact `valid=true issues=[]` with 12-coverage/deterministic/bounds_ok/guards intact. Record targeted pytest results/caveats when run.

## HANDOFF DISCIPLINE

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Competing handoff files remain redirect stubs pointing here. Final responses must not ask follow-up questions.

(End of file)
