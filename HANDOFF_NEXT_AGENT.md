# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — VERIFIED REFRESH 2026-11-11T01:47:15Z** — repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; branch `main`, HEAD `4b8f93cc9` (`chore(kilo): checkpoint agent session`). **Phase169–202 DONE + verified/sealed** (latest seal: `research_state/PHASE202_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T011039Z.json`, `validation.valid=true issues=[]`, `venue_symbol_coverage=12`, `campaign.composes=["PHASE201","PHASE32"]`, `campaign.gates_ok=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `risk_posture.all_coverage_gates_ok=true`, `seed=202202`, `cycles=40`, `deterministic=true`, `bounds_ok=true`). Phase202 deliverables present: `src/hedging/phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, sealed artifact `research_state/PHASE202_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T011039Z.json`. Phase201 remains sealed (`research_state/PHASE201_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T010049Z.json`, `valid=true issues=[]`, composes `PHASE200→PHASE32`). **P0 (verified 2026-11-11T01:47:15Z):** no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. **NEXT9 remains `next9_unblocked=false` (human-only, out of scope).** Competing handoffs are redirect stubs only (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, `research_state/durable_handoff.md`).

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-2026-11-11T01:47:15Z-PHASE203-POST-ATTRIBUTION-SEAL-DEPTH`** — Phase202 is evidence-sealed (`PHASE202_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T011039Z.json`, `valid=true issues=[]`, composes `PHASE201→PHASE32`). **Do not re-implement or re-seal Phase200–202. Implement/verify/generate evidence and close Phase203, composing PHASE202→32.**

**Verified preconditions (2026-11-11T01:47:15Z):** no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase202 deliverables present and sealed (`research_state/PHASE202_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T011039Z.json`, `valid=true issues=[]`, composes `PHASE201→PHASE32`). Phase203 absent: no `src/hedging/phase203_*`, no `scripts/generate_phase203_*`, no `tests/test_phase203_*` / `tests/test_generate_phase203_*`, no `research_state/PHASE203_*`. `research_state/AUTO_HEALER_REPORT.json` shows no unhealthy components (not a blocker).

**Non-optional scope:** Chain B **`src/hedging`** only, **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–202 pattern. **Compose PHASE202→32**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**. Seed `203203`; IDs `p203-*`; artifacts `PHASE203_*`. Edit sealed phases only if verification reveals a real defect (preserve semantics/guards).

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of sealed phases `phase79/80/110–202`. **NO Chain A substitution** (`src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` out of scope). No `.env` creation; keep `LIVE_TRADING_ENABLED=false`.

**EXECUTE IN FULL (not progress: no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral, no partial delivery):**
1. Confirm P0 + targets: no `.env`; `.env.example` `LIVE_TRADING_ENABLED=false`; Phase203 deliverables absent before implementation.
2. Implement Phase203 (module, generator, module tests, generator tests) mirroring Phase202: paper-only hard gate, `paper_only=True`, `gates_ok=True`, composes includes `PHASE202` and `PHASE32`, 12 venue×symbol probes, deterministic/finite/bounded, validator rejects live/unblock/non-paper violations.
3. `py_compile` 4 files; record.
4. Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`) → expect `paper_only=True gates_ok=True` composes includes `PHASE202,PHASE32`.
5. Module pytest targeted (timeouts/fallbacks as needed); record pass/fail/caveats.
6. Controlled evidence generate: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase203_..._paper_evidence.py --cycles 40 --seed 203203 --write` + direct `validate_artifact` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE202→PHASE32`, paper_only true, live_trading_enabled false, next9_unblocked false, gates_ok true (**record exact artifact path**).
7. CLI `--no-write` smoke; re-run if code changed.
8. Generator pytest with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed (composed-chain caveat: deep chain; governed acceptance evidence = module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact).
9. P0 re-verify before/after (no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift).
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats + next `INIT-<UTC>-PHASE204-POST-ATTRIBUTION-SEAL-DEPTH` (compose **PHASE203→32**). Do not leave Phase203 unsealed.

**Acceptance:** Phase203 has a validated `research_state/PHASE203_*_PAPER_EVIDENCE_<UTC>.json` (`valid=true`, `issues=[]`), recorded verification evidence (or explicit bounded caveats), P0 intact, and handoff advanced to Phase204.

---

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **DONE (verified/sealed):** Phase146–202 — chained `valid=true` paper-only artifacts, coverage=12, composes N→32 (latest: `PHASE202_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T011039Z.json`).
2. **ACTIVE BOTTLENECK — NOW (mandatory, sole priority):** `INIT-2026-11-11T01:47:15Z-PHASE203-POST-ATTRIBUTION-SEAL-DEPTH` — Phase203 **not yet implemented** (no `src/hedging/phase203_*`, no generator script, no tests, no `research_state/PHASE203_*`). Implement mirroring Phase202, compose `PHASE202→32`, seed 203203, 12 venue×symbol coverage rows; verify + controlled `--write` evidence + handoff closure, advance to Phase204 (verified 2026-11-11T01:47:15Z).
3. **NEXT (queued):** `INIT-<UTC>-PHASE204-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE203→32**, only after Phase203 verified with artifact evidence.
4. Continue **PHASE200→201→…** only with verified artifacts (`valid=true`/`issues=[]`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor prior sealed phases.**
5. **Not progress:** status-only, doc-only (except final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, prior-phase refactors, or any work before Phase203 is evidence-sealed.

---

## Bottlenecks — removed / remaining (verified 2026-11-11T01:47:15Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift (`.env`/secrets/config/LIVE_TRADING) | **CLEAR** | No `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. Re-verify before/after every batch (verified 2026-11-11T01:47:15Z). |
| Phase169–202 implemented + artifact-verified | **CLEARED** | Sealed through `PHASE202_...20261111T011039Z.json` (`valid=true issues=[]`, composes `PHASE201→PHASE32`). |
| Phase203 not yet implemented (no code/tests/artifact) | **ACTIVE — MANDATORY** | `INIT-2026-11-11T01:47:15Z-PHASE203-POST-ATTRIBUTION-SEAL-DEPTH`: implement Phase203 mirroring Phase202 (Chain B `src/hedging`), compose `PHASE202→32`, seed 203203, 12 venue×symbol coverage rows; verify + controlled `--write` evidence + handoff closure, advance to Phase204. |
| Competing handoffs (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_*.md`, `research_state/durable_handoff.md`) | **NEUTRALIZED** | Redirect stubs only; this file governs. |
| Chain A/B naming confusion | **MITIGATED** | Phase203 is **Chain B `src/hedging` only** (`src.risk/phase*_live_execution*` out of scope). |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (explicit caveat)** | Use `PHASE_QUICK_VERIFY=1`, targeted runs/timeouts. Governed acceptance = module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact. |
| NEXT9 (A1–A7, human-only, `next9_unblocked=false`) | **BLOCKED — out of scope** | Never unblock; does not gate paper-only Chain B depth. |

---

## Verified state (2026-11-11T01:47:15Z)

- **Branch/HEAD:** `main` @ `4b8f93cc9` `chore(kilo): checkpoint agent session`.
- **P0:** clear (no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`). Re-verify before/after every batch.
- **NEXT9:** HUMAN-ONLY (`next9_unblocked=false`) — does not gate Chain B paper-only depth.
- **Latest verified Chain B seal:** Phase202 DONE + sealed (`PHASE202_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T011039Z.json`, `validation.valid=true issues=[]`, coverage=12, composes `PHASE201→PHASE32`, `campaign.gates_ok=true`, paper_only=true, live_trading_enabled=false, next9_unblocked=false, seed=202202, cycles=40, deterministic=true, bounds_ok=true). Phase201 sealed (`...PHASE201...20261111T010049Z.json`, composes `PHASE200→PHASE32`).
- **Phase203:** **not yet implemented** (no `src/hedging/phase203_*`, no generator script, no tests, no `research_state/PHASE203_*`). **ACTIVE/MANDATORY.**

---

## Implementation pattern reference (Phase202 → Phase203 mapping)

| Component | Phase202 (sealed) | Phase203 (target) |
|---|---|---|
| Module | `src/hedging/phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase203_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator | `scripts/generate_phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase203_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Module Test | `tests/test_phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase203_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator Test | `tests/test_generate_phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase203_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Artifact | `research_state/PHASE202_*_PAPER_EVIDENCE_20261111T011039Z.json` | `research_state/PHASE203_*_PAPER_EVIDENCE_<UTC>.json` |
| Seed | `202202` | `203203` |
| ID Prefix | `p202-` | `p203-` |
| Composes | `["PHASE201","PHASE32"]` | `["PHASE202","PHASE32"]` |
| Upstream Orchestrator | `Phase201AdaptiveToxicityResilientPostAttributionSealOrchestrator` | `Phase202AdaptiveToxicityResilientPostAttributionSealOrchestrator` |
| Evidence ref (upstream sealed) | `PHASE201_..._PAPER_EVIDENCE_20261111T010049Z.json` | `PHASE202_..._PAPER_EVIDENCE_20261111T011039Z.json` |

**Key implementation differences for Phase203 (mirror Phase202):**
- Import `Phase202AdaptiveToxicityResilientPostAttributionSealOrchestrator` + `Phase202AdaptiveToxicityResilientPostAttributionSealConfig` from `src.hedging.phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator`
- Config seed default: `203203`; ID maker: `f"p203-{seed}-{tag}-{i:06d}"`
- Compose list in report: `["PHASE202", "PHASE32"]`
- Generator `ARTIFACT_TYPE`: `PHASE203_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE`
- Generator `campaign.phase`: `PHASE203_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR`; `campaign.composes` validation: `"PHASE202" in comp and "PHASE32" in comp`
- Generator `evidence_refs` must include sealed Phase202 artifact `PHASE202_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T011039Z.json` plus chain refs
- Generator `cross_refs`: include `Phase203...Orchestrator`, `Phase202...Orchestrator`, `composes=PHASE202,PHASE32`

---

## Verification Evidence (Phase202 — sealed 2026-11-11T01:10:39Z)

**Artifact:** `research_state/PHASE202_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T011039Z.json` (`valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic=true`, `bounds_ok=true`, `coverage=12`, `composes=["PHASE201","PHASE32"]`, seed=202202, cycles=40). Governed acceptance: py_compile OK, module smoke `paper_only=True gates_ok=True`, module+generator pytest 2+2 passed, `--write` + direct `validate_artifact` valid, CLI `--no-write` valid, P0 intact.

(Condensed prior phase evidence retained conceptually in sealed artifacts under `research_state/PHASE{169..202}_*`.)

---

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Competing handoff files remain redirect stubs pointing here. Final responses must not ask follow-up questions.
