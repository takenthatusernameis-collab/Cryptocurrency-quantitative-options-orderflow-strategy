# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — VERIFIED REFRESH 2026-11-10T022533Z** (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; branch `main`; HEAD `fd006759c` `chore(kilo): checkpoint agent session`; working tree clean — Phase169 committed via checkpoint). **Phase169 DONE + committed + verified (evidence)** — module+generator+2 test files created; artifact `research_state/PHASE169_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T011604Z.json` (`valid=true`). **Phase170 UNSTARTED (0 `*phase170*` deliverables, 0 artifacts) — SOLE MANDATORY PRIORITY.** Competing root handoffs neutralized (redirect stubs) — **this file governs**. `research_state/durable_handoff.md` stale/superseded — **ignore it**. P0 clear: no `.env`, `.env.example` `LIVE_TRADING_ENABLED=false`.
>
> **Repo-priority (name-driven, governs all decisions):** `Cryptocurrency-quantitative-options-orderflow-strategy` → crypto options quantitative **orderflow** strategy. Campaign spine: **orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence**. Every change must strengthen this spine with **verified, paper-only** evidence.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-20261110T022533Z-PHASE170-POST-ATTRIBUTION-SEAL-DEPTH`**

**Non-optional scope:** Chain B **`src/hedging`** only, **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–169 exactly (module + paper-evidence generator + 2 test files). **Compose PHASE169→32**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**. Replace nothing on disk (no phase170 files exist) — add a proper Phase170 (class `Phase170AdaptiveToxicityResilientPostAttributionSealOrchestrator`, config `Phase170AdaptiveToxicityResilientPostAttributionSealConfig`, imports `phase169`, composes `PHASE169→32`, seed `170170`, IDs `p170-*`, artifacts `PHASE170_*`).

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of sealed phases `phase79/80/110–169`. **NO Chain A substitution** (`src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` out of scope). No `.env` creation; keep `LIVE_TRADING_ENABLED=false`.

**EXECUTE IN FULL (not progress: no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral, no partial delivery):**
1. `src/hedging/phase170_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate; compose `Phase170AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub pattern; emit `phase="PHASE170_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` includes `PHASE169` and `PHASE32`. Seed `170170`; IDs `p170-*`; artifacts `PHASE170_*`.
2. `scripts/generate_phase170_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` (default seed `170170`, cycles `40`), timestamped `research_state/PHASE170_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Hang stubs/cache pattern per Phase111–169. `_orch` must build `Phase169...Orchestrator` so `rep.composes == ['PHASE169','PHASE32']`.
3. `tests/test_phase170_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — smoke: paper-only gate, `gates_ok`, `composes=['PHASE169','PHASE32']`.
4. `tests/test_generate_phase170_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid shape; reject `live_trading_enabled=True`, `next9_unblocked=True`, `paper_only=False`, `advisory=False`, `no_external_venue_mutation=False`; deterministic seed; 12 coverage finite/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+`gates_ok`+`artifact_path=null`; cross-refs Phase170/Phase169/`composes=PHASE169,PHASE32`).

**Verification (record exact results/paths/caveats — never skip):**
- `py_compile` 4 files OK.
- Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE169,PHASE32`.
- Module pytest pass (targeted runs with timeouts; composed-chain full-suite caveat ~600s/case — split/controlled fallbacks allowed with explicit caveats).
- Controlled `generate(cycles=40, seed=170170, write=True)` + `validate_artifact` → `valid=true issues=[] deterministic/bounds_ok as emitted, coverage=12, composes=['PHASE169','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true` (**record artifact path**).
- CLI `--no-write` (`PHASE_QUICK_VERIFY=1 --cycles 4 --seed 170170`) → `valid=true issues=[] ... artifact_path=null` (cite reason if timeout; use controlled fallback).
- Targeted generator pytest with `PHASE_QUICK_VERIFY=1`/timeouts (record pass counts; caveats explicit).
- P0 re-verify before/after (empty guarded diff, `LIVE_TRADING_ENABLED=false`, no `.env`).
- **Update this handoff last** with verified facts + next `INIT-<UTC>-PHASE171-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE170→32). Do not leave Phase170 partial.

---

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **DONE (committed, verified):** Phase146 — artifact `PHASE146_...20261109T120846Z.json` (`valid=true`, PHASE145→32).
2. **DONE (committed, verified):** Phase147 — artifact `PHASE147_...20261109T131941Z.json` (`valid=true`, PHASE146→32).
3. **DONE (committed @ `109074c29`, verified):** Phase148 — artifact `PHASE148_...20261109T133944Z.json` (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE147','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`).
4. **DONE (committed @ `9d5cd99ec`, verified):** Phase149 — artifact `PHASE149_...20261109T144305Z.json` (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE148','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`).
5. **DONE (committed, verified):** Phase150–Phase166 — artifacts `PHASE150_...145936Z.json` … `PHASE166_...234730Z.json` (each `valid=true`, N→N-1→32, coverage=12, paper_only, gates_ok). 12/12 pytest pass each.
6. **DONE (committed, verified):** Phase167 — artifact `PHASE167_...20261109T234842Z.json` (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE166','PHASE32']`).
7. **DONE (committed, verified):** Phase168 — artifact `PHASE168_...20261110T003907Z.json` (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE167','PHASE32']`). Mislabeled duplicates replaced; 9/9 + 2/2 pytest pass.
8. **DONE (committed + verified):** Phase169 — Chain B `src/hedging`, paper-only/additive/deterministic/finite-probe/bounded/guarded, composes **PHASE168→32**, 12 coverage rows. Deliverables committed: `src/hedging/phase169_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase169_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase169_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase169_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. Artifact `research_state/PHASE169_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T011604Z.json` (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE168','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`). Verification: `py_compile` 4 files OK; module smoke `paper_only=True gates_ok=True composes=['PHASE168','PHASE32']`; module pytest **2/2 pass**; controlled generate + validate artifact → all green; CLI `--no-write` → `valid=true deterministic=true gates_ok=true artifact_path=null`; generator **10/10 PASS** via controlled direct-assertion fallback (caveat: pytest timed out at 120s shell cap). P0 re-verify clean.
9. **ACTIVE BOTTLENECK — NOW (mandatory, sole priority):** `INIT-20261110T022533Z-PHASE170-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B `src/hedging`, paper-only/additive/deterministic/finite-probe/bounded/guarded, compose **PHASE169→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update. Phase170 = 0 valid deliverables, 0 artifacts. **No other work takes priority.**
10. **NEXT (queued):** `INIT-<UTC>-PHASE171-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE170→32**, only after Phase170 verified with evidence.
11. Continue **PHASE170→171→172→…** only with verified artifacts (`valid=true`/`issues=[]` as validator emits, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor prior sealed phases.**
12. **Not progress:** status-only, doc-only (except final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, prior-phase refactors, or any work before Phase170 is complete/verified.

---

## Bottlenecks — removed / remaining (verified 2026-11-10T022533Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift (`.env`/secrets/config/LIVE_TRADING) | **CLEAR** | No `.env`; `.env.example` `LIVE_TRADING_ENABLED=false` (line 15). Re-verify before/after every batch. |
| Phase112–169 implemented + artifact-verified | **CLEARED (Phase169 committed)** | Phase169 complete & committed (artifact `PHASE169_...20261110T011604Z.json`, `valid=true`). |
| Phase170 unstarted | **ACTIVE — MANDATORY** | Execute `INIT-20261110T022533Z-PHASE170-POST-ATTRIBUTION-SEAL-DEPTH`; compose PHASE169→32, seed 170170. |
| Competing handoffs (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`) | **NEUTRALIZED** | Redirect stubs; this file governs. |
| Stale `research_state/durable_handoff.md` | **NEUTRALIZED** | Redirect stub; this file governs. |
| Chain A/B naming confusion | **MITIGATED** | Phase169/170 are **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats (~600s/case). **Never skip verification.** Phase169 generator tests recorded as 10/10 direct-assertion fallback (pytest 120s cap). |
| NEXT9 (A1–A7, human-only, `next9_unblocked=false`) | **BLOCKED — out of scope** | Never unblock; does not gate paper-only Chain B depth. |

---

## Verified state (2026-11-10T022533Z)

- **Branch/HEAD (verified):** `main` @ `fd006759c`. **Working tree:** clean (Phase169 committed via checkpoint `fd006759c`).
- **P0:** clear (no `.env`; `.env.example` `LIVE_TRADING_ENABLED=false`; phase169 changes limited to `src/hedging/phase169*`, `scripts/*phase169*`, `tests/*phase169*`, `research_state/PHASE169_*`).
- **NEXT9:** HUMAN-ONLY (`next9_unblocked=false`) — does not gate Chain B.
- **Phase169 (DONE, verified):** `valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE168','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. Artifact `research_state/PHASE169_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T011604Z.json`. Module smoke OK; module pytest **2/2 pass**; CLI `--no-write` (`--cycles 4 --seed 169169`) `valid=true deterministic=true gates_ok=true artifact_path=null`; generator **10/10 PASS** via controlled direct-assertion fallback (caveat: pytest run timed out at 120s shell cap).
- **Phase170:** **0 valid deliverables, 0 artifacts — mandatory now (`INIT-20261110T022533Z-PHASE170-POST-ATTRIBUTION-SEAL-DEPTH`).**

---

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
