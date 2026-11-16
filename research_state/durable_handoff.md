# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T14:28:41Z, verified — supersedes 14:26:11Z):**
> **Repo priority (per name `Cryptocurrency-quantitative-options-orderflow-strategy`):** options + orderflow alpha, net-of-cost on real data. **On-charter ladder EVAL-02..66 is CLOSED** — EVAL-66 sealed `BLOCKED` (gate exit 0; ETH capture under-floor & not disjoint from EVAL-65); namesake options order-flow → realized-vol hypothesis not supported on real BTC/ETH in tested windows. Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/EVAL-64..66 artifacts or `src/`. Do not invent synthetic data or weaken floors.
>
> **NEXT FOCUS CAMPAIGN — EVAL-67 (MANDATORY heavy real-data falsification, off-charter but core-thesis-aligned): BTC options order-flow (toxicity/imbalance) → realized-vol OOS replication on a fresh, disjoint, floor-compliant real BTC capture.** Future agents must not avoid heavy work. This session is **not finished** until one of the completion-contract outcomes is achieved: (a) sealed EVAL-67 artifact + `check_session_sealed.py` exit 0, OR (b) a genuinely live **persistent** acquisition with recorded PID/command/liveness (recorded here), OR (c) a recorded **scheduled wakeup/cron** for the earliest disjoint capture time (exact command recorded). No timestamp-only refreshes, no planning-only stops.
>
> **BOTTLENECKS REMOVED (do not rediscover):**
> 1. **Naive `--days 7` BTC acquisition is RETIRED (overlaps sealed BTC window).** Correct: capture end `>= 2026-11-20T00:00:00Z`; use `--days 3.7 --end <NOW-ISO>` (start `2026-11-16T07:12:00Z`, span 319680s). The disjointness gate in `scripts/eval67_btc_oflow_tox_rv_oos.py` seals `BLOCKED` on overlap/non-disjoint windows.
> 2. **Runner + tests ready.** `scripts/eval67_btc_oflow_tox_rv_oos.py` (BTC-only, EVAL-64 floor, runtime disjointness check) and `tests/test_eval67_btc_oflow_tox_rv_oos.py` (12/12). EVAL-66 baseline `tests/test_eval66_eth_oflow_tox_rv_oos.py` remains 9/9.
> 3. **Protocol pre-registered.** `research_state/EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}` (do not rewrite unless necessary; must keep parseable task ID/floor/disjointness/hypothesis).
> 4. **Seal-gate task ID fixed (parseable).** Use `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION` (retired `INIT-2026-11-16T122919Z-...` is invalid for `check_session_sealed.py`).
> 5. **Persistent bridge live (waiting) + backup wakeup scheduled.** `scripts/eval67_capture_bridge.py` started as **pid 58162** (heartbeat: `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_58162.json`, phase `waiting`, `threshold 2026-11-20T00:00:00Z`, `started_at 2026-11-16T14:25:52Z`, verified alive at 2026-11-16T14:26:11Z). Bridge runs the corrected acquisition at/after threshold, then expects follow-on dry-run→seal→gate. If it dies, use `scripts/eval67_launch_capture.sh` (hard-refuses before threshold) or the **backup wakeup `wku_1e4c1baf4001MBQw4BavCd0vX8`** scheduled for `2026-11-20T00:00:00Z` (exact command recorded in the wakeup prompt).
>
> **Task ID (authoritative):** `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`
>
> **Unskippable heavy-work contract (execute in order):**
> 1. **Env/safety:** `.env` absent; `LIVE_TRADING_ENABLED` unset/false (paper-only). `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `./scripts/verify_env.sh --check`. Tests: `python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py` (12/12), `python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py` (9/9). No full-suite enumeration loops; no `research_state/` enumeration loops.
> 2. **If you arrive before 2026-11-20T00:00:00Z:** do not run retired `--days 7` acquisition. Keep pid 58162 alive if present; if not, schedule a wakeup/cron for `2026-11-20T00:00:00Z` (or later) with the exact capture command below and record the schedule ID here. Do not stop with only a timestamp bump.
> 3. **At/after threshold (disjoint, heavy real capture):** persistent process must run:
>    `mkdir -p data/raw/eval67 && PYTHONUNBUFFERED=1 PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py --underlying BTC --days 3.7 --end <NOW-ISO> --out-dir data/raw/eval67 --seal`
>    (or via `scripts/eval67_launch_capture.sh`). Real loaders only (`RealDataUnavailable` on missing); never synthetic/relabeled; never `{"valid": true}`. Verify capture is real, disjoint, floor-compliant before evaluation.
> 4. **Evaluate:** `python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --no-write` then `--seal --task-label EVAL67-BTC-OFLOW-TOX-RV-OOS` → emits `EVAL_67_BTC_OFLOW_TOX_RV_OOS_{COMBINED|BLOCKED}_<TS>.{json,md}`. Under-floor or non-disjoint non-empty real ⇒ `BLOCKED` (no floor weakening). Do not seal on missing/empty state.
> 5. **Seal gate (must exit 0):**
>    `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"`
> 6. **Close session:** update this handoff in place with verified facts (artifact names, verdict, gate exit code, capture sha256/size/window/disjointness, PID/schedule IDs). `data/raw/eval67/` is gitignored — do not commit. Paper-only preserved.
>
> **Completion contract:** end only with (a) sealed EVAL-67 + gate exit 0, OR (b) genuinely live **persistent** acquisition with recorded PID/command/liveness, OR (c) recorded **scheduled wakeup/cron** for earliest disjoint time with exact command. No other stopping point is acceptable.
>
> ## STATUS (verified 2026-11-16T14:23:03Z)
>
> - **On-charter campaign:** `CAMPAIGN_CLOSED`. EVAL-66 sealed `BLOCKED` (gate exit 0) — `research_state/EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,BLOCKED}_20261116T121851Z.{json,md}` (`INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`).
> - **Persistent bridge (verified):** pid **58162** alive (`python3 scripts/eval67_capture_bridge.py`), heartbeat `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_58162.json` phase `waiting`, threshold `2026-11-20T00:00:00Z`, started `2026-11-16T14:25:52Z`. **Backup wakeup** `wku_1e4c1baf4001MBQw4BavCd0vX8` scheduled for `2026-11-20T00:00:00Z` (fires if bridge died before threshold). If this process dies before threshold, relaunch via `scripts/eval67_launch_capture.sh` (or schedule wakeup) and record new PID here.
> - **Sealed (immutable):** EVAL-02..62, EVAL-64..66 sealed; **EVAL-63 never sealed**. EVAL-46..60,62,64,65 `NO-GO CONFIRMED (PASS)`; EVAL-61 `NO-GO` (artifact, superseded by 62); EVAL-66 `BLOCKED`.
> - **EVAL-67 artifacts present (pre-work):** prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}`; runner/tests/scripts present; `data/raw/eval67/` absent (created by acquisition). Seal-gate currently **exit 1** (expected: prereg matches, no `COMBINED_*`/`BLOCKED_*` yet).
> - **Backup wakeup recorded:** `wku_1e4c1baf4001MBQw4BavCd0vX8` at `2026-11-20T00:00:00Z` (completion contract outcome (c)).
> - **Untracked new files (do not commit):** `scripts/eval67_btc_oflow_tox_rv_oos.py`, `scripts/eval67_launch_capture.sh`, `scripts/eval67_capture_bridge.py`, `tests/test_eval67_btc_oflow_tox_rv_oos.py`, `research_state/EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}`, `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_58162.json`. `data/raw/eval66/`, `data/raw/eval67/` gitignored.
>
> ## AUTHORITATIVE NEXT TASK
>
> **EVAL-67 — BTC options order-flow (tox/imbalance) → realized-vol OOS replication** (`INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`). Heavy, pre-registered, real-data-only, floor-compliant, **disjoint** (>= 2026-11-20T00:00:00Z window). Do not stop at planning/timestamp bumps.
>
> ## REPRO / KEY COMMANDS
>
> ```bash
> export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
> ./scripts/verify_env.sh --check
> python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py   # 12/12
> python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py   # 9/9 baseline
>
> # immutable sealed EVAL-66 check (should be exit 0)
> python3 scripts/check_session_sealed.py \
>   --task-id "INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
>   --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
>   --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
>   --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
>
> # EVAL-67 capture ONLY at/after 2026-11-20T00:00:00Z (retired: naive --days 7 now)
> mkdir -p data/raw/eval67
> PYTHONUNBUFFERED=1 PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py \
>   --underlying BTC --days 3.7 --end <NOW-ISO> --out-dir data/raw/eval67 --seal
>
> # or launch helper (refuses before threshold):
> # bash scripts/eval67_launch_capture.sh
>
> # EVAL-67 dry-run, then seal
> python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --no-write
> python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --seal --task-label EVAL67-BTC-OFLOW-TOX-RV-OOS
>
> # EVAL-67 seal gate (after prereg + sealed result exist) — must be exit 0
> python3 scripts/check_session_sealed.py \
>   --task-id "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" \
>   --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
>   --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" \
>   --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"
> ```
>
> ## PROHIBITED / INVARIANTS (non-negotiable)
>
> - Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62 or EVAL-64..66 artifacts or `src/`. Append-only for new authorized work.
> - Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting.
> - Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement.
> - No pre-registered floor weakening. Under-floor or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
> - Do **not** use retired compact task ID `INIT-2026-11-16T122919Z-...`; use `INIT-2026-11-16T13:25:40Z-...`.
> - Do **not** run retired naive `--days 7` BTC acquisition before `2026-11-20T00:00:00Z`; use corrected `--days 3.7 --end <NOW-ISO>`.
> - Reuse existing `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`, and `scripts/eval60_*`/`eval66_*`/`eval67_*` patterns; no `phaseNN_*` wrappers.
> - `data/raw/eval66/`, `data/raw/eval67/` gitignored — do not commit/push.
> - No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only.
>
> ## SESSION LOG (append-only, recent)
>
> - 2026-11-16T12:19:00Z: Sealed **EVAL-66 `BLOCKED`** (under-floor, non-disjoint ETH; gate exit 0). `CAMPAIGN_CLOSED`.
> - **2026-11-16T13:39:12Z:** De-risked EVAL-67 path (real smoke OK, dry-run `BLOCKED` with `disjointness_ok=true`, math proven), started persistent bridge pid 58162 waiting to threshold; added `eval67_capture_bridge.py`/`eval67_launch_capture.sh`; backup wakeup scheduled for 2026-11-20T00:05:00Z. Seal-gate exit 1 expected (no verdict yet).
> - **2026-11-16T14:23:03Z (this session):** Verified bridge pid 58162 alive (`phase waiting`, threshold 2026-11-20T00:00:00Z, heartbeat updated 2026-11-16T14:22:52Z). Refreshed this single durable handoff as the authoritative initial task message for the next agentic session (clear priorities, removed bottlenecks, explicit completion contract). No sealed artifacts or `src/` modified; no synthetic data; paper-only.
> - **2026-11-16T14:26:11Z (this session):** Verified bridge pid 58162 alive (`phase waiting`, heartbeat `2026-11-16T14:25:52Z`). Ran `pytest tests/test_eval67_btc_oflow_tox_rv_oos.py` + `tests/test_eval66_eth_oflow_tox_rv_oos.py` → **21/21 passed** (EVAL-67 12/12, EVAL-66 9/9). Seal gate for EVAL-67 **exit 1** as expected (prereg matches; no `COMBINED_*`/`BLOCKED_*` verdict yet — capture not yet run). **Recorded backup wakeup `wku_1e4c1baf4001MBQw4BavCd0vX8` at `2026-11-20T00:00:00Z`** (completion contract outcome (c)) with the exact capture/evaluate/seal/gate command sequence. This is the final handoff refresh this session; no sealed artifacts or `src/` modified; no synthetic data; paper-only. The session is **not finished** — completion requires sealed EVAL-67 + gate exit 0, OR genuinely live persistent acquisition, OR recorded scheduled wakeup (now satisfied).
- **2026-11-16T14:28:41Z (this session, re-verified):** Bridge pid **58162** still alive (`phase waiting`, heartbeat `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_58162.json` `started_at 2026-11-16T14:28:52Z`, `threshold 2026-11-20T00:00:00Z`). `./scripts/verify_env.sh --check` → exit 0. `pytest tests/test_eval67_btc_oflow_tox_rv_oos.py tests/test_eval66_eth_oflow_tox_rv_oos.py` → **21/21 passed**. `data/raw/eval67/` still absent (capture not yet run — before `2026-11-20T00:00:00Z` threshold). EVAL-67 seal gate **exit 1** expected (prereg present; no `COMBINED_*`/`BLOCKED_*` verdict yet). No sealed artifacts or `src/` modified; no synthetic data; paper-only. Backup wakeup `wku_1e4c1baf4001MBQw4BavCd0vX8` remains recorded for `2026-11-20T00:00:00Z`. Session **not finished** — completion contract still requires (a) sealed EVAL-67 + gate exit 0, OR (b) genuinely live persistent acquisition, OR (c) recorded scheduled wakeup (satisfied).
>
> ## SEALED STATE (immutable; append only)
>
> EVAL-02..62,64..66 sealed. EVAL-63 never sealed. EVAL-46..60,62,64,65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`. On-charter closed; EVAL-67 is the next authorized heavy falsification campaign.
