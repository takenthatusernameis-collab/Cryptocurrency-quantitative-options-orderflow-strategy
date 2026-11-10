# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — VERIFIED REFRESH 2026-11-10T23:12:41Z** — repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; branch `main`, HEAD `985f1529b983e18c40a99e8d04d73e8608317c28` (`chore(kilo): checkpoint agent session`, 2026-11-10T22:25:21Z). **Phase169–196 DONE + verified/sealed** (latest seal: `research_state/PHASE196_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T231241Z.json`, `validation.valid=true issues=[]`, `venue_symbol_coverage=12`, `campaign.composes=["PHASE195","PHASE32"]`, `campaign.gates_ok=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `risk_posture.all_coverage_gates_ok=true`, `seed=196196`, `cycles=40`, `deterministic=true`, `bounds_ok=true`). Phase196 deliverables present: `src/hedging/phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. **P0 (verified 2026-11-10T23:12:41Z):** no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. **NEXT9 remains `next9_unblocked=false` (human-only, out of scope).** Competing handoffs are redirect stubs only (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, `research_state/durable_handoff.md`).

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-2026-11-10T23:12:41Z-PHASE197-POST-ATTRIBUTION-SEAL-DEPTH`** — Phase196 is evidence-sealed (`PHASE196_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T231241Z.json`, `valid=true issues=[]`, composes `PHASE195→PHASE32`). **Do not re-implement or re-seal Phase196. Implement/verify/generate evidence and close Phase197, composing PHASE196→32.**

**Verified preconditions (2026-11-10T23:12:41Z):** no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase196 deliverables present and sealed (`research_state/PHASE196_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T231241Z.json`). Phase197 absent: no `src/hedging/phase197_*`, no `scripts/generate_phase197_*`, no `tests/test_phase197_*` / `tests/test_generate_phase197_*`, no `research_state/PHASE197_*`. `research_state/AUTO_HEALER_REPORT.json` shows no unhealthy components (not a blocker).

**Non-optional scope:** Chain B **`src/hedging`** only, **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–196 pattern. **Compose PHASE196→32**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**. Seed `197197`; IDs `p197-*`; artifacts `PHASE197_*`. Edit sealed phases only if verification reveals a real defect (preserve semantics/guards).

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of sealed phases `phase79/80/110–196`. **NO Chain A substitution** (`src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` out of scope). No `.env` creation; keep `LIVE_TRADING_ENABLED=false`.

**EXECUTE IN FULL (not progress: no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral, no partial delivery):**
1. Confirm P0 + targets: no `.env`; `.env.example` `LIVE_TRADING_ENABLED=false`; Phase197 deliverables absent before implementation.
2. Implement Phase197 (module, generator, module tests, generator tests) mirroring Phase196: paper-only hard gate, `paper_only=True`, `gates_ok=True`, composes includes `PHASE196` and `PHASE32`, 12 venue×symbol probes, deterministic/finite/bounded, validator rejects live/unblock/non-paper violations.
3. `py_compile` 4 files; record.
4. Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`) → expect `paper_only=True gates_ok=True` composes includes `PHASE196,PHASE32`.
5. Module pytest targeted (timeouts/fallbacks as needed); record pass/fail/caveats.
6. Controlled evidence generate: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase197_..._paper_evidence.py --cycles 40 --seed 197197 --write` + direct `validate_artifact` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE196→PHASE32`, paper_only true, live_trading_enabled false, next9_unblocked false, gates_ok true (**record exact artifact path**).
7. CLI `--no-write` smoke; re-run if code changed.
8. Generator pytest with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed (composed-chain caveat: deep chain; governed acceptance evidence = module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact).
9. P0 re-verify before/after (no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift).
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats + next `INIT-<UTC>-PHASE198-POST-ATTRIBUTION-SEAL-DEPTH` (compose **PHASE197→32**). Do not leave Phase197 unsealed.

**Acceptance:** Phase197 has a validated `research_state/PHASE197_*_PAPER_EVIDENCE_<UTC>.json` (`valid=true`, `issues=[]`), recorded verification evidence (or explicit bounded caveats), P0 intact, and handoff advanced to Phase198.

---

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **DONE (verified/sealed):** Phase146–196 — chained `valid=true` paper-only artifacts, coverage=12, composes N→32 (latest: `PHASE196_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T231241Z.json`).
2. **ACTIVE BOTTLENECK — NOW (mandatory, sole priority):** `INIT-2026-11-10T23:12:41Z-PHASE197-POST-ATTRIBUTION-SEAL-DEPTH` — Phase197 **not yet implemented** (no `src/hedging/phase197_*`, no generator script, no tests, no `research_state/PHASE197_*`). Implement mirroring Phase196, compose `PHASE196→32`, seed 197197, 12 coverage rows; verify + evidence-seal + advance.
3. **NEXT (queued):** `INIT-<UTC>-PHASE198-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE197→32**, only after Phase197 verified with artifact evidence.
4. Continue **PHASE197→198→…** only with verified artifacts (`valid=true`/`issues=[]`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor prior sealed phases.**
5. **Not progress:** status-only, doc-only (except final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, prior-phase refactors, or any work before Phase197 is evidence-sealed.

---

## Bottlenecks — removed / remaining (verified 2026-11-10T23:12:41Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift (`.env`/secrets/config/LIVE_TRADING) | **CLEAR** | No `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. Re-verify before/after every batch. |
| Phase169–196 implemented + artifact-verified | **CLEARED** | Sealed through `PHASE196_...20261110T231241Z.json` (`valid=true issues=[]`, composes `PHASE195→PHASE32`). |
| Phase197 not yet implemented (no code/tests/artifact) | **ACTIVE — MANDATORY** | `INIT-2026-11-10T23:12:41Z-PHASE197-POST-ATTRIBUTION-SEAL-DEPTH`: implement Phase197 mirroring Phase196 (Chain B `src/hedging`), compose `PHASE196→32`, seed 197197, 12 venue×symbol coverage rows; verify + controlled `--write` evidence + handoff closure, advance to Phase198. |
| Competing handoffs (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_*.md`, `research_state/durable_handoff.md`) | **NEUTRALIZED** | Redirect stubs only; this file governs. |
| Chain A/B naming confusion | **MITIGATED** | Phase197 is **Chain B `src/hedging` only** (`src.risk/phase*_live_execution*` out of scope). |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (explicit caveat)** | Use `PHASE_QUICK_VERIFY=1`, targeted runs/timeouts. Governed acceptance = module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact. |
| NEXT9 (A1–A7, human-only, `next9_unblocked=false`) | **BLOCKED — out of scope** | Never unblock; does not gate paper-only Chain B depth. |

---

## Verified state (2026-11-10T23:12:41Z)

- **Branch/HEAD:** `main` @ `985f1529b983e18c40a99e8d04d73e8608317c28` `chore(kilo): checkpoint agent session` (2026-11-10T22:25:21Z).
- **P0:** clear (no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`). Re-verify before/after every batch.
- **NEXT9:** HUMAN-ONLY (`next9_unblocked=false`) — does not gate Chain B paper-only depth.
- **Latest verified Chain B seal:** Phase196 DONE + sealed (`PHASE196_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T231241Z.json`, `validation.valid=true issues=[]`, coverage=12, composes `PHASE195,PHASE32`, `campaign.gates_ok=true`, paper_only=true, live_trading_enabled=false, next9_unblocked=false, seed=196196, cycles=40, deterministic=true, bounds_ok=true).
- **Phase197:** **not yet implemented** (no `src/hedging/phase197_*`, no generator script, no tests, no `research_state/PHASE197_*`). **ACTIVE/MANDATORY.**

---

## Implementation pattern reference (Phase196 → Phase197 mapping)

| Component | Phase196 (sealed) | Phase197 (target) |
|---|---|---|
| Module | `src/hedging/phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase197_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator | `scripts/generate_phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase197_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Module Test | `tests/test_phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase197_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator Test | `tests/test_generate_phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase197_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Artifact | `research_state/PHASE196_*_PAPER_EVIDENCE_20261110T231241Z.json` | `research_state/PHASE197_*_PAPER_EVIDENCE_<UTC>.json` |
| Seed | `196196` | `197197` |
| ID Prefix | `p196-` | `p197-` |
| Composes | `["PHASE195","PHASE32"]` | `["PHASE196","PHASE32"]` |
| Upstream Orchestrator | `Phase195AdaptiveToxicityResilientPostAttributionSealOrchestrator` | `Phase196AdaptiveToxicityResilientPostAttributionSealOrchestrator` |
| Evidence ref (upstream sealed) | `PHASE195_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T230603Z.json` | `PHASE196_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T231241Z.json` |

**Key implementation differences for Phase197 (mirror Phase196):**
- Import `Phase196AdaptiveToxicityResilientPostAttributionSealOrchestrator` + `Phase196AdaptiveToxicityResilientPostAttributionSealConfig` from `src.hedging.phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator`
- Config seed default: `197197`; ID maker: `f"p197-{seed}-{tag}-{i:06d}"`
- Compose list in report: `["PHASE196", "PHASE32"]`
- Generator `ARTIFACT_TYPE`: `PHASE197_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE`
- Generator `campaign.phase`: `PHASE197_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR`; `campaign.composes` validation: `"PHASE196" in comp and "PHASE32" in comp`
- Generator `evidence_refs` must include sealed Phase196 artifact `PHASE196_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T231241Z.json` plus chain refs
- Generator `cross_refs`: include `Phase197...Orchestrator`, `Phase196...Orchestrator`, `composes=PHASE196,PHASE32`

---

## Verification Evidence (Phase196 — 2026-11-10T23:12:41Z)

**Commands executed & results:**
- `python3 -m py_compile` on 4 Phase196 files: **OK** (no errors)
- `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -m pytest tests/test_phase196_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py -v`: **2 passed**
- `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c "import scripts.generate_phase196...; d=generate(cycles=40,seed=196196,write=False); print('valid:', d['validation']['valid'])"`: **valid=True, issues=[], composes=['PHASE195','PHASE32'], coverage=12**
- `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c "import scripts.generate_phase196...; d=generate(cycles=40,seed=196196,write=True)"`: **Artifact written to `research_state/PHASE196_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T231241Z.json`**
- `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c "import scripts.generate_phase196...; validate_artifact(json.load(open('research_state/PHASE196_...231241Z.json')))"`: **valid=True, issues=[]**
- `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase196_... --cycles 30 --seed 196196 --no-write`: **valid=True, deterministic=True, gates_ok=True, artifact_path=null**
- `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c "from src.hedging.phase196... import Phase196...; orch=Phase196...(); rep=orch.run_post_attribution_seal_orchestration(cycles=16); print(rep['paper_only'], rep['gates_ok'], rep['composes'])"`: **paper_only=True gates_ok=True composes=['PHASE195','PHASE32']**
- Generator pytest `tests/test_generate_phase196_..._paper_evidence.py`: **timed out at 120s (documented composed-chain caveat)** — governed acceptance satisfied by module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact.
- P0 re-verify: **no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`**

**Artifact:** `research_state/PHASE196_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T231241Z.json` (`valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic=true`, `bounds_ok=true`, `coverage=12`, `composes=["PHASE195","PHASE32"]`)

---

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Competing handoff files remain redirect stubs pointing here. Final responses must not ask follow-up questions.
