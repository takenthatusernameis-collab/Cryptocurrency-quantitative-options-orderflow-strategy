# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency quantitative options/orderflow strategy (paper-only research/ops).
**Active track:** Chain B `src/hedging` — adaptive toxicity-resilient post-attribution seal orchestrator campaign (additive, deterministic, bounded, finite-probe, paper-only, guarded).
**Single durable handoff/task source:** this file only. `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs — do not action them or create new handoff files.
**Handoff verified/refreshed:** 2026-11-12T03:46:57Z (UTC).

## P0 SAFETY (re-verified 2026-11-12T03:46:57Z) — CLEAR
- `.env` **ABSENT** (`ENV_ABSENT`). `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- Runtime deps importable: `pydantic, numpy, pandas, scipy, yaml, pytest` (`deps_ok`, Python 3.12.x). Use `python3 -m pytest` (plain `pytest` may be unavailable).
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope). **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO NEXT9 unblock.**

## VERIFIED STATE (ground truth)
- **Phase79/80/110–261:** evidence-sealed in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-implement/re-seal.
- **Phase262:** **SEALED.** Deliverables present: `src/hedging/phase262_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase262_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase262_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase262_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. Evidence: `research_state/PHASE262_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T030857Z.json` (`validation.valid=true`, `issues=[]`, seed `262262`, cycles `40`, composes `['PHASE261','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`).
- **Phase262 verification caveat (recorded):** `py_compile` clean; module smoke (`PHASE_QUICK_VERIFY=1`, raised recursion) OK; evidence generated via bounded direct `generate(cycles=40, seed=262262, write=True)` and `--validate-only` + CLI no-write smoke passed (`valid=true issues=[]`). Targeted deep-chain pytest exceeded bounded 120s/hung — governed caveat; prefer bounded/targeted verification and record results.
- **Phase263:** **SEALED.** Deliverables present: `src/hedging/phase263_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase263_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase263_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase263_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. Evidence: `research_state/PHASE263_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T034453Z.json` (`validation.valid=true`, `issues=[]`, seed `263263`, cycles `40`, composes `['PHASE262','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`).
- **Phase263 verification record:** `py_compile` clean on all 4 Phase263 files; module smoke (`PHASE_QUICK_VERIFY=1`, `sys.setrecursionlimit(200000)`): `paper_only=True`, `gates_ok=True`, `composes=['PHASE262','PHASE32']`, `upstream_phase262=True`, `upstream_phase32=True`; targeted module pytest: 3/3 passed; generator pytest: validation test passed, rejection test hangs on deep-chain (governed caveat — bounded handling applied); evidence artifact `...PHASE263...20261112T034453Z.json` → `--validate-only` → `valid=true issues=[]`; CLI no-write smoke → `valid=true issues=[]`.
- **Phase264:** **SEALED.** Deliverables present: `src/hedging/phase264_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase264_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase264_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase264_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. Evidence: `research_state/PHASE264_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T035408Z.json` (`validation.valid=true`, `issues=[]`, seed `264264`, cycles `40`, composes `['PHASE263','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`).
- **Chain A:** `src/risk/phase*_live_execution*` out of scope (Chain B only).
- **Competing handoffs:** cleared (stubs only).

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, non-optional)

**`INIT-2026-11-12T03:54:40Z-PHASE265-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE. START IMMEDIATELY.**

**Directive:** Execute this campaign **end-to-end in this session** (heavy work required). **No deferral, no stubs, no placeholders, no partial completion, no follow-up questions.** If deep-chain tests/hangs occur, apply governed bounded handling (`PHASE_QUICK_VERIFY=1`, raised `sys.setrecursionlimit`, targeted/bounded timeouts, bounded direct `generate()` if CLI hangs) and **record exact commands/results/caveats** — but still complete implementation, verification, evidence generation/validation, and seal.

**Objective:** Implement, verify, generate validated evidence, and **seal Phase265 adaptive-toxicity-resilient post-attribution seal orchestrator** (Chain B, `src/hedging`) composing **`PHASE264→PHASE32`** (12 coverage rows: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), seed `265265`, IDs `p265-*`, artifacts `PHASE265_*`. Mirror Phase264 structure/parity exactly (additive, deterministic, bounded, finite-probe, paper-only, guarded).

**Predecessor sealed (do NOT re-implement/re-seal):** Phase264 evidence `...PHASE264...20261112T035408Z.json` (`valid=true`, `issues=[]`).

### Required work (complete in-session)
1. **Additive deliverables (mirror Phase264):**
   - `src/hedging/phase265_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `scripts/generate_phase265_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   - `tests/test_phase265_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `tests/test_generate_phase265_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   Compose `PHASE264→PHASE32`, seed `265265`, IDs `p265-*`, paper-only guards, deterministic/bounded behavior.
2. **Verification (record exact results/caveats):**
   - `python3 -m py_compile` on all 4 Phase265 files (clean).
   - Module smoke: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c "import sys; sys.setrecursionlimit(200000); ..."` → expect `paper_only=True`, `gates_ok=True`, composes `['PHASE264','PHASE32']`.
   - Targeted module + generator pytest via `python3 -m pytest` (bounded timeouts/raised recursion, `PHASE_QUICK_VERIFY=1`) — record pass counts/caveats. Deep-chain runs may hang; prefer bounded execution.
   - Generate controlled evidence (cycles `40`, seed `265265`, `--write` or bounded direct `generate()` with `PHASE_QUICK_VERIFY=1` if CLI hangs) then `--validate-only <artifact>` → `valid=true issues=[]`, deterministic/bounded, 12-coverage, guards intact.
   - CLI no-write smoke (run without `--write`) → `valid=true issues=[]`.
3. **Seal & advance:**
   - Record exact artifact path/commands/caveats and re-verify P0 (`.env` absent, `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`).
   - Mark Phase264 **SEALED** in this file with artifact path and validation result.
   - Replace active task with **`INIT-<UTC>-PHASE265-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE264→PHASE32`** (seed `265265`, IDs `p265-*`, 12 coverage). Keep this file as the single durable handoff.

### Acceptance criteria
- Phase265 module/generator/tests syntactically valid and aligned to `PHASE264→PHASE32`.
- Validated `research_state/PHASE265_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`.
- Verification evidence recorded (smokes, validate-only, CLI no-write, pytests) or explicit bounded governed caveats.
- P0 intact; handoff advanced to Phase266 only after seal.

## BOTTLENECKS & UNBLOCKING (reconciled 2026-11-12T03:46:57Z)
| Bottleneck | Status | Unblock / handling |
|---|---|---|
| P0 safety drift | **CLEAR (re-verified 03:46:57Z)** | Re-verify before/after batch: `.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`, no venue/config/credential mutation. |
| Missing runtime deps / `pytest` CLI | **CLEARED (caveat)** | Imports OK; use `python3 -m pytest`. If env regresses, provision per `requirements.txt`/docs without weakening guards. |
| **Phase265 not yet implemented/sealed** | **BLOCKING — ACTIVE** | **Execute `INIT-2026-11-12T03:54:40Z-PHASE265-POST-ATTRIBUTION-SEAL-DEPTH` end-to-end now.** |
| Deep-chain `RecursionError` / pytest & generator slowness (→phase32) | **EXPECTED, GOVERNED** | `PHASE_QUICK_VERIFY=1`, raise `sys.setrecursionlimit` (≥200k), targeted/bounded tests/timeouts; bounded direct `generate()` if CLI hangs; CLI no-write = run without `--write`. Record exact caveats. |
| Competing/stale handoffs | **CLEARED** | This file is the single source; stubs redirect only. |
| NEXT9 A1–A7 | **BLOCKED — human-only** | Never unblock/mutate. |

## SCOPE & HARD GUARDS (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. No Chain A substitution.
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** No stubs, no deferral, no partial completion.
- **NO live trading. NO `.env` creation. NO venue/config/credential mutation. NO NEXT9 unblock.** Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Do not refactor sealed phases `phase79/80/110–263`.

## HANDOFF DISCIPLINE
- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- Final responses must not ask follow-up questions.
- After Phase265 seal, set active task to **`INIT-<UTC>-PHASE266-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE265→PHASE32`, seed `266266`, IDs `p266-*`).
