# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T08:49:47Z, verified):** Execute **`INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`** end-to-end now (or honestly close the campaign if infeasible per the floor). EVAL-65 is **SEALED `NO-GO CONFIRMED (PASS)`** (gate exit 0): the options order-flow toxicity signal does **not** predict subsequent realized volatility on **both** BTC and ETH on the wrapper-free real 7d rank-IC falsification (BTC 0 aggregated passing configs, best IC 0.0883; ETH 2 aggregated passing configs at `tox::bar60::h72` and `imbalance::bar60::h72`, best IC 0.1176, but **BH-FDR rejected both** ETH configs — so the GO bar "on BOTH assets and BH-FDR rejects that config" fails). The namesake signal is non-predictive on real BTC+ETH; the only pre-registered next rung that remains on-charter is an **isolated, disjoint-window out-of-sample replication** of the single ETH predictive slice (1m bar, 72-bar horizon) to determine if it was sample-specific. Do NOT stop at handoff edits or env checks. Do NOT re-run, re-litigate, or re-seal EVAL-02..65. Do NOT produce a timestamp-only checkpoint. Required path: (1) `./scripts/verify_env.sh --check` + `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`, confirm `.env` absent / `LIVE_TRADING_ENABLED` unset (paper-only); (2) **fresh, disjoint real ETH acquisition** (public read-only, polite rate limiting, exactly ONE acquisition process): `mkdir -p data/raw/eval66 && python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal` — verify the capture is real, hashes recorded, and the feasible floor is met (`scripts/eval64_orderflow_realized_vol_markpath_feasible.py` floor: `n_surface_snapshots>=1000`, `n_surface_instruments>=100`, `n_surface_bars_5m>=1000`, `n_option_trades>=2000`, `n_of_instruments>=150`, `of_span_seconds>=82000`, `n_of_bars_5m>=240`, `n_perp_bars_5m>=1000`, `perp_span_seconds>=300000`, `n_common_bars_5m>=240`). If the feasible floor cannot be met on a fresh window, seal **`EVAL_66_..._BLOCKED_<UTC>`** (never `NO-GO`) with honest floor diagnostics and move to campaign closure — do **not** weaken the floor. (3) Copy-and-retarget the **sealed EVAL-65** tooling to `scripts/eval66_eth_oflow_tox_rv_oos.py` + `tests/test_eval66_eth_oflow_tox_rv_oos.py` **before** sealing: ETH-only, restricted to the pre-registered configs `tox::bar60.0::h72` and `imbalance::bar60.0::h72` (the two ETH configs that aggregated-pass in EVAL-65), same EVAL-64 feasible floor, same stats/GO bar logic (IC>0, directional permutation p<0.05, block-bootstrap 95% CI lower>0, BH-FDR rejects), new `EVAL_66_*` artifact IDs. Test first (`pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py`), `--no-write` on the new capture, then `--seal` (heavy). **Under-floor or unavailable real data ⇒ `BLOCKED`, never `NO-GO`.** No synthetic data, no sealed-artifact edits. (4) Seal gate: `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" --require-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*"` (or the `BLOCKED` variant if blocked) — **exit 0 required**. (5) Update this handoff in place with verified paths/numbers and the definitive outcome: if EVAL-66 fails to replicate (NO-GO) or is blocked-with-no-path, the namesake is **definitively closed** — record `CAMPAIGN_CLOSED` with rationale and do not invent further rungs.

## STATUS (verified 2026-11-16T08:53:05Z)

- **EVAL-65 (wrapper-free predictiveness, namesake information-content) is SEALED `NO-GO CONFIRMED (PASS)`** on the real 7d BTC+ETH captures (this session).
  - Task: `INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL`
  - Prereg: `research_state/EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_20261116T084947Z.{json,md}`
  - Combined: `research_state/EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_20261116T084947Z.{json,md}`
  - Seal gate exit 0. Captures (real, 7d, local gitignored): `data/raw/eval63/three_way_BTC_20261116T064816Z.json`, `data/raw/eval63/three_way_ETH_20261116T064816Z.json`.
  - Measured (floor_ok=true, BTC+ETH): verdict `NO-GO CONFIRMED (PASS)`. BTC aggregated: 0 passing configs, best IC **0.08833117025428101** (`imbalance::bar60.0::h72`), `any_pass=false`. ETH aggregated: **2** passing configs (`tox::bar60.0::h72`, IC 0.08325402088791962, p=0.006993; `imbalance::bar60.0::h72`, IC **0.11759773937293551**, p=0.000999, bootstrap CI [0.11737230730730694, 0.06809082156907384, 0.16698495368749275]), best IC 0.11759773937293551, `any_pass=true`. BH-FDR rejected: `ETH::tox::bar60.0::h72`, `ETH::imbalance::bar60.0::h72` (2 configs). Note (per-config detail): `BTC::imbalance::bar60.0::h6` is individually `pass=true` in `per_config` (IC 0.07778425653186352, p=0.012987, bootstrap CI lower 0.002275768270283054) but **not** in BTC aggregated `pass_configs` (`n_pass` 0); GO bar requires both assets + BH-FDR-rejected config(s) and is not met.
  - **Conclusion (information-content):** the options order-flow toxicity signal does **not** predict subsequent realized volatility on **both** real BTC and ETH; the traded-form NO-GO (EVAL-62/64) is not explained by a wrapper cost masking a robust cross-asset signal. The ETH 1m/72-bar slice is the only suggestive signal and is BH-FDR-rejected in-pool — it requires isolated OOS replication on a disjoint real window (EVAL-66) before any claim; absent replication, the namesake is informationally closed.
- **EVAL-64 (feasible-floor traded form) is SEALED `NO-GO CONFIRMED (PASS)`** (immutable). Task `INIT-2026-11-16T07:59:00Z-EVAL64-FEASIBLE-FLOOR-OFLOW-RV-MARKPATH`; `EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_{PREREGISTRATION,COMBINED}_20261116T082210Z`; gate exit 0.
- **EVAL-63 was NEVER actually sealed** (no artifact exists); superseded by EVAL-64. Do not claim sealed.
- **Persistence (prior recovery, this run):** `origin/main` == local `main` == `4f26fb5859dacbde5632a761ac8537044805cc75` before this session's work; `data/raw/eval63/` captures present locally, gitignored. Session 58 backup: `recovery/session-58-checkpoint-d98a38942`.
- Env (verified this session): `./scripts/verify_env.sh --check` OK (pytest/numpy/pandas/scipy/pydantic/yaml/requests; sealed EVAL-37/36 tests passed). `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` set. `.env` absent; `LIVE_TRADING_ENABLED` unset. `python3 -m pytest -q tests/test_eval65_orderflow_tox_rv_predictiveness.py` → 8 passed.

## AUTHORITATIVE NEXT TASK (timestamped, heavy — execute in full)

**Task ID:** `INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`

**Objective (on-charter, final replication check):** Isolated, out-of-sample replication on a **disjoint** real ETH window of the only suggestive EVAL-65 slice (`tox::bar60.0::h72`, `imbalance::bar60.0::h72`) using the sealed EVAL-65/EVAL-62 signal construction and the sealed EVAL-64 feasible floor. This determines whether the ETH 1m/72-bar signal is real or sample-specific. A failed replication or an honest `BLOCKED` with no feasible fresh window ⇒ **campaign closure** (namesake definitively closed). A successful replication on the pre-registered configs/floor ⇒ only then consider a further traded-form test (new pre-registered task).

**Step 1 — Env/bootstrap (must pass):**
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
- Use a window disjoint from `data/raw/eval63/three_way_ETH_20261116T064816Z.json` (record/verify timestamps and hashes). No synthetic data. If rate-limited, retry politely; do not run parallel acquisition.
- Verify the feasible floor is met on the new capture (EVAL-64 floor): `n_surface_snapshots>=1000`, `n_surface_instruments>=100`, `n_surface_bars_5m>=1000`, `n_option_trades>=2000`, `n_of_instruments>=150`, `of_span_seconds>=82000`, `n_of_bars_5m>=240`, `n_perp_bars_5m>=1000`, `perp_span_seconds>=300000`, `n_common_bars_5m>=240`. **If not met ⇒ seal `EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_<UTC>` with honest diagnostics, do not weaken floor, and proceed to campaign closure.**

**Step 3 — Build, test, and seal EVAL-66 (copy-and-retarget sealed EVAL-65):**
- Create `scripts/eval66_eth_oflow_tox_rv_oos.py` and `tests/test_eval66_eth_oflow_tox_rv_oos.py` by retargeting sealed EVAL-65: **ETH-only**, configs restricted to `tox::bar60.0::h72` and `imbalance::bar60.0::h72` (pre-registered), reuse `e62.build_states` and `e64` feasible floor verbatim, same stats/GO bar (IC>0, directional permutation p<0.05, block-bootstrap 95% CI lower>0, BH-FDR rejects), artifact IDs `EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,COMBINED|BLOCKED}`. Keep EVAL-65 immutable.
- Run: `python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py`
- Dry-run: `python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --no-write`
- Seal (heavy): `python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS`

**Step 4 — Seal gate (exit 0 required):**
```bash
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*"
```
(If blocked, require the `BLOCKED` glob instead of `COMBINED` per the script's block-seal convention — but gate must exit 0 against the actual sealed state.)

**Step 5 — After sealing:** update this handoff in place with verified paths/numbers and the **definitive outcome**. If EVAL-66 `NO-GO` (fails to replicate) or `BLOCKED` with no feasible path: record `CAMPAIGN_CLOSED` (namesake options order-flow → realized-vol hypothesis not supported on real BTC/ETH, traded and informational forms closed, ETH slice non-replicating), and state that no further on-charter rungs are justified. If EVAL-66 GO (replicates on the pre-registered slice/floor): define a concrete, pre-registered traded-form follow-up as the next task (new ID). Do not invent synthetic or off-charter rungs.

## REPRO / KEY COMMANDS

```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check

# (sealed, immutable) re-verify EVAL-64 / EVAL-65
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T07:59:00Z-EVAL64-FEASIBLE-FLOOR-OFLOW-RV-MARKPATH" \
  --glob "EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_PREREGISTRATION_*" \
  --require-glob "EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_COMBINED_*"
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL" \
  --glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_*" \
  --require-glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_*"
python3 -m json.tool research_state/EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_20261116T084947Z.json | head -120

# --- EVAL-66 (authoritative next, heavy) ---
mkdir -p data/raw/eval66
python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal
# then copy-and-retarget sealed EVAL-65 -> eval66 (ETH-only, tox/imbalance bar60 h72), test, --no-write, --seal
# python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py
# python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS
# python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" --require-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*"
```

## BOTTLENECKS

- **Cleared:** EVAL-64 sealed (traded form closed). EVAL-65 sealed (gate exit 0) — namesake information-content tested on real BTC+ETH; only an isolated ETH-slice OOS replication (EVAL-66) remains on-charter. EVAL-65 tooling/tests/captures proven; env bootstrapped.
- **Active (EVAL-66):** requires a **fresh, disjoint real ETH 7d acquisition** meeting the sealed EVAL-64 feasible floor (Deribit `{ETH}-PERPETUAL` 1m candles cap at 300000 s / 5001 candles / 1000 5m bars and tick-trade retention ≈24h are the known public-API limits; surface 5m scales to 7d). Acquire exactly ONE process, polite rate limiting, dedupe, record span/hashes honestly. **If the feasible floor cannot be met on a fresh window, seal `BLOCKED` (never `NO-GO`) and close the campaign — do not weaken the floor.** `data/raw/eval66/` (if created) will be real and large; keep gitignored, do not commit captures.
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

EVAL-02..65 sealed. EVAL-46..60, EVAL-62, EVAL-64, **EVAL-65**: **NO-GO CONFIRMED (PASS)**, gate exit 0. EVAL-61: **NO-GO CONFIRMED (PASS)** but measurement-artifact (superseded by EVAL-62). **EVAL-63: NEVER sealed (no artifact exists); superseded by EVAL-64.** Re-running/re-sealing prohibited.

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

(End of file)
