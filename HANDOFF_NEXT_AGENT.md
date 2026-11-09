# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — VERIFIED REFRESH 2026-11-09T12:22:48Z** (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; branch `main`; HEAD `1d7e676ee` `chore(kilo): checkpoint agent session`; P0 re-verified 2026-11-09T12:22:48Z — `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**, `.env.example` `LIVE_TRADING_ENABLED=false`; Phase112–146 COMPLETE+verified+artifact-verified; Phase146 artifact `research_state/PHASE146_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T120846Z.json` present/valid (`valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE145','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`); 4 `*phase146*` deliverables present + artifact; **0 `*phase147*` deliverables, 0 Phase147 artifacts** → Phase147 **UNSTARTED / MANDATORY NOW**; competing handoffs `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs; `research_state/durable_handoff.md` stale/superseded — **this file governs**.)

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy)

**`INIT-20261109T122248Z-PHASE147-POST-ATTRIBUTION-SEAL-DEPTH`**

**Scope (non-optional):** Chain B **`src/hedging`** only, **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–146 exactly (module + paper-evidence generator + 2 test files). **Compose PHASE146→32**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.

**Repo-priority (name-driven, must guide all decisions):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy. Campaign spine: **orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence**. Every Phase147 change must strengthen this spine with verified, paper-only evidence.

**HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of `phase79/80/110–145`. **NO Chain A substitution** (`src.risk/phase*_live_execution*`, `tests/test_phase*_live_execution*` out of scope).

**EXECUTE IN FULL (not progress: no status-only, no doc-only-except-final-handoff, no stubs, no skipped verification, no deferral):**
1. `src/hedging/phase147_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate; compose `Phase146AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub; emit `phase="PHASE147_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` includes `PHASE146` and `PHASE32`. Seed `147147`; IDs `p147-*`; artifacts `PHASE147_*`.
2. `scripts/generate_phase147_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` (default seed `147147`, cycles `40`), timestamped `research_state/PHASE147_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Hang stubs/cache pattern per Phase111–146.
3. `tests/test_phase147_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — smoke: paper-only gate, `gates_ok`, `composes=['PHASE146','PHASE32']`.
4. `tests/test_generate_phase147_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid shape; reject `live_trading_enabled=True`, `next9_unblocked=True`, `paper_only=False`, `advisory=False`, `no_external_venue_mutation=False`; deterministic seed; 12 coverage finite/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+`artifact_path=null`; cross-refs Phase147/Phase146/`composes=PHASE146,PHASE32`).

**Verification (record exact results/paths/caveats — never skip):**
- `py_compile` 4 files OK.
- Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE146,PHASE32`.
- Module pytest pass.
- Controlled `generate(cycles=40, seed=147147, write=True)` + `validate_artifact` → `valid=true issues=[] deterministic=true bounds_ok=true coverage=12 composes=['PHASE146','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true` (**record artifact path**).
- CLI `--no-write` (`PHASE_QUICK_VERIFY=1 --cycles 4 --seed 147147`) → `valid=true issues=[] ... artifact_path=null` (cite reason if timeout; use controlled fallback).
- Targeted generator pytest with `PHASE_QUICK_VERIFY=1`/timeouts (record pass counts; split/controlled fallbacks allowed with explicit caveats).
- P0 re-verify before/after (empty guarded diff, `LIVE_TRADING_ENABLED=false`).
- **Update this handoff last** with verified facts + next `INIT-<UTC>-PHASE148-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE147→32).

---

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261109T122248Z-PHASE147-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, compose **PHASE146→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE148-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE147→32**, only after Phase147 verified with evidence.
3. Continue **PHASE147→148→149→…** only with verified artifacts (`validation.valid=true`/`ok=true` as validator emits, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor prior sealed phases.**
4. **Not progress:** status-only, doc-only (except final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, prior-phase refactors, or any work before Phase147 is complete/verified.

## Bottlenecks — removed / remaining (verified 2026-11-09T12:22:48Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift (`.env`/secrets/config/LIVE_TRADING) | **CLEAR** | Empty guarded diff; `LIVE_TRADING_ENABLED=false`. Re-verify before/after every batch. |
| Phase112–146 implemented + artifact-verified | **CLEARED** | Complete through Phase146. |
| **Phase147 not implemented (0 files/artifacts)** | **ACTIVE — MANDATORY** | Execute `INIT-20261109T122248Z-PHASE147-POST-ATTRIBUTION-SEAL-DEPTH` (PHASE146→32). **No other work takes priority.** |
| Competing handoffs (`NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`) | **NEUTRALIZED (redirect stubs)** | Do not action; this file governs. |
| Stale `research_state/durable_handoff.md` Phase 110 campaign | **REMOVED as active focus** | Superseded; this file governs. |
| Chain A/B naming confusion | **MITIGATED** | Phase147 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. Never skip verification. |
| NEXT9 (A1–A7, human-only, session gate NO_GO, `next9_unblocked=false`) | **BLOCKED — out of scope** | Never unblock; does not gate paper-only Chain B depth. |

## Verified state (2026-11-09T12:22:48Z)

- **Branch/HEAD:** `main` @ `1d7e676ee` (dirty state may reflect uncommitted session artifacts; Phase146 deliverables/artifact present).
- **P0:** clear (empty guarded diff; `LIVE_TRADING_ENABLED=false`).
- **NEXT9:** HUMAN-ONLY (`next9_unblocked=false`) — does not gate Chain B.
- **Phase146 (latest verified):** 4 deliverables + `research_state/PHASE146_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T120846Z.json` (`valid=true`, PHASE145→32, 12 coverage, guards intact). Module smoke (`PHASE_QUICK_VERIFY=1`): `PHASE146... paper_only=True gates_ok=True composes=['PHASE145','PHASE32']`.
- **Phase147:** **0 files, 0 artifacts — mandatory now.**

## Prior chain evidence (condensed)

- **Phase145:** `...PHASE145_..._20261109T113031Z.json` (`valid=true`, PHASE144→32, 12 coverage, guards intact).
- **Phase144:** `...PHASE144_..._20261109T111724Z.json` (`valid=true`, PHASE143→32).
- **Phase143:** `...PHASE143_..._20261109T103520Z.json` (`valid=true`, PHASE142→32).
- **Phase142:** `...PHASE142_..._20261109T102927Z.json` (`valid=true`, PHASE141→32).
- **Phase141:** `...PHASE141_..._20261109T094526Z.json` (`valid=true`, PHASE140→32).
- **Phase140:** `...PHASE140_..._20261109T093119Z.json` (`valid=true`, PHASE139→32).

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
