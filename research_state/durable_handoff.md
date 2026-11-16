# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T09:22:30Z, verified):** Continue and complete **`INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`** end-to-end now (or honestly close the campaign if infeasible per the floor). EVAL-65 is **SEALED `NO-GO CONFIRMED (PASS)`** (gate exit 0): only the isolated ETH 1m/72-bar slice remains on-charter as EVAL-66 OOS replication. **This session progress (not sealed):** env verified (`./scripts/verify_env.sh --check` OK; `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `.env` absent; `LIVE_TRADING_ENABLED` unset), and EVAL-66 tooling/tests are built and passing (`python3 -m py_compile scripts/eval66_eth_oflow_tox_rv_oos.py tests/test_eval66_eth_oflow_tox_rv_oos.py` OK; `python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py` → 7 passed). A fresh real ETH 7d acquisition was started into `data/raw/eval66/` via `scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66` (single process, public read-only, polite rate limiting) but **no capture file has been written to `data/raw/eval66/` yet** as of this handoff update (acquisition is heavy/slow and may still be running; log `/tmp/eval66_acquire.log` currently empty). **No EVAL-66 PREREGISTRATION/COMBINED/BLOCKED artifact is sealed.** Do NOT stop at handoff edits or env checks. Do NOT re-run, re-litigate, or re-seal EVAL-02..65. Do NOT produce a timestamp-only checkpoint.

## STATUS (verified 2026-11-16T09:22:30Z)

- **EVAL-65 (wrapper-free predictiveness, namesake information-content) is SEALED `NO-GO CONFIRMED (PASS)`** on the real 7d BTC+ETH captures (immutable).
  - Task: `INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL`
  - Prereg: `research_state/EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_20261116T084947Z.{json,md}`
  - Combined: `research_state/EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_20261116T084947Z.{json,md}`
  - Seal gate exit 0. BTC 0 aggregated pass (best IC 0.08833117025428101, `imbalance::bar60.0::h72`). ETH 2 aggregated pass `tox::bar60.0::h72` (IC 0.08325402088791962, p=0.006993) and `imbalance::bar60.0::h72` (IC 0.11759773937293551, p=0.000999); BH-FDR rejected both ETH configs. GO bar not met (not on both assets + BH-FDR). ETH 1m/72-bar slice is the only suggestive signal and requires isolated disjoint-window OOS replication (EVAL-66).
- **EVAL-64 sealed `NO-GO CONFIRMED (PASS)`** (immutable, gate exit 0). **EVAL-63 never sealed** (no artifact). EVAL-02..62 sealed immutable as previously recorded.
- **EVAL-66 (this session, in progress, NOT sealed):** `INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`.
  - Tooling ready: `scripts/eval66_eth_oflow_tox_rv_oos.py`, `tests/test_eval66_eth_oflow_tox_rv_oos.py` (ETH-only, configs restricted to `tox::bar60.0::h72` and `imbalance::bar60.0::h72`; reuses `e62.build_states` and `e64._underlying_floor_strict`/floor verbatim; EVAL-65 stats/GO bar). `py_compile` OK; `pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py` → **7 passed**. `--no-write` on empty `data/raw/eval66` reports `BLOCKED` (floor_ok false, n_configs 0) as expected.
  - Acquisition attempted (fresh, real ETH, 7d): `python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 [--seal]` started 2026-11-16T~09:01Z (single process, public read-only, polite rate limiting). As of 2026-11-16T09:22:30Z `data/raw/eval66/` is empty and `/tmp/eval66_acquire.log` has no output; acquisition may still be running or may need restart/monitoring in this environment. **No `three_way_ETH_*.json` captured yet; disjointness from eval63 ETH window (`data/raw/eval63/three_way_ETH_20261116T064816Z.json`, 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z) is not yet verifiable.**
  - **No sealed EVAL-66 artifacts exist** (`research_state/EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,COMBINED,BLOCKED}_*` absent for this task).
- Env (verified): `./scripts/verify_env.sh --check` OK. `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`. `.env` absent; `LIVE_TRADING_ENABLED` unset. Paper-only.

## AUTHORITATIVE NEXT TASK (timestamped, heavy — execute in full)

**Task ID:** `INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`

**Objective (on-charter, final replication check):** Complete EVAL-66: acquire a fresh, disjoint real ETH 7d window meeting the sealed EVAL-64 feasible floor, then seal EVAL-66 (COMBINED or honest BLOCKED) with exit-0 gate. This determines whether the suggestive EVAL-65 ETH 1m/72-bar slice (`tox::bar60.0::h72`, `imbalance::bar60.0::h72`) is real or sample-specific. Failed replication or honest `BLOCKED` with no feasible path ⇒ **campaign closure** (namesake definitively closed). Successful replication on the pre-registered configs/floor ⇒ define a concrete, pre-registered traded-form follow-up as the next task (new ID).

**Step 1 — Env/bootstrap (verified; re-confirm):**
```bash
./scripts/verify_env.sh --check
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
Confirm `.env` absent and `LIVE_TRADING_ENABLED` unset. Paper-only.

**Step 2 — Complete fresh, disjoint real ETH acquisition (public read-only, polite rate limiting, ONE process):**
- Monitor/complete the in-progress acquisition or (re)start it if not running: `mkdir -p data/raw/eval66 && python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal` (single process). Capture must land in `data/raw/eval66/` as `three_way_ETH_*.json` (+ manifest if `--seal`).
- **Disjointness:** verify the new capture window is disjoint from `data/raw/eval63/three_way_ETH_20261116T064816Z.json` (2026-11-09T06:48:16Z..2026-11-16T06:48:16Z); record/verify timestamps and hashes. No synthetic data.
- **Feasible floor (EVAL-64, must meet on the new capture):** `n_surface_snapshots>=1000`, `n_surface_instruments>=100`, `n_surface_bars_5m>=1000`, `n_option_trades>=2000`, `n_of_instruments>=150`, `of_span_seconds>=82000`, `n_of_bars_5m>=240`, `n_perp_bars_5m>=1000`, `perp_span_seconds>=300000`, `n_common_bars_5m>=240`. Check via `scripts.eval64_orderflow_realized_vol_markpath_feasible._underlying_floor_strict`.
- **If floor not met ⇒ seal `EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_<UTC>` with honest diagnostics, do not weaken floor, and proceed to campaign closure (Step 5).**

**Step 3 — Dry-run, then seal EVAL-66 (tooling already built/tested):**
- `python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py` (confirm 7 passed)
- Dry-run: `python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --no-write`
- Seal (heavy): `python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS`

**Step 4 — Seal gate (exit 0 required):**
```bash
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
```

**Step 5 — After sealing:** update this handoff in place with verified paths/numbers and the **definitive outcome**. If EVAL-66 `NO-GO` (fails to replicate) or `BLOCKED` with no feasible path: record `CAMPAIGN_CLOSED` (namesake options order-flow → realized-vol hypothesis not supported on real BTC/ETH, traded and informational forms closed, ETH slice non-replicating), and state that no further on-charter rungs are justified. If EVAL-66 GO (replicates on the pre-registered slice/floor): define a concrete, pre-registered traded-form follow-up as the next task (new ID). Do not invent synthetic or off-charter rungs.

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
# verify floor on capture, then:
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --no-write
python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
```

## BOTTLENECKS

- **Cleared:** EVAL-65 sealed (gate exit 0). EVAL-66 tooling/tests built and passing (7/7); env bootstrapped; `.env` absent / paper-only.
- **Active (EVAL-66, blocking seal):** fresh disjoint real ETH 7d capture not yet present in `data/raw/eval66/` (acquisition attempted 2026-11-16T~09:01Z, single process, public read-only; log `/tmp/eval66_acquire.log` empty at 2026-11-16T09:22:30Z, dir still empty). Must complete acquisition, verify disjointness vs eval63 ETH window (2026-11-09T06:48:16Z..2026-11-16T06:48:16Z) and verify sealed EVAL-64 feasible floor on the capture. Acquisition is heavy (Deribit+OKX, polite rate limiting); run exactly ONE process and monitor to completion. **If the feasible floor cannot be met on a fresh window, seal `BLOCKED` (never `NO-GO`) and close the campaign — do not weaken the floor.** `data/raw/eval66/` (if created) will be real and large; keep gitignored, do not commit captures.
- **Cleared (process):** timestamp-only handoff-edit loop prohibited. A session that does not produce a sealed artifact for its task-id (or an honest `BLOCKED` with exit 0 gate) is a failure.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal EVAL-02..65; do not edit sealed artifacts or `src/`. EVAL-66 must be sealed once (append-only); do not edit its artifacts after sealing.
- Never synthetic fallback; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement. Public read-only network only, polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`; no `phaseNN_*` wrappers.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies (root retired pointers stay retired). Update this file in place with verified facts only.
- Any P&L must be spot-normalized and use mark-path/realized costed returns (regression-guard pattern as in EVAL-62); never reintroduce the EVAL-61 dollar-as-return artifact.
- Do not weaken a pre-registered floor to force a verdict. Under-floor real data ⇒ `BLOCKED`, not `NO-GO`.

## SEALED STATE (immutable; append only)

EVAL-02..65 sealed. EVAL-46..60, EVAL-62, EVAL-64, **EVAL-65**: **NO-GO CONFIRMED (PASS)**, gate exit 0. EVAL-61: **NO-GO CONFIRMED (PASS)** but measurement-artifact (superseded by EVAL-62). **EVAL-63: NEVER sealed (no artifact exists); superseded by EVAL-64.** **EVAL-66: not yet sealed** (no PREREG/COMBINED/BLOCKED artifact). Re-running/re-sealing prohibited for sealed evals.

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
- **2026-11-16T08:49:47Z (this session, heavy seal):** Verified env (`./scripts/verify_env.sh --check` OK), EVAL-64 gate exit 0, EVAL-65 tests 8/8. **Sealed EVAL-65 `NO-GO CONFIRMED (PASS)`** (`EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_{PREREGISTRATION,COMBINED}_20261116T084947Z.{json,md}`; task `INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL`; floor_ok=true; BTC 0 aggregated pass, best IC 0.0883; ETH 2 aggregated pass `tox::bar60::h72` IC 0.0833 and `imbalance::bar60::h72` IC 0.1176; BH-FDR rejected `ETH::tox::bar60::h72`, `ETH::imbalance::bar60::h72`; GO bar not met). **Seal gate exit 0.** Handoff updated in place with EVAL-66 (isolated disjoint-window ETH OOS replication of 1m/72-bar slice, or campaign closure on BLOCKED/non-replication) as the next heavy on-charter task. No synthetic data; no sealed EVAL-02..64 edits; no re-runs.
- **2026-11-16T09:22:30Z (this session):** Verified env (`./scripts/verify_env.sh --check` OK, paper-only). Built EVAL-66 `scripts/eval66_eth_oflow_tox_rv_oos.py` + `tests/test_eval66_eth_oflow_tox_rv_oos.py` (retarget of sealed EVAL-65, ETH-only `tox/imbalance::bar60::h72`, EVAL-64 floor); `py_compile` OK, `pytest` 7 passed, `--no-write` on empty eval66 dir → BLOCKED as expected. Attempted fresh real ETH 7d acquisition into `data/raw/eval66/` (single process, public read-only, polite rate limiting) — **no capture written yet** as of 09:22:30Z (dir empty, log empty); acquisition must be completed/monitored. **No EVAL-66 artifacts sealed.** Handoff updated in place with verified progress and explicit completion steps (acquire+verify disjoint/floor → dry-run → seal → gate, or honest BLOCKED). No EVAL-02..65 modified/re-run; no synthetic data.

(End of file)
