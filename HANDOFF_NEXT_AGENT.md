# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Last verified refresh:** 2026-11-11T04:01:49Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`, branch `main`, HEAD `82c723b75` `chore(kilo): checkpoint agent session`; working tree clean; P0 re-verified at session start). This file is the only durable handoff; competing handoff files are redirect stubs.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-2026-11-11T03:43:00Z-PHASE208-POST-ATTRIBUTION-SEAL-DEPTH`** — Phase207 is evidence-sealed (`research_state/PHASE207_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T034018Z.json`, `validation.valid=true issues=[]`, composes `PHASE206→PHASE32`). **Do not re-implement or re-seal Phase200–207. Implement, verify, generate evidence, and seal Phase208 composing `PHASE207→PHASE32`.**

**Non-optional scope:** Chain B **`src/hedging`** only; **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–207 pattern. **Compose `PHASE207→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**. Seed `208208`; IDs `p208-*`; artifacts `PHASE208_*`. Edit sealed phases only if verification reveals a real defect (preserve semantics/guards).

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of sealed phases `phase79/80/110–207`. **NO Chain A substitution**. No `.env` creation; keep `LIVE_TRADING_ENABLED=false`.

**EXECUTE IN FULL (no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral, no partial delivery):**
1. Confirm P0 + targets: no `.env`; `.env.example` `LIVE_TRADING_ENABLED=false`; Phase208 deliverables absent before implementation.
2. Implement Phase208 (module, generator, module tests, generator tests) mirroring Phase207: paper-only hard gate, `paper_only=True`, `gates_ok=True`, composes includes `PHASE207` and `PHASE32`, 12 venue×symbol probes, deterministic/finite/bounded, validator rejects live/unblock/non-paper violations.
3. `py_compile` 4 files; record.
4. Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`) → expect `paper_only=True gates_ok=True` composes includes `PHASE207,PHASE32`.
5. Module pytest targeted (timeouts/fallbacks as needed); record pass/fail/caveats.
6. Controlled evidence generate: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase208_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py --cycles 40 --seed 208208 --write` + direct `validate_artifact` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE207→PHASE32`, paper_only true, live_trading_enabled false, next9_unblocked false, gates_ok true (**record exact artifact path**).
7. CLI `--no-write` smoke; re-run if code changed.
8. Generator pytest with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed (composed-chain caveat: deep chain; governed acceptance evidence = module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact).
9. P0 re-verify before/after (no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift).
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats + next `INIT-<UTC>-PHASE209-POST-ATTRIBUTION-SEAL-DEPTH` (compose **PHASE208→32**). Do not leave Phase208 unsealed.

**Acceptance:** Phase208 has a validated `research_state/PHASE208_*_PAPER_EVIDENCE_<UTC>.json` (`valid=true`, `issues=[]`), recorded verification evidence (or explicit bounded caveats), P0 intact, and handoff advanced to Phase209.

## VERIFIED STATE (ground truth, 2026-11-11T04:01:49Z)

- **P0 safety:** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- **Working tree:** clean (`git status --short` empty).
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Chain B sealed:** Phase169–207 DONE/sealed (`src/hedging` paper-only chain). Latest: `research_state/PHASE207_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T034018Z.json` (`validation.valid=true issues=[]`, `venue_symbol_coverage=12`, `campaign.composes=["PHASE206","PHASE32"]`, `campaign.gates_ok=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `seed=207207`, `cycles=40`, `deterministic=true`, `bounds_ok=true`). **Do not re-implement or re-seal Phase200–207.**
- **Phase208 absent (verified):** no `src/hedging/phase208_*`, no `scripts/generate_phase208_*`, no `tests/test_phase208_*`/`tests/test_generate_phase208_*`, no `research_state/PHASE208_*`.
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, `research_state/durable_handoff.md` are redirect stubs — ignore.
- **Chain A out of scope:** `src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` — do not substitute.

## NEXT SESSION INIT — PHASE209 (pre-staged, execute immediately after Phase208 seal)

**`INIT-<PHASE208_SEAL_TIMESTAMP>-PHASE209-POST-ATTRIBUTION-SEAL-DEPTH`** — after Phase208 is evidence-sealed (`research_state/PHASE208_*_PAPER_EVIDENCE_<UTC>.json`, `valid=true issues=[]`, composes `PHASE207→PHASE32`). **Do not re-implement/re-seal Phase200–208. Implement/verify/generate evidence and close Phase209, composing `PHASE208→32`.** Same guards/scope/12-coverage/verification pattern as Phase208 with seed `209209`, IDs `p209-*`, artifacts `PHASE209_*`, upstream `Phase208...` orchestrator/artifact. Advance handoff to Phase210 on seal.

## BOTTLENECKS (verified 2026-11-11T04:01:49Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift | **CLEAR** | No `.env`; `LIVE_TRADING_ENABLED=false`. Re-verify before/after every batch. |
| Phase169–207 sealed | **CLEARED** | Latest `PHASE207_...20261111T034018Z.json` valid. |
| Phase208 not implemented | **ACTIVE — SOLE PRIORITY** | Execute `INIT-2026-11-11T03:43:00Z-PHASE208-POST-ATTRIBUTION-SEAL-DEPTH` now; no planning/deferral. |
| Competing handoffs | **NEUTRALIZED** | Redirect stubs only; this file governs. |
| Chain A/B confusion | **MITIGATED** | Phase208 is Chain B `src/hedging` only. |
| Composed-chain pytest slowness/RecursionError at collect | **MITIGATED** | Governed acceptance = `py_compile` (4) + module smoke + CLI `--no-write` + direct `validate_artifact` on `--write`; targeted generator pytest with `PHASE_QUICK_VERIFY=1`/timeouts. |
| NEXT9 A1–A7 | **BLOCKED — out of scope** | Human-only; `next9_unblocked=false`. |

## IMPLEMENTATION MAP (Phase207 → 208 → 209)

| Item | Phase207 (sealed) | Phase208 (active) | Phase209 (next) |
|---|---|---|---|
| Module | `src/hedging/phase207_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase208_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase209_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator | `scripts/generate_phase207_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase208_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase209_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Module test | `tests/test_phase207_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase208_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase209_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator test | `tests/test_generate_phase207_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase208_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase209_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Artifact | `research_state/PHASE207_*_PAPER_EVIDENCE_20261111T034018Z.json` | `research_state/PHASE208_*_PAPER_EVIDENCE_<UTC>.json` | `research_state/PHASE209_*_PAPER_EVIDENCE_<UTC>.json` |
| Seed / IDs | `207207` / `p207-*` | `208208` / `p208-*` | `209209` / `p209-*` |
| Composes | `["PHASE206","PHASE32"]` | `["PHASE207","PHASE32"]` | `["PHASE208","PHASE32"]` |
| Upstream orchestrator | `Phase206AdaptiveToxicityResilientPostAttributionSealOrchestrator` | `Phase207AdaptiveToxicityResilientPostAttributionSealOrchestrator` | `Phase208AdaptiveToxicityResilientPostAttributionSealOrchestrator` |
| Upstream sealed evidence ref | `PHASE206_..._PAPER_EVIDENCE_20261111T030309Z.json` | `PHASE207_..._PAPER_EVIDENCE_20261111T034018Z.json` | `PHASE208_..._PAPER_EVIDENCE_<UTC>.json` |

**Phase208 key deltas from Phase207:** import `Phase207AdaptiveToxicityResilientPostAttributionSealConfig` + `Phase207AdaptiveToxicityResilientPostAttributionSealOrchestrator` from `src.hedging.phase207_adaptive_toxicity_resilient_post_attribution_seal_orchestrator`; default seed `208208`; ID maker `f"p208-{seed}-{tag}-{i:06d}"`; report composes `["PHASE207","PHASE32"]`; generator `ARTIFACT_TYPE`/campaign phase `PHASE208_*`; campaign composes validation requires `PHASE207` and `PHASE32`; evidence_refs include sealed `PHASE207_*_20261111T034018Z.json` plus chain refs; cross_refs include `Phase208...Orchestrator`, `Phase207...Orchestrator`, `composes=PHASE207,PHASE32`.

## VERIFICATION CAVEATS (governed acceptance)

- Deep composed chain (→phase32) may cause pytest collection `RecursionError` and generator pytest slowness; acceptance for seal: `py_compile` (4) + module smoke (`PHASE_QUICK_VERIFY=1`, `paper_only=True gates_ok=True`, composes correct) + CLI `--no-write` valid + direct `validate_artifact` on `--write` artifact `valid=true issues=[]` with 12-coverage/deterministic/bounds_ok/guards intact. Record targeted pytest results/caveats when run.

## HANDOFF DISCIPLINE

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Competing handoff files remain redirect stubs pointing here. Final responses must not ask follow-up questions.
