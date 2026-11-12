# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency quantitative options/orderflow strategy (paper-only research/ops).
**Active track:** Chain B `src/hedging` — adaptive toxicity-resilient post-attribution seal orchestrator campaign (additive, deterministic, bounded, finite-probe, paper-only, guarded).
**Single durable handoff/task source:** this file only. `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs — do not action them or create new handoff files.
**Handoff verified/refreshed:** 2026-11-12T07:34:12Z (UTC).

## P0 SAFETY (re-verified 2026-11-12T07:34:12Z) — CLEAR
- `.env` **ABSENT** (`ENV_ABSENT`). `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- Runtime deps importable: `pydantic, numpy, pandas, scipy, yaml, pytest` (`deps_ok`, Python 3.12.x). Use `python3 -m pytest` (plain `pytest` may be unavailable).
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope). **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO NEXT9 unblock.**

## VERIFIED STATE (ground truth)
- **Phase79/80/110–261:** evidence-sealed in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-implement/re-seal.
- **Phase262–271:** **SEALED** (evidence in `research_state/PHASE262..271_*_PAPER_EVIDENCE_*.json`, `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, guards intact). Do not re-implement/re-seal.
- **Phase272:** **SEALED.** Evidence: `research_state/PHASE272_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T063957Z.json` (`valid=true`, `issues=[]`, seed `272272`, cycles `40`, composes `['PHASE271','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`).
- **Phase273:** **SEALED.** Deliverables present: `src/hedging/phase273_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase273_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase273_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase273_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. Evidence: `research_state/PHASE273_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T064901Z.json` (`validation.valid=true`, `issues=[]`, seed `273273`, cycles `40`, composes `['PHASE272','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`).
- **Phase273 verification record:** `py_compile` clean on all 4 Phase273 files; module smoke (`PHASE_QUICK_VERIFY=1`, `sys.setrecursionlimit(200000)`): `paper_only=True`, `gates_ok=True`, composes `['PHASE272','PHASE32']`, `upstream_phase272=True`, `upstream_phase32=True`; targeted module pytest: 2/2 passed (~44.86s); generator pytest: 1/1 passed (~28.11s); generated via CLI `--cycles 40 --seed 273273 --write`; `--validate-only` → `valid=true issues=[]`; CLI no-write smoke → `valid=true issues=[]`. **Sealed 2026-11-12T06:49:01Z**.
- **Phase274:** **SEALED.** Deliverables present: `src/hedging/phase274_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase274_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase274_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase274_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. Evidence: `research_state/PHASE274_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T073308Z.json` (`validation.valid=true`, `issues=[]`, seed `274274`, cycles `40`, composes `['PHASE273','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`).
- **Phase274 verification record:** `py_compile` clean on all 4 Phase274 files; module smoke (`PHASE_QUICK_VERIFY=1`, `sys.setrecursionlimit(200000)`): `paper_only=True`, `gates_ok=True`, composes `['PHASE273','PHASE32']`, `upstream_phase273=True`, `upstream_phase32=True`, `n_seal_attestations=2`, `n_seal_certifications=2`, `n_hedging_seal_attestations=3`, `n_cross_venue_seal_consistencies=3`; targeted module pytest: 2/2 passed (~44.97s); generator pytest: 1/1 passed (~27.98s); generated via CLI `--cycles 40 --seed 274274 --write` → artifact `research_state/PHASE274_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T073308Z.json`; `--validate-only` on artifact → `valid=true issues=[]`; CLI no-write smoke → `valid=true issues=[]`. **Sealed 2026-11-12T07:34:12Z**.
- **Phase275:** **NOT STARTED** (no `src/hedging/phase275_*`, `scripts/generate_phase275_*`, `tests/test_phase275_*`, or `research_state/PHASE275_*` artifacts present). **ACTIVE TASK.**
- **Chain A:** `src/risk/phase*_live_execution*` out of scope (Chain B only).
- **Competing handoffs:** cleared (stubs only). `research_state/durable_handoff.md` is a stale redirect — root `HANDOFF_NEXT_AGENT.md` is authoritative.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, non-optional)

**`INIT-2026-11-12T07:34:12Z-PHASE275-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE. START IMMEDIATELY.**

**Directive:** Execute this campaign **end-to-end in this session** (heavy work required). **No deferral, no stubs, no placeholders, no partial completion, no follow-up questions.** If deep-chain tests/hangs occur, apply governed bounded handling (`PHASE_QUICK_VERIFY=1`, raised `sys.setrecursionlimit`, targeted/bounded timeouts, bounded direct `generate()` if CLI hangs) and **record exact commands/results/caveats** — but still complete implementation, verification, evidence generation/validation, and seal.

**Objective:** Implement, verify, generate validated evidence, and **seal Phase275 adaptive-toxicity-resilient post-attribution seal orchestrator** (Chain B, `src/hedging`) composing **`PHASE274→PHASE32`** (12 coverage rows: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), seed `275275`, IDs `p275-*`, artifacts `PHASE275_*`. Mirror Phase274 structure/parity exactly (additive, deterministic, bounded, finite-probe, paper-only, guarded).

**Predecessor sealed (do NOT re-implement/re-seal):** Phase274 evidence `research_state/PHASE274_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T073308Z.json` (`valid=true`, `issues=[]`).

### Required work (complete in-session)
1. **Additive deliverables (mirror Phase274):**
   - `src/hedging/phase275_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `scripts/generate_phase275_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   - `tests/test_phase275_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `tests/test_generate_phase275_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   Compose `PHASE274→PHASE32`, seed `275275`, IDs `p275-*`, paper-only guards, deterministic/bounded behavior.
2. **Verification (record exact results/caveats):**
   - `python3 -m py_compile` on all 4 Phase275 files (clean).
   - Module smoke: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c "import sys; sys.setrecursionlimit(200000); ..."` → expect `paper_only=True`, `gates_ok=True`, composes `['PHASE274','PHASE32']`.
   - Targeted module + generator pytest via `python3 -m pytest` (bounded timeouts/raised recursion, `PHASE_QUICK_VERIFY=1`) — record pass counts/caveats. Deep-chain runs may hang; prefer bounded execution.
   - Generate controlled evidence (cycles `40`, seed `275275`, `--write` or bounded direct `generate()` if CLI hangs) then `--validate-only <artifact>` → `valid=true issues=[]`, deterministic/bounded, 12-coverage, guards intact.
   - CLI no-write smoke (run without `--write`) → `valid=true issues=[]`.
3. **Seal & advance:**
   - Record exact artifact path/commands/caveats and re-verify P0 (`.env` absent, `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`).
   - Mark Phase275 **SEALED** in this file with artifact path and validation result.
   - Replace active task with **`INIT-<UTC>-PHASE276-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE275→PHASE32`** (seed `276276`, IDs `p276-*`, 12 coverage). Keep this file as the single durable handoff.

### Acceptance criteria
- Phase275 module/generator/tests syntactically valid and aligned to `PHASE274→PHASE32`.
- Validated `research_state/PHASE275_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`.
- Verification evidence recorded (smokes, validate-only, CLI no-write, pytests) or explicit bounded governed caveats.
- P0 intact; handoff advanced to Phase276 only after seal.

## BOTTLENECKS & UNBLOCKING (reconciled 2026-11-12T07:34:12Z)
| Bottleneck | Status | Unblock / handling |
|---|---|---|
| P0 safety drift | **CLEAR (re-verified 07:34:12Z)** | Re-verify before/after batch: `.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`, no venue/config/credential mutation. |
| Missing runtime deps / `pytest` CLI | **CLEARED (caveat)** | Imports OK; use `python3 -m pytest`. If env regresses, provision per `requirements.txt`/docs without weakening guards. |
| **Phase273 implemented & SEALED** | **DONE** | Artifact `research_state/PHASE273_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T064901Z.json` (`valid=true`, `issues=[]`, seed `273273`, cycles `40`, composes `['PHASE272','PHASE32']`, 12 coverage, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`). |
| **Phase274 implemented & SEALED** | **DONE** | Artifact `research_state/PHASE274_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T073308Z.json` (`valid=true`, `issues=[]`, seed `274274`, cycles `40`, composes `['PHASE273','PHASE32']`, 12 coverage, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`). |
| **Phase275 not yet implemented/sealed** | **BLOCKING — ACTIVE** | **Execute `INIT-2026-11-12T07:34:12Z-PHASE275-POST-ATTRIBUTION-SEAL-DEPTH` end-to-end now.** Compose `PHASE274→PHASE32`, seed `275275`, IDs `p275-*`. |
| Deep-chain `RecursionError` / pytest & generator slowness (→phase32) | **EXPECTED, GOVERNED** | `PHASE_QUICK_VERIFY=1`, raise `sys.setrecursionlimit` (≥200k), targeted/bounded tests/timeouts; bounded direct `generate()` if CLI hangs; CLI no-write = run without `--write`. Record exact caveats. |
| Competing/stale handoffs | **CLEARED** | This file is the single source; stubs redirect only. |
| NEXT9 A1–A7 | **BLOCKED — human-only** | Never unblock/mutate. |

## SCOPE & HARD GUARDS (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. No Chain A substitution.
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** No stubs, no deferral, no partial completion.
- **NO live trading. NO `.env` creation. NO venue/config/credential mutation. NO NEXT9 unblock.** Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Do not refactor sealed phases `phase79/80/110–274`.

## HANDOFF DISCIPLINE
- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- Final responses must not ask follow-up questions.
- After Phase275 seal, set active task to **`INIT-<UTC>-PHASE276-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE275→PHASE32`, seed `276276`, IDs `p276-*`). Keep this file as the single durable handoff.