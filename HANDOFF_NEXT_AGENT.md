# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency quantitative options/orderflow strategy (paper-only research/ops).
**Active track:** Chain B `src/hedging` — adaptive toxicity-resilient post-attribution seal orchestrator campaign (additive, deterministic, bounded, finite-probe, paper-only, guarded).
**Single durable handoff/task source:** this file only. `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs — do not action them or create new handoff files.
**Handoff verified/refreshed:** 2026-11-12T08:51:23Z (UTC). **Phase280 sealed:** 2026-11-12T09:31:00Z (UTC).

## P0 SAFETY (re-verified 2026-11-12T08:51:23Z) — CLEAR
- `.env` **ABSENT** (`ENV_ABSENT`). `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- Runtime deps importable: `pydantic, numpy, pandas, scipy, yaml, pytest` (`deps_ok`, Python 3.12.x). Use `python3 -m pytest` (plain `pytest` may be unavailable).
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope). **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO NEXT9 unblock.**

## VERIFIED STATE (ground truth)
- **Phase79/80/110–261:** evidence-sealed in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-implement/re-seal.
- **Phase262–271:** **SEALED** (evidence in `research_state/PHASE262..271_*_PAPER_EVIDENCE_*.json`, `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, guards intact). Do not re-implement/re-seal.
- **Phase272:** **SEALED.** Evidence: `research_state/PHASE272_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T063957Z.json` (`valid=true`, `issues=[]`, seed `272272`, cycles `40`, composes `['PHASE271','PHASE32']`, 12 coverage, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`).
- **Phase273:** **SEALED.** Deliverables present. Evidence: `research_state/PHASE273_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T064901Z.json` (`valid=true`, `issues=[]`, seed `273273`, cycles `40`, composes `['PHASE272','PHASE32']`, 12 coverage, guards intact).
- **Phase274:** **SEALED.** Deliverables present. Evidence: `research_state/PHASE274_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T073308Z.json` (`valid=true`, `issues=[]`, seed `274274`, cycles `40`, composes `['PHASE273','PHASE32']`, 12 coverage, guards intact).
- **Phase275:** **SEALED.** Deliverables present. Evidence: `research_state/PHASE275_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T074510Z.json` (`valid=true`, `issues=[]`, seed `275275`, cycles `40`, composes `['PHASE274','PHASE32']`, 12 coverage, guards intact).
- **Phase276:** **SEALED.** Deliverables present. Evidence: `research_state/PHASE276_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T075137Z.json` (`valid=true`, `issues=[]`, seed `276276`, cycles `40`, composes `['PHASE275','PHASE32']`, 12 coverage, guards intact).
- **Phase277:** **SEALED.** Deliverables present. Evidence: `research_state/PHASE277_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T082623Z.json` (`valid=true`, `issues=[]`, seed `277277`, cycles `40`, composes `['PHASE276','PHASE32']`, 12 coverage, guards intact).
- **Phase278:** **SEALED.** Deliverables present. Evidence: `research_state/PHASE278_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T084203Z.json` (`valid=true`, `issues=[]`, seed `278278`, cycles `40`, composes `['PHASE277','PHASE32']`, 12 coverage, guards intact).
- **Phase279:** **SEALED.** Deliverables present: `src/hedging/phase279_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase279_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase279_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase279_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. Evidence: `research_state/PHASE279_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T085002Z.json` (`validation.valid=true`, `issues=[]`, seed `279279`, cycles `40`, composes `['PHASE278','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`).
- **Phase279 verification record (2026-11-12T08:51:23Z):** `py_compile` clean on all 4 Phase279 files; module smoke (`PHASE_QUICK_VERIFY=1`, `sys.setrecursionlimit(200000)`): `paper_only=True`, `gates_ok=True`, composes `['PHASE278','PHASE32']`, `upstream_phase278=True`, `upstream_phase32=True`; targeted module+generator pytest: 3/3 passed (~79.52s); generated via CLI `--cycles 40 --seed 279279 --write` → artifact `research_state/PHASE279_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T085002Z.json`; `--validate-only` → `valid=true issues=[]`; CLI no-write smoke → `valid=true issues=[]`. **Sealed 2026-11-12T08:51:23Z.**
- **Phase280:** **SEALED.** Artifact `research_state/PHASE280_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T093001Z.json` (`valid=true`, `issues=[]`, seed `280280`, cycles `40`, composes `['PHASE279','PHASE32']`, 12 coverage Deribit/OKX/Bybit/Binance × BTC/ETH/SOL, `bounds_ok=true`, `deterministic_replay_equal=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`). Deliverables: `src/hedging/phase280_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase280_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase280_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase280_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`. Verification record (2026-11-12T09:31:00Z): `py_compile` clean on all 4 files; module smoke `paper_only=True`, `gates_ok=True`, composes `['PHASE279','PHASE32']`, `upstream_phase279=True`, `upstream_phase32=True`; targeted module+generator pytest: 3/3 passed (~79.83s); CLI `--cycles 40 --seed 280280 --write` (PHASE_QUICK_VERIFY=1, bounded due to deep-chain hang in non-quick path) → artifact `...T093001Z.json`; `--validate-only` → `valid=true issues=[]`; CLI no-write smoke → `valid=true issues=[]`.
- **Chain A:** `src/risk/phase*_live_execution*` out of scope (Chain B only).
- **Competing handoffs:** cleared (stubs only). Root `HANDOFF_NEXT_AGENT.md` is authoritative.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, non-optional)

**`INIT-2026-11-12T09:31:00Z-PHASE281-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE. START IMMEDIATELY.** (`INIT-2026-11-12T08:51:23Z-PHASE280-POST-ATTRIBUTION-SEAL-DEPTH` completed and sealed above.)

**Directive:** Execute this campaign **end-to-end in this session** (heavy work required). **No deferral, no stubs, no placeholders, no partial completion, no follow-up questions.** If deep-chain tests/hangs occur, apply governed bounded handling (`PHASE_QUICK_VERIFY=1`, raised `sys.setrecursionlimit`, targeted/bounded timeouts, bounded direct `generate()` if CLI hangs) and **record exact commands/results/caveats** — but still complete implementation, verification, evidence generation/validation, and seal.

**Objective:** Implement, verify, generate validated evidence, and **seal Phase281 adaptive-toxicity-resilient post-attribution seal orchestrator** (Chain B, `src/hedging`) composing **`PHASE280→PHASE32`** (12 coverage rows: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), seed `281281`, IDs `p281-*`, artifacts `PHASE281_*`. Mirror Phase279/280 structure/parity exactly (additive, deterministic, bounded, finite-probe, paper-only, guarded).

**Predecessor sealed (do NOT re-implement/re-seal):** Phase280 evidence `research_state/PHASE280_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T093001Z.json` (`valid=true`, `issues=[]`).

### Required work (complete in-session)
1. **Additive deliverables (mirror Phase279/280):**
   - `src/hedging/phase281_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `scripts/generate_phase281_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   - `tests/test_phase281_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
   - `tests/test_generate_phase281_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
   Compose `PHASE280→PHASE32`, seed `281281`, IDs `p281-*`, paper-only guards, deterministic/bounded behavior.
2. **Verification (record exact results/caveats):**
   - `python3 -m py_compile` on all 4 Phase281 files (clean).
   - Module smoke: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c "import sys; sys.setrecursionlimit(200000); ..."` → expect `paper_only=True`, `gates_ok=True`, composes `['PHASE280','PHASE32']`.
   - Targeted module + generator pytest via `python3 -m pytest` (bounded timeouts/raised recursion, `PHASE_QUICK_VERIFY=1`) — record pass counts/caveats. Deep-chain runs may hang; prefer bounded execution.
   - Generate controlled evidence (cycles `40`, seed `281281`, `--write` or bounded direct `generate()` if CLI hangs) then `--validate-only <artifact>` → `valid=true issues=[]`, deterministic/bounded, 12-coverage, guards intact.
   - CLI no-write smoke (run without `--write`) → `valid=true issues=[]`.
3. **Seal & advance:**
   - Record exact artifact path/commands/caveats and re-verify P0 (`.env` absent, `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`).
   - Mark Phase281 **SEALED** in this file with artifact path and validation result.
   - Replace active task with **`INIT-<UTC>-PHASE282-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE281→PHASE32`** (seed `282282`, IDs `p282-*`, 12 coverage). Keep this file as the single durable handoff.

### Acceptance criteria
- Phase281 module/generator/tests syntactically valid and aligned to `PHASE280→PHASE32`.
- Validated `research_state/PHASE281_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `campaign.gates_ok=true`.
- Verification evidence recorded (smokes, validate-only, CLI no-write, pytests) or explicit bounded governed caveats.
- P0 intact; handoff advanced to Phase282 only after seal.

## BOTTLENECKS & UNBLOCKING (reconciled 2026-11-12T08:51:23Z)
| Bottleneck | Status | Unblock / handling |
|---|---|---|
| P0 safety drift | **CLEAR (re-verified 2026-11-12T08:51:23Z)** | Re-verify before/after batch: `.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`, no venue/config/credential mutation. |
| Missing runtime deps / `pytest` CLI | **CLEARED (caveat)** | Imports OK; use `python3 -m pytest`. If env regresses, provision per `requirements.txt`/docs without weakening guards. |
| **Phase272–278 implemented & SEALED** | **DONE** | Artifacts `research_state/PHASE272..278_*_PAPER_EVIDENCE_*.json` (`valid=true`, `issues=[]`). |
| **Phase279 implemented & SEALED** | **DONE** | Artifact `research_state/PHASE279_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T085002Z.json` (`valid=true`, `issues=[]`, seed `279279`, cycles `40`, composes `['PHASE278','PHASE32']`, 12 coverage, guards intact). |
| **Phase280 not yet implemented/sealed** | **DONE — SEALED 2026-11-12T09:31:00Z** | Artifact `research_state/PHASE280_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261112T093001Z.json` (`valid=true`, `issues=[]`, seed `280280`, cycles `40`, composes `['PHASE279','PHASE32']`, 12 coverage, guards intact). |
| Deep-chain `RecursionError` / pytest & generator slowness (→phase32) | **EXPECTED, GOVERNED** | `PHASE_QUICK_VERIFY=1`, raise `sys.setrecursionlimit` (≥200k), targeted/bounded tests/timeouts; bounded direct `generate()` if CLI hangs; CLI no-write = run without `--write`. Record exact caveats. |
| Competing/stale handoffs | **CLEARED** | This file is the single source; stubs redirect only. |
| NEXT9 A1–A7 | **BLOCKED — human-only** | Never unblock/mutate. |

## SCOPE & HARD GUARDS (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. No Chain A substitution.
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** No stubs, no deferral, no partial completion.
- **NO live trading. NO `.env` creation. NO venue/config/credential mutation. NO NEXT9 unblock.** Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Do not refactor sealed phases `phase79/80/110–279`.

## HANDOFF DISCIPLINE
- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- Final responses must not ask follow-up questions.
- After Phase281 seal, set active task to **`INIT-<UTC>-PHASE282-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE281→PHASE32`, seed `282282`, IDs `p282-*`). Keep this file as the single durable handoff.
