# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority lens):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work remains paper-only.**

**Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
**Durable handoff refreshed (UTC):** **2026-11-08T12:27:22Z** — initial task message front-loaded; Phase96 mandatory campaign confirmed; P0 re-verified; bottlenecks controlled/recorded.

## P0 SAFETY (RE-VERIFIED, NO LIVE ENABLEMENT)
- `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty** (2026-11-08T12:03:41Z).
- `LIVE_TRADING_ENABLED=false` confirmed (`.env.example:15`, `src/config/secrets.py:69`).
- **No live capital. No venue mutation. No NEXT9 unblock.** NEXT9 is HUMAN-ONLY and **does not gate** paper-only research depth.

---

## TIMESTAMPED INITIAL TASK MESSAGE (2026-11-08T12:26:54Z) — MANDATORY, HEAVY, NON-OPTIONAL

**Campaign ID:** `INIT-20261108T120341Z-PHASE96-POST-ATTRIBUTION-SEAL-DEPTH`
**Chain:** B (`src.hedging`) — adaptive-toxicity resilient post-attribution-seal depth
**Status:** **PENDING — EXECUTE NOW.** Future agents must not avoid this work, must not regress Phase84–95, and must not duplicate Chain A `src.risk` settlement/custody phases as Chain B hedging work.

### Objective (repo-priority)
Advance Chain B hedging post-attribution-seal depth for crypto options **orderflow→execution/risk→delta-neutral hedging→PnL attribution→reconciliation/monitoring** evidence across **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL (4×3=12)** with deterministic seeded replay, finite probes, bounded/guarded posture, and kill-switch/SLO paper guardrails. **PAPER-ONLY.**

### Required deliverables (additive only; do not regress)
1. `src/hedging/phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — `Phase96AdaptiveToxicityResilientPostAttributionSealOrchestrator` hard-gated `paper_only=True` (`__post_init__` + runtime guard; live path hard-gated). Import/compose `src.hedging.phase95_*` (`Phase95...Config/Orchestrator`). Composes **PHASE95/94/93/92/91/90/89/88/87/86/85/84/83/82/81/80/79/78/77/76/75/74/73/72/71/70/69/58/54/39/32**. Venue×symbol scope 4×3=12. Deterministic seeded replay. Finite probes. Bounded/guarded posture. `PHASE_QUICK_VERIFY` path.
2. `scripts/generate_phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — `validate_artifact`, CLI `--write/--no-write`, deterministic strip, `os._exit` on write, `PHASE_QUICK_VERIFY`/daemon-thread safety; hang stubs for orderflow/toxicity/risk/SLO modules + daemon `threading.Thread.start` (mirror Phase95 exactly).
3. `tests/test_generate_phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 cases**: valid advisory paper shape; rejects live/next9/paper_only_false/advisory_false/no_external; deterministic seed reproducibility (+different seed differs); venue×symbol coverage + finite probes + bounds; bounds+risk posture; CLI `--no-write` (record harness-timeout caveat if needed); cross_refs (phase96, phase95 artifact ref, composes PHASE95→32, PAPER_OPS gate ref). Use `PHASE_QUICK_VERIFY=1` + stubs.
4. `tests/test_phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (stub/`PHASE_QUICK_VERIFY` safe; asserts paper_only/gates_ok/phase/cycles/counts/composes head=PHASE95, tail includes PHASE32).
5. `python3 -m py_compile` on all 4 touched files → **OK**.
6. Module smoke → **OK**.
7. Generator `generate(cycles=40, seed=96096, write=True)` → `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, deterministic replay equal, `bounds_ok=true`, `coverage_rows=12`, composes **PHASE95→32**.
8. Artifact: `research_state/PHASE96_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` valid per above. **If full CLI/test harness times out** (composed stack expensive), emit via controlled pre-validated `generate()` + `validate_artifact` and **record caveat** (established Phase91–95 fallback). Targeted tests for touched code remain mandatory.
9. **P0 re-verify after work** → diff empty on `.env/.env.example/src/config/secrets.py/config/settings.yaml`; `LIVE_TRADING_ENABLED=false` intact.
10. **Update this handoff LAST** with `INIT-20261108T120341Z-PHASE96-...` outcome, UTC timestamp, session note, cited artifacts/commands, and next mandatory `INIT-*` (Phase97). **No live capital. No venue mutation. No NEXT9 unblock.**

### Controlled-env discipline (mandatory)
- Use `PYTHONPATH=. /usr/share/miniconda/bin/python` (pytest CLI may be unavailable; use `unittest` or controlled inline), `PHASE_QUICK_VERIFY=1`, stubs, daemon threads, `timeout`, `os._exit` on script write.
- Each composed generator test is expensive; do not run many full composed cases back-to-back under a tight harness timeout — prefer module smoke + focused generator tests + controlled `generate()` artifact emission with recorded caveat.

### Definition of Done (Phase96)
- ≥1 additive timestamped paper evidence/risk-reduction artifact `PHASE96_..._PAPER_EVIDENCE_<UTC>.json` (valid, gates_ok, deterministic, bounds_ok, coverage=12, composes PHASE95→32) **and**
- targeted tests for touched code (≥7 generator cases + module smoke) with exact commands/results cited (or recorded controlled-fallback caveat) **and**
- strict session gate verified fresh for material decisions if stale (`gate_passed=true`, `next9_unblocked=false`, `gates.cv_fresh_for_material_decisions=true`) **and**
- this handoff updated **last** with `INIT-*` outcome, UTC timestamp, session note, cited artifacts, and next mandatory `INIT-*`. **No live capital. No venue mutation. No NEXT9 unblock.**

---

## BOTTLENECKS (truthful; agent-removable/controllable addressed)

| Bottleneck | State | Action |
|---|---|---|
| NEXT9 A1–A7 human approvals missing/unapproved | **OPEN — HUMAN-ONLY, not agent-removable** | Keep blocked. Record approvals only in an additive, validated artifact when humans provide them. **Does not block paper-only depth (Phase96+).** Never claim unblocked; no live capital/config/venue mutation. |
| Controlled env/hang (pytest CLI unavailable; composed PHASE stacks expensive) | **CONTROLLED** | Use `PYTHONPATH=. /usr/share/miniconda/bin/python`, stubs/`PHASE_QUICK_VERIFY=1`, daemon threads, `timeout`, `os._exit`. Controlled pre-validated `generate()` + `validate_artifact` fallback acceptable with recorded caveat. |
| Chain confusion / re-execution of committed work | **REMOVED** | Phase84–95 complete (Chain B). Do not regress. Do not touch Chain A `src.risk` LATEST-unclean phases as Chain B duplicates. |
| Session gate/CV staleness before material decisions | **CONTROLLED — RERUN IF STALE** | Gate/CV cited below were fresh at 2026-11-08T10:02Z. Phase96 is paper-only depth; **rerun strict CV+session gate if >2h stale or not fresh before material decisions** and cite new artifacts. |

---

## CHAIN CLARIFICATION (DO NOT DUPLICATE / DO NOT REGRESS)
- **Chain A (`src.risk`) cross-venue settlement/custody:** `phase87/88_*` committed; LATEST artifacts (`PHASE87_RES_LATEST.json`, `PHASE88_RES_LATEST.json`, ts 2026-11-06T17:29:43Z) `ok=false`, pass_rate 0.9167 < 0.97 — **not cleanly validated**. Different chain.
- **Chain B (`src.hedging`) adaptive-toxicity resilient post-attestation/finality/attribution seal:** Phase84→95 **COMPLETE** with valid paper evidence. `src/hedging/phase95_*` exists. Mirror established pattern; **no refactors** to `phase79/80/110`. Next is **Phase96**.

---

## VERIFIED CURRENT STATE (evidence-cited)
- **P0:** diff empty on `.env/.env.example/src/config/secrets.py/config/settings.yaml`; `LIVE_TRADING_ENABLED=false` (2026-11-08T12:03:41Z).
- **Strict session gate (2026-11-08T10:02:37Z, FRESH then):** `research_state/PAPER_OPS_SESSION_GATE_20261108T100237Z.json` — `gate_passed=true`, `gates.cv_fresh_for_material_decisions=true`, `gates.no_live_capital=true`, `gates.next9_not_unblocked=true`, `gates.paper_ops_ready=true`, `next9_unblocked=false`, `checkpoint_decision=NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL` (A1–A7), `action_required=[record_a1_a7_human_approvals_before_next9]`. **Rerun if stale before material decisions.**
- **Strict CV (2026-11-08T10:02:13Z, FRESH then):** `research_state/CONTINUOUS_VALIDATION_20261108T100213Z.json` — strict, seed 42, BTC,ETH, 5/5, all critical passed, paper_only, live_trading_not_enabled.
- **NEXT9 (HUMAN-ONLY, BLOCKED):** `next9_unblocked=false`, `NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL` (A1–A7). Not agent-removable.
- **Phase91–95 (Chain B, COMPLETE):** valid paper evidence artifacts — `PHASE91_..._20261108T103708Z.json`, `PHASE92_..._20261108T105403Z.json`, `PHASE93_..._20261108T112908Z.json`, `PHASE94_..._20261108T113851Z.json`, `PHASE95_..._20261108T120144Z.json` (all `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, deterministic, `bounds_ok=true`, `coverage_rows=12`, composes through prior chain).

### Prior completed Chain B campaigns (do not regress)
Phase70–95 complete. All paper-only, live disabled, next9 false, gates_ok, deterministic, bounds_ok, coverage=12.

---

## COMPLETED PRIOR CAMPAIGN (Phase95) — INIT-20261108T115309Z — COMPLETE
Outcome (2026-11-08T12:01:44Z handoff; artifact 2026-11-08T12:01:44Z): `src/hedging/phase95_*` created (paper-only hard-gated; composes PHASE94→32; 4×3=12); generator script (+x) created; 2 test files created. `py_compile` OK (4 files). Controlled module smoke → `MODULE_SMOKE_OK ... PHASE94 PHASE32`. Generator `generate(cycles=40, seed=95095, write=True)` → `VALID True, ISSUES [], GATES_OK True, DETERMINISTIC True, COVERAGE_ROWS 12, BOUNDS_OK True`, paper_only/live/next9 gates correct. Artifact `PHASE95_..._20261108T120144Z.json` valid (controlled pre-validated fallback; full unittest harness timeout caveat recorded). P0 diff empty; `LIVE_TRADING_ENABLED=false` intact.

## COMPLETED PRIOR CAMPAIGN (Phase94) — INIT-20261108T113349Z — COMPLETE
Outcome (2026-11-08T11:50:37Z handoff; artifact 2026-11-08T11:38:51Z): `src/hedging/phase94_*` created; generator/tests created; `py_compile` OK; smoke OK; artifact `PHASE94_..._20261108T113851Z.json` valid (controlled fallback). P0 intact.
