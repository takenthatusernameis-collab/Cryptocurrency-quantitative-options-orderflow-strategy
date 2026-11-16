# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T13:28:44Z, verified):**
> **Repo priority (per name `Cryptocurrency-quantitative-options-orderflow-strategy`):** options + orderflow alpha, net-of-cost on real data. **On-charter ladder EVAL-02..66 is CLOSED** — EVAL-66 sealed `BLOCKED` (gate exit 0; ETH capture under-floor & not disjoint from EVAL-65); namesake options order-flow → realized-vol hypothesis not supported on real BTC/ETH in tested windows. Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/EVAL-64..66 artifacts or `src/`. Do not invent synthetic data or weaken floors.
>
> **NEXT FOCUS CAMPAIGN — EVAL-67 (MANDATORY heavy real-data falsification, off-charter but core-thesis-aligned): BTC options order-flow (toxicity/imbalance) → realized-vol OOS replication on a fresh, disjoint, floor-compliant real BTC capture.** Future agents must not avoid heavy work: execute this end-to-end; end only with a sealed COMBINED/BLOCKED/NO-GO artifact **+ seal gate exit 0**, or a genuinely live **persistent** acquisition with recorded PID/command/liveness, or a **recorded scheduled wakeup/cron** for the earliest disjoint capture time. No timestamp-only refreshes, no planning-only stops.
>
> **BOTTLENECKS REMOVED THIS SESSION (do not rediscover them):**
> 1. **Non-disjoint acquisition plan fixed.** The prior handoff's `python3 scripts/eval60_acquire_three_way.py --underlying BTC --days 7 ...` would produce a capture `2026-11-09T13:xx..2026-11-16T13:xx`, which **overlaps the sealed EVAL-64/65 BTC window `2026-11-09T06:48:16Z..2026-11-16T06:48:16Z`** and would seal `BLOCKED`. A naive `--days 7` capture is RETIRED. Correct rule: capture end **>= 2026-11-20T00:00:00Z**, `--days 3.7` (start `2026-11-16T07:12:00Z`, span 319,680 s), or generally `start >= 2026-11-16T06:48:16Z` and `span >= 300,000 s`.
> 2. **Runner pre-staged and tested.** `scripts/eval67_btc_oflow_tox_rv_oos.py` is a copy-and-retarget of sealed EVAL-66 with BTC-only filtering, the EVAL-64 floor verbatim, and a **runtime disjointness gate** (`check_disjointness`) that seals `BLOCKED` on overlap. `tests/test_eval67_btc_oflow_tox_rv_oos.py` passes **12/12**; EVAL-66 baseline still passes **9/9**; `verify_env.sh --check` OK.
> 3. **Protocol pre-registered before capture.** `research_state/EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}` fixes BTC-only, `tox/imbalance::bar60::h72`, EVAL-64 floor (`min_underlyings=1`), disjointness rule, and verdict `∈ {NO-GO CONFIRMED (PASS), BLOCKED}`.
> 4. **Seal-gate task ID fixed.** The old compact ID `INIT-2026-11-16T122919Z-...` is RETIRED because `check_session_sealed.py` cannot parse it (`FAIL: task id has no ISO-8601 UTC timestamp`). The authoritative parseable ID is below.
>
> **Task ID:** `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION` (use this exact ID for prereg/seal/gate; gate currently finds the prereg and exits 1 only because no result artifact exists yet — that is expected until step 4).
>
> **Unskippable heavy-work contract (execute in order):**
> 1. **Env/safety (must pass):** `.env` absent; `LIVE_TRADING_ENABLED` unset/false; paper-only. `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `./scripts/verify_env.sh --check`. Run targeted tests: `python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py` (expect 12/12) and `python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py` (expect 9/9). Do **not** run the full suite and do **not** enumerate `research_state/`.
> 2. **Pre-register before capture (DONE):** authoritative prereg is `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}`. Do not rewrite the protocol; if a new prereg is unavoidable it must keep the same hypothesis, floor, disjointness rule, and a parseable task ID.
> 3. **Heavy real capture (mandatory, DISJOINT):** Do **not** run the retired `--days 7` command now. **At/after 2026-11-20T00:00:00Z** run as a **persistent** background process: `mkdir -p data/raw/eval67; PYTHONUNBUFFERED=1 PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py --underlying BTC --days 3.7 --end <NOW-ISO> --out-dir data/raw/eval67 --seal`. If the session starts before 2026-11-20T00:00:00Z, **schedule a wakeup/cron for 2026-11-20T00:00:00Z (or later) first**, then execute; record the schedule ID/command here. Real loaders only (`RealDataUnavailable` on missing); **never synthetic, never relabel, never `{"valid": true}`**. Verify the capture is real, disjoint, and meets the EVAL-64 floor before proceeding.
> 4. **Evaluate:** dry-run `python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --no-write` → then `--seal --task-label EVAL67-BTC-OFLOW-TOX-RV-OOS` to emit `EVAL_67_BTC_OFLOW_TOX_RV_OOS_{COMBINED|BLOCKED}_<TS>.{json,md}`. Under-floor or non-disjoint non-empty real ⇒ `BLOCKED` (do not weaken the floor). Do not seal on missing/empty state.
> 5. **Seal gate (must be exit 0):** `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"` → **exit 0**.
> 6. **Close session:** update this handoff with verified facts (artifact names, verdict, gate exit code, capture sha256/size/window/disjointness, PIDs or schedule IDs if any). `data/raw/eval67/` is gitignored real data — do not commit. Paper-only preserved.
>
> **Completion contract:** session ends only with (a) sealed EVAL-67 artifact + gate exit 0, OR (b) a genuinely live **persistent** acquisition with recorded PID/command/liveness, OR (c) a recorded **scheduled wakeup/cron** for the earliest disjoint capture time (with the exact capture command) when the runtime cannot keep a process alive that long. No other stopping point is acceptable.

## STATUS (verified 2026-11-16T13:28:44Z)

- **On-charter campaign:** `CAMPAIGN_CLOSED`. EVAL-66 sealed `BLOCKED` (gate exit 0, rechecked this session) — `research_state/EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,BLOCKED}_20261116T121851Z.{json,md}` (task `INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`). ETH capture `data/raw/eval66/three_way_ETH_20261116T111833Z.json` (93,667,786 B, sha256 `d9873…d37e1`, 2026-11-09T11:18:33Z..2026-11-16T11:18:33Z) overlapped EVAL-65 and failed EVAL-64 floor ⇒ BLOCKED.
- **Bottlenecks:** **Removed this session (4 above).** No eval/acquisition processes running; `.env` absent; `LIVE_TRADING_ENABLED` unset; `data/raw/eval67/` not yet created; `data/raw/eval66/` present (gitignored); `.venv-deps` bootstrapped. New EVAL-67 runner + tests are untracked; prereg is untracked. Secondary root handoff files are retired pointers (no task IDs); single durable handoff is authoritative.
- **Sealed (immutable):** EVAL-02..62, EVAL-64..66 sealed; **EVAL-63 never sealed**. EVAL-46..60,62,64,65 `NO-GO CONFIRMED (PASS)`; EVAL-61 `NO-GO` (artifact, superseded by 62); EVAL-66 `BLOCKED`.
- **Next required action:** execute **EVAL-67** per the corrected heavy-work contract above. Earliest disjoint capture end is **2026-11-20T00:00:00Z** (`--days 3.7`); schedule a wakeup/cron if the session starts earlier. No other stopping point acceptable.

## AUTHORITATIVE NEXT TASK

**EVAL-67 — BTC options order-flow (tox/imbalance) → realized-vol OOS replication** (`INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`). Heavy, pre-registered, real-data-only, floor-compliant, **disjoint**. The runner and prereg are already staged; the remaining heavy work is the disjoint capture, dry-run, seal, and gate exit 0. Do not stop at planning or timestamp bumps.

## REPRO / KEY COMMANDS

```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check
python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py   # 12/12
python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py   # 9/9 baseline

# immutable sealed EVAL-66 check
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"

# EVAL-67 capture (ONLY at/after 2026-11-20T00:00:00Z; never naive --days 7 now)
mkdir -p data/raw/eval67
PYTHONUNBUFFERED=1 PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py \
  --underlying BTC --days 3.7 --end <NOW-ISO> --out-dir data/raw/eval67 --seal

# EVAL-67 dry-run, then seal
python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --no-write
python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --seal \
  --task-label EVAL67-BTC-OFLOW-TOX-RV-OOS

# EVAL-67 seal gate (after prereg + sealed result exist)
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"
```

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62 or EVAL-64..66 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real data; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor **or non-disjoint** non-empty real capture ⇒ `BLOCKED`, not `NO-GO`.
- **Do not use the retired compact task ID** `INIT-2026-11-16T122919Z-...`; use `INIT-2026-11-16T13:25:40Z-...`.
- **Do not run the retired naive `--days 7` BTC acquisition before 2026-11-20T00:00:00Z**; it overlaps the sealed BTC window. Use the corrected `--days 3.7 --end <NOW-ISO>` rule.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`, and existing `scripts/eval60_*`/`eval66_*`/`eval67_*` patterns; no `phaseNN_*` wrappers.
- `data/raw/eval66/`, `data/raw/eval67/` real captures are gitignored — do not commit/push.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only.

## SESSION LOG (append-only, recent)

- 2026-11-16T12:19:00Z: Sealed **EVAL-66 `BLOCKED`** (under-floor, non-disjoint ETH capture; gate exit 0). `CAMPAIGN_CLOSED`.
- 2026-11-16T12:23:50Z / 12:25:20Z / 12:26:20Z / 12:27:06Z: verification/timestamp refresh sessions; no sealed artifacts modified.
- **2026-11-16T12:29:19Z:** Refreshed this single durable handoff with a timestamped initial task and built **EVAL-67** as the mandatory next focus campaign: heavy 7d real BTC options+orderflow acquisition, pre-registered, disjoint/floor-compliant, dry-run→seal→gate-exit-0, no timestamp-only stops. No sealed artifacts modified; no synthetic data; paper-only.
- **2026-11-16T12:33:59Z:** Re-verified state and refreshed the timestamped initial task; confirmed **EVAL-67** remained mandatory.
- **2026-11-16T12:35:17Z:** Confirmed `research_state/durable_handoff.md` is the sole actionable handoff; other `*HANDOFF*` root files are retired pointers with no task IDs.
- **2026-11-16T12:36:59Z:** Re-verified repo state and handoff integrity; **EVAL-67** remained mandatory per contract.
- **2026-11-16T12:38:24Z:** Re-verified EVAL-66 seal gate exit 0, no running eval/acquisition processes, `.env` absent, `LIVE_TRADING_ENABLED` unset, `data/raw/eval67/` absent, `data/raw/eval66/` present (gitignored). No bottlenecks found/removed.
- **2026-11-16T13:18:17Z:** Verified repo state and handoff integrity; no running eval acquisition; `.env` absent; `data/raw/eval67/` absent; `data/raw/eval66/` present (gitignored). No bottlenecks to remove.
- **2026-11-16T13:28:44Z (this session):** **Bottlenecks removed, not just timestamped.** (1) Proved the prior EVAL-67 `--days 7` capture plan was **non-disjoint** (would overlap sealed BTC window `2026-11-09T06:48:16Z..2026-11-16T06:48:16Z` by ~6.75 d) and corrected the rule to `--days 3.7 --end <NOW-ISO>` at/after 2026-11-20T00:00:00Z. (2) Pre-staged `scripts/eval67_btc_oflow_tox_rv_oos.py` (BTC-only, EVAL-64 floor verbatim, runtime disjointness gate) + `tests/test_eval67_btc_oflow_tox_rv_oos.py` (**12/12 pass**; EVAL-66 baseline **9/9**; `verify_env.sh --check` OK). (3) Pre-registered `research_state/EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}` with the corrected rule. (4) Replaced the unparseable compact task ID with `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION` (gate now finds the prereg and exits 1 only for the missing result). No sealed EVAL-02..66 artifacts or `src/` modified; no synthetic data; paper-only.

## SEALED STATE (immutable; append only)

EVAL-02..62,64..66 sealed. EVAL-63 never sealed. EVAL-46..60,62,64,65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`. On-charter campaign closed; EVAL-67 is the next authorized heavy falsification campaign.