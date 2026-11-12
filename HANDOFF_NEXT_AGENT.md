# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency quantitative options/orderflow strategy (paper-only research/ops).
**Active track:** Chain B `src/hedging` — adaptive toxicity-resilient post-attribution seal orchestrator campaign (additive, deterministic, bounded, finite-probe, paper-only, guarded).
**Single durable handoff/task source:** this file only. `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs — do not action them or create new handoff files.
**Handoff verified/refreshed:** 2026-11-12T09:45:00Z (UTC).

## P0 SAFETY (re-verified 2026-11-12T09:39:54Z) — CLEAR
- `.env` **ABSENT** (`ENV_ABSENT`). `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- Runtime deps importable: `pydantic, numpy, pandas, scipy, yaml, pytest` (Python 3.12.x). Use `python3 -m pytest`.
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope). **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO NEXT9 unblock.**

## VERIFIED STATE (ground truth)
- **Phase79/80/110–271:** evidence-sealed in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-implement/re-seal.
- **Phase272–279:** **SEALED** (deliverables/evidence in `research_state/PHASE272..279_*_PAPER_EVIDENCE_*.json`, `valid=true`, `issues=[]`, 12 coverage, deterministic/bounded, guards intact).
- **Phase280:** **SEALED.** Artifact: `research_state/PHASE280_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T093001Z.json` (`validation.valid=true`, `issues=[]`, seed `280280`, cycles `40`, composes `['PHASE279','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, `upstream_phase279=true`, `upstream_phase32=true`). Deliverables present in `src/hedging/`, `scripts/`, `tests/`. Verification record (2026-11-12T09:31:00Z): `py_compile` clean (4 files), module smoke OK, targeted module+generator pytest 3/3 passed (~79.83s), CLI `--write`/`--validate-only`/no-write smoke → `valid=true issues=[]` (governed bounded handling: `PHASE_QUICK_VERIFY=1`, raised recursion where needed). Do not re-implement/re-seal.
- **Phase281:** **SEALED.** Artifact: `research_state/PHASE281_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T094433Z.json` (`validation.valid=true`, `issues=[]`, seed `281281`, cycles `40`, composes `['PHASE280','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`, `upstream_phase280=true`, `upstream_phase32=true`). Deliverables: `src/hedging/phase281_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase281_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase281_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase281_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. Verification record (2026-11-12T09:45:00Z): `py_compile` clean (4 files), module smoke OK (`paper_only=True`, `gates_ok=True`, composes `['PHASE280','PHASE32']`, `upstream_phase280=True`, `upstream_phase32=True`), targeted module+generator pytest 3/3 passed (~80s), CLI `--write`/`--validate-only`/no-write smoke → `valid=true issues=[]` (governed bounded handling: `PHASE_QUICK_VERIFY=1`, raised recursion where needed). Do not re-implement/re-seal.
- **Chain A:** `src/risk/phase*_live_execution*` out of scope (Chain B only).
- **Competing handoffs:** cleared (stubs only). This file is authoritative.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, non-optional)

**`INIT-2026-11-12T09:45:00Z-PHASE282-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE. START IMMEDIATELY.**

**Directive:** Execute this campaign **end-to-end in this session** (heavy work required). **No deferral, no stubs, no placeholders, no partial completion, no follow-up questions.** If deep-chain tests/CLI hang or recurse, apply governed bounded handling (`PHASE_QUICK_VERIFY=1`, `sys.setrecursionlimit(200000)`, targeted/bounded timeouts, bounded direct `generate()` if CLI hangs) and **record exact commands/results/caveats** — but still complete implementation, verification, evidence generation/validation, and seal.

**Objective:** Implement, verify, generate validated evidence, and **seal Phase282 adaptive-toxicity-resilient post-attribution seal orchestrator** (Chain B, `src/hedging`) composing **`PHASE281→PHASE32`** (12 coverage: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), seed `282282`, IDs `p282-*`, artifacts `PHASE282_*`. Mirror Phase281 structure/parity exactly (additive, deterministic, bounded, finite-probe, paper-only, guarded).

**Predecessor sealed (do NOT re-implement/re-seal):** `research_state/PHASE281_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T094433Z.json` (`valid=true`, `issues=[]`, composes `['PHASE280','PHASE32']`).

### Required work (complete in-session)
1. **Additive deliverables (mirror Phase281):**
   - `src/hedging/phase282_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `scripts/generate_phase282_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   - `tests/test_phase282_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `tests/test_generate_phase282_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   Compose `PHASE281→PHASE32`, seed `282282`, IDs `p282-*`, paper-only guards, deterministic/bounded behavior.
2. **Verification (record exact results/caveats):**
   - `python3 -m py_compile` on all 4 Phase282 files (clean).
   - Module smoke: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c "import sys; sys.setrecursionlimit(200000); ..."` → expect `paper_only=True`, `gates_ok=True`, composes `['PHASE281','PHASE32']`, `upstream_phase281=True`, `upstream_phase32=True`.
   - Targeted module + generator pytest via `python3 -m pytest` (bounded, `PHASE_QUICK_VERIFY=1`, raised recursion/timeouts as needed) — record pass counts/caveats.
   - Generate evidence (cycles `40`, seed `282282`, `--write` or bounded direct `generate()` if CLI hangs) then `--validate-only <artifact>` → `valid=true issues=[]`, deterministic/bounded, 12-coverage, guards intact.
   - CLI no-write smoke (run without `--write`) → `valid=true issues=[]`.
3. **Seal & advance:**
   - Record exact artifact path/commands/caveats and re-verify P0 (`.env` absent, `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`).
   - Mark Phase282 **SEALED** in this file with artifact path and validation result.
   - Replace active task with **`INIT-<UTC>-PHASE283-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE282→PHASE32`** (seed `283283`, IDs `p283-*`, 12 coverage). Keep this file as the single durable handoff.

### Acceptance criteria
- Phase281 module/generator/tests syntactically valid and aligned to `PHASE280→PHASE32`.
- Validated `research_state/PHASE281_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`.
- Verification evidence recorded (smokes, validate-only, CLI no-write, pytests) or explicit bounded governed caveats.
- P0 intact; handoff advanced to Phase282 only after seal.

## BOTTLENECKS & UNBLOCKING (reconciled 2026-11-12T09:39:54Z)
| Bottleneck | Status | Unblock / handling |
|---|---|---|
| P0 safety drift | **CLEAR** | Re-verify before/after batch: `.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`, no venue/config/credential mutation. |
| Missing runtime deps / `pytest` CLI | **CLEARED (caveat)** | Imports OK; use `python3 -m pytest`. If env regresses, provision per `requirements.txt`/docs without weakening guards. |
| **Phase272–280 implemented & SEALED** | **DONE** | Artifacts `research_state/PHASE272..280_*_PAPER_EVIDENCE_*.json` (`valid=true`, `issues=[]`). |
| **Phase281 not yet implemented/sealed** | **DONE** | Implemented, verified, evidence validated `valid=true issues=[]`, SEALED at `research_state/PHASE281_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T094433Z.json`. |
| **Phase282 not yet implemented/sealed** | **ACTIVE (INIT above)** | Execute `INIT-2026-11-12T09:45:00Z-PHASE282-POST-ATTRIBUTION-SEAL-DEPTH` end-to-end now (mirror Phase281, compose `PHASE281→PHASE32`, seed `282282`). |
| Deep-chain `RecursionError` / hangs (→phase32) | **EXPECTED, GOVERNED** | `PHASE_QUICK_VERIFY=1`, raise `sys.setrecursionlimit` (≥200k), targeted/bounded tests/timeouts; bounded direct `generate()` if CLI hangs; CLI no-write = run without `--write`. Record exact caveats. |
| Competing/stale handoffs | **CLEARED** | This file is the single source; stubs redirect only. |
| NEXT9 A1–A7 | **BLOCKED — human-only** | Never unblock/mutate. |

## SCOPE & HARD GUARDS (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. No Chain A substitution.
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** No stubs, no deferral, no partial completion.
- **NO live trading. NO `.env` creation. NO venue/config/credential mutation. NO NEXT9 unblock.** Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Do not refactor sealed phases `phase79/80/110–280`.

## HANDOFF DISCIPLINE
- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- Final responses must not ask follow-up questions.
- After Phase282 seal, set active task to **`INIT-<UTC>-PHASE283-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE282→PHASE32`, seed `283283`, IDs `p283-*`). Keep this file as the single durable handoff.
