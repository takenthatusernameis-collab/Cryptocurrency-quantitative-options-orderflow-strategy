# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK (do this next; no other task is valid until it is done)

================================================================================
>>> NEXT SESSION STARTS HERE — EXECUTE THIS TASK IN ORDER, NO EXCEPTIONS <<<
================================================================================

**EVAL-54 is COMPLETE and sealed.** Heavy real work executed this session:
`synchronized Deribit BTC+ETH options-surface capture` →
`EVAL_54_SYNCHRONIZED_ACQUISITION_20261115T174956Z` (floor OK: BTC 289 snaps/102 inst/289 5m bars/4439 trades/86304 s/287 common; ETH 289/103/289/3045/86269/287),
`EVAL_54_PREREGISTRATION_20261115T175351Z` (+175410Z) pre-registered BEFORE verdict,
`EVAL_54_COMBINED_20261115T175410Z` — **NO-GO CONFIRMED (PASS)** (floor OK True; BTC best Sharpe 0.2478 `BTC::atm_put::2026-11-15::reb2` median IV 0.7955 any_pass false; ETH best Sharpe 0.4178 `ETH::atm_put::2026-11-15::reb1` median IV 0.9021 any_pass false; pooled PBO 0.5417; BH-FDR rejected []; all underlyings pass false). Seal gate exit 0; `py_compile` OK; `pytest -q tests/test_eval54_...` 8 passed. EVAL-54 immutable.

**EVAL-55 IS THE NEXT FOCUS CAMPAIGN AND ITS TOOLING DOES NOT YET EXIST.** `scripts/eval55_*` and `tests/test_eval55_*` are absent. The heavy real-data work (build tooling → acquire → prereg → measure → seal → gate) is the next session's job and cannot be skipped.

EVAL-55 is a **fresh, pre-registered, heavy real-data falsification** aligned with the repo charter
(`Cryptocurrency-quantitative-options-orderflow-strategy` = quantitative **OPTIONS** + orderflow
strategy; net-of-cost evaluation). Every options+orderflow fusion cell (EVAL-46..53) is sealed
`NO-GO CONFIRMED (PASS)`; EVAL-54 (delta-hedged short-vol net-of-cost) is sealed `NO-GO CONFIRMED (PASS)`;
re-litigating fused options+orderflow or re-running EVAL-02..54 is prohibited. The unmeasured heavy
rung per the charter is **real options pricing/greeks/vol-surface → gamma-hedged P&L net of execution
costs** on real Deribit BTC+ETH option surface — gamma scalping/hedging is distinct from EVAL-54's
delta-hedging and is a pure options-native campaign not yet measured.

**TASK `INIT-2026-11-15T17:57:53Z-EVAL-55-REAL-OPTIONS-GAMMA-HEDGED-NET-OF-COST-BTC-ETH-BUILD-TOOLING-ACQUIRE-MEASURE-AND-SEAL`.**

EVAL-55 is a fresh, pre-registered, heavy real-data falsification: real Deribit options vol-surface /
greeks → gamma-hedged P&L net of bid-ask spread and execution fees on **BTC and ETH** over a synchronized
~24h window, measured with a pre-registered net-of-cost protocol, combined in a single verdict. Deribit
option-trade history is ~24h-capped, so the capture is genuinely new real evidence. **New timestamped
task ID; never re-run/re-seal EVAL-02..54. No other task is valid until step 8 exits 0.**

**YOU MUST, in this session, in this order, and may not skip any step:**

1. **Verify env (fast; do NOT run the full test suite):**
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   ./scripts/verify_env.sh --check
   ```
   If green, proceed.

2. **Build the EVAL-55 tooling (it does not exist — do not hand off without it):**
   - `scripts/eval55_acquire_options_surface.py` — real Deribit surface + options-venue trades + perp candles, writes `EVAL_55_SYNCHRONIZED_ACQUISITION_<UTC>` manifest to `research_state/`.
   - `scripts/eval55_gamma_hedged_net_of_cost.py` — gamma-hedged net-of-cost P&L; IV from real marks via `implied_volatility`, greeks from `black_scholes_greeks`; prereg/verdict/floor/GO-bar; `--prereg-only` + `--no-write` modes.
   - `tests/test_eval55_gamma_hedged_net_of_cost.py` — deterministic fixtures.
   ```bash
   python3 -m py_compile scripts/eval55_acquire_options_surface.py \
       scripts/eval55_gamma_hedged_net_of_cost.py \
       tests/test_eval55_gamma_hedged_net_of_cost.py
   python3 -m pytest -q tests/test_eval55_gamma_hedged_net_of_cost.py   # must be green
   ```
   **Do not edit sealed EVAL-02..54 scripts/tests/artifacts or `src/`.**

3. **Independent heavy real acquisition (live public read-only Deribit, BTC+ETH, synchronized ~24h
   window, all three legs):**
   ```bash
   python3 scripts/eval55_acquire_options_surface.py --underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval55 --seal
   ```
   ensuring an `EVAL_55_SYNCHRONIZED_ACQUISITION_<UTC>` manifest is written to `research_state/`.
   **Do not proceed unless both underlyings clear the per-underlying floor:**
   surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options trades ≥2000 trades / ≥50
   instruments / ≥240 bars / ≥79200 s span; legs time-overlapping (common 5m bars ≥240). Below floor
   ⇒ widen capture parameters and retry; **never** weaken the floor and **never** emit `{"valid": true}`
   for a below-floor capture.

4. **Pre-register BEFORE measurement:**
   ```bash
   python3 scripts/eval55_gamma_hedged_net_of_cost.py --prereg-only
   ```
   This seals `EVAL_55_PREREGISTRATION_<UTC>` from the pre-declared protocol (structures, expiry/rebalance
   grid, cost model, P&L definition, floors, GO bar) **without measuring**. It must be stamped **before**
   the verdict run (step 6).

5. **Smoke measurement (seals nothing):** dry-run and confirm `floor_ok: true` for both underlyings;
   inspect per-underlying net-of-cost P&L / Sharpe / median IV:
   ```bash
   python3 scripts/eval55_gamma_hedged_net_of_cost.py --no-write --capture-dir data/raw/eval55
   ```

6. **Seal the verdict:** then run the full measurement, which seals `EVAL_55_COMBINED_<UTC>` (or
   `EVAL_55_BLOCKED_<UTC>` only if floor unmet — never a substitute for a floor-passing verdict):
   ```bash
   python3 scripts/eval55_gamma_hedged_net_of_cost.py --capture-dir data/raw/eval55
   ```

7. **Seal gate — session FAILS unless a window acquisition AND a floor-passing combined verdict exist
   with stamp ≥ task timestamp:**
   ```bash
   python3 scripts/check_session_sealed.py \
       --task-id "INIT-2026-11-15T17:57:53Z-EVAL-55-REAL-OPTIONS-GAMMA-HEDGED-NET-OF-COST-BTC-ETH-BUILD-TOOLING-ACQUIRE-MEASURE-AND-SEAL" \
       --glob "EVAL_55_SYNCHRONIZED_ACQUISITION_*" \
       --require-glob "EVAL_55_PREREGISTRATION_*" \
       --require-glob "EVAL_55_COMBINED_*"
   ```
   Must exit `0`.

8. **Append a session-log line** to this file (measured numbers, floor metrics, per-underlying +
   combined verdict, artifact paths) and leave this handoff as the single durable record. Then set the
   **next** focus rung (a fresh, pre-registered heavy real-data falsification with a new timestamped
   task ID — never a re-run/re-seal of EVAL-02..55).

**Definition of done:** step 7 exits `0` with `EVAL_55_SYNCHRONIZED_ACQUISITION_<UTC>`,
`EVAL_55_PREREGISTRATION_<UTC>` (pre-verdict), and a floor-passing `EVAL_55_COMBINED_<UTC>` (verdict
`GO CONFIRMED` or `NO-GO CONFIRMED (PASS)`) all stamped ≥ `2026-11-15T17:57:53Z`. A handoff-only
session, re-run/re-seal of EVAL-02..54, full-test-suite discovery loop, `research_state/` enumeration,
or `EVAL_55_BLOCKED_*` in place of a floor-passing combined verdict are **all failures**.

## WHY THIS IS THE RIGHT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE)
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined options + orderflow** strategy,
but every options+orderflow fusion cell (EVAL-46..53) and EVAL-54 (delta-hedged short-vol net-of-cost)
are sealed `NO-GO CONFIRMED (PASS)`; re-running fused options+orderflow or EVAL-54 is prohibited
re-litigation. The charter's unmeasured heavy rung is **real options pricing/greeks/vol-surface →
net-of-cost evaluation**. EVAL-55 measures whether real Deribit options vol-surface **gamma-hedging**
(IV backed out of real marks → Black-Scholes greeks → gamma-hedged P&L net of bid-ask + fees) is
net-of-cost tradable on BTC and ETH — the pure options-native rung not yet measured (delta done in
EVAL-54), requiring new live heavy data (Deribit option trades ~24h-capped = genuinely new evidence),
not a re-run of sealed artifacts. **New timestamped task ID, never a re-run/re-seal of EVAL-02..54.**

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
New synchronized real Deribit options surface capture (BTC+ETH) over the same ~24h window meeting
per-underlying floor (surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options-venue trades
≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span; legs time-overlapping/common 5m bars ≥240)
→ real vol-surface/greeks gamma-hedged P&L net of bid-ask and fees (causal, no look-ahead,
floor-aligned grid) → pre-register `EVAL_55_PREREGISTRATION_*` BEFORE verdict → seal
`EVAL_55_SYNCHRONIZED_ACQUISITION_*` and `EVAL_55_COMBINED_*` (or BLOCKED only if floor unmet, never as
substitute) → pass seal gate. No prior-EVAL re-runs/re-seals, no `research_state/` enumeration, no
full test suite, no handoff-only session.

## BOTTLENECKS — CLEARED / REMAINING (verified 2026-11-15T17:57:53Z)
1. **CLEARED (this session):** EVAL-54 heavy real work complete — acquisition `EVAL_54_SYNCHRONIZED_ACQUISITION_20261115T174956Z`, prereg `EVAL_54_PREREGISTRATION_20261115T175351Z`, verdict `EVAL_54_COMBINED_20261115T175410Z` **NO-GO CONFIRMED (PASS)**, seal gate exit 0. Handoff updated; EVAL-54 no longer pending.
2. **CLEARED:** Deribit public network — EVAL-54 BTC+ETH capture completed at 2026-11-15T17:49:56Z (`data/raw/eval54/`). No active network blocker. If a future capture dips below floor, widen capture parameters and retry.
3. **CLEARED:** EVAL-52/EVAL-53/EVAL-54 sealed `NO-GO CONFIRMED (PASS)` with gate exit 0; their captures `data/raw/eval52/`, `data/raw/eval53/`, `data/raw/eval54/` are present and reusable (read-only). No handoff-only loop.
4. **CLEARED:** env ready — `.venv-deps/` present; `./scripts/verify_env.sh --check` exit 0; `.env` absent; `LIVE_TRADING_ENABLED` unset/false.
5. **CLEARED:** `scripts/check_session_sealed.py` supports `--glob` + repeatable `--require-glob` (AND); the EVAL-55 gate is executable as written in step 7.
6. **REMAINING (next session must clear):** EVAL-55 tooling does not exist — `scripts/eval55_acquire_options_surface.py`, `scripts/eval55_gamma_hedged_net_of_cost.py`, `tests/test_eval55_gamma_hedged_net_of_cost.py` are absent. Build + test them before the heavy acquisition.

## ANTI-STALL RULE (read before touching this file)
- **Only** acceptable outputs: (a) sealed `EVAL_55_SYNCHRONIZED_ACQUISITION_*` + `EVAL_55_PREREGISTRATION_*` +
  `EVAL_55_COMBINED_*` with gate exit 0, or (b) a *narrower* timestamped handoff whose floor is
  **identical or stricter** and whose only change is the corrected task timestamp.
- **Do NOT** re-issue at a new timestamp without either sealing or making stricter. A session whose only
  diff to this file is the timestamp is a failed session.
- **Do NOT** weaken the floor, drop an underlying, drop a bar size, or convert the gate to accept
  `EVAL_55_BLOCKED_*` as a verdict.
- **Do NOT** create `EVAL_55_BLOCKED_*` and stop: below-floor means *widen the capture*, not *stop*.
- If external outage blocks capture, re-run with wider capture parameters first; only then record a
  blocked artifact **plus** the exact failing floor metric and the command to resume.

## PROHIBITED (hard constraints)
- Do **not** re-run, re-litigate, or re-seal EVAL-02..54; do not edit sealed artifacts, sealed EVAL-52/
  EVAL-53/EVAL-54 scripts/tests, or `src/`.
- Do **not** fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel
  synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential
  mutation, or order placement. Network: public read-only market data only, polite rate limiting.
- Do **not** run the full test suite as discovery; do **not** enumerate `research_state/`; do **not**
  create timestamped handoff copies or new handoff files (root `HANDOFF_NEXT_AGENT.md`,
  `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers).
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`,
  `src/features/options_pricing.py`; no `phaseNN_*` orchestrator wrappers.

## SEALED STATE (immutable; do not re-run; append only)
EVAL-02..54 sealed. EVAL-46..54 (options+orderflow ladder + options-surface delta-hedging) all
**NO-GO CONFIRMED (PASS)**:
- **EVAL-46** integrated options+orderflow net-of-cost on full dense BTC → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z.{json,md}`.
- **EVAL-47** ETH combined → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_47_ETH_COMBINED_20261115T071330Z.{json,md}`.
- **EVAL-48** BTC cross-venue (Deribit options + OKX BTC orderflow) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z.{json,md}`.
- **EVAL-49** ETH cross-venue (Deribit ETH options + OKX ETH orderflow) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z.{json,md}`.
- **EVAL-50** real L2 order-book OFI (BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_50_L2_OFI_COMBINED_20261115T134705Z.{json,md}`.
- **EVAL-51** real Deribit options-venue order flow standalone (BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_51_OPTIONS_ORDERFLOW_COMBINED_20261115T152005Z.{json,md}`.
- **EVAL-52** synchronized options SURFACE × options-venue ORDER FLOW (pure options-side, BTC+ETH) →
  `NO-GO CONFIRMED (PASS)` `research_state/EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_20261115T165018Z.{json,md}`
  (pooled PBO 0.6389; best Sharpe BTC −0.7473, ETH −1.6028; all NO-GO).
- **EVAL-53** synchronized options SURFACE × options-venue ORDER FLOW cross-window replication
  (pure options-side, BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_53_CROSS_WINDOW_COMBINED_20261115T171712Z.{json,md}` (pooled PBO window A 0.6389 /
  window B 0.5556; all NO-GO; seal gate exit 0).
- **EVAL-54** real Deribit options vol-surface/greeks **delta-hedged** net-of-cost (BTC+ETH) →
  `NO-GO CONFIRMED (PASS)` `research_state/EVAL_54_COMBINED_20261115T175410Z.{json,md}`
  (acq `EVAL_54_SYNCHRONIZED_ACQUISITION_20261115T174956Z`, prereg `EVAL_54_PREREGISTRATION_20261115T175351Z`;
  pooled PBO 0.5417; BH-FDR rejected []; seal gate exit 0). EVAL-54 immutable.

**EVAL-55 is the next focus rung and is NOT yet sealed.** Its tooling is absent; build + test it,
then run the heavy real capture/measurement/seal per the authoritative task above.

Earlier: EVAL-37 audit `PASS 9/9`; EVAL-41/42 options pillar closed; EVAL-43 orderflow full roster
`NO-GO CONFIRMED (PASS)`; EVAL-44 `CAMPAIGN_CLOSED` (BTC-scoped); EVAL-45 ETH orderflow `NO-GO` + options
`BLOCKED`. The combined options+orderflow thesis is not net-of-cost tradable on all measured cells;
the pure options-native delta-hedged rung (EVAL-54) is also NO-GO. EVAL-55 (gamma-hedged net-of-cost)
is the next unmeasured heavy rung.

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (imports `src/` → needs numpy).
- **EVAL-54 capture schema** (`scripts/eval54_acquire_options_surface.py`): one file per underlying,
  `data/raw/eval54/options_surface_{BTC,ETH}_<stamp>.json`, with `surface.snapshots[]` (each has
  `bar_ms`, causal `spot` = perp close at bar end, and `quotes[]` with `strike`/`expiry`/`option_type`/
  `bid`/`ask`/`mark`), `option_trades[]` (for the floor parity), and `perp_candles[]` (1m). No synthetic
  data; `source.provenance` records real Deribit public provenance.
- **EVAL-54 MEASUREMENT GRID ALIGNMENT:** the delta-hedge walks the real 5m surface snapshots in
  ascending time; each snapshot is treated as an end-of-bar state at `bar_ms + 300s` (its `spot` is the
  causal perp close). IV is backed out of the *real* mark (`implied_volatility(mark*spot, spot, K, 0, T,
  type)`) and greeks come from `black_scholes_greeks` at that IV (intrinsic-delta fallback if the IV
  solve fails). P&L is causal: decision at bar `k` → outcome over `[k, k+1]`.
- **EVAL-54 COST MODEL:** hedge turnover `HEDGE_FEE_BPS=5` on `|Δhedge|*S`, plus the option's real half
  bid/ask charged at entry and exit; return = net-of-cost P&L / S per 1-unit underlying notional.
- Deribit options **candles** (surface): `GET /public/get_tradingview_chart_data` per option instrument,
  resolution `5` (historical candles available). Deribit options **trades**:
  `GET /public/get_last_trades_by_instrument_and_time` (paginate `start_timestamp = last_trade_ts + 1`
  while `has_more`; ~24h cap per instrument). Perp: `get_tradingview_chart_data` `{BTC,ETH}-PERPETUAL`
  resolution `1` as in EVAL-52.
- `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 → DSR may report 0.0; use perm/bootstrap/PBO/BH-FDR.
- `permutation_test(rets, flat, statistic=_mean, paired=True, seed=42)` → `p_value`. `block_bootstrap_ci`
  → `(point, lo, hi)`. Run full capture; no fixed tail slices.

## HARD INVARIANTS
Paper-only; `.env` absent; `LIVE_TRADING_ENABLED=false`. Never fall back to synthetic; real loaders raise
`RealDataUnavailable`; never relabel synthetic as real. Sealed artifacts immutable; append new timestamped
artifacts only. Public read-only network only. Reuse `src/` modules; no `phaseNN_*`.

## HANDOFF DISCIPLINE
This file is the **single durable handoff**. Update in place with verified facts/timestamps/paths/commands
only; no timestamped handoff copies. Record measured numbers, not intentions. No GO without a verifying
sealed artifact. Final responses must not ask follow-up questions.

## SESSION LOG (append-only)
- 2026-11-14T18:21:06Z→2026-11-15T11:03:55Z: EVAL-41..49 executed and sealed (all NO-GO). EVAL-50 tooling
  built/tested; prior handoff claimed heavy capture in progress (pid 9687) with short pre-capture below floor.
- 2026-11-15T12:08:31Z–13:03:42Z: re-verified `pid 9687` not running; `data/raw/eval50/` short pre-capture
  only (266 snaps/~598 s each, below floor). Repeatedly set EVAL-50 task. No EVAL-50 verdict sealed.
- **2026-11-15T13:47:05Z (EVAL-50 COMPLETED):** capture `--duration 1000 --cadence 2 --levels 25` → BTC
  443 snaps/999.6 s, ETH 444 snaps/999.6 s (floor met); `EVAL_50_L2_DEPTH_ACQUISITION_20261115T134456Z`;
  prereg `EVAL_50_PREREGISTRATION_20261115T134705Z`; verdict `EVAL_50_L2_OFI_COMBINED_20261115T134705Z`
  — **NO-GO CONFIRMED (PASS)** (best BTC −2.68 / ETH −1.01, pooled PBO 0.5000). Seal gate exit 0.
- **2026-11-15T15:06:06Z & 15:11:17Z:** EVAL-51 task refreshes, no verdict (handoff-only).
- **2026-11-15T15:18:43Z–15:20:05Z (EVAL-51 COMPLETED):** acquisition `--days 1` BTC+ETH → BTC 5347 trades
  / 98 instruments / 289 5m bars / 86010 s; ETH 3429 trades / 102 instruments / 289 bars / 86381 s;
  `EVAL_51_OPTIONS_ORDERFLOW_ACQUISITION_20261115T151843Z`; prereg `EVAL_51_PREREGISTRATION_20261115T152005Z`;
  verdict `EVAL_51_OPTIONS_ORDERFLOW_COMBINED_20261115T152005Z` — **NO-GO CONFIRMED (PASS)** (best BTC
  −1.864, ETH −1.897, pooled PBO 0.5000). Seal gate exit 0. `pytest ...eval51...` 14 passed.
- 2026-11-15T15:22:00Z–15:26:16Z: EVAL-52 task set/hardened; no verdict until executed.
- **2026-11-15T16:42:09Z–16:50:18Z (EVAL-52 COMPLETED):** ... `EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_20261115T165018Z` — **NO-GO CONFIRMED (PASS)** ... Seal gate exit 0.
- **2026-11-15T17:12:10Z–17:17:12Z (EVAL-53 COMPLETED):** ... `EVAL_53_CROSS_WINDOW_COMBINED_20261115T171712Z` — **NO-GO CONFIRMED (PASS)** ... Seal gate exit 0. Deribit network blocker RESOLVED.
- **2026-11-15T17:44:03Z–17:47:58Z (EVAL-54 tooling built):** `scripts/eval54_acquire_options_surface.py`,
  `scripts/eval54_options_surface_hedging_net_of_cost.py`, `tests/test_eval54_options_surface_hedging_net_of_cost.py`
  (`py_compile` OK; `pytest -q` 8 passed). Authoritative EVAL-54 task set.
- **2026-11-15T17:49:56Z–17:54:10Z (EVAL-54 COMPLETED — this session):** heavy real synchronized Deribit
  capture BTC+ETH → `EVAL_54_SYNCHRONIZED_ACQUISITION_20261115T174956Z` (floor met: BTC 289/102/289/4439/86304/287;
  ETH 289/103/289/3045/86269/287); prereg `EVAL_54_PREREGISTRATION_20261115T175351Z` (+175410Z); verdict
  `EVAL_54_COMBINED_20261115T175410Z` — **NO-GO CONFIRMED (PASS)** (pooled PBO 0.5417; BH-FDR rejected [];
  BTC best Sharpe 0.2478 any_pass false; ETH best Sharpe 0.4178 any_pass false; all underlyings pass false).
  Seal gate exit 0. EVAL-54 immutable. Handoff updated; EVAL-54 bottleneck cleared.
- **2026-11-15T17:57:53Z (this session — EVAL-54 sealed complete; EVAL-55 tooling absent):** verified
  EVAL-54 sealed (gate exit 0), env green, no `scripts/eval55_*`/`tests/test_eval55_*` present. Set
  authoritative task **`INIT-2026-11-15T17:57:53Z-EVAL-55-REAL-OPTIONS-GAMMA-HEDGED-NET-OF-COST-BTC-ETH-BUILD-TOOLING-ACQUIRE-MEASURE-AND-SEAL`**
  with step-7 gate (`--glob "EVAL_55_SYNCHRONIZED_ACQUISITION_*" --require-glob "EVAL_55_PREREGISTRATION_*" --require-glob "EVAL_55_COMBINED_*"`, stamp ≥ task). Next session must build EVAL-55 tooling,
  run the heavy real synchronized Deribit acquisition (BTC+ETH ~24h) meeting the per-underlying floor,
  pre-register (prereg-only) BEFORE measuring, measure gamma-hedged net-of-cost P&L, seal acquisition+
  prereg+combined verdict, and pass the gate; no other task valid.
