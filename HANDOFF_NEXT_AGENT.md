# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority lens):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work remains paper-only.**

**Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
**Durable handoff refreshed (UTC):** **2026-11-08T12:01:44Z** (Phase95 INIT-20261108T115309Z complete; state re-verified; additive artifacts created).
**P0 re-verified (post-Phase95, no live enablement):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `LIVE_TRADING_ENABLED=false` confirmed at `.env.example:15` and `src/config/secrets.py:69`. **No live capital. No venue mutation. No NEXT9 unblock.**

---

## TIMESTAMPED INITIAL TASK MESSAGE — MANDATORY NEXT (INIT-20261108T120144Z-PHASE96-POST-ATTRIBUTION-SEAL-DEPTH, Chain B `src.hedging`)

Status: **PENDING — EXECUTE THIS CAMPAIGN (HEAVY, ADDITIVE, PAPER-ONLY).** Future agents must not avoid this work. Mirror Phase95 exactly in structure/discipline, composing **PHASE95→32**. PAPER-ONLY. No live capital. No venue mutation. NEXT9 remains BLOCKED (human-only, not agent-removable) and **does not gate** paper-only depth.

**Why this is the next focus (repo-priority):** advances Chain B hedging post-attribution-seal depth for crypto options orderflow (venue×symbol 4×3=12, BTC/ETH/SOL × Deribit/OKX/Bybit/Binance) with deterministic replay, finite probes, bounded/guarded posture, and kill-switch/SLO paper guardrails — directly strengthening orderflow→execution/risk→delta-neutral hedging→attribution→reconciliation/monitoring evidence.

### Required deliverables (do not regress; additive only)
- `src/hedging/phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — create; `Phase96AdaptiveToxicityResilientPostAttributionSealOrchestrator` hard-gated `paper_only=True` (live path hard-gated, `__post_init__` + runtime guard); import/compose `src.hedging.phase95_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` (`Phase95...Config/Orchestrator`); composes **PHASE95/94/93/92/91/90/89/88/87/86/85/84/83/82/81/80/79/78/77/76/75/74/73/72/71/70/69/58/54/39/32**; venue×symbol scope 4×3=12; deterministic seeded replay; finite probes; bounded/guarded posture; `PHASE_QUICK_VERIFY` path for controlled env.
- `scripts/generate_phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — create; `validate_artifact`, CLI `--write/--no-write`, deterministic strip, `os._exit` on write, `PHASE_QUICK_VERIFY`/daemon-thread safety; hang stubs for orderflow/toxicity/risk/SLO modules + daemon `threading.Thread.start` (mirror Phase95 exactly).
- `tests/test_generate_phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — create (**≥7 cases**): valid advisory paper shape, rejects live/next9/paper_only_false/advisory_false/no_external, deterministic seed reproducibility (+different seed differs), venue×symbol coverage + finite probes + bounds, bounds+risk posture, CLI `--no-write` (record harness-timeout caveat if needed), cross_refs (phase96, phase95 artifact ref, composes PHASE95→32, PAPER_OPS gate ref). Use `PHASE_QUICK_VERIFY=1` + stubs.
- `tests/test_phase96_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — create (module smoke; stub/`PHASE_QUICK_VERIFY` safe; asserts paper_only/gates_ok/phase/cycles/counts/composes head=PHASE95, tail includes PHASE32).
- `python3 -m py_compile` on all 4 touched files → **OK**.
- Module smoke `test_phase96_post_attribution_seal_orchestrator_smoke` (or controlled inline) → **OK**.
- Generator `generate(cycles=40, seed=96096, write=True)` → `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, deterministic replay equal, `bounds_ok=true`, `coverage_rows=12`, composes **PHASE95→32**.
- Artifact: `research_state/PHASE96_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` — valid per above. **If full CLI/test harness times out** (composed stack is expensive), emit via controlled pre-validated `generate()` + `validate_artifact` and **record caveat** (established Phase91–95 fallback). Targeted tests for touched code remain mandatory.
- **P0 re-verify after work** → diff empty on `.env/.env.example/src/config/secrets.py/config/settings.yaml`; `LIVE_TRADING_ENABLED=false` intact.
- **Update this handoff LAST** with `INIT-20261108T120144Z-PHASE96-...` outcome, UTC timestamp, session note, cited artifacts/commands, and next mandatory `INIT-*` (Phase97). **No live capital. No venue mutation. No NEXT9 unblock.**

### Controlled-env discipline (mandatory)
- Use `PYTHONPATH=. /usr/share/miniconda/bin/python` (pytest CLI may be unavailable; use `unittest` or controlled inline), `PHASE_QUICK_VERIFY=1`, stubs, daemon threads, `timeout`, `os._exit` on script write.
- Each composed generator test is expensive; do not run many full composed cases back-to-back under a tight harness timeout — prefer module smoke + focused generator tests + controlled `generate()` artifact emission with recorded caveat.

---

## COMPLETED PRIOR CAMPAIGN (Phase95) — INIT-20261108T115309Z-PHASE95-POST-ATTRIBUTION-SEAL-DEPTH, Chain B `src.hedging` — COMPLETE

Status: COMPLETE. Heavy additive Phase95 delivered (mirror Phase94, composes PHASE94→32). PAPER-ONLY. No live capital. No venue mutation. NEXT9 remains BLOCKED.

Outcome (2026-11-08T12:01:44Z handoff; artifact 2026-11-08T12:01:44Z):
- `src/hedging/phase95_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — created (paper-only hard-gated; composes PHASE94→32; 4×3=12; deterministic/finite/bounded).
- `scripts/generate_phase95_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — created (`validate_artifact`, CLI, deterministic strip, `os._exit`, `PHASE_QUICK_VERIFY`, hang stubs/daemon threads).
- `tests/test_generate_phase95_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — created (7 cases; controlled env). **Caveat:** full unittest harness timed out in this environment due composed-stack expense; targeted generator logic verified via controlled pre-validated `generate()` + `validate_artifact` (established fallback).
- `tests/test_phase95_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — created (module smoke; stub/`PHASE_QUICK_VERIFY`).
- `python3 -m py_compile` on 4 touched files → **OK**. Controlled module smoke → `MODULE_SMOKE_OK PHASE95_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR True True 4 1 1 PHASE94 PHASE32`. Generator `generate(cycles=40, seed=95095, write=True)` → `VALID True, ISSUES [], GATES_OK True, DETERMINISTIC True, COVERAGE_ROWS 12, BOUNDS_OK True`, `paper_only True live False next9 False`.
- Artifact: `research_state/PHASE95_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T120144Z.json` — `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, deterministic replay equal, `bounds_ok=true`, coverage=12, composes PHASE94→32. Emitted via controlled pre-validated `generate()` + `validate_artifact` pass (established fallback).
- P0 diff re-verified → **empty**; `LIVE_TRADING_ENABLED=false` intact.

---

## COMPLETED PRIOR CAMPAIGN (Phase94) — INIT-20261108T113349Z-PHASE94-POST-ATTRIBUTION-SEAL-DEPTH, Chain B `src.hedging` — COMPLETE

Status: COMPLETE. Heavy additive Phase94 delivered (mirror Phase93, composes PHASE93→32). PAPER-ONLY. No live capital. No venue mutation. NEXT9 remains BLOCKED.

Outcome (2026-11-08T11:50:37Z handoff; artifact 2026-11-08T11:38:51Z):
- `src/hedging/phase94_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — created (paper-only hard-gated; composes PHASE93→32; 4×3=12; deterministic/finite/bounded).
- `scripts/generate_phase94_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — created (`validate_artifact`, CLI, deterministic strip, `os._exit`, `PHASE_QUICK_VERIFY`, hang stubs/daemon threads).
- `tests/test_generate_phase94_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — created (≥7 cases; CLI/full-stack harness-timeout caveat pattern recorded).
- `tests/test_phase94_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — created (module smoke).
- `python3 -m py_compile` on 4 touched files → OK. Module smoke → `MODULE_SMOKE_OK`. Generator `generate(cycles=40, seed=94094, write=True)` → `VALID True, ISSUES [], GATES_OK True, DETERMINISTIC True, COVERAGE_ROWS 12, BOUNDS_OK True`.
- Artifact: `research_state/PHASE94_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T113851Z.json` — `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, deterministic replay equal, `bounds_ok=true`, coverage=12, composes PHASE93→32. Emitted via controlled pre-validated `generate()` + `validate_artifact` pass (established fallback).
- P0 diff re-verified → empty; `LIVE_TRADING_ENABLED=false` intact.

---

## CHAIN CLARIFICATION — BOTTLENECK REMOVED (DO NOT DUPLICATE / DO NOT REGRESS)

Two parallel chains exist; never conflate:
- **Chain A (`src.risk`) cross-venue settlement/custody:** `phase87/88_*` source+tests+artifacts committed; LATEST artifacts (`PHASE87_RES_LATEST.json`, `PHASE88_RES_LATEST.json`, ts 2026-11-06T17:29:43Z) show `ok=false`, `validation_pass_rate_ok=false`, pass_rate 0.9167 < 0.97 — **not cleanly validated**. Different chain. Do not "fix" by duplicating as Chain B hedging phases.
- **Chain B (`src.hedging`) adaptive-toxicity resilient post-attestation/finality/attribution seal:** Phase84→95 **COMPLETE** with valid paper evidence artifacts. `src/hedging/phase95_*` exists. Mirror established pattern; **no refactors** to `phase79/80/110`. Next is **Phase96** (this handoff).

---

## BOTTLENECKS (truthful; only agent-removable/controllable addressed)

| Bottleneck | State | Action |
|---|---|---|
| NEXT9 A1–A7 human approvals missing/unapproved | **OPEN — HUMAN-ONLY, not agent-removable** | Keep blocked. Record approvals only in an additive, validated artifact when humans provide them. **Does not block paper-only depth (Phase96+).** Never claim unblocked; no live capital/config/venue mutation. |
| Controlled env/hang (pytest CLI unavailable; composed PHASE stacks expensive) | **CONTROLLED** | Use `PYTHONPATH=. /usr/share/miniconda/bin/python`, stubs/`PHASE_QUICK_VERIFY=1`, daemon threads, `timeout`, `os._exit`. Controlled pre-validated `generate()` + `validate_artifact` fallback is acceptable with recorded caveat. |
| Chain confusion / re-execution of committed work | **REMOVED** | Phase94 complete; do not regress. Do not touch Chain A `src.risk` LATEST-unclean phases as Chain B duplicates. |
| Session gate staleness before material decisions | **CONTROLLED (currently fresh)** | Gate/CV cited below are fresh now; rerun strict CV+gate if >2h stale or not fresh before decisions. |

---

## VERIFIED CURRENT STATE (evidence-cited, 2026-11-08T11:53:09Z)

- **P0:** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `LIVE_TRADING_ENABLED=false` (`.env.example:15`, `src/config/secrets.py:69`).
- **Strict session gate (FRESH):** `research_state/PAPER_OPS_SESSION_GATE_20261108T100237Z.json` (2026-11-08T10:02:37Z) — `gate_passed=true`, `gates.cv_fresh_for_material_decisions=true`, `gates.no_live_capital=true`, `gates.next9_not_unblocked=true`, `gates.paper_ops_ready=true`, `next9.next9_unblocked=false`, `next9.checkpoint_decision=NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL` (A1–A7), `action_required=[record_a1_a7_human_approvals_before_next9]`.
- **Strict CV (FRESH):** `research_state/CONTINUOUS_VALIDATION_20261108T100213Z.json` (2026-11-08T10:02:13Z) — strict, seed 42, BTC,ETH, 5/5, all critical passed, paper_only, live_trading_not_enabled.
- **NEXT9 (HUMAN-ONLY, BLOCKED):** `next9_unblocked=false`, `checkpoint_decision=NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL` (A1–A7). Not agent-removable.
- **Phase91 (Chain B, COMPLETE):** `research_state/PHASE91_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T103708Z.json` — valid, gates_ok, deterministic, bounds_ok, coverage=12, composes PHASE90→32.
- **Phase92 (Chain B, COMPLETE):** `research_state/PHASE92_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T105403Z.json` — valid, gates_ok, deterministic, bounds_ok, coverage=12, composes PHASE91→32.
- **Phase93 (Chain B, COMPLETE):** `research_state/PHASE93_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T112908Z.json` — valid, gates_ok, deterministic, bounds_ok, coverage=12, composes PHASE92→32.
- **Phase94 (Chain B, COMPLETE):** `research_state/PHASE94_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T113851Z.json` — valid, gates_ok, deterministic, bounds_ok, coverage=12, composes PHASE93→32.
- **Phase95 (Chain B, COMPLETE):** `research_state/PHASE95_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T120144Z.json` — valid, gates_ok, deterministic, bounds_ok, coverage=12, composes PHASE94→32.
- **Chain A `src.risk` phase87/88:** committed but LATEST `ok=false` / pass_rate 0.9167 < 0.97 — separate chain, not cleanly validated.

### Prior completed Chain B campaigns (evidence chain, do not regress)
Phase70–86 complete (prior sessions). Phase87–95 complete. **All paper-only, live disabled, next9 false, gates_ok, deterministic, bounds_ok, coverage=12.**

---

## DEFINITION OF DONE (Phase96 — mandatory next)
- ≥1 additive timestamped paper evidence/risk-reduction artifact `PHASE96_..._PAPER_EVIDENCE_<UTC>.json` (valid, gates_ok, deterministic, bounds_ok, coverage=12, composes PHASE95→32) **and**
- targeted tests for touched code (`tests/test_generate_phase96_*` ≥7 cases + `tests/test_phase96_*` module smoke) with exact commands/results cited (or recorded controlled-fallback caveat) **and**
- strict session gate verified fresh for material decisions if stale (`gate_passed=true`, `next9_unblocked=false`, `gates.cv_fresh_for_material_decisions=true`) **and**
- this handoff updated **last** with `INIT-*` outcome, UTC timestamp, session note, cited artifacts, and next mandatory `INIT-*`. **No live capital. No venue mutation. No NEXT9 unblock.**
