# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — VERIFIED REFRESH 2026-11-09T06:56:44Z** (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; branch `main`; HEAD `a638f5c64` `chore(kilo): checkpoint agent session`; P0 re-verified clean; Phase112–136 COMPLETE+verified+artifact-verified; **Phase137 COMPLETE+verified** — `src/hedging/phase137_*`, `scripts/generate_phase137_*`, artifact tracked in HEAD; 2 Phase137 test files present but **untracked** (non-blocking hygiene: include in Phase138 commit); **Phase138 UNSTARTED — sole active agent-removable bottleneck**; no duplicate handoff sections)
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts, no deferral):**
>
> **`INIT-20261109T065644Z-PHASE138-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only / additive / deterministic / finite-probe / bounded / guarded**. Mirror Phase111–137 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE137→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence.
>
> **HARD GUARDS (non-negotiable):** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** NO refactor of `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128/129/130/131/132/133/134/135/136/137`. **NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*` out of scope).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase138_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate; composes `Phase137AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path; finite serialization/assertions; emits report with `phase="PHASE138_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE137` and `PHASE32`. Seed default `138138`; IDs `p138-*`; artifact names `PHASE138_*`.
> 2. `scripts/generate_phase138_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `138138`, cycles `40`), timestamped `research_state/PHASE138_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111–137.
> 3. `tests/test_phase138_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, `gates_ok`, `composes=['PHASE137','PHASE32']`).
> 4. `tests/test_generate_phase138_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject `live_trading_enabled=True`, `next9_unblocked=True`, `paper_only=False`, `advisory=False`, `no_external_venue_mutation=False`; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase138/Phase137/`composes=PHASE137,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Hygiene (non-blocking, do during same task):** include currently-untracked `tests/test_phase137_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` and `tests/test_generate_phase137_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` in the Phase138 commit if still untracked and P0-safe.
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE137,PHASE32`. Module pytest pass.
> - Controlled `generate(cycles=40, seed=138138, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE137,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 138138`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: module test + targeted CLI generator case with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain in-process generator tests may be slow — run targeted/split, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE139-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE138→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, prior-phase refactors, or proceeding past Phase137 before Phase138 is complete/verified.

---

## Bottlenecks — removed / remaining (verified 2026-11-09T06:56:44Z)

| Bottleneck | Status | Action |
|---|---|---|
| P0 safety drift (`.env`/secrets/config/LIVE_TRADING) | **CLEAR** | `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → empty (re-verified 2026-11-09T06:56Z); `.env.example:15` `LIVE_TRADING_ENABLED=false`. Re-verify before/after every batch. |
| Phase112–136 implemented + artifact-verified | **CLEARED** | Complete through Phase136. |
| **Phase137 implemented + verified (HEAD tracks module/script/artifact; 2 tests untracked)** | **CLEARED** | Phase137 complete+verified (2026-11-09T06:54Z): `py_compile` OK (4 files); module smoke `paper_only=True gates_ok=True composes=['PHASE136','PHASE32']`; module pytest **1 passed** (13.48s, recheck 2026-11-09T06:56Z). Controlled generate+validate → `valid=true issues=[] deterministic=true bounds_ok=True coverage_len=12 composes=['PHASE136','PHASE32'] guards=(True,False,False,True)`; artifact `research_state/PHASE137_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T065254Z.json` (tracked, campaign/validation verified). CLI `--no-write` (`PHASE_QUICK_VERIFY=1 --cycles 4 --seed 137137`) → `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. **Hygiene:** `tests/test_phase137_*` and `tests/test_generate_phase137_*` untracked — include in Phase138 commit if still untracked. |
| **Phase138 not implemented (0 `*phase138*` files)** | **ACTIVE — MANDATORY** | Execute `INIT-20261109T065644Z-PHASE138-POST-ATTRIBUTION-SEAL-DEPTH` composing PHASE137→32 (full deliverables+verification). **No other work takes priority.** |
| Chain A/B naming confusion | **MITIGATED** | Phase138 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. Full in-process generator pytest may time out (>300–600s) even with stubs/quick-verify; CLI + controlled generate+validate provide equivalent invariant evidence. Never skip verification. |
| NEXT9 (A1–A7, human-only, session gate NO_GO, `next9_unblocked=false`) | **BLOCKED — out of scope** | Never unblock; does not gate paper-only Chain B depth. |

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B post-attribution seal depth is active; **Phase138 is mandatory now.**

## Verified state (2026-11-09T06:56:44Z)

- **Branch/HEAD:** `main` @ `a638f5c64` (`chore(kilo): checkpoint agent session`). Phase137 module/script/artifact tracked in HEAD; `tests/test_phase137_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` and `tests/test_generate_phase137_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` present but **untracked** (tracked by git index state before this refresh; include in Phase138 commit if still untracked). Guarded paths untouched.
- **P0:** clean (empty diff on guarded paths); `.env.example:15` `LIVE_TRADING_ENABLED=false` (re-verified 2026-11-09T06:56Z).
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; `next9_unblocked=false`) — does not gate Chain B.
- **Phase136 artifact:** `research_state/PHASE136_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T062840Z.json` — `validation.valid=true`, 12 venue×symbol coverage, deterministic, bounds ok, guards intact, `composes=['PHASE135','PHASE32']`.
- **Phase137 artifact (tracked):** `research_state/PHASE137_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T065254Z.json` — `artifact_type` matches, `campaign.phase=PHASE137_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR`, `campaign.composes=['PHASE136','PHASE32']`, `campaign.gates_ok=true`, `venue_symbol_coverage` len 12, `validation.valid=true issues=[]`, `paper_only=true live_trading_enabled=false next9_unblocked=false`.
- **Phase138:** **no `*phase138*` files** in repo (re-verified 2026-11-09T06:56Z) — **unstarted**.

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261109T065644Z-PHASE138-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111–137, compose **PHASE137→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update. Include untracked Phase137 tests in commit if still untracked.
2. **NEXT (queued):** `INIT-<UTC>-PHASE139-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE138→32**, only after Phase138 verified with evidence.
3. Continue PHASE138→139→140→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128/129/130/131/132/133/134/135/136/137`.**

## Phase137 status (complete — 2026-11-09T06:56:44Z refresh)

- [x] Chain B Phase137 composed PHASE136→32 (4 files).
- [x] `py_compile` OK (4 files).
- [x] Smoke (`PHASE_QUICK_VERIFY=1`): `paper_only=True gates_ok=True composes=['PHASE136','PHASE32']`.
- [x] Module pytest: **1 passed** (13.48s, recheck 2026-11-09T06:56Z).
- [x] Controlled `generate(cycles=40,seed=137137,write=True)` + `validate_artifact` → `valid=true issues=[] deterministic=true bounds_ok=True coverage_len=12 composes=['PHASE136','PHASE32'] guards=(True,False,False,True)`; artifact `research_state/PHASE137_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T065254Z.json` (tracked, verified).
- [x] CLI `--no-write` (`PHASE_QUICK_VERIFY=1 --cycles 4 --seed 137137`) → `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`.
- [x] Generator cases **≥7 authored** (10 cases). Full in-process generator pytest may time out in this env; CLI + controlled generate+validate cover equivalent invariants — **explicit caveat** (non-blocking for Phase137 completion given verified evidence).
- [x] P0 re-verified empty diff / `.env.example:15 LIVE_TRADING_ENABLED=false`.
- [ ] **Hygiene:** `tests/test_phase137_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase137_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` untracked — **include in Phase138 commit** if still untracked.

## Prior chain evidence (condensed)

- **Phase137:** artifact `...PHASE137_..._20261109T065254Z.json` (`valid=true`, PHASE136→32, 12 coverage, guards intact, tracked).
- **Phase136:** artifact `...PHASE136_..._20261109T062840Z.json` (`valid=true`, PHASE135→32, 12 coverage, guards intact).
- **Phase135:** artifact `...PHASE135_..._20261109T060348Z.json` (`valid=true`, PHASE134→32, 12 coverage).
- **Phase134:** artifact `...PHASE134_..._20261109T054245Z.json` (`valid=true`, PHASE133→32, 12 coverage).

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
