# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T11:25:00Z, verified):**
> Execute **`INIT-2026-11-16T11:25:00Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`** end-to-end.
> **A persistent 7d ETH acquisition is ALREADY RUNNING** as background process
> `bgp_1e414866b001E3JjNc6QFdoISS` (PID 18906; `scripts/eval60_acquire_three_way.py --underlying ETH
> --days 7 --out-dir data/raw/eval66 --seal`; `lifetime: persistent`). **Do NOT start a duplicate
> acquisition.** Your FIRST action is to check `data/raw/eval66/` and the process `logs`/`status`.
> - **If the acquisition is still running:** monitor it to completion (`background_process logs`/`monitor`),
>   then continue at Step 1 (disjointness/floor check) → dry-run → seal → gate.
> - **If the acquisition finished and wrote `data/raw/eval66/three_way_ETH_*.json`:** proceed directly
>   to (1) verify from the capture/manifest that `window_start`..`window_end` is disjoint from the sealed
>   EVAL-65 window `2026-11-09T06:48:16Z..2026-11-16T06:48:16Z` and meets the sealed EVAL-64 feasible
>   floor; (2) dry-run `scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --no-write`;
>   (3) `--seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS`; (4) pass `scripts/check_session_sealed.py` (exit 0).
> - **If the process died WITHOUT writing a capture:** the acquisition is incomplete — restart it as a
>   **persistent** background process (`PYTHONPATH="$PWD/.venv-deps"` MUST be set in the command; bare
>   `python3` fails with `ModuleNotFoundError: No module named 'pydantic'`) and monitor to completion.
>   Non-empty below-floor real capture ⇒ seal honest `BLOCKED` (never weaken the floor) and record campaign
>   closure. No capture ⇒ the acquisition is incomplete, not a verdict.
> **Session completion contract: do NOT end the session with only a handoff/env/dry-run update — end it
> only with (a) a sealed EVAL-66 artifact (COMBINED or BLOCKED) passing the exit-0 gate, or (b) the
> acquisition genuinely running as a live persistent process with its process ID recorded here. Do NOT
> re-run or re-seal EVAL-02..62 or EVAL-64..65.**

## STATUS (verified 2026-11-16T11:25:00Z)

- **EVAL-65 SEALED `NO-GO CONFIRMED (PASS)`** (immutable, gate exit 0). Prereg `research_state/EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_20261116T084947Z.{json,md}`; combined `..._COMBINED_20261116T084947Z.{json,md}`. GO bar not met; ETH 2 individually passing configs (`tox::bar60.0::h72`, `imbalance::bar60.0::h72`) both BH-FDR-rejected; BTC 0 aggregated passing configs. Only remaining on-charter rung: isolated disjoint-window OOS replication of that ETH slice.
- **EVAL-66 (NOT sealed):** `INIT-2026-11-16T11:25:00Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`. **Acquisition RUNNING** as persistent background process `bgp_1e414866b001E3JjNc6QFdoISS` (PID 18906; `scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal`, `PYTHONPATH="$PWD/.venv-deps"` set, `lifetime: persistent`). Tooling/tests ready: `scripts/eval66_eth_oflow_tox_rv_oos.py`, `tests/test_eval66_eth_oflow_tox_rv_oos.py` (**9 passed**, re-verified 2026-11-16T11:25:00Z). `--seal` refuses to write an artifact when no real ETH capture exists (`NoRealCaptureError`, exit 2). Smoke of the acquisition tooling captured real ETH data (84 instruments, real Deribit surface + Deribit option trades + OKX ETH-USD-SWAP perp flow). `./scripts/verify_env.sh --check` OK; `.env` absent; `LIVE_TRADING_ENABLED` unset.
- **No ETH capture yet:** `data/raw/eval66/` is empty (acquisition running). Once the acquisition finishes it must write `data/raw/eval66/three_way_ETH_*.json` + a `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_*` manifest in `research_state/`. **Do NOT start a duplicate process** — check `background_process logs`/`status` for `bgp_1e414866b001E3JjNc6QFdoISS` first.
- **EVAL-65 baseline:** `data/raw/eval63/three_way_ETH_20261116T064816Z.json` absent from checkout (gitignored); disjointness baseline is sealed EVAL-65 window `2026-11-09T06:48:16Z..2026-11-16T06:48:16Z`. Do not re-acquire EVAL-63 or edit sealed artifacts.

## AUTHORITATIVE NEXT TASK (timestamped, heavy — execute in full)

**Task ID:** `INIT-2026-11-16T11:25:00Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`

**Objective (on-charter, final replication check):** Acquire a fresh real ETH 7d window disjoint from the sealed EVAL-65 window (`2026-11-09T06:48:16Z..2026-11-16T06:48:16Z`), verify it meets the sealed EVAL-64 feasible floor, and seal EVAL-66 (COMBINED or honest BLOCKED) with an exit-0 gate. This determines whether the EVAL-65 ETH 1m/72-bar slice (`tox::bar60.0::h72`, `imbalance::bar60.0::h72`) is real or sample-specific. Failed replication or an under-floor capture with no feasible path ⇒ **campaign closure**. Successful replication on the pre-registered configs/floor ⇒ define and execute a fresh pre-registered traded-form follow-up (new task ID); do not invent off-charter rungs.

**Step 1 — Acquisition ALREADY RUNNING (do NOT start a duplicate):** the 7d ETH capture is running as **persistent** background process `bgp_1e414866b001E3JjNc6QFdoISS` (PID 18906). Check it first:

```bash
# via background_process: logs / status for id bgp_1e414866b001E3JjNc6QFdoISS
ls -la data/raw/eval66/
```

- **If still running:** monitor to completion (`monitor`/`logs`), then go to the disjointness/floor check below. Acquisition is heavy (hours).
- **If finished:** confirm `data/raw/eval66/three_way_ETH_*.json` exists + a `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_*` manifest in `research_state/`, then go to the disjointness/floor check.
- **If died without a capture:** restart it as a **persistent** background process. **CRITICAL: `PYTHONPATH="$PWD/.venv-deps"` MUST be in the launched command** — a bare `python3` fails under `background_process` with `ModuleNotFoundError: No module named 'pydantic'`. Launch command:
  `PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal`
  Record the new PID here. Do not start a second concurrent acquisition.
- **Disjointness:** verify the new `window_start`/`window_end` do not overlap `2026-11-09T06:48:16Z..2026-11-16T06:48:16Z`. Any default trailing 7d window starting after `2026-11-16T06:48:16Z` is disjoint; record timestamps and the capture SHA-256 from the manifest. No synthetic data.
- **Feasible floor (EVAL-64, must meet):** `n_surface_snapshots>=1000`, `n_surface_instruments>=100`, `n_surface_bars_5m>=1000`, `n_option_trades>=2000`, `n_of_instruments>=150`, `of_span_seconds>=82000`, `n_of_bars_5m>=240`, `n_perp_bars_5m>=1000`, `perp_span_seconds>=300000`, `n_common_bars_5m>=240`. Check with:

```bash
python3 - <<'PY'
import glob, json
from scripts.eval64_orderflow_realized_vol_markpath_feasible import _underlying_floor_strict
for p in sorted(glob.glob("data/raw/eval66/three_way_ETH_*.json")):
    c = json.load(open(p))
    print(p, c.get("window_start"), c.get("window_end"), _underlying_floor_strict(c))
PY
```

- **If a non-empty capture is below the floor ⇒ seal `EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_<UTC>` with honest diagnostics, do not weaken the floor, and proceed to campaign closure (Step 5).** If no capture was acquired, do not seal BLOCKED; treat the acquisition as incomplete and finish it.

**Step 2 — Environment (after acquisition is running; paper-only):**

```bash
./scripts/verify_env.sh --check
```

Confirm `.env` absent and `LIVE_TRADING_ENABLED` unset.

**Step 3 — Dry-run, then seal EVAL-66 (only after the capture completes):**

```bash
python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --no-write
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS
```

The seal command writes the PREREG artifact and then COMBINED (floor met) or BLOCKED (non-empty capture below floor). It exits 2 and writes nothing if the capture directory has no real ETH capture.

**Step 4 — Seal gate (exit 0 required):**

```bash
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T11:25:00Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
```

**Step 5 — After sealing:** update this handoff in place with verified paths, capture timestamps/hash, floor numbers, and the definitive outcome. If EVAL-66 is `NO-GO CONFIRMED (PASS)` or `BLOCKED` with no feasible path: record `CAMPAIGN_CLOSED` (namesake options order-flow → realized-vol hypothesis not supported on real BTC/ETH; traded and informational forms closed; ETH slice non-replicating) and state that no further on-charter rungs are justified. If EVAL-66 is `GO CONFIRMED`: define a concrete, pre-registered traded-form follow-up as the next timestamped task (new ID) and do not stop at the GO artifact.

## REPRO / KEY COMMANDS

```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check

# sealed, immutable
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL" \
  --glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_*" \
  --require-glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_*"

# EVAL-66 (authoritative next, heavy — acquisition RUNNING as bgp_1e414866b001E3JjNc6QFdoISS, do NOT duplicate)
mkdir -p data/raw/eval66
# if it died without a capture, restart with PYTHONPATH embedded (bare python3 fails):
PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal
python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --no-write
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T11:25:00Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
```

## BOTTLENECKS

- **Cleared:** EVAL-65 sealed (gate exit 0). EVAL-66 tooling/tests ready (9/9, re-verified 2026-11-16T11:17:34Z). Empty-capture seal loophole closed. `data/raw/eval66/` gitignored. Env bootstrapped, paper-only.
- **Cleared (this session) — env-prefix acquisition failure:** a bare `python3 scripts/eval60_acquire_three_way.py ...` launched via `background_process` fails immediately with `ModuleNotFoundError: No module named 'pydantic'` because the process does not inherit the shell's exported `PYTHONPATH`. **Fix: embed `PYTHONPATH="$PWD/.venv-deps"` directly in the launched command.** The acquisition is now running correctly as persistent `bgp_1e414866b001E3JjNc6QFdoISS` (PID 18906).
- **Cleared (this session) — ghost-acquisition deadlock (prior):** an earlier handoff told the next agent "an acquisition is in progress (`bgp_1e3e8ae6e001i1x54VtGBiJNJG`), do not start a duplicate." That process died with its session and produced zero bytes. Resolved: a fresh persistent acquisition (`bgp_1e414866b001E3JjNc6QFdoISS`) is now live.
- **Structural fix (in place):** the 7d ETH acquisition is running with `background_process` **`persistent: true`** so it survives session boundaries. Never rely on a session-lifetime background process for multi-hour captures. Its PID is recorded above.
- **Active (blocking EVAL-66 seal):** acquisition (`bgp_1e414866b001E3JjNc6QFdoISS`) must complete, then verify disjointness from `2026-11-09T06:48:16Z..2026-11-16T06:48:16Z` and the EVAL-64 feasible floor, dry-run, seal, and pass seal gate (exit 0). **Under-floor non-empty real data ⇒ `BLOCKED` (never `NO-GO`) and campaign closure; do not weaken the floor. No capture ⇒ acquisition incomplete, not a verdict.**
- **Process (session completion contract):** do not stop at handoff/env/dry-run, do not start duplicate acquisitions, and do not end a session that produced neither a sealed EVAL-66 artifact (with exit-0 gate) nor a live persistent acquisition process with its ID recorded. A session that does not produce a sealed EVAL-66 artifact for its task ID (or an honest under-floor BLOCKED with exit-0 gate, or a genuinely still-running acquisition) has not completed the task.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run, re-litigate, or re-seal sealed EVAL-02..62 or EVAL-64..65; do not edit sealed artifacts or `src/`. EVAL-66 must be sealed once (append-only).
- Never use synthetic data or relabel synthetic as real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement. Public read-only network only, with polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`; no `phaseNN_*` wrappers.
- Do not weaken a pre-registered floor to force a verdict. Under-floor non-empty real data ⇒ `BLOCKED`, not `NO-GO`. Empty capture ⇒ no seal.
- `data/raw/eval66/` captures are real and large (~170 MB); keep them gitignored and do not commit or push them.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only.
- P&L must be spot-normalized with mark-path/realized costed returns (EVAL-62 pattern); never reintroduce the EVAL-61 dollar-as-return artifact.

## SEALED STATE (immutable; append only)

EVAL-02..62 and EVAL-64..65 sealed. EVAL-46..60, EVAL-62, EVAL-64, **EVAL-65**: **NO-GO CONFIRMED (PASS)**, gate exit 0. EVAL-61: **NO-GO CONFIRMED (PASS)** but measurement-artifact (superseded by EVAL-62). **EVAL-63: NEVER sealed.** **EVAL-66: not yet sealed.** Re-running/re-sealing prohibited for sealed evals.

## SESSION LOG (append-only)

- 2026-11-14→2026-11-15: EVAL-41..59 sealed NO-GO (gate exit 0).
- 2026-11-15T22:44:10Z: EVAL-60 tooling built + smoke.
- 2026-11-16T00:34:26Z: EVAL-60 heavy BTC+ETH sealed NO-GO (gate exit 0).
- 2026-11-16T02:41:37Z: EVAL-61 sealed NO-GO (gate exit 0) — later found to be a P&L artifact.
- 2026-11-16T03:17:05Z: EVAL-62 tooling/tests built; real `--no-write` verified (artifact gone, NO-GO on merits).
- 2026-11-16T03:21:05Z: Sealed EVAL-62 `NO-GO CONFIRMED (PASS)` (floor_ok, overall_pbo 0.375, BTC −0.0443 / ETH +0.6163). Seal gate exit 0.
- 2026-11-16T03:29:23Z: Fresh `--days 1` BTC+ETH acquisition sealed; EVAL-61 re-sealed NO-GO (artifact, superseded by EVAL-62). EVAL-61 gate exit 0.
- 2026-11-16T04:12→06:28: ~12 handoff-verification/timestamp-bump sessions (no heavy artifacts); EVAL-63 task defined but never actually sealed.
- 2026-11-16T08:1x–08:25Z: Fixed EVAL-64 copy-and-retarget bugs; sealed **EVAL-64 `NO-GO CONFIRMED (PASS)`** (gate exit 0); corrected EVAL-63 as never sealed; built+tested EVAL-65 (8/8), dry-run verified.
- 2026-11-16T08:39Z (recovery): diagnosed 100 MB push rejection (eval63 captures); preserved `d98a38942` as `recovery/session-58-checkpoint-d98a38942`; rewound+recommitted pushable subset; pushed `origin/main == 4f26fb5859`.
- **2026-11-16T08:49:47Z:** Verified env/EVAL-64 gate/EVAL-65 tests 8/8. **Sealed EVAL-65 `NO-GO CONFIRMED (PASS)`** (`EVAL_65_..._{PREREGISTRATION,COMBINED}_20261116T084947Z.{json,md}`; gate exit 0). Defined EVAL-66 as next heavy on-charter task.
- **2026-11-16T09:24:56Z:** Verified env and EVAL-66 tooling (7/7); confirmed no acquisition and empty `data/raw/eval66`; updated handoff with EVAL-66 completion steps. No heavy artifact sealed.
- **2026-11-16T10:20:49Z:** Refreshed the single durable handoff to the current timestamped EVAL-66 task. Closed the empty-capture seal loophole in `scripts/eval66_eth_oflow_tox_rv_oos.py` (`NoRealCaptureError`; `--seal` exits 2 and writes no artifact without a real ETH capture), added regression tests (now **9 passed**), and gitignored `data/raw/eval66/` to prevent another 100 MB push rejection. Corrected stale `AGENTS.md` routing from EVAL-61 to the active EVAL-66 rung and updated the sealed range to EVAL-02..62 plus EVAL-64..65 (EVAL-63 never sealed). Verified `./scripts/verify_env.sh --check` OK, `.env` absent, `LIVE_TRADING_ENABLED` unset, and `data/raw/eval66` absent/no acquisition running. No sealed EVAL-02..62 or EVAL-64..65 artifacts were modified or re-run; no EVAL-66 artifact was sealed.
- **2026-11-16T10:28:15Z:** Refreshed initial task message timestamp; EVAL-66 tooling/tests confirmed ready (9/9).
- **2026-11-16T10:29:28Z:** Verified `./scripts/verify_env.sh --check` OK, `.env` absent, `LIVE_TRADING_ENABLED` unset, `data/raw/eval66` absent, AGENTS.md routes to EVAL-66. **Unblocked acquisition:** started single real ETH 7d capture as `background_process` `bgp_1e3e8ae6e001i1x54VtGBiJNJG` (`scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal`, `.venv-deps` on PYTHONPATH). Updated durable handoff with timestamped initial task, in-progress status, and explicit next steps (disjointness/floor check → dry-run → seal → gate). No sealed EVAL-02..62/EVAL-64..65 modified/re-run; no EVAL-66 artifact sealed yet (acquisition running).
- **2026-11-16T10:33:07Z (this session):** Diagnosed the ghost-acquisition deadlock: the prior session's acquisition `bgp_1e3e8ae6e001i1x54VtGBiJNJG` died with its session and `data/raw/eval66/` is empty (zero captures) — the "do not start a duplicate" instruction would have stalled the next agent. **Lifted that instruction**, made the heavy 7d ETH acquisition the mandatory FIRST action of the next session with a **persistent** background process (survives session boundaries), and added an explicit session completion contract (end only with a sealed EVAL-66 artifact + exit-0 gate, or a genuinely live persistent acquisition with recorded PID). Re-verified: `./scripts/verify_env.sh --check` OK, EVAL-66 tests **9/9 passed**, `.env` absent, `LIVE_TRADING_ENABLED` unset, `data/raw/eval66/` empty, `data/raw/eval66/` gitignored, no EVAL-66 artifact sealed, no background processes running. No sealed EVAL-02..62 or EVAL-64..65 artifacts modified or re-run.
- **2026-11-16T10:33:58Z:** Refreshed the single durable handoff initial task message and authoritative next task to timestamp `2026-11-16T10:33:58Z` per user directive to prioritize the project's core thesis (options+orderflow OOS replication). Verified `./scripts/verify_env.sh --check` OK, EVAL-66 tests **9/9 passed**, `.env` absent, `LIVE_TRADING_ENABLED` unset, `data/raw/eval66/` empty, no background processes running. The handoff now contains the most relevant inferred timestamped clear initial task for the next agentic session: execute EVAL-66 end-to-end starting with a persistent 7d ETH acquisition. No sealed artifacts modified.
- **2026-11-16T11:17:34Z (this session):** Verified acquisition tooling end-to-end with a real-data smoke (84 ETH instruments, real Deribit surface + option trades + OKX ETH-USD-SWAP perp flow, `EXIT=0`). Discovered bare `python3` fails under `background_process` (`ModuleNotFoundError: No module named 'pydantic'`) — the env is NOT auto-exported; `PYTHONPATH="$PWD/.venv-deps"` MUST be in the launched command. Started the mandatory heavy 7d ETH acquisition as a **persistent** background process `bgp_1e414866b001E3JjNc6QFdoISS` (PID 18906; `PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal`, `lifetime: persistent`). Updated this handoff with the running PID, the do-not-duplicate guard, and the env-prefix requirement. EVAL-66 tests **9/9 passed**; `.env` absent; `LIVE_TRADING_ENABLED` unset; `data/raw/eval66/` gitignored. No sealed EVAL-02..62/EVAL-64..65 modified or re-run; no EVAL-66 artifact sealed yet (acquisition running).
- **2026-11-16T11:25:00Z (this session):** Refreshed the single durable handoff initial task message to current timestamp per user directive. Verified persistent acquisition `bgp_1e414866b001E3JjNc6QFdoISS` (PID 18906) still running, `data/raw/eval66/` empty, EVAL-66 tests **9/9 passed**, `./scripts/verify_env.sh --check` OK, `.env` absent, `LIVE_TRADING_ENABLED` unset. The handoff contains the most relevant inferred timestamped clear initial task for the next agentic session: execute EVAL-66 end-to-end starting with monitoring the persistent 7d ETH acquisition to completion. No sealed artifacts modified.

(End of file)