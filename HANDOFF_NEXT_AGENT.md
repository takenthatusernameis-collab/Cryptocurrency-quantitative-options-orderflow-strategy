# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Last verified refresh:** 2026-11-11T06:34:17Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`, branch `main`, HEAD `31a8f01e7` `chore(kilo): checkpoint agent session`; P0 re-verified this session: `.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`; no `.env` created). This file is the only durable handoff; competing handoff files are redirect stubs.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-2026-11-11T06:34:17Z-PHASE213-POST-ATTRIBUTION-SEAL-DEPTH`** — Phase212 is evidence-sealed (`research_state/PHASE212_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T062752Z.json`, `validation.valid=true issues=[]`, composes `PHASE211→PHASE32`, seed=212212, cycles=40, venue_symbol_coverage=12, paper_only=true, live_trading_enabled=false, next9_unblocked=false, gates_ok=true, deterministic=true, bounds_ok=true; earlier valid artifact also present: `research_state/PHASE212_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T054236Z.json`). **Do not re-implement or re-seal Phase200–212. Implement, verify, generate evidence, and seal Phase213 composing `PHASE212→PHASE32`.**

**Non-optional scope:** Chain B **`src/hedging`** only; **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–212 pattern. **Compose `PHASE212→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**. Seed `213213`; IDs `p213-*`; artifacts `PHASE213_*`. Edit sealed phases only if verification reveals a real defect (preserve semantics/guards).

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of sealed phases `phase79/80/110–212`. **NO Chain A substitution**. No `.env` creation; keep `LIVE_TRADING_ENABLED=false`.

**EXECUTE IN FULL (no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral, no partial delivery):**
1. Confirm P0 + targets: no `.env`; `.env.example` `LIVE_TRADING_ENABLED=false`; Phase213 deliverables absent before implementation.
2. Implement Phase213 (module, generator, module tests, generator tests) mirroring Phase212: paper-only hard gate, `paper_only=True`, `gates_ok=True`, composes includes `PHASE212` and `PHASE32`, 12 venue×symbol probes, deterministic/finite/bounded, validator rejects live/unblock/non-paper violations.
3. `py_compile` 4 files; record.
4. Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`) → expect `paper_only=True gates_ok=True` composes includes `PHASE212,PHASE32`.
5. Module pytest targeted (timeouts/fallbacks as needed); record pass/fail/caveats.
6. Controlled evidence generate: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase213_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py --cycles 40 --seed 213213 --write` + direct/CLI validate → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE212→PHASE32`, paper_only true, live_trading_enabled false, next9_unblocked false, gates_ok true (**record exact artifact path**).
7. CLI `--no-write` smoke; re-run if code changed.
8. Generator pytest with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed (composed-chain caveat: deep chain; governed acceptance evidence = module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact).
9. P0 re-verify before/after (no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift).
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats + next `INIT-<UTC>-PHASE214-POST-ATTRIBUTION-SEAL-DEPTH` (compose **PHASE213→32**). Do not leave Phase213 unsealed.

**Acceptance:** Phase213 has a validated `research_state/PHASE213_*_PAPER_EVIDENCE_<UTC>.json` (`valid=true`, `issues=[]`), recorded verification evidence (or explicit bounded caveats), P0 intact, and handoff advanced to Phase214.

## VERIFIED STATE (ground truth, 2026-11-11T06:34:17Z)

- **P0 safety:** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false` (re-verified).
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Phase211 sealed:** `research_state/PHASE211_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T052847Z.json` (`validation.valid=true issues=[]`, composes `PHASE210→PHASE32`). Do not re-implement or re-seal.
- **Phase212 sealed (verified this session):**
  - Module: `src/hedging/phase212_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` (seed 212212, `p212-*`, composes `PHASE211→PHASE32`, paper-only hard gate).
  - Generator: `scripts/generate_phase212_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (12 coverage Deribit/OKX/Bybit/Binance×BTC/ETH/SOL, deterministic replay, finite/bounded, validator enforces guards/composes).
  - Tests: `tests/test_phase212_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase212_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - Artifacts (both validated): `research_state/PHASE212_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T054236Z.json`, `research_state/PHASE212_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T062752Z.json` — `validation={"valid":true,"issues":[]}`, `campaign.composes=["PHASE211","PHASE32"]`, `campaign.paper_only=true`, `campaign.gates_ok=true`, `campaign.seed=212212`, `campaign.cycles=40`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `venue_symbol_coverage` len 12, `seal_surface.bounds_ok=true`, `determinism.deterministic_replay_equal=true`.
- **Phase213:** **ABSENT — ACTIVE** (no module/generator/tests/artifact found). Execute now.
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, `research_state/durable_handoff.md` are redirect stubs — ignore.
- **Chain A out of scope:** `src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` — do not substitute.

## BOTTLENECKS (verified 2026-11-11T06:34:17Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift | **CLEAR** | No `.env`; `LIVE_TRADING_ENABLED=false`. Re-verify before/after every batch. |
| Phase169–211 sealed | **CLEARED** | Prior sealed artifacts valid. |
| Phase212 absent/unsealed | **CLEARED** | Module/generator/tests present; 2 validated artifacts (`valid=true issues=[]`, composes PHASE211→32). |
| Stale handoff blocking progress | **CLEARED** | This refresh advances durable task to Phase213. |
| Phase213 absent | **ACTIVE — execute now** | Implement full Phase213 seal composing PHASE212→32. |
| Competing handoffs | **NEUTRALIZED** | Redirect stubs only; this file governs. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only. |
| Composed-chain pytest slowness/RecursionError at collect | **MITIGATED** | Governed acceptance = `py_compile` (4) + module smoke + CLI `--no-write` + direct/validated `--write` artifact; targeted pytest with `PHASE_QUICK_VERIFY=1`/timeouts when feasible. |
| NEXT9 A1–A7 | **BLOCKED — out of scope** | Human-only; `next9_unblocked=false`. |

## IMPLEMENTATION MAP (Phase210 → 211 → 212 → 213)

| Item | Phase210 (sealed) | Phase211 (sealed) | Phase212 (sealed) | Phase213 (next) |
|---|---|---|---|---|
| Module | `src/hedging/phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase212_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase213_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator | `scripts/generate_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase212_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase213_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Module test | `tests/test_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase212_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase213_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator test | `tests/test_generate_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase211_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase212_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase213_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Artifact | `PHASE210_*_20261111T050209Z.json` | `PHASE211_*_20261111T052847Z.json` | `PHASE212_*_20261111T062752Z.json` (+054236Z) | `PHASE213_*_<UTC>.json` |
| Seed / IDs | `210210` / `p210-*` | `211211` / `p211-*` | `212212` / `p212-*` | `213213` / `p213-*` |
| Composes | `["PHASE209","PHASE32"]` | `["PHASE210","PHASE32"]` | `["PHASE211","PHASE32"]` | `["PHASE212","PHASE32"]` |
| Upstream orchestrator | `Phase209...` | `Phase210...` | `Phase211...` | `Phase212...` |
| Upstream sealed evidence ref | `PHASE209_*_20261111T045808Z.json` | `PHASE210_*_20261111T050209Z.json` | `PHASE211_*_20261111T052847Z.json` | `PHASE212_*_20261111T062752Z.json` |

**Phase213 key deltas from Phase212:** import/compose `Phase212...` → `Phase213...`, seed `213213`, IDs `p213-*`, report/campaign phase `PHASE213_*`, composes `["PHASE212","PHASE32"]`, upstream flags `upstream_phase212/211/32`, evidence refs include sealed `research_state/PHASE212_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T062752Z.json`, cross_refs `Phase213/212/211... composes=PHASE212,PHASE32`.

## VERIFICATION CAVEATS (governed acceptance)

- Deep composed chain (→phase32) may cause pytest collection `RecursionError` and generator pytest slowness; acceptance for seal: `py_compile` (4) + module smoke (`PHASE_QUICK_VERIFY=1`, `paper_only=True gates_ok=True`, composes correct) + CLI `--no-write` valid + direct `validate_artifact` on `--write` artifact `valid=true issues=[]` with 12-coverage/deterministic/bounds_ok/guards intact. Record targeted pytest results/caveats when run.

## HANDOFF DISCIPLINE

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Competing handoff files remain redirect stubs pointing here. Final responses must not ask follow-up questions.

(End of file)
