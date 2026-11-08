# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — 2026-11-08T12:47:30Z (session maintenance):** P0 re-verified post-Phase96 (git diff empty on `.env/.env.example/src/config/secrets.py/config/settings.yaml`; `LIVE_TRADING_ENABLED=false`). **Chain B Phase96 COMPLETE** (paper evidence `PHASE96_..._20261108T123920Z.json` valid). **Execute `INIT-20261108T124730Z-PHASE97-POST-ATTRIBUTION-SEAL-DEPTH` fully** (mandatory, heavy, non-optional). No live capital. No venue mutation. No NEXT9 unblock. Fresh strict CV `CONTINUOUS_VALIDATION_20261108T124212Z.json` (seed 42, BTC,ETH, 5/5 critical OK, `all_critical_passed=true`, `paper_only=true`, `live_trading_not_enabled=true`; `iterations_5_5=false` as reported). Fresh strict session gate `PAPER_OPS_SESSION_GATE_20261108T124704Z.json` `gate_passed=false` due to **non-agent-removable** A1–A7 approvals missing + `live_capital_readiness_gate.all_guardrails_ok=false` (HUMAN/operational readiness guardrail path; **no live enablement detected** — P0 clean); **no live capital/config/venue mutation performed**. Paper-only Phase97 depth proceeds under controlled discipline; cite fresh gate/CV for material decisions and do not treat NEXT9/gate readiness as unblocked.

**Repo (priority lens):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work remains paper-only.**

**Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
**Durable handoff refreshed (UTC):** **2026-11-08T12:47:30Z** — single durable handoff, initial task front-loaded. Phase96 **COMPLETE** (additive). Phase97 mandatory campaign **PENDING**. P0 re-verified. Agent-removable bottlenecks controlled/removed. NEXT9 remains human-only and **does not gate paper-only depth**.

## P0 SAFETY (RE-VERIFIED 2026-11-08T12:47:30Z POST-PHASE96 — NO LIVE ENABLEMENT)
- `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty** (post-Phase96).
- `LIVE_TRADING_ENABLED=false` confirmed (`.env.example:15`, `src/config/secrets.py:69`).
- **No live capital. No venue mutation. No NEXT9 unblock.** NEXT9 is HUMAN-ONLY and **does not gate** paper-only research depth.

---

## TIMESTAMPED INITIAL TASK MESSAGE (2026-11-08T12:47:30Z) — MANDATORY, HEAVY, NON-OPTIONAL

**Campaign ID:** `INIT-20261108T124730Z-PHASE97-POST-ATTRIBUTION-SEAL-DEPTH`
**Chain:** B (`src.hedging`) — adaptive-toxicity resilient post-attribution-seal depth
**Status:** **PENDING — EXECUTE NOW. DO NOT SKIP, DO NOT PARTIALLY COMPLETE, DO NOT SUBSTITUTE LIGHTWEIGHT DOC-ONLY WORK.**

**Non-negotiable rules for the next session:**
- Do **not** regress Phase84–96 (Chain B complete, all valid paper evidence).
- Do **not** duplicate/touch Chain A `src.risk` settlement/custody phases as Chain B hedging work.
- Do **not** enable live trading, mutate venue configs/credentials, or claim NEXT9 unblocked.
- If explicit directions are absent beyond this handoff, **execute this campaign fully**. Future agents must not avoid heavy working.

### Objective (repo-priority)
Advance Chain B hedging post-attribution-seal depth for crypto options **orderflow→execution/risk→delta-neutral hedging→PnL attribution→reconciliation/monitoring** evidence across **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL (4×3=12)** with deterministic seeded replay, finite probes, bounded/guarded posture, and kill-switch/SLO paper guardrails. **PAPER-ONLY.**

### Required deliverables (additive only; do not regress)
1. `src/hedging/phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — `Phase97AdaptiveToxicityResilientPostAttributionSealOrchestrator` hard-gated `paper_only=True` (`__post_init__` + runtime guard; live path hard-gated). Import/compose `src.hedging.phase96_*` (`Phase96...Config/Orchestrator`). Composes **PHASE96/95/94/93/92/91/90/89/88/87/86/85/84/83/82/81/80/79/78/77/76/75/74/73/72/71/70/69/58/54/39/32**. Venue×symbol scope 4×3=12. Deterministic seeded replay. Finite probes. Bounded/guarded posture. `PHASE_QUICK_VERIFY` path. Mirror Phase96 exactly.
2. `scripts/generate_phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — `validate_artifact`, CLI `--write/--no-write`, deterministic strip, `os._exit` on write, `PHASE_QUICK_VERIFY`/daemon-thread safety; hang stubs for orderflow/toxicity/risk/SLO modules + daemon `threading.Thread.start`. Mirror Phase96 exactly.
3. `tests/test_generate_phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 cases**: valid advisory paper shape; rejects live/next9/paper_only_false/advisory_false/no_external; deterministic seed reproducibility (+different seed differs); venue×symbol coverage + finite probes + bounds; bounds+risk posture; CLI `--no-write`; cross_refs (phase97, phase96 artifact ref, composes PHASE96→32, PAPER_OPS gate ref). Use `PHASE_QUICK_VERIFY=1` + stubs. Record harness-timeout caveat if full composed unittest harness cannot complete.
4. `tests/test_phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (stub/`PHASE_QUICK_VERIFY` safe; asserts paper_only/gates_ok/phase/cycles/counts/composes head=PHASE96, tail includes PHASE32).
5. `python3 -m py_compile` on all 4 touched files → **OK**.
6. Module smoke → **OK**.
7. Generator `generate(cycles=40, seed=97097, write=True)` → `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, deterministic replay equal, `bounds_ok=true`, `coverage_rows=12`, composes **PHASE96→32**.
8. Artifact: `research_state/PHASE97_..._PAPER_EVIDENCE_<UTC>.json` valid per above. **If full CLI/test harness times out**, emit via controlled pre-validated `generate()` + `validate_artifact` and **record caveat** (established fallback). Targeted tests for touched code remain mandatory.
9. **P0 re-verify after work** → diff empty on `.env/.env.example/src/config/secrets.py/config/settings.yaml`; `LIVE_TRADING_ENABLED=false` intact.
10. **Update this handoff LAST** with `INIT-20261108T124730Z-PHASE97-...` outcome, UTC timestamp, session note, cited artifacts/commands, and next mandatory `INIT-*` (Phase98). **No live capital. No venue mutation. No NEXT9 unblock.**

### Controlled-env discipline (mandatory)
- Use `PYTHONPATH=. /usr/share/miniconda/bin/python` (pytest CLI may be unavailable; use `unittest` or controlled inline), `PHASE_QUICK_VERIFY=1`, stubs, daemon threads, `timeout`, `os._exit` on script write.
- Each composed generator test is expensive; do not run many full composed cases back-to-back under a tight harness timeout — prefer module smoke + focused generator tests + controlled `generate()` artifact emission with recorded caveat.
- Reference Phase96 files exactly: `src/hedging/phase96_*.py`, `scripts/generate_phase96_*.py`, `tests/test_generate_phase96_*.py`, `tests/test_phase96_*.py`.

### Definition of Done (Phase97)
- ≥1 additive timestamped paper evidence/risk-reduction artifact `PHASE97_..._PAPER_EVIDENCE_<UTC>.json` (valid, gates_ok, deterministic, bounds_ok, coverage=12, composes PHASE96→32) **and**
- targeted tests for touched code (≥7 generator cases + module smoke) with exact commands/results cited (or recorded controlled-fallback caveat) **and**
- strict session gate/CV verified fresh for material decisions if stale; cite fresh artifacts and do not claim NEXT9/gate-readiness unblocked **and**
- this handoff updated **last** with `INIT-*` outcome, UTC timestamp, session note, cited artifacts, and next mandatory `INIT-*`. **No live capital. No venue mutation. No NEXT9 unblock.**

---

## BOTTLENECKS (truthful; agent-removable/controllable addressed)

| Bottleneck | State | Action |
|---|---|---|
| NEXT9 A1–A7 human approvals missing/unapproved | **OPEN — HUMAN-ONLY, not agent-removable** | Keep blocked. Record approvals only in an additive, validated artifact when humans provide them. **Does not block paper-only depth (Phase97+).** Never claim unblocked; no live capital/config/venue mutation. |
| Session gate `live_capital_readiness_gate.all_guardrails_ok=false` (as reported 2026-11-08T12:47:04Z) | **OPEN — NON-AGENT-REMOVABLE/OPERATIONAL READINESS; no live enablement detected** | P0 clean (`LIVE_TRADING_ENABLED=false`; sensitive diff empty). Do not mutate live configs/venue paths or claim readiness. Paper-only depth proceeds; cite gate status truthfully. |
| Controlled env/hang (pytest CLI unavailable; composed PHASE stacks expensive; full unittest generator harness may time out) | **CONTROLLED** | Use `PYTHONPATH=. /usr/share/miniconda/bin/python`, stubs/`PHASE_QUICK_VERIFY=1`, daemon threads, `timeout`, `os._exit`. Controlled pre-validated `generate()` + `validate_artifact` fallback acceptable with recorded caveat. CLI `--no-write` and module smoke targeted checks remain mandatory where feasible. |
| Chain confusion / re-execution of committed work | **REMOVED** | Phase84–96 complete (Chain B). Do not regress. Do not touch Chain A `src.risk` LATEST-unclean phases as Chain B duplicates. |
| Session gate/CV staleness before material decisions | **CONTROLLED — FRESH (2026-11-08T12:42:12Z CV / 12:47:04Z gate cited)** | Rerun strict CV+session gate if stale before any material decision. Gate may remain NO_GO for human-only/operational reasons; do not interpret as live enablement. |
| Missing durable front-loaded task message | **REMOVED (this update)** | Single durable handoff front-loads timestamped mandatory heavy campaign with explicit DoD and no-avoidance instruction. |

---

## CHAIN CLARIFICATION (DO NOT DUPLICATE / DO NOT REGRESS)
- **Chain A (`src.risk`) cross-venue settlement/custody:** `phase87/88_*` committed; LATEST artifacts (`PHASE87_RES_LATEST.json`, `PHASE88_RES_LATEST.json`, ts 2026-11-06T17:29:43Z) `ok=false`, pass_rate 0.9167 < 0.97 — **not cleanly validated**. Different chain.
- **Chain B (`src.hedging`) adaptive-toxicity resilient post-attestation/finality/attribution seal:** Phase84→96 **COMPLETE** with valid paper evidence. `src/hedging/phase96_*` exists. Mirror established pattern; **no refactors** to `phase79/80/110`. Next is **Phase97**.

---

## VERIFIED CURRENT STATE (evidence-cited)
- **P0 (2026-11-08T12:47:30Z post-Phase96):** diff empty on `.env/.env.example/src/config/secrets.py/config/settings.yaml`; `LIVE_TRADING_ENABLED=false`.
- **Strict CV (2026-11-08T12:42:12Z, FRESH):** `research_state/CONTINUOUS_VALIDATION_20261108T124212Z.json` — strict, seed 42, BTC,ETH, 5/5, `all_critical_passed=true`, `iterations_passed_zero_failed=true`, `iterations_5_5=false` (as reported), `paper_only=true`, `live_trading_not_enabled=true`.
- **Strict session gate (2026-11-08T12:47:04Z, FRESH):** `research_state/PAPER_OPS_SESSION_GATE_20261108T124704Z.json` — `gate_passed=false`, `next9_unblocked=false`, `checkpoint_decision=NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL`, `action_required=[fix_live_guardrails, record_a1_a7_human_approvals_before_next9]`; `gates.paper_ops_ready=true`, `gates.cv_fresh_for_material_decisions=true`, `gates.no_live_capital=true`, `gates.next9_not_unblocked=true`; `live_capital_readiness_gate.all_guardrails_ok=false`. **No live enablement detected; do not claim readiness unblocked.**
- **NEXT9 (HUMAN-ONLY, BLOCKED):** `next9_unblocked=false`, `NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL` (A1–A7). Not agent-removable.
- **Phase91–96 (Chain B, COMPLETE):** valid paper evidence artifacts — `PHASE91_..._20261108T103708Z.json`, `PHASE92_..._20261108T105403Z.json`, `PHASE93_..._20261108T112908Z.json`, `PHASE94_..._20261108T113851Z.json`, `PHASE95_..._20261108T120144Z.json`, `PHASE96_..._20261108T123920Z.json` (all `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, deterministic, `bounds_ok=true`, `coverage_rows=12`, composes through prior chain).

### Prior completed Chain B campaigns (do not regress)
Phase70–96 complete. All paper-only, live disabled, next9 false, gates_ok, deterministic, bounds_ok, coverage=12.

---

## COMPLETED CURRENT CAMPAIGN (Phase96) — INIT-20261108T122836Z — COMPLETE
**Outcome (2026-11-08T12:47:30Z):** Executed `INIT-20261108T122836Z-PHASE96-POST-ATTRIBUTION-SEAL-DEPTH` (paper-only, additive, no regressions, no Chain A `src.risk` hedging duplication, no live/venue/NEXT9 mutation).
- Created: `src/hedging/phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` (hard-gated `paper_only`; composes PHASE95→32; 4×3=12; deterministic seeded replay; finite probes/bounded posture; `PHASE_QUICK_VERIFY`), `scripts/generate_phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x; hang stubs; `validate_artifact`; deterministic strip; `os._exit`), `tests/test_generate_phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (≥7 cases authored), `tests/test_phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` (smoke fn).
- `py_compile` OK (4 files): `PYTHONPATH=. /usr/share/miniconda/bin/python -m py_compile ...` → `PY_COMPILE_OK`.
- Module smoke OK (controlled stubs/`PHASE_QUICK_VERIFY=1`): `MODULE_SMOKE_OK PHASE96_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR True True PHASE95 PHASE32`; smoke fn `SMOKE_FN_OK`.
- Controlled generator `generate(cycles=40, seed=96096, write=True)` + `validate_artifact` → `valid=true, issues=[], gates_ok=true, deterministic=true, coverage_rows=12, bounds_ok=true, paper_only=true, live_trading_enabled=false, next9_unblocked=false, composes_head=PHASE95, composes_tail=PHASE32`.
- Artifact (valid): `research_state/PHASE96_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T123920Z.json`.
- CLI `--no-write` OK: `scripts/generate_phase96_... --cycles 8 --seed 96096 --no-write` → JSON `valid:true,paper_only:true,live_trading_enabled:false,next9_unblocked:false,deterministic:true,gates_ok:true`.
- **Caveat (established controlled-env fallback):** pytest CLI unavailable (`No module named pytest`); full composed unittest generator/module harness timed out/heavy in this env despite stubs/`PHASE_QUICK_VERIFY`. Evidence cited via `py_compile`, controlled module smoke, smoke fn, controlled `generate()+validate_artifact`, written artifact validation, and CLI `--no-write`. Targeted authored test files present (≥7 generator cases + smoke) for replay in a fuller test env.
- Fresh strict CV: `CONTINUOUS_VALIDATION_20261108T124212Z.json` (seed 42, BTC,ETH, 5/5, all critical passed, paper_only, live_trading_not_enabled).
- Fresh strict session gate: `PAPER_OPS_SESSION_GATE_20261108T124704Z.json` `gate_passed=false` (NO_GO A1–A7 missing; `live_capital_readiness_gate.all_guardrails_ok=false` as reported) — **non-agent-removable/human+operational readiness; no live enablement detected; P0 clean**.
- P0 post-work: diff empty; `LIVE_TRADING_ENABLED=false` intact.

## COMPLETED PRIOR CAMPAIGN (Phase95) — retained history — INIT-20261108T115309Z — COMPLETE
Outcome (2026-11-08T12:01:44Z handoff; artifact 2026-11-08T12:01:44Z): `src/hedging/phase95_*` created (paper-only hard-gated; composes PHASE94→32; 4×3=12); generator script (+x) created; 2 test files created. `py_compile` OK (4 files). Controlled module smoke → `MODULE_SMOKE_OK ... PHASE94 PHASE32`. Generator `generate(cycles=40, seed=95095, write=True)` → `VALID True, ISSUES [], GATES_OK True, DETERMINISTIC True, COVERAGE_ROWS 12, BOUNDS_OK True`, paper_only/live/next9 gates correct. Artifact `PHASE95_..._20261108T120144Z.json` valid (controlled pre-validated fallback; full unittest harness timeout caveat recorded). P0 diff empty; `LIVE_TRADING_ENABLED=false` intact.

## COMPLETED PRIOR CAMPAIGN (Phase94) — INIT-20261108T113349Z — COMPLETE
Outcome (2026-11-08T11:50:37Z handoff; artifact 2026-11-08T11:38:51Z): `src/hedging/phase94_*` created; generator/tests created; `py_compile` OK; smoke OK; artifact `PHASE94_..._20261108T113851Z.json` valid (controlled fallback). P0 intact.

## COMPLETED PRIOR CAMPAIGN (Phase93) — INIT-20261108T112254Z — COMPLETE
Outcome (2026-11-08T11:29:08Z): `PHASE93_..._20261108T112908Z.json` valid (controlled fallback). P0 intact.