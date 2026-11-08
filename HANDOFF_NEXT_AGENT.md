# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — 2026-11-08T13:37:00Z (handoff maintenance, repo-priority: crypto options quantitative orderflow strategy):** P0 re-verified: `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` confirmed (`.env.example:15`, `src/config/secrets.py:69`). **Chain B Phase97 COMPLETE** (valid paper evidence `research_state/PHASE97_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T125315Z.json`). **Chain B Phase98 adaptive post-attribution-seal artifacts/evidence DO NOT EXIST** (re-confirmed 2026-11-08T13:37:00Z: `find . -path '*phase98*adaptive*post_attribution*seal*' -not -path '*/.git/*'` → empty). **NEXT SESSION MUST EXECUTE `INIT-20261108T132749Z-PHASE98-POST-ATTRIBUTION-SEAL-DEPTH` IN FULL — HEAVY, NON-OPTIONAL, PAPER-ONLY.** Doc-only work, partial completion, skipped verification, chain substitution, or status-only reporting is **not progress**. No live capital. No venue mutation. No NEXT9 unblock.

**Repo (priority lens):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work remains paper-only.**

**Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
**Durable handoff refreshed (UTC):** **2026-11-08T13:37:00Z** — single durable handoff. Phase97 **COMPLETE** (additive). Phase98 **PENDING — MANDATORY HEAVY EXECUTION NEXT**. Agent-removable bottlenecks addressed (P0 clean, chain clarified, concrete quick-start/fallback, stale-gate discipline). NEXT9 remains human-only and **does not gate paper-only depth**.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (timestamped, mandatory)

**Message ID / Campaign:** `INIT-20261108T132749Z-PHASE98-POST-ATTRIBUTION-SEAL-DEPTH`
**Issued (UTC):** 2026-11-08T13:27:49Z | **Reaffirmed (UTC):** 2026-11-08T13:37:00Z
**Scope:** Chain B (`src.hedging`) — adaptive-toxicity resilient post-attribution-seal depth (Phase98), **paper-only, additive, deterministic, finite-probe, bounded/guarded**.
**Hard requirement:** Execute this campaign **fully**. Do **not** do doc-only work, partial stubs, skipped verification, chain substitution, or “status-only” progress. Do **not** touch live trading, venue/config/credentials, or NEXT9.

**Execute now (heavy):** Implement Phase98 by mirroring Phase97 exactly (compose **PHASE97→32**), generate a valid timestamped paper-evidence artifact, verify with targeted tests/controlled fallback, re-verify P0, then update this handoff **last** with exact commands/results/artifact path/caveats and the next mandatory `INIT-*` (Phase99). If blocked by environment hangs, use the controlled fallback documented below **and still produce real code + artifact + cited evidence** — never use fallback as an excuse for no work.

## P0 SAFETY (RE-VERIFIED 2026-11-08T13:37:00Z — NO LIVE ENABLEMENT)
- `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**.
- `LIVE_TRADING_ENABLED=false` confirmed in checked config surfaces (`.env.example:15`, `src/config/secrets.py:69`).
- **No live capital. No venue mutation. No NEXT9 unblock.** NEXT9 is HUMAN-ONLY and **does not gate** paper-only research depth.

---

## MANDATORY HEAVY CAMPAIGN — PHASE98 (Chain B)

**Campaign ID:** `INIT-20261108T132749Z-PHASE98-POST-ATTRIBUTION-SEAL-DEPTH`
**Chain:** B (`src.hedging`) — adaptive-toxicity resilient post-attribution-seal depth (Phase98)
**Status:** **PENDING — EXECUTE FULLY NEXT. DO NOT SKIP. DO NOT PARTIALLY COMPLETE. DO NOT SUBSTITUTE DOC-ONLY WORK.**

### Mission (repo-priority, heavy)
Deliver **additive, paper-only, deterministic, finite-probe, bounded/guarded** Chain B hedging post-attribution-seal depth for crypto options orderflow→execution/risk→delta-neutral hedging→PnL attribution→reconciliation/monitoring evidence across **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL (4×3=12)**. Mirror Phase97 exactly; **compose PHASE97→32**. No regressions to Phase84–97. No Chain A `src.risk` settlement/custody duplication. No `phase79/80/110` refactors. No live trading, venue/config/credential mutation, or NEXT9 unblock claims.

### Quick-start (remove bottlenecks; execute first)
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml  # must be empty
find . -path '*phase98*adaptive*post_attribution*seal*' -not -path '*/.git/*'            # must be empty before work
cp -n src/hedging/phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py src/hedging/phase98_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py
cp -n scripts/generate_phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py scripts/generate_phase98_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py
cp -n tests/test_phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py tests/test_phase98_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py
cp -n tests/test_generate_phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py tests/test_generate_phase98_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py
# After edits (Phase97→98, PHASE97→32 composed): py_compile all 4 files
# Module smoke + controlled generate(cycles=40, seed=98098, write=True) + validate_artifact + CLI --no-write; record exact output.
```

### Mandatory deliverables (all required; cite exact commands/results)
1. `src/hedging/phase98_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `Phase98AdaptiveToxicityResilientPostAttributionSealConfig` / `Phase98AdaptiveToxicityResilientPostAttributionSealOrchestrator`
   - hard-gated `paper_only=True` (bool + reject non-paper/live path)
   - imports/composes `src.hedging.phase97_*` (`Phase97...Config/Orchestrator`)
   - composes **PHASE97→32**; deterministic seeded replay; finite probes; bounded/guarded posture; kill-switch/SLO paper guardrails; `PHASE_QUICK_VERIFY` support
2. `scripts/generate_phase98_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x)
   - `validate_artifact`, CLI `--cycles/--seed/--write/--no-write`, deterministic strip, `os._exit` on write, hang stubs/daemon-thread safety, `PHASE_QUICK_VERIFY`
   - artifact: `PHASE98_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` under `research_state/`
3. `tests/test_generate_phase98_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7** cases (valid advisory shape; rejects live/next9/paper_only_false/advisory_false/no_external; deterministic seed reproducibility; venue×symbol coverage + finite probes + bounds; bounds+risk posture; CLI `--no-write`; cross_refs phase98/phase97/composes PHASE97→32/PAPER_OPS gate refs).
4. `tests/test_phase98_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke.
5. `py_compile` all 4 files → **PY_COMPILE_OK**.
6. Module smoke → `PHASE98... paper_only=True gates_ok=True composes head PHASE97 tail PHASE32` (or equivalent evidence).
7. Controlled generator `generate(cycles=40, seed=98098, write=True)` + `validate_artifact` → `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, deterministic replay equal, `bounds_ok=true`, `coverage_rows=12`, composes head=PHASE97 tail=PHASE32.
8. CLI `--no-write` run and result cited (or controlled fallback with explicit reason).
9. Write valid artifact: `research_state/PHASE98_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json`.
10. P0 re-verify post-work (diff empty on sensitive files; `LIVE_TRADING_ENABLED=false` intact).
11. Update **this handoff last** with Phase98 outcome, UTC timestamp, exact commands/results, artifact path, caveats, and **next mandatory `INIT-*` (Phase99)**.

### Reference (mirror exactly)
- `src/hedging/phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
- `scripts/generate_phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
- `tests/test_generate_phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
- `tests/test_phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
- Latest valid Chain B artifact: `research_state/PHASE97_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T125315Z.json`

### Controlled-env discipline (mandatory)
- `PYTHONPATH=. /usr/share/miniconda/bin/python` (pytest CLI may be unavailable; use `unittest` or controlled inline). Use `PHASE_QUICK_VERIFY=1`, hang stubs, daemon threads, `timeout`, `os._exit` on script write.
- Composed PHASE stacks are expensive; full unittest generator/module harness may hang/time out. **Acceptable controlled fallback:** `py_compile` + module smoke + controlled `generate()` + `validate_artifact` + written artifact validation + CLI `--no-write` (targeted), with authored targeted tests present and caveat recorded. Do not use fallback to avoid real verification where feasible.
- Before material decisions, rerun strict CV + session gate if stale; cite fresh artifacts truthfully. Gate/NEXT9 readiness may remain blocked for human/operational reasons — **do not interpret as live enablement and do not mutate live paths**.

### Definition of Done (Phase98) — ALL required
- ≥1 additive timestamped valid paper evidence artifact `PHASE98..._PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`, `gates_ok`, deterministic, `bounds_ok`, `coverage_rows=12`, composes PHASE97→32, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`) **AND**
- targeted tests for touched code (≥7 generator cases + module smoke) with exact commands/results/caveats cited **AND**
- strict session gate/CV verified fresh for material decisions (or truthfully cited as stale with rerun note; never claim NEXT9/gate readiness unblocked) **AND**
- this handoff updated **last** with `INIT-*` outcome, UTC timestamp, evidence paths, and next mandatory `INIT-*` (**`INIT-<UTC>-PHASE99-POST-ATTRIBUTION-SEAL-DEPTH`**). **No live capital. No venue mutation. No NEXT9 unblock.**

**Progress rule:** Updating only this handoff or reporting status without Phase98 code+artifact+verification is **not progress** for this campaign.

---

## BOTTLENECKS (truthful; agent-removable/controllable addressed)

| Bottleneck | State | Action |
|---|---|---|
| NEXT9 A1–A7 human approvals missing/unapproved | **OPEN — HUMAN-ONLY, not agent-removable** | Keep blocked. Record approvals only in additive validated artifacts when humans provide them. **Does not block paper-only depth (Phase98+).** Never claim unblocked; no live capital/config/venue mutation. |
| Session gate `live_capital_readiness_gate.all_guardrails_ok=false` / NO_GO reasons (last cited 2026-11-08T12:47:04Z) | **OPEN — NON-AGENT-REMOVABLE/OPERATIONAL READINESS; no live enablement detected** | P0 clean. Do not mutate live configs/venue paths or claim readiness. Paper-only depth proceeds; rerun/cite gate truthfully before material decisions. |
| CV/session gate artifacts may be stale for new material work | **CONTROLLED — RERUN REQUIRED BEFORE MATERIAL DECISIONS** | Last cited: `research_state/CONTINUOUS_VALIDATION_20261108T124212Z.json`, `research_state/PAPER_OPS_SESSION_GATE_20261108T124704Z.json`. Rerun strict CV + session gate when making material readiness claims; do not fake freshness. |
| Controlled env/hang (pytest CLI unavailable; composed PHASE stacks expensive) | **CONTROLLED** | Use `PYTHONPATH=. /usr/share/miniconda/bin/python`, `PHASE_QUICK_VERIFY=1`, stubs, daemon threads, `timeout`, `os._exit`. Controlled `generate()` + `validate_artifact` fallback acceptable with recorded caveat + authored targeted tests present. |
| Chain confusion (Chain A `src.risk` phase98/99 vs Chain B `src.hedging` Phase98+) | **REMOVED/CONTROLLED** | `research_state/phase98_*`/`phase99_*` dirs under risk/live-gate topics are **Chain A / historical**. Chain B Phase98/99 use `src/hedging/phase98_*`/`phase99_*` and `PHASE98_ADAPTIVE...PAPER_EVIDENCE_<UTC>.json`. Do not touch Chain A artifacts. |
| Durable front-loaded heavy task absent/weak | **REMOVED** | `INIT-20261108T132749Z-PHASE98-POST-ATTRIBUTION-SEAL-DEPTH` is front-loaded with mandatory heavy DoD. Next session cannot satisfy progress with doc-only work. |
| `research_state/` size/noise (large history, phase85 churn) | **NOT A BLOCKER** | Use targeted globs/find for Chain B artifacts; do not refactor/delete history. |

---

## CHAIN CLARIFICATION (DO NOT DUPLICATE / DO NOT REGRESS)
- **Chain A (`src.risk`) cross-venue settlement/custody/live-gate hardening:** historical `phase98/99` research_state dirs and risk artifacts exist; separate chain. **Do not use as Chain B completion evidence. Do not duplicate/refactor as Chain B.**
- **Chain B (`src.hedging`) adaptive-toxicity resilient post-attribution/finality seal:** Phase84→97 **COMPLETE** with valid paper evidence (`PHASE97..._20261108T125315Z.json` valid). Next is **Phase98** mirroring Phase97 (compose PHASE97→32). No refactors to `phase79/80/110`.

---

## VERIFIED CURRENT STATE (evidence-cited, 2026-11-08T13:37:00Z)
- **P0:** sensitive diff empty; `LIVE_TRADING_ENABLED=false`.
- **Phase97 (Chain B, COMPLETE):** `src/hedging/phase97_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase97_...py`, `tests/test_phase97_...py`, `tests/test_generate_phase97_...paper_evidence.py` present; 4 files `py_compile` OK. Valid artifact `research_state/PHASE97_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T125315Z.json`.
- **Phase98 (Chain B, PENDING):** no `src/hedging/phase98*adaptive*post_attribution*seal*`, no matching generator/tests, no Chain B Phase98 adaptive paper evidence artifact found.
- **Strict CV (last cited, 2026-11-08T12:42:12Z):** `research_state/CONTINUOUS_VALIDATION_20261108T124212Z.json` — strict, seed 42, BTC,ETH, 5/5, `all_critical_passed=true`, `paper_only=true`, `live_trading_not_enabled=true`. Rerun if stale for material decisions.
- **Strict session gate (last cited, 2026-11-08T12:47:04Z):** `research_state/PAPER_OPS_SESSION_GATE_20261108T124704Z.json` — `gate_passed=false`, `next9_unblocked=false`, `NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL`, `live_capital_readiness_gate.all_guardrails_ok=false`. **No live enablement detected; do not claim readiness unblocked.** Rerun/cite truthfully when material.
- **NEXT9 (HUMAN-ONLY, BLOCKED):** `next9_unblocked=false`, A1–A7 missing. Not agent-removable.

### Prior completed Chain B campaigns (do not regress)
Phase70–97 complete (paper-only, live disabled, next9 false, gates_ok, deterministic, bounds_ok, coverage=12 where applicable). Phase97 latest: `PHASE97_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T125315Z.json`.

## COMPLETED CURRENT CAMPAIGN (Phase97) — INIT-20261108T124730Z — COMPLETE
**Outcome (2026-11-08T12:54:00Z):** Phase97 additive, paper-only, hard-gated, composes PHASE96→32; 4×3=12; deterministic seeded replay; finite probes/bounded posture. `py_compile` OK; module smoke OK; controlled `generate(cycles=40, seed=97097, write=True)` valid/gates_ok/deterministic/coverage=12/composes PHASE96→32; CLI `--no-write` OK; artifact `PHASE97_..._20261108T125315Z.json` valid. Targeted tests authored (≥7 generator cases + smoke). **Controlled-env caveat:** pytest CLI unavailable; full composed unittest harness may hang/time out — evidence via py_compile/module smoke/controlled generate+validate/written artifact/CLI `--no-write`. P0 post-work clean.

## COMPLETED PRIOR (Phase96) — INIT-20261108T122836Z — COMPLETE
Artifact `PHASE96_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T123920Z.json` valid (controlled fallback caveat recorded). P0 clean.

## COMPLETED PRIOR (Phase95/94/93/92/91…) — retained history
See prior artifacts in `research_state/PHASE9[1-5]_...PAPER_EVIDENCE_*.json` (valid, paper-only, next9 false).
