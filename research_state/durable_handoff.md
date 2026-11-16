# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T09:24:56Z, verified):** Execute and complete **`INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`** end-to-end now (or honestly close the campaign if infeasible per the floor). EVAL-65 is **SEALED `NO-GO CONFIRMED (PASS)`** (gate exit 0): only the isolated ETH 1m/72-bar slice remains on-charter as EVAL-66 OOS replication. **Verified this session:** env bootstrapped (`./scripts/verify_env.sh --check` OK; `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `.env` absent; `LIVE_TRADING_ENABLED` unset, paper-only). EVAL-66 tooling/tests exist and pass: `scripts/eval66_eth_oflow_tox_rv_oos.py`, `tests/test_eval66_eth_oflow_tox_rv_oos.py` (`python3 -m py_compile ...` OK; `PYTHONPATH=.venv-deps python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py` → **7 passed**). `--no-write` on empty `data/raw/eval66` reports `BLOCKED` (floor_ok false, n_configs 0) as expected. **Bottleneck:** `data/raw/eval66/` is empty, no `eval60_acquire`/`eval66` process is running, and `/tmp/eval66_acquire.log` is empty — **no fresh disjoint ETH capture exists; no EVAL-66 PREREG/COMBINED/BLOCKED artifact is sealed.** Do NOT stop at handoff edits or env checks. Do NOT re-run, re-litigate, or re-seal EVAL-02..65. Do NOT produce a timestamp-only checkpoint.

## STATUS (verified 2026-11-16T09:24:56Z)

- **EVAL-65 SEALED `NO-GO CONFIRMED (PASS)`** (immutable, gate exit 0). Task `INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL`. Prereg `research_state/EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_20261116T084947Z.{json,md}`; combined `research_state/EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_20261116T084947Z.{json,md}`. GO bar not met; only ETH 1m/72-bar slice (`tox::bar60.0::h72`, `imbalance::bar60.0::h72`) remains suggestive and requires isolated disjoint-window OOS replication (EVAL-66).
- **EVAL-64 sealed `NO-GO CONFIRMED (PASS)`** (immutable). **EVAL-63 never sealed** (no artifact). EVAL-02..62 sealed immutable.
- **EVAL-66 (NOT sealed):** `INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`. Tooling/tests ready and passing (7/7). Acquisition **not running**; `data/raw/eval66/` empty; no `three_way_ETH_*.json`; disjointness vs eval63 ETH window (`data/raw/eval63/three_way_ETH_20261116T064816Z.json`, 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z) unverified. `research_state/EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,COMBINED,BLOCKED}_*` absent.
- Env: `./scripts/verify_env.sh --check` OK. `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`. `.env` absent; `LIVE_TRADING_ENABLED` unset. Paper-only.

## AUTHORITATIVE NEXT TASK (timestamped, heavy — execute in full)

**Task ID:** `INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`

**Objective (on-charter, final replication check):** Acquire a fresh, **disjoint** real ETH 7d window meeting the sealed EVAL-64 feasible floor, then seal EVAL-66 (COMBINED or honest BLOCKED) with exit-0 gate. Determines whether the EVAL-65 ETH 1m/72-bar slice (`tox::bar60.0::h72`, `imbalance::bar60.0::h72`) is real or sample-specific. Failed replication or honest `BLOCKED` with no feasible path ⇒ **campaign closure** (namesake definitively closed). Successful replication on the pre-registered configs/floor ⇒ define a concrete, pre-registered traded-form follow-up as the next task (new ID).

**Step 1 — Env/bootstrap (re-confirm):**
```bash
./scripts/verify_env.sh --check
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
Confirm `.env` absent and `LIVE_TRADING_ENABLED` unset. Paper-only.

**Step 2 — Fresh, disjoint real ETH acquisition (public read-only, polite rate limiting, ONE process):**
```bash
mkdir -p data/raw/eval66
python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal
```
- Capture must land in `data/raw/eval66/` as `three_way_ETH_*.json` (+ manifest). **Disjointness:** verify new window disjoint from `data/raw/eval63/three_way_ETH_20261116T064816Z.json` (2026-11-09T06:48:16Z..2026-11-16T06:48:16Z); record/verify timestamps and hashes. No synthetic data.
- **Feasible floor (EVAL-64, must meet):** `n_surface_snapshots>=1000`, `n_surface_instruments>=100`, `n_surface_bars_5m>=1000`, `n_option_trades>=2000`, `n_of_instruments>=150`, `of_span_seconds>=82000`, `n_of_bars_5m>=240`, `n_perp_bars_5m>=1000`, `perp_span_seconds>=300000`, `n_common_bars_5m>=240`. Check via `scripts.eval64_orderflow_realized_vol_markpath_feasible._underlying_floor_strict`.
- **If floor not met ⇒ seal `EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_<UTC>` with honest diagnostics, do not weaken floor, and proceed to campaign closure (Step 5).**

**Step 3 — Dry-run, then seal EVAL-66:**
```bash
python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --no-write
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS
```

**Step 4 — Seal gate (exit 0 required):**
```bash
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
```

**Step 5 — After sealing:** update this handoff in place with verified paths/numbers and the **definitive outcome**. If EVAL-66 `NO-GO` (fails to replicate) or `BLOCKED` with no feasible path: record `CAMPAIGN_CLOSED` (namesake options order-flow → realized-vol hypothesis not supported on real BTC/ETH, traded and informational forms closed, ETH slice non-replicating) and state that no further on-charter rungs are justified. If EVAL-66 GO (replicates on pre-registered slice/floor): define a concrete, pre-registered traded-form follow-up as the next task (new ID). Do not invent synthetic or off-charter rungs.

## REPRO / KEY COMMANDS
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check

# sealed, immutable
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL" \
  --glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_*" \
  --require-glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_*"

# EVAL-66 (authoritative next, heavy)
python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py
mkdir -p data/raw/eval66
python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --no-write
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
```

## BOTTLENECKS

- **Cleared:** EVAL-65 sealed (gate exit 0). EVAL-66 tooling/tests built and passing (7/7). Env bootstrapped (`.venv-deps` present); `.env` absent / paper-only.
- **Active (blocking EVAL-66 seal):** no fresh disjoint real ETH 7d capture in `data/raw/eval66/` (dir empty); no acquisition process running. Must run acquisition (single process, public read-only, polite rate limiting), verify disjointness vs `data/raw/eval63/three_way_ETH_20261116T064816Z.json` (2026-11-09T06:48:16Z..2026-11-16T06:48:16Z) and verify EVAL-64 feasible floor on the capture. Acquisition is heavy (Deribit+OKX); monitor to completion. **Under-floor real data ⇒ seal `BLOCKED` (never `NO-GO`) and close campaign — do not weaken floor.** `data/raw/eval66/` captures are real/large; keep gitignored, do not commit.
- **Process:** timestamp-only handoff-edit loop prohibited. A session that does not produce a sealed artifact for its task-id (or an honest `BLOCKED` with exit-0 gate) is a failure.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal EVAL-02..65; do not edit sealed artifacts or `src/`. EVAL-66 must be sealed once (append-only).
- Never synthetic fallback; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement. Public read-only network only, polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`; no `phaseNN_*` wrappers.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only.
- P&L must be spot-normalized with mark-path/realized costed returns (EVAL-62 pattern); never reintroduce EVAL-61 dollar-as-return artifact.
- Do not weaken a pre-registered floor to force a verdict. Under-floor real data ⇒ `BLOCKED`, not `NO-GO`.

## SEALED STATE (immutable; append only)

EVAL-02..65 sealed. EVAL-46..60, EVAL-62, EVAL-64, **EVAL-65**: **NO-GO CONFIRMED (PASS)**, gate exit 0. EVAL-61: **NO-GO CONFIRMED (PASS)** but measurement-artifact (superseded by EVAL-62). **EVAL-63: NEVER sealed.** **EVAL-66: not yet sealed.** Re-running/re-sealing prohibited for sealed evals.

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
- **2026-11-16T09:24:56Z (this session):** Verified env (`./scripts/verify_env.sh --check` OK, paper-only), EVAL-66 tooling/tests present and passing (7/7 via `.venv-deps`), `--no-write` on empty eval66 → BLOCKED as expected. Confirmed **no acquisition running** and `data/raw/eval66/` empty (no capture). Updated durable handoff in place with verified bottleneck and explicit, unambiguous EVAL-66 completion steps (acquire+verify disjoint/floor → dry-run → seal → gate, or honest BLOCKED → campaign closure). No EVAL-02..65 modified/re-run; no synthetic data; no sealed artifacts produced.

(End of file)
