# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — VERIFIED REFRESH 2026-11-10T000102Z** (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; branch `main`; HEAD `ba275f713` `chore(kilo): checkpoint agent session` — **working tree clean**; phases 100–167 committed + artifact-verified; **Phase167 is the last sealed phase** (artifact `research_state/PHASE167_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T234842Z.json`, `valid=true`). **Phase168 files exist on disk but are mislabeled phase167 duplicates** (module defines `Phase167...Orchestrator`, imports phase166, composes PHASE166→32; generator writes PHASE167 artifact type; tests import phase167) with **no PHASE168 artifact** — this tail defect is the ACTIVE bottleneck. **Phase168 UNSTARTED (0 valid deliverables, 0 artifacts) — MANDATORY NOW.** Competing root handoffs neutralized (redirect stubs) — **this file governs**. `research_state/durable_handoff.md` stale/superseded — **ignore it**.)
>
> **Repo-priority (name-driven, governs all decisions):** `Cryptocurrency-quantitative-options-orderflow-strategy` → crypto options quantitative **orderflow** strategy. Campaign spine: **orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence**. Every change must strengthen this spine with **verified, paper-only** evidence.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-20261110T000102Z-PHASE168-POST-ATTRIBUTION-SEAL-DEPTH`**

**Non-optional scope:** Chain B **`src/hedging`** only, **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–167 exactly (module + paper-evidence generator + 2 test files). **Compose PHASE167→32**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**. **Replace the mislabeled phase168 duplicates on disk** (module defines Phase167 class / imports phase166 / composes PHASE166→32; generator writes PHASE167 artifact type; tests import phase167) with a proper Phase168 (class `Phase168AdaptiveToxicityResilientPostAttributionSealOrchestrator`, config `Phase168AdaptiveToxicityResilientPostAttributionSealConfig`, imports `phase167`, composes `PHASE167→32`, seed `168168`, IDs `p168-*`, artifacts `PHASE168_*`).

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of sealed phases `phase79/80/110–167` (phase168 is **not sealed** — it is the target; replace its mislabeled duplicates). **NO Chain A substitution** (`src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` out of scope). No `.env` creation; keep `LIVE_TRADING_ENABLED=false`.

**EXECUTE IN FULL (not progress: no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral, no partial delivery):**
1. `src/hedging/phase168_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate; compose `Phase168AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub pattern; emit `phase="PHASE168_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` includes `PHASE167` and `PHASE32`. Seed `168168`; IDs `p168-*`; artifacts `PHASE168_*`.
2. `scripts/generate_phase168_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` (default seed `168168`, cycles `40`), timestamped `research_state/PHASE168_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Hang stubs/cache pattern per Phase111–167.
3. `tests/test_phase168_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — smoke: paper-only gate, `gates_ok`, `composes=['PHASE167','PHASE32']`.
4. `tests/test_generate_phase168_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid shape; reject `live_trading_enabled=True`, `next9_unblocked=True`, `paper_only=False`, `advisory=False`, `no_external_venue_mutation=False`; deterministic seed; 12 coverage finite/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+`gates_ok`+`artifact_path=null`; cross-refs Phase168/Phase167/`composes=PHASE167,PHASE32`).

**Verification (record exact results/paths/caveats — never skip):**
- `py_compile` 4 files OK.
- Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE167,PHASE32`.
- Module pytest pass (targeted runs with timeouts; composed-chain full-suite caveat ~600s/case — split/controlled fallbacks allowed with explicit caveats).
- Controlled `generate(cycles=40, seed=168168, write=True)` + `validate_artifact` → `valid=true issues=[] deterministic/bounds_ok as emitted, coverage=12, composes=['PHASE167','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true` (**record artifact path**).
- CLI `--no-write` (`PHASE_QUICK_VERIFY=1 --cycles 4 --seed 168168`) → `valid=true issues=[] ... artifact_path=null` (cite reason if timeout; use controlled fallback).
- Targeted generator pytest with `PHASE_QUICK_VERIFY=1`/timeouts (record pass counts; caveats explicit).
- P0 re-verify before/after (empty guarded diff, `LIVE_TRADING_ENABLED=false`, no `.env`).
- **Update this handoff last** with verified facts + next `INIT-<UTC>-PHASE169-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE168→32). Do not leave Phase168 partial.

---

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **DONE (committed, verified):** Phase147 — artifact `PHASE147_...20261109T131941Z.json` (`valid=true`, PHASE146→32).
2. **DONE (committed @ `109074c29`, verified):** Phase148 — artifact `PHASE148_...20261109T133944Z.json` (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE147','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`).
3. **DONE (committed @ `9d5cd99ec`, verified):** Phase149 — artifact `PHASE149_...20261109T144305Z.json` (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE148','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`).
4. **DONE (committed, verified):** Phase150–Phase166 — artifacts `PHASE150_...145936Z.json` … `PHASE166_...234730Z.json` (each `valid=true`, N→N-1→32, coverage=12, paper_only, gates_ok). 12/12 pytest pass each.
5. **DONE (committed, verified, LAST SEALED PHASE):** Phase167 — artifact `PHASE167_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T234842Z.json` (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE166','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`). 12/12 pytest pass.
6. **ACTIVE BOTTLENECK — NOW (mandatory, sole priority):** `INIT-20261110T000102Z-PHASE168-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B `src/hedging`, paper-only/additive/deterministic/finite-probe/bounded/guarded, compose **PHASE167→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update. Replace mislabeled phase168 duplicates. **No other work takes priority.** Phase168 = 0 valid deliverables, 0 artifacts.
7. **NEXT (queued):** `INIT-<UTC>-PHASE169-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE168→32**, only after Phase168 verified with evidence.
8. Continue **PHASE168→169→170→171→172→…** only with verified artifacts (`valid=true`/`issues=[]` as validator emits, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor prior sealed phases.**
9. **Not progress:** status-only, doc-only (except final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, prior-phase refactors, or any work before Phase168 is complete/verified.

---

## Bottlenecks — removed / remaining (verified 2026-11-10T000102Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift (`.env`/secrets/config/LIVE_TRADING) | **CLEAR** | Empty guarded diff; `LIVE_TRADING_ENABLED=false`; no `.env`. Re-verify before/after every batch. |
| Phase112–167 implemented + committed/artifact-verified | **CLEARED** | Complete through Phase167 (last sealed artifact `PHASE167_...234842Z.json`, `valid=true`). |
| Phase168 tail defect: mislabeled phase167 duplicates, no PHASE168 artifact | **ACTIVE — MANDATORY** | Execute `INIT-20261110T000102Z-PHASE168-POST-ATTRIBUTION-SEAL-DEPTH`; replace mislabeled phase168 module/generator/tests with proper Phase168 (class Phase168…, imports phase167, composes PHASE167→32, seed 168168). |
| Competing handoffs (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`) | **NEUTRALIZED** | Redirect stubs; this file governs. |
| Stale `research_state/durable_handoff.md` | **NEUTRALIZED** | Redirect stub; this file governs. |
| Chain A/B naming confusion | **MITIGATED** | Phase168 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats (~600s/case). **Never skip verification.** |
| NEXT9 (A1–A7, human-only, `next9_unblocked=false`) | **BLOCKED — out of scope** | Never unblock; does not gate paper-only Chain B depth. |

---

## Verified state (2026-11-10T000102Z)

- **Branch/HEAD:** `main` @ `ba275f713`. Working tree clean. Phase167 last sealed @ artifact `PHASE167_...20261109T234842Z.json`.
- **P0:** clear (empty guarded diff; `.env.example` `LIVE_TRADING_ENABLED=false`; no `.env`).
- **NEXT9:** HUMAN-ONLY (`next9_unblocked=false`) — does not gate Chain B.
- **Phase167 (last sealed, committed, artifact-verified):** `valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE166','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`.
- **Phase168:** **0 valid deliverables, 0 artifacts — mandatory now (`INIT-20261110T000102Z-PHASE168-POST-ATTRIBUTION-SEAL-DEPTH`).** Existing `phase168_*` files are mislabeled phase167 duplicates and must be replaced.

---

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
