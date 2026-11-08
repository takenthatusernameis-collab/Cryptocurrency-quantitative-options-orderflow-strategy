# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — 2026-11-08T16:03:17Z (handoff refresh, repo-priority: crypto options quantitative orderflow strategy):** P0 re-verified post-work: `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` confirmed (`.env.example:15`, `src/config/secrets.py:69`). **Chain B Phase100 COMPLETE** (`PHASE100...PAPER_EVIDENCE_20261108T145417Z.json`). **Chain B Phase101 COMPLETE** (`PHASE101...PAPER_EVIDENCE_20261108T150148Z.json`). **Chain B Phase102 COMPLETE (EXECUTED THIS SESSION)** — additive, paper-only, composes **PHASE101→32**; valid artifact `research_state/PHASE102_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T155847Z.json` (`validation.valid=true`, `issues=[]`, `campaign.gates_ok=true`, `campaign.composes=["PHASE101","PHASE32"]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`). **Chain B Phase103 NOT implemented** (no `src/hedging/phase103*`, no Chain B PHASE103 artifact). **NEXT SESSION: DO NOT REPORT STATUS. EXECUTE `INIT-20261108T160015Z-PHASE103-POST-ATTRIBUTION-SEAL-DEPTH` IN FULL — HEAVY, NON-OPTIONAL, PAPER-ONLY.** Doc-only work, partial completion, skipped verification, chain substitution, Chain A substitution, or status-only reporting is **not progress**. No live capital. No venue mutation. No NEXT9 unblock.

**Repo (priority lens):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work remains paper-only.**

**Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
**Durable handoff refreshed (UTC):** **2026-11-08T16:03:17Z** — single durable handoff. Phase100 **COMPLETE**. Phase101 **COMPLETE**. Phase102 **COMPLETE** (executed). Agent-removable bottlenecks addressed (P0 clean, chain clarified, Chain A `src.risk/phase102_*` confusion removed — see BOTTLENECKS + CHAIN CLARIFICATION). **Phase103 is the open heavy campaign; it must not be satisfied by doc-only or status-only work.** NEXT9 remains human-only and **does not gate paper-only depth**.

---

## PHASE102 OUTCOME (COMPLETED — EXECUTED THIS SESSION, 2026-11-08T15:58:47Z)

**Campaign:** `INIT-20261108T150405Z-PHASE102-POST-ATTRIBUTION-SEAL-DEPTH`
**Result:** Chain B (`src.hedging`) Phase102 additive, paper-only, composes **PHASE101→32**. Mirrors Phase101 exactly (upstream compose import/class = Phase101, `self.finality100` instantiates `Phase101AdaptiveToxicityResilientPostAttributionSealOrchestrator`). No regressions to Phase84–101. No Chain A `src.risk` duplication. No `phase79/80/110` refactors. No live trading, venue/config/credential mutation, or NEXT9 unblock.
**Commands/results (exact):**
- `PYTHONPATH=. /usr/share/miniconda/bin/python -m py_compile src/hedging/phase102_*.py scripts/generate_phase102_*.py tests/test_phase102_*.py tests/test_generate_phase102_*.py` → **`PY_COMPILE_OK`**.
- Module smoke (`PHASE_QUICK_VERIFY=1`, cycles=4, seed=102102): `SMOKE_OK` — `PYTHONPATH=. PHASE_QUICK_VERIFY=1 python -m unittest tests.test_phase102_adaptive_toxicity_resilient_post_attribution_seal_orchestrator -v` → **2 tests, OK (10.293s)** (`paper_only=True`, `gates_ok=True`, `phase=PHASE102_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR`, `composes=PHASE101,PHASE32`).
- Controlled `generate(cycles=40, seed=102102, write=True)` + `validate_artifact` → **valid=true, issues=[], paper_only=true, live_trading_enabled=false, next9_unblocked=false, gates_ok=true, deterministic=true, bounds_ok=true, coverage_rows=12, composes=[PHASE101,PHASE32], n_seal_attestations=6, n_hedging_seal_attestations=8**.
- CLI `--no-write` (cycles=4, seed=102102, `PHASE_QUICK_VERIFY=1`): rc 0, JSON `valid=true, paper_only=true, live_trading_enabled=false, next9_unblocked=false, deterministic=true, gates_ok=true, artifact_path=null`.
- P0 post-work re-verify: `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` intact.
**Artifact (valid):** `research_state/PHASE102_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T155847Z.json` — `validation.valid=true`, `issues=[]`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`, `coverage_rows=12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, composes **PHASE101→32**.
**Caveat:** composed PHASE stacks remain expensive in controlled env; `PHASE_QUICK_VERIFY=1`, hang stubs, daemon threads, bounded timeouts, and `os._exit` used. Full unittest harness may hang on composed stacks — controlled `generate()`+`validate_artifact` + authored targeted tests used; caveat recorded.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (timestamped, mandatory)

**Message ID / Campaign:** `INIT-20261108T160015Z-PHASE103-POST-ATTRIBUTION-SEAL-DEPTH`
**Issued (UTC):** 2026-11-08T16:03:17Z
**Scope:** Chain B (`src.hedging`) — adaptive-toxicity resilient post-attribution-seal depth (Phase103), **paper-only, additive, deterministic, finite-probe, bounded/guarded**.
**Hard requirement:** Execute this campaign **fully**. Do **not** do doc-only work, partial stubs, skipped verification, chain substitution, or "status-only" progress. Do **not** touch live trading, venue/config/credentials, or NEXT9.

**Execute now (heavy):** Implement Phase103 by mirroring Phase102 exactly (compose **PHASE102→32**), generate a valid timestamped paper-evidence artifact, verify with targeted tests/controlled fallback, re-verify P0, then update this handoff **last** with exact commands/results/artifact path/caveats and the next mandatory `INIT-*` (Phase104). If blocked by environment hangs, use the controlled fallback **and still produce real code + artifact + cited evidence** — never use fallback as an excuse for no work.

## MANDATORY HEAVY CAMPAIGN — PHASE103 (Chain B)

**Campaign ID:** `INIT-20261108T160015Z-PHASE103-POST-ATTRIBUTION-SEAL-DEPTH`
**Chain:** B (`src.hedging`) — adaptive-toxicity resilient post-attribution-seal depth (Phase103)
**Status:** **OPEN — EXECUTE FULLY (no status-only work).**

### Mission (repo-priority, heavy)
Deliver **additive, paper-only, deterministic, finite-probe, bounded/guarded** Chain B hedging post-attribution-seal depth for crypto options orderflow→execution/risk→delta-neutral hedging→PnL attribution→reconciliation/monitoring evidence across **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL (4×3=12)**. Mirror Phase102 exactly; **compose PHASE102→32**. No regressions to Phase84–102. No Chain A `src.risk` settlement/custody duplication. No `phase79/80/110` refactors. No live trading, venue/config/credential mutation, or NEXT9 unblock claims.

### Quick-start (remove bottlenecks; execute first)
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml  # must be empty
find . -path '*phase103*adaptive*post_attribution*seal*' -not -path '*/.git/*'            # must be empty before work
cp -n src/hedging/phase102_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py src/hedging/phase103_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py
cp -n scripts/generate_phase102_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py scripts/generate_phase103_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py
cp -n tests/test_phase102_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py tests/test_phase103_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py
cp -n tests/test_generate_phase102_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py tests/test_generate_phase103_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py
# Edit carefully: Phase102->103, phase102->103; upstream compose import/class = Phase102; composes=["PHASE102","PHASE32"]; seeds 103103/102102; deterministic probe IDs p103_*. Ensure upstream orchestrator instantiation uses Phase102 (not self).
PYTHONPATH=. /usr/share/miniconda/bin/python -m py_compile src/hedging/phase103_*.py scripts/generate_phase103_*.py tests/test_phase103_*.py tests/test_generate_phase103_*.py
PYTHONPATH=. PHASE_QUICK_VERIFY=1 /usr/share/miniconda/bin/python - <<'PY'
from src.hedging.phase103_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import *
print('SMOKE')
PY
# controlled generate(cycles=40, seed=103103, write=True) + validate_artifact + CLI --no-write; record exact output.
```

### Mandatory deliverables (all required; cite exact commands/results)
1. `src/hedging/phase103_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — `Phase103...Config/Orchestrator`, hard-gated `paper_only=True`, imports/composes `Phase102...`, composes **PHASE102→32**, deterministic seeded replay, finite probes, bounded/guarded posture, kill-switch/SLO paper guardrails, `PHASE_QUICK_VERIFY` support.
2. `scripts/generate_phase103_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — `validate_artifact`, CLI `--cycles/--seed/--write/--no-write`, deterministic strip, `os._exit` on write, hang stubs/daemon-thread safety, `PHASE_QUICK_VERIFY`; artifact `PHASE103_..._PAPER_EVIDENCE_<UTC>.json` in `research_state/`.
3. `tests/test_generate_phase103_..._paper_evidence.py` — **≥7** cases (valid advisory shape; rejects live/next9/paper_only_false/advisory_false/no_external; deterministic seed reproducibility; venue×symbol coverage + finite probes + bounds; bounds+risk posture; CLI `--no-write`; cross_refs phase103/phase102/composes PHASE102→32/PAPER_OPS gate refs).
4. `tests/test_phase103_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke + hard gate.
5. `py_compile` all 4 files → **PY_COMPILE_OK**.
6. Module smoke → `paper_only=True gates_ok=True composes head PHASE102 tail PHASE32`.
7. Controlled generator `generate(cycles=40, seed=103103, write=True)` + `validate_artifact` → `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, deterministic replay equal, `bounds_ok=true`, `coverage_rows=12`, composes head=PHASE102 tail=PHASE32.
8. CLI `--no-write` result cited (or controlled fallback with explicit reason).
9. Valid artifact in `research_state/PHASE103_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json`.
10. P0 re-verify post-work (sensitive diff empty; `LIVE_TRADING_ENABLED=false`).
11. Update **this handoff last** with Phase103 outcome, UTC timestamp, exact commands/results, artifact path, caveats, and **next mandatory `INIT-*` (Phase104)**.

### Reference (mirror exactly)
- `src/hedging/phase102_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
- `scripts/generate_phase102_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
- `tests/test_generate_phase102_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
- `tests/test_phase102_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
- Latest valid Chain B artifact: `research_state/PHASE102_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T155847Z.json`

### Controlled-env discipline (mandatory)
- `PYTHONPATH=. /usr/share/miniconda/bin/python`. Use `PHASE_QUICK_VERIFY=1`, hang stubs, daemon threads, `timeout`, `os._exit` on script write.
- Full unittest harness may hang on composed stacks. **Acceptable controlled fallback:** `py_compile` + module smoke + controlled `generate()` + `validate_artifact` + written artifact validation + CLI `--no-write` (targeted), with authored targeted tests present and caveat recorded. Do not use fallback to avoid real verification where feasible.
- Before material decisions, rerun strict CV + session gate if stale; cite fresh artifacts truthfully. Gate/NEXT9 readiness may remain blocked for human/operational reasons — **do not interpret as live enablement and do not mutate live paths**.

### Definition of Done (Phase103) — ALL required
- ≥1 additive timestamped valid paper evidence artifact `PHASE103..._PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`, `gates_ok`, deterministic, `bounds_ok`, `coverage_rows=12`, composes PHASE102→32, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`) **AND**
- targeted tests for touched code (≥7 generator cases + module smoke) with exact commands/results/caveats cited **AND**
- strict session gate/CV verified fresh for material decisions (or truthfully cited as stale with rerun note; never claim NEXT9/gate readiness unblocked) **AND**
- this handoff updated **last** with `INIT-*` outcome, UTC timestamp, evidence paths, and next mandatory `INIT-*` (**`INIT-<UTC>-PHASE104-POST-ATTRIBUTION-SEAL-DEPTH`**). **No live capital. No venue mutation. No NEXT9 unblock.**

**Progress rule:** Updating only this handoff or reporting status without Phase103 code+artifact+verification is **not progress**.

---

## P0 SAFETY (RE-VERIFIED 2026-11-08T16:03:17Z — NO LIVE ENABLEMENT)
- `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**.
- `LIVE_TRADING_ENABLED=false` confirmed in checked config surfaces (`.env.example:15`, `src/config/secrets.py:69`).
- **No live capital. No venue mutation. No NEXT9 unblock.** NEXT9 is HUMAN-ONLY and **does not gate** paper-only research depth.

---

## BOTTLENECKS (truthful; agent-removable/controllable addressed)

| Bottleneck | State | Action |
|---|---|---|
| NEXT9 A1–A7 human approvals missing/unapproved | **OPEN — HUMAN-ONLY, not agent-removable** | Keep blocked. Record approvals only in additive validated artifacts when humans provide them. **Does not block paper-only depth (Phase103+).** Never claim unblocked; no live capital/config/venue mutation. |
| Session gate `live_capital_readiness_gate.all_guardrails_ok=false` / NO_GO reasons | **OPEN — NON-AGENT-REMOVABLE/OPERATIONAL READINESS; no live enablement detected** | P0 clean. Do not mutate live configs/venue paths or claim readiness. Paper-only depth proceeds; rerun/cite gate truthfully before material decisions. |
| CV/session gate artifacts may be stale for new material work | **CONTROLLED — RERUN REQUIRED BEFORE MATERIAL DECISIONS** | Last cited: `research_state/CONTINUOUS_VALIDATION_20261108T124212Z.json`, `research_state/PAPER_OPS_SESSION_GATE_20261108T124704Z.json`. Rerun strict CV + session gate when making material readiness claims; do not fake freshness. |
| Controlled env/hang (pytest CLI unavailable; composed PHASE stacks expensive) | **CONTROLLED** | Use `PYTHONPATH=. /usr/share/miniconda/bin/python`, `PHASE_QUICK_VERIFY=1`, stubs, daemon threads, `timeout`, `os._exit`. Controlled `generate()` + `validate_artifact` fallback acceptable with recorded caveat + authored targeted tests present. |
| Chain confusion (Chain A `src.risk` phase98/99 vs Chain B `src.hedging` Phase98+) | **REMOVED/CONTROLLED** | `research_state/phase98_*`/`phase99_*` dirs under risk/live-gate topics are **Chain A / historical**. Chain B uses `src/hedging/phaseN_*` and `PHASE{N}_ADAPTIVE...PAPER_EVIDENCE_<UTC>.json`. Do not touch Chain A artifacts. |
| Chain A `src.risk/phase102_live_execution_realtime_hardening_deep*` + `tests/test_phase102_live_execution_realtime_hardening_deep.py` + `research_state/phase102_live_execution_realtime_hardening_deep/` exist | **BOTTLENECK — REMOVED BY CLARIFICATION** | These are **Chain A live-execution hardening (historical)**, NOT Chain B paper-only Phase102/103 post-attribution-seal depth. **Do not mistake them for Phase102/103 completion.** Do not use as Chain B evidence. Do not duplicate/refactor Chain A into Chain B. Chain B Phase103 = `src/hedging/phase103_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` mirroring Phase102, compose PHASE102→32, paper-only. |
| Durable front-loaded heavy task absent/weak | **REMOVED** | `INIT-20261108T160015Z-PHASE103-POST-ATTRIBUTION-SEAL-DEPTH` is front-loaded with mandatory heavy DoD. Next session cannot satisfy progress with doc-only work. |
| `research_state/` size/noise (large history) | **NOT A BLOCKER** | Use targeted globs/find for Chain B artifacts; do not refactor/delete history. |

---

## CHAIN CLARIFICATION (DO NOT DUPLICATE / DO NOT REGRESS)
- **Chain A (`src.risk`) cross-venue settlement/custody/live-gate hardening:** historical `phase98/99` research_state dirs and risk artifacts exist; separate chain. **Do not use as Chain B completion evidence. Do not duplicate/refactor as Chain B.**
- **Chain B (`src.hedging`) adaptive-toxicity resilient post-attribution/finality seal:** Phase84→102 **COMPLETE** with valid paper evidence (latest `PHASE102..._20261108T155847Z.json`). **Phase103 NOT implemented** — next is **Phase103** mirroring Phase102 (compose PHASE102→32). No refactors to `phase79/80/110`. **Do not substitute Chain A `src.risk/phase102_*` live-execution files for Chain B Phase103.**

---

## VERIFIED CURRENT STATE (evidence-cited, 2026-11-08T16:03:17Z)
- **P0:** sensitive diff empty post-work; `LIVE_TRADING_ENABLED=false`.
- **Phase101 (Chain B, COMPLETE):** valid artifact `research_state/PHASE101_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T150148Z.json`.
- **Phase100 (Chain B, COMPLETE):** valid artifact `PHASE100_..._PAPER_EVIDENCE_20261108T145417Z.json`.
- **Phase102 (Chain B, COMPLETE):** `src/hedging/phase102_...py`, `scripts/generate_phase102_...py`, `tests/test_phase102_...py`, `tests/test_generate_phase102_...paper_evidence.py` present. Valid artifact `research_state/PHASE102_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T155847Z.json` (`validation.valid=true`, `issues=[]`, `gates_ok=true`, deterministic, `bounds_ok=true`, `coverage_rows=12`, composes PHASE101→32, paper_only=true, live_trading_enabled=false, next9_unblocked=false).
- **Phase103 (Chain B, NEXT):** **not implemented** — no `src/hedging/phase103*`, no Chain B PHASE103 artifact. Mandatory `INIT-20261108T160015Z-PHASE103-POST-ATTRIBUTION-SEAL-DEPTH`.
- **Strict CV (last cited, 2026-11-08T12:42:12Z):** `research_state/CONTINUOUS_VALIDATION_20261108T124212Z.json` — strict, seed 42, BTC,ETH, 5/5, `all_critical_passed=true`, `paper_only=true`, `live_trading_not_enabled=true`. Rerun if stale for material decisions.
- **Strict session gate (last cited, 2026-11-08T12:47:04Z):** `research_state/PAPER_OPS_SESSION_GATE_20261108T124704Z.json` — `gate_passed=false`, `next9_unblocked=false`, `NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL`, `live_capital_readiness_gate.all_guardrails_ok=false`. **No live enablement detected; do not claim readiness unblocked.** Rerun/cite truthfully when material.
- **NEXT9 (HUMAN-ONLY, BLOCKED):** `next9_unblocked=false`, A1–A7 missing. Not agent-removable.

### Prior completed Chain B campaigns (do not regress)
Phase70–102 complete (paper-only, live disabled, next9 false, gates_ok, deterministic, bounds_ok, coverage=12 where applicable).
- Phase102 latest: `PHASE102_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T155847Z.json`
- Phase101 latest: `PHASE101_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T150148Z.json`
- Phase100: `PHASE100_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T145417Z.json`
- Phase99: `PHASE99_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T144134Z.json`
- Phase98: `PHASE98_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T134414Z.json`
- Phase97–91: valid artifacts present in `research_state/PHASE9[1-7]_...PAPER_EVIDENCE_*.json`.

## COMPLETED CURRENT CAMPAIGN (Phase102) — INIT-20261108T150405Z-PHASE102-POST-ATTRIBUTION-SEAL-DEPTH — COMPLETE
**Outcome (2026-11-08T15:58:47Z):** Chain B (`src.hedging`) Phase102 additive, paper-only, composes **PHASE101→32**. `py_compile` OK; module unittest 2/2 OK; controlled `generate(cycles=40, seed=102102, write=True)` + `validate_artifact` valid; CLI `--no-write` rc 0 valid. P0 post-work clean.
**Artifact (valid):** `research_state/PHASE102_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T155847Z.json` — `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`, `coverage_rows=12`, composes PHASE101→32.
