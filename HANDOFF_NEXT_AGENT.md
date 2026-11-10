# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — VERIFIED REFRESH 2026-11-10T22:27:16Z** — repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; branch `main`, HEAD `985f1529b983e18c40a99e8d04d73e8608317c28` (`chore(kilo): checkpoint agent session`, 2026-11-10T22:25:21Z). **Phase169–194 DONE + verified/sealed** (latest seal: `research_state/PHASE194_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T222334Z.json`, `validation.valid=true issues=[]`, `venue_symbol_coverage=12`, `campaign.composes=["PHASE193","PHASE32"]`, `campaign.gates_ok=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `risk_posture.all_coverage_gates_ok=true`, `seed=194194`, `cycles=40`, `deterministic=true`, `bounds_ok=true`). Phase194 deliverables present: `src/hedging/phase194_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase194_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase194_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase194_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. **P0 (verified 2026-11-10T22:27:16Z):** no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. **NEXT9 remains `next9_unblocked=false` (human-only, out of scope).** Competing handoffs are redirect stubs only (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, `research_state/durable_handoff.md`).

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-2026-11-10T22:27:16Z-PHASE195-POST-ATTRIBUTION-SEAL-DEPTH`** — Phase194 is evidence-sealed (`PHASE194_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T222334Z.json`, `valid=true issues=[]`, composes `PHASE193→PHASE32`). **Do not re-implement or re-seal Phase194. Implement/verify/generate evidence and close Phase195, composing PHASE194→32.**

**Verified preconditions (2026-11-10T22:27:16Z):** no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase194 deliverables present and sealed (`research_state/PHASE194_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T222334Z.json`). Phase195 absent: no `src/hedging/phase195_*`, no `scripts/generate_phase195_*`, no `tests/test_phase195_*` / `tests/test_generate_phase195_*`, no `research_state/PHASE195_*`. `research_state/AUTO_HEALER_REPORT.json` shows no unhealthy components (not a blocker).

**Non-optional scope:** Chain B **`src/hedging`** only, **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–194 pattern. **Compose PHASE194→32**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**. Seed `195195`; IDs `p195-*`; artifacts `PHASE195_*`. Edit sealed phases only if verification reveals a real defect (preserve semantics/guards).

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of sealed phases `phase79/80/110–194`. **NO Chain A substitution** (`src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` out of scope). No `.env` creation; keep `LIVE_TRADING_ENABLED=false`.

**EXECUTE IN FULL (not progress: no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral, no partial delivery):**
1. Confirm P0 + targets: no `.env`; `.env.example` `LIVE_TRADING_ENABLED=false`; Phase195 deliverables absent before implementation.
2. Implement Phase195 (module, generator, module tests, generator tests) mirroring Phase194: paper-only hard gate, `paper_only=True`, `gates_ok=True`, composes includes `PHASE194` and `PHASE32`, 12 venue×symbol probes, deterministic/finite/bounded, validator rejects live/unblock/non-paper violations.
3. `py_compile` 4 files; record.
4. Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`) → expect `paper_only=True gates_ok=True` composes includes `PHASE194,PHASE32`.
5. Module pytest targeted (timeouts/fallbacks as needed); record pass/fail/caveats.
6. Controlled evidence generate: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase195_..._paper_evidence.py --cycles 40 --seed 195195 --write` + direct `validate_artifact` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE194→PHASE32`, paper_only true, live_trading_enabled false, next9_unblocked false, gates_ok true (**record exact artifact path**).
7. CLI `--no-write` smoke; re-run if code changed.
8. Generator pytest with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed (composed-chain caveat: deep chain; governed acceptance evidence = module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact).
9. P0 re-verify before/after (no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift).
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats + next `INIT-<UTC>-PHASE196-POST-ATTRIBUTION-SEAL-DEPTH` (compose **PHASE195→32**). Do not leave Phase195 unsealed.

**Acceptance:** Phase195 has a validated `research_state/PHASE195_*_PAPER_EVIDENCE_<UTC>.json` (`valid=true`, `issues=[]`), recorded verification evidence (or explicit bounded caveats), P0 intact, and handoff advanced to Phase196.

---

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **DONE (verified/sealed):** Phase146–194 — chained `valid=true` paper-only artifacts, coverage=12, composes N→32 (latest: `PHASE194_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T222334Z.json`).
2. **ACTIVE BOTTLENECK — NOW (mandatory, sole priority):** `INIT-2026-11-10T22:27:16Z-PHASE195-POST-ATTRIBUTION-SEAL-DEPTH` — Phase195 **not yet implemented** (no `src/hedging/phase195_*`, no generator script, no tests, no `research_state/PHASE195_*`). Implement mirroring Phase194, compose `PHASE194→32`, seed 195195, 12 coverage rows; verify + evidence-seal + advance.
3. **NEXT (queued):** `INIT-<UTC>-PHASE196-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE195→32**, only after Phase195 verified with artifact evidence.
4. Continue **PHASE195→196→…** only with verified artifacts (`valid=true`/`issues=[]`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor prior sealed phases.**
5. **Not progress:** status-only, doc-only (except final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, prior-phase refactors, or any work before Phase195 is evidence-sealed.

---

## Bottlenecks — removed / remaining (verified 2026-11-10T22:27:16Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift (`.env`/secrets/config/LIVE_TRADING) | **CLEAR** | No `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. Re-verify before/after every batch. |
| Phase169–194 implemented + artifact-verified | **CLEARED** | Sealed through `PHASE194_...20261110T222334Z.json` (`valid=true issues=[]`, composes `PHASE193→PHASE32`). |
| Phase195 not yet implemented (no code/tests/artifact) | **ACTIVE — MANDATORY** | `INIT-2026-11-10T22:27:16Z-PHASE195-POST-ATTRIBUTION-SEAL-DEPTH`: implement Phase195 mirroring Phase194 (Chain B `src/hedging`), compose `PHASE194→32`, seed 195195, 12 venue×symbol coverage rows; verify + controlled `--write` evidence + handoff closure, advance to Phase196. |
| Competing handoffs (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_*.md`, `research_state/durable_handoff.md`) | **NEUTRALIZED** | Redirect stubs only; this file governs. |
| Chain A/B naming confusion | **MITIGATED** | Phase195 is **Chain B `src/hedging` only** (`src.risk/phase*_live_execution*` out of scope). |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (explicit caveat)** | Use `PHASE_QUICK_VERIFY=1`, targeted runs/timeouts. Governed acceptance = module smoke + CLI `--no-write` + direct `validate_artifact` on `--write` artifact. |
| NEXT9 (A1–A7, human-only, `next9_unblocked=false`) | **BLOCKED — out of scope** | Never unblock; does not gate paper-only Chain B depth. |

---

## Verified state (2026-11-10T22:27:16Z)

- **Branch/HEAD:** `main` @ `985f1529b983e18c40a99e8d04d73e8608317c28` `chore(kilo): checkpoint agent session` (2026-11-10T22:25:21Z).
- **P0:** clear (no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`). Re-verify before/after every batch.
- **NEXT9:** HUMAN-ONLY (`next9_unblocked=false`) — does not gate Chain B paper-only depth.
- **Latest verified Chain B seal:** Phase194 DONE + sealed (`PHASE194_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T222334Z.json`, `validation.valid=true issues=[]`, coverage=12, composes `PHASE193,PHASE32`, `campaign.gates_ok=true`, paper_only=true, live_trading_enabled=false, next9_unblocked=false, seed=194194, cycles=40, deterministic=true, bounds_ok=true).
- **Phase195:** **not yet implemented** (no `src/hedging/phase195_*`, no generator script, no tests, no `research_state/PHASE195_*`). **ACTIVE/MANDATORY.**

---

## Implementation pattern reference (Phase194 → Phase195 mapping)

| Component | Phase194 (sealed) | Phase195 (target) |
|---|---|---|
| Module | `src/hedging/phase194_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `src/hedging/phase195_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator | `scripts/generate_phase194_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `scripts/generate_phase195_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Module Test | `tests/test_phase194_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` | `tests/test_phase195_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` |
| Generator Test | `tests/test_generate_phase194_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` | `tests/test_generate_phase195_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` |
| Artifact | `research_state/PHASE194_*_PAPER_EVIDENCE_<UTC>.json` | `research_state/PHASE195_*_PAPER_EVIDENCE_<UTC>.json` |
| Seed | `194194` | `195195` |
| ID Prefix | `p194-` | `p195-` |
| Composes | `["PHASE193","PHASE32"]` | `["PHASE194","PHASE32"]` |
| Upstream Orchestrator | `Phase193AdaptiveToxicityResilientPostAttributionSealOrchestrator` | `Phase194AdaptiveToxicityResilientPostAttributionSealOrchestrator` |
| Evidence ref (upstream sealed) | `PHASE193_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T220722Z.json` | `PHASE194_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T222334Z.json` |

**Key implementation differences for Phase195 (mirror Phase194):**
- Import `Phase194AdaptiveToxicityResilientPostAttributionSealOrchestrator` + `Phase194AdaptiveToxicityResilientPostAttributionSealConfig` from `src.hedging.phase194_adaptive_toxicity_resilient_post_attribution_seal_orchestrator`
- Config seed default: `195195`; ID maker: `f"p195-{seed}-{tag}-{i:06d}"`
- Compose list in report: `["PHASE194", "PHASE32"]`
- Generator `ARTIFACT_TYPE`: `PHASE195_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE`
- Generator `campaign.phase`: `PHASE195_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR`; `campaign.composes` validation: `"PHASE194" in comp and "PHASE32" in comp`
- Generator `evidence_refs` must include sealed Phase194 artifact `PHASE194_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T222334Z.json` plus chain refs
- Generator `cross_refs`: include `Phase195...Orchestrator`, `Phase194...Orchestrator`, `composes=PHASE194,PHASE32`

---

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Competing handoff files remain redirect stubs pointing here. Final responses must not ask follow-up questions.
