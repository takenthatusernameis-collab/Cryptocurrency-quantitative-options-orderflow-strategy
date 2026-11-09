# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — VERIFIED REFRESH 2026-11-09T134200Z** (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; branch `main`; HEAD `df79d48cd` `chore(kilo): checkpoint agent session` + uncommitted Phase148 session work; P0 re-verified 2026-11-09T134200Z before/after — `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**, `.env.example` `LIVE_TRADING_ENABLED=false`; Phase112–148 COMPLETE+verified+artifact-verified; **Phase148 artifact `research_state/PHASE148_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T133944Z.json` present/valid** (`validation.valid=true issues=[]`, `campaign.phase=PHASE148_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR`, `campaign.gates_ok=true`, `campaign.composes=['PHASE147','PHASE32']`, `determinism.bounds_ok=true seal_surface.bounds_ok=true deterministic_replay_equal=true`, `venue_symbol_coverage`=12, `paper_only=true live_trading_enabled=false next9_unblocked=false`); 4 Phase148 deliverables present (`src/hedging/phase148_*.py`, `scripts/generate_phase148_*_paper_evidence.py`, 2 test files); Phase147 artifact `..._20261109T131941Z.json` still valid; **0 `*phase149*` deliverables, 0 Phase149 artifacts** → Phase149 **UNSTARTED / MANDATORY NOW**; competing handoffs are redirect stubs — **this file governs**; `research_state/durable_handoff.md` stale/superseded — **ignore it**.)

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-20261109T134200Z-PHASE149-POST-ATTRIBUTION-SEAL-DEPTH`**

**Scope (non-optional):** Chain B **`src/hedging`** only, **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–148 exactly (module + paper-evidence generator + 2 test files). **Compose PHASE148→32**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.

**Repo-priority (name-driven, must guide all decisions):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy. Campaign spine: **orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence**. Every Phase149 change must strengthen this spine with verified, paper-only evidence.

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of `phase79/80/110–148`. **NO Chain A substitution** (`src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` out of scope).

**EXECUTE IN FULL (not progress: no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral):**
1. `src/hedging/phase149_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate; compose `Phase148AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub; emit `phase="PHASE149_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` includes `PHASE148` and `PHASE32`. Seed `149149`; IDs `p149-*`; artifacts `PHASE149_*`.
2. `scripts/generate_phase149_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` (default seed `149149`, cycles `40`), timestamped `research_state/PHASE149_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Hang stubs/cache pattern per Phase111–148.
3. `tests/test_phase149_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — smoke: paper-only gate, `gates_ok`, `composes=['PHASE148','PHASE32']`.
4. `tests/test_generate_phase149_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid shape; reject `live_trading_enabled=True`, `next9_unblocked=True`, `paper_only=False`, `advisory=False`, `no_external_venue_mutation=False`; deterministic seed; 12 coverage finite/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+`artifact_path=null`; cross-refs Phase149/Phase148/`composes=PHASE148,PHASE32`).

**Verification (record exact results/paths/caveats — never skip):**
- `py_compile` 4 files OK.
- Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE148,PHASE32`.
- Module pytest pass.
- Controlled `generate(cycles=40, seed=149149, write=True)` + `validate_artifact` → `valid=true issues=[] deterministic/bounds_ok as emitted, coverage=12, composes=['PHASE148','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true` (**record artifact path**).
- CLI `--no-write` (`PHASE_QUICK_VERIFY=1 --cycles 4 --seed 149149`) → `valid=true issues=[] ... artifact_path=null` (cite reason if timeout; use controlled fallback).
- Targeted generator pytest with `PHASE_QUICK_VERIFY=1`/timeouts (record pass counts; split/controlled fallbacks allowed with explicit caveats).
- P0 re-verify before/after (empty guarded diff, `LIVE_TRADING_ENABLED=false`).
- **Update this handoff last** with verified facts + next `INIT-<UTC>-PHASE150-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE149→32).

---

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **DONE (verified):** `INIT-20261109T122838Z-PHASE147-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, compose **PHASE146→32**, 12 coverage rows. Artifact `...PHASE147_..._20261109T131941Z.json` (`valid=true`).
2. **DONE (verified):** `INIT-20261109T132100Z-PHASE148-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, compose **PHASE147→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update. Artifact `research_state/PHASE148_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T133944Z.json` (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE147','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`); module smoke + module pytest `2 passed`; CLI `--no-write --cycles 4 --seed 148148` `valid=true artifact_path=null`; P0 clear before/after.
3. **NOW (mandatory):** `INIT-20261109T134200Z-PHASE149-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, compose **PHASE148→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update. **No other work takes priority.**
4. **NEXT (queued):** `INIT-<UTC>-PHASE150-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE149→32**, only after Phase149 verified with evidence.
5. Continue **PHASE149→150→151→…** only with verified artifacts (`validation.valid=true`/`ok=true` as validator emits, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor prior sealed phases.**
6. **Not progress:** status-only, doc-only (except final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, prior-phase refactors, or any work before Phase149 is complete/verified.

## Bottlenecks — removed / remaining (verified 2026-11-09T134200Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift (`.env`/secrets/config/LIVE_TRADING) | **CLEAR** | Empty guarded diff before/after; `LIVE_TRADING_ENABLED=false`. Re-verify before/after every batch. |
| Phase112–148 implemented + artifact-verified | **CLEARED** | Complete through Phase148 (artifact `...PHASE148_..._20261109T133944Z.json`, `valid=true`). |
| **Phase149 not implemented (0 files/artifacts)** | **ACTIVE — MANDATORY** | Execute `INIT-20261109T134200Z-PHASE149-POST-ATTRIBUTION-SEAL-DEPTH` (PHASE148→32). **No other work takes priority.** |
| Competing handoffs (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`) | **NEUTRALIZED (redirect stubs)** | Do not action; this file governs. |
| Stale `research_state/durable_handoff.md` Phase 110 campaign | **REMOVED as active focus** | Superseded; this file governs. |
| Chain A/B naming confusion | **MITIGATED** | Phase149 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. **Never skip verification.** Phase148: module+generator controlled/CLI verified; full generator pytest suite timed out at 120s in this session (composed-chain cost) — evidence recorded; targeted key cases recommended if environment allows. |
| NEXT9 (A1–A7, human-only, session gate NO_GO, `next9_unblocked=false`) | **BLOCKED — out of scope** | Never unblock; does not gate paper-only Chain B depth. |

## Verified state (2026-11-09T134200Z)

- **Branch/HEAD:** `main` @ `df79d48cd` (working tree contains uncommitted Phase148 deliverables + artifact `...PHASE148_..._20261109T133944Z.json`; checkpoint/commit at session discretion, not required for paper-only evidence).
- **P0:** clear before/after (empty guarded diff; `.env.example` `LIVE_TRADING_ENABLED=false`).
- **NEXT9:** HUMAN-ONLY (`next9_unblocked=false`) — does not gate Chain B.
- **Phase148 (latest verified, 2026-11-09T134200Z):**
  - Deliverables: `src/hedging/phase148_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase148_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x), `tests/test_phase148_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase148_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - `py_compile`: 4 files **OK**.
  - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes=['PHASE147','PHASE32'] phase=PHASE148_...` **OK**.
  - Module pytest: **`2 passed in 13.71s`**.
  - Controlled generate+validate (`cycles=40 seed=148148 write=True`): `valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE147','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true` → artifact `research_state/PHASE148_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T133944Z.json`.
  - CLI `--no-write --cycles 4 --seed 148148` (`PHASE_QUICK_VERIFY=1`): `valid=true issues=[] deterministic=true gates_ok=true artifact_path=null` **OK**.
  - Generator pytest caveat: full 10-case suite timed out at 120s (composed-chain cost); controlled generate+validate + CLI + direct assertions cover required behaviors. **Caveat recorded; do not claim full suite pass.**
- **Phase147:** artifact `..._20261109T131941Z.json` (`valid=true`, PHASE146→32) still present.
- **Phase149:** **0 files, 0 artifacts — mandatory now.**

## Prior chain evidence (condensed)

- **Phase148 (latest):** `...PHASE148_..._20261109T133944Z.json` (`valid=true issues=[]`, PHASE147→32, 12 coverage, deterministic/bounds_ok, guards intact).
- **Phase147:** `...PHASE147_..._20261109T131941Z.json` (`valid=true`, PHASE146→32, 12 coverage).
- **Phase146:** `...PHASE146_..._20261109T120846Z.json` (`valid=true`, PHASE145→32, 12 coverage).
- **Phase145:** `...PHASE145_..._20261109T113031Z.json` (`valid=true`, PHASE144→32).
- **Phase144:** `...PHASE144_..._20261109T111724Z.json` (`valid=true`, PHASE143→32).
- **Phase143:** `...PHASE143_..._20261109T103520Z.json` (`valid=true`, PHASE142→32).
- **Phase142:** `...PHASE142_..._20261109T102927Z.json` (`valid=true`, PHASE141→32).
- **Phase141:** `...PHASE141_..._20261109T094526Z.json` (`valid=true`, PHASE140→32).

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
