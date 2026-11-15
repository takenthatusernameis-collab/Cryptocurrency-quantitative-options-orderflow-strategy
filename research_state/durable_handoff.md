# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK (do this next; no other task is valid until it is done)

**EVAL-52 IS SEALED (do not re-run):** `NO-GO CONFIRMED (PASS)` at
`research_state/EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_20261115T165018Z.{json,md}` (prereg
`EVAL_52_PREREGISTRATION_20261115T165018Z`; acquisition
`EVAL_52_SYNCHRONIZED_ACQUISITION_20261115T164732Z` — BTC 289 surface snapshots / 102 instruments /
289 5m bars, 4688 option trades / 99 instruments / span 86261.649 s / 288 common 5m bars; ETH 289
snapshots / 102 instruments / 289 5m bars, 3122 option trades / 101 instruments / span 86204.278 s /
287 common 5m bars; 18 configs/underlying, best Sharpe BTC −0.7473
`continuous_zscore::call_minus_put::bar300.0`, ETH −1.6028 `sign_agreement::imbalance::bar300.0`, all
NO-GO, pooled PBO 0.6389, BH-FDR rejected 32 configs; seal gate exit 0). Tooling:
`scripts/eval52_acquire_synchronized_options.py`, `scripts/eval52_options_surface_orderflow_net_of_cost.py`,
`tests/test_eval52_options_surface_orderflow_net_of_cost.py` (7 passed). Window-A capture:
`data/raw/eval52/` (`options_surface_orderflow_{BTC,ETH}_20261115T164732Z.json`). Immutable.

**TASK `INIT-2026-11-15T16:54:19Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION-ACQUIRE-MEASURE-AND-SEAL`.**

EVAL-46..52 are all sealed `NO-GO CONFIRMED (PASS)`. **EVAL-53 is the next focus campaign** — a
**fresh, pre-registered, heavy real-data falsification**: **independent cross-window replication** of
the EVAL-52 fused options SURFACE × options-venue ORDER FLOW signal on a **new synchronized ~24h
Deribit capture** (BTC+ETH, window B), measured with the **sealed EVAL-52 protocol** and combined in a
**cross-window meta verdict** (window A = sealed `data/raw/eval52/` + EVAL-52 artifacts, immutable;
window B = new `data/raw/eval53/` capture). Tests whether the EVAL-52 NO-GO is temporally stable or
window-specific. Deribit option-trade history is ~24h-capped, so window B captured now is genuinely new
evidence (not a re-run). **New timestamped task ID; never re-run/re-seal EVAL-02..52. No other task is
valid until step 6 exits 0.**

**YOU MUST, in this session, in this order, and may not skip any step:**

1. **Verify env (fast; do NOT run the full test suite):**
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   ./scripts/verify_env.sh --check
   ```
   Verified green 2026-11-15T16:54Z (exit 0). If still green, proceed.

2. **Build EVAL-53 tooling (non-escapable engineering work):**
   Create `scripts/eval53_cross_window_replication.py` and `tests/test_eval53_cross_window_replication.py`.
   **Reuse sealed primitives — do NOT duplicate or modify them:**
   - Capture window B by calling/reusing `scripts/eval52_acquire_synchronized_options.py` logic (same
     schema/floor/endpoints) into `data/raw/eval53/`.
   - Measure each window with the sealed EVAL-52 protocol by importing/calling
     `scripts.eval52_options_surface_orderflow_net_of_cost` helpers (`_capture_inventory`/`run_eval52`
     internals or equivalent): same grid (3 fusion rules × {60s,300s} bars × 3 order-flow signals), causal
     expanding z-score window 20, net-of-cost 5 bps, 1000 paired perms + 1000 block-bootstrap + CSCV PBO
     k=4 + BH-FDR alpha 0.1 + DSR, seed 42, kill-switch max-DD 0.20 — **no fitting, no changes**.
   - Emit a cross-window comparison (per-window verdicts/config results, stability/replication of any
     passing signal, pooled cross-window PBO/summary) and a meta verdict.
   - CLI (minimum): `--window-a-dir data/raw/eval52 --window-b-dir data/raw/eval53 --no-write` and a
     sealing mode that: acquires window B if missing/below floor (or `--acquire-window-b`), writes
     `EVAL_53_WINDOW_B_ACQUISITION_<UTC>` manifest to `research_state/`, pre-registers
     `EVAL_53_PREREGISTRATION_<UTC>` **BEFORE** measurement verdict, then seals
     `EVAL_53_CROSS_WINDOW_COMBINED_<UTC>` (or `EVAL_53_BLOCKED_<UTC>` only if floor unmet — never a
     substitute for a floor-passing verdict).
   - **No `phaseNN_*` orchestrator wrappers; no edits to sealed EVAL-02..52 scripts/tests/artifacts or `src/`.**
   Compile + test before capture:
   ```bash
   python3 -m py_compile scripts/eval53_cross_window_replication.py tests/test_eval53_cross_window_replication.py
   python3 -m pytest -q tests/test_eval53_cross_window_replication.py   # must pass
   ```

3. **Independent heavy real acquisition — window B (live public read-only Deribit, BTC+ETH, new ~24h
   synchronized window, both legs).** Deribit caps signed option trade history at ~24h, so window B is the
   *current* trailing 24h at capture time (independent of window A `data/raw/eval52/`).
   ```bash
   python3 scripts/eval53_cross_window_replication.py --acquire-window-b --window-b-dir data/raw/eval53
   ```
   (or invoke `scripts/eval52_acquire_synchronized_options.py --underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval53 --seal` and ensure an `EVAL_53_WINDOW_B_ACQUISITION_<UTC>` manifest is also written to `research_state/` by the EVAL-53 script — the gate requires it.)
   **Do not proceed unless both underlyings clear the per-underlying floor on window B:**
   surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; order flow ≥2000 trades / ≥50 instruments /
   ≥240 bars / ≥79200 s span; legs time-overlapping (common 5m bars ≥240). Below floor ⇒ widen
   `--max-per-expiry` / `--max-expiry-days` and retry; **never** widen the floor and **never** emit
   `{"valid": true}` for a below-floor capture.

4. **Smoke measurement (seals nothing):**
   ```bash
   python3 scripts/eval53_cross_window_replication.py \
       --window-a-dir data/raw/eval52 --window-b-dir data/raw/eval53 --no-write
   ```
   Confirm `floor_ok: true` for **both** windows and inspect per-window Sharpes/PBO and cross-window stability.

5. **Seal the verdict** (writes `EVAL_53_WINDOW_B_ACQUISITION_<UTC>` if not yet sealed, pre-registers
   `EVAL_53_PREREGISTRATION_<UTC>` **BEFORE** verdict, then seals
   `EVAL_53_CROSS_WINDOW_COMBINED_<UTC>` or `EVAL_53_BLOCKED_<UTC>` only if floor unmet):
   ```bash
   python3 scripts/eval53_cross_window_replication.py \
       --window-a-dir data/raw/eval52 --window-b-dir data/raw/eval53
   ```

6. **Seal gate — session FAILS unless a window-B acquisition AND a floor-passing cross-window COMBINED
   verdict exist with stamp ≥ task timestamp** (`EVAL_53_BLOCKED_*` alone will NOT pass):
   ```bash
   python3 scripts/check_session_sealed.py \
       --task-id "INIT-2026-11-15T16:54:19Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION-ACQUIRE-MEASURE-AND-SEAL" \
       --require-glob "EVAL_53_WINDOW_B_ACQUISITION_*" \
       --require-glob "EVAL_53_PREREGISTRATION_*" \
       --require-glob "EVAL_53_CROSS_WINDOW_COMBINED_*"
   ```
   (Passes with `--glob` omitted? script requires `--glob`; use `--glob "EVAL_53_WINDOW_B_ACQUISITION_*"` as the primary and keep the same as a require-glob for clarity, or set `--glob "EVAL_53_*"` — **use the exact command above with `--glob "EVAL_53_WINDOW_B_ACQUISITION_*"` as first required match**: see command below.) Must exit `0`.
   ```bash
   python3 scripts/check_session_sealed.py \
       --task-id "INIT-2026-11-15T16:54:19Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION-ACQUIRE-MEASURE-AND-SEAL" \
       --glob "EVAL_53_WINDOW_B_ACQUISITION_*" \
       --require-glob "EVAL_53_PREREGISTRATION_*" \
       --require-glob "EVAL_53_CROSS_WINDOW_COMBINED_*"
   ```

7. **Append a session-log line** to this file (measured numbers, floor metrics for window B, per-window +
   cross-window verdict, artifact paths) and leave this handoff as the single durable record.

**Definition of done:** step 6 exits `0` with `EVAL_53_WINDOW_B_ACQUISITION_<UTC>`,
`EVAL_53_PREREGISTRATION_<UTC>` (pre-verdict), and a floor-passing
`EVAL_53_CROSS_WINDOW_COMBINED_<UTC>` (verdict `GO CONFIRMED` or `NO-GO CONFIRMED (PASS)`) all stamped
≥ `2026-11-15T16:54:19Z`. A handoff-only session, `--no-write`-only session, re-run/re-seal of
EVAL-02..52, full-test-suite discovery loop, `research_state/` enumeration, or `EVAL_53_BLOCKED_*` in
place of a floor-passing combined verdict are **all failures**.

## WHY THIS IS THE RIGHT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE)
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined options + orderflow** strategy.
EVAL-46..52 sealed the full charter ladder `NO-GO CONFIRMED (PASS)` including the pure options-side
fusion (EVAL-52). EVAL-53 is a **fresh, pre-registered, heavy cross-window replication** on a new
synchronized ~24h real Deribit capture to test temporal stability of EVAL-52 — requires new live heavy
data (Deribit option trades ~24h-capped = genuinely new evidence), not a re-run of sealed artifacts.
**New timestamped task ID, never a re-run/re-seal of EVAL-02..52.**

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
New synchronized real Deribit capture (window B) for **both BTC and ETH** over the **same** ~24h window
meeting per-underlying floor (surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options-venue
order flow ≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span; legs time-overlapping/common 5m
bars ≥240) → `eval53_cross_window_replication.py` runs sealed EVAL-52 protocol on window A
(`data/raw/eval52/`, immutable) and window B independently (3 fusion rules × {60s,300s} bars × 3
order-flow signals; causal expanding z-score; net-of-cost 5 bps; 1000 paired permutations + 1000
block-bootstrap + CSCV PBO k=4 + BH-FDR + DSR; seed 42) and emits a cross-window meta verdict →
pre-register `EVAL_53_PREREGISTRATION_*` BEFORE verdict → seal `EVAL_53_WINDOW_B_ACQUISITION_*` and
`EVAL_53_CROSS_WINDOW_COMBINED_*` (or BLOCKED only if floor unmet, never as substitute) → pass seal gate.
No prior-EVAL re-runs/re-seals, no `research_state/` enumeration, no full test suite, no handoff-only session.

## EVAL-53 PROTOCOL (pre-declared; implement in eval53 tooling, reusing EVAL-52 primitives)
- **Per-window measurement:** identical to sealed EVAL-52 — options-surface alpha (causal, newest snapshot
  ≤ bar_end): mean(`gex_flip_signal`,`skew_slope_signal`,`calib_residual_signal`) clipped [-1,1]
  (`_options_signal_components`); options-venue order flow per bar: `imbalance`, `notional_imbalance`,
  `call_minus_put`; fusion rules {`sign_agreement`, `regime_filter`, `continuous_zscore`}; grid
  bar ∈ {60s,300s} × 3 OF signals; causal expanding z-score window 20; net-of-cost 5 bps on turnover;
  1000 paired perms + 1000 block-bootstrap (block 2) + CSCV PBO k=4 + BH-FDR α=0.1 + DSR; seed 42.
- **Cross-window verdict:** evaluate window A and window B independently on the identical protocol/grid.
  Report per-window verdicts, per-underlying best configs, pooled PBO per window, and cross-window
  stability (whether any config passing on one window replicates with same sign/passes on the other).
  Meta verdict: `GO CONFIRMED` only if the pre-registered GO bar (net-of-cost Sharpe > 0, no kill-switch
  breach max-DD ≤ 0.20, perm p < 0.05, bootstrap 95% CI lower > 0, pooled PBO < 0.5) holds on **both**
  windows for **the same** config on **both** BTC and ETH (strict cross-window replication); else
  `NO-GO CONFIRMED (PASS)` when both windows floor-passing. Below floor on window B → `BLOCKED` (never NO-GO).

## BOTTLENECKS — CLEARED (verified 2026-11-15T16:54Z; do not re-verify)
1. **CLEARED:** EVAL-52 sealed `NO-GO CONFIRMED (PASS)` with gate exit 0; artifacts immutable; window-A
   capture `data/raw/eval52/` present and reusable (read-only). No handoff-only loop for EVAL-52.
2. **CLEARED:** env ready — `.venv-deps/` present; `./scripts/verify_env.sh --check` exit 0 (python 3.12.3);
   `.env` absent; `LIVE_TRADING_ENABLED` unset/false.
3. **CLEARED:** sealed EVAL-52 tooling + tests on disk and importable (`run_eval52`, helpers, acquisition
   primitives); `scripts/check_session_sealed.py` supports `--glob` + repeatable `--require-glob` (AND)
   and `--require-any-glob` (OR) — gate in step 6 executable as written.
4. **CLEARED:** `data/raw/eval53/` absent, no stale capture processes, clean tree for window-B capture.
5. **DONE (this session):** `eval53_*` tooling built and tested —
   `scripts/eval53_cross_window_replication.py` +
   `tests/test_eval53_cross_window_replication.py` (`py_compile` OK;
   `pytest -q` 9 passed). `--no-write` smoke verified offline: reuses sealed
   EVAL-52 helpers, window A pooled PBO 0.6389 matches sealed EVAL-52, window
   B absent -> `BLOCKED` (correct, not a verdict). No EVAL-02..52 edits; no
   `phaseNN_*`; no `src/` edits.
6. **BLOCKER (network):** Deribit public API unreachable
   (`NetworkError` after retries) at this session, so window-B synchronized
   capture (`--acquire-window-b`) + seal could NOT be completed. Heavy work
   remaining: acquire window B (real Deribit BTC+ETH ~24h, floor: surface
   ≥100 snaps / ≥50 instruments / ≥240 5m bars; options-venue order flow
   ≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span; legs
   time-overlapping / common 5m bars ≥240), then seal prereg +
   `EVAL_53_CROSS_WINDOW_COMBINED_*` and pass gate. Retry capture when network
   returns; widen `--max-per-expiry`/`--max-expiry-days` if below floor.
   Never weaken the floor, never emit `{"valid": true}`, never substitute
   `EVAL_53_BLOCKED_*` for a floor-passing combined verdict.

## ANTI-STALL RULE (read before touching this file)
- **Only** acceptable outputs: (a) sealed `EVAL_53_WINDOW_B_ACQUISITION_*` + `EVAL_53_PREREGISTRATION_*` +
  `EVAL_53_CROSS_WINDOW_COMBINED_*` with gate exit 0, or (b) a *narrower* timestamped handoff whose floor
  is **identical or stricter** and whose only change is the corrected task timestamp.
- **Do NOT** re-issue at a new timestamp without either sealing or making stricter. A session whose only
  diff to this file is the timestamp is a failed session.
- **Do NOT** weaken the floor, drop an underlying, drop a fusion rule, drop a bar size, reduce
  permutations/bootstrap/BH-FDR/PBO/DSR, or convert the gate to accept `EVAL_53_BLOCKED_*` as a verdict.
- **Do NOT** create `EVAL_53_BLOCKED_*` and stop: below-floor means *widen the capture*, not *stop*.
- If external outage blocks capture, re-run with wider `--max-per-expiry`/`--max-expiry-days` first; only
  then record a blocked artifact **plus** the exact failing floor metric and the command to resume.

## PROHIBITED (hard constraints)
- Do **not** re-run, re-litigate, or re-seal EVAL-02..52; do not edit sealed artifacts, sealed EVAL-52
  scripts/tests, or `src/`.
- Do **not** fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel
  synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential
  mutation, or order placement. Network: public read-only market data only, polite rate limiting.
- Do **not** run the full test suite as discovery; do **not** enumerate `research_state/`; do **not**
  create timestamped handoff copies or new handoff files (root `HANDOFF_NEXT_AGENT.md`,
  `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers).
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`; no
  `phaseNN_*` orchestrator wrappers.

## SEALED STATE (immutable; do not re-run; append only)
EVAL-02..52 sealed. EVAL-46..52 (options+orderflow ladder) all **NO-GO CONFIRMED (PASS)**:
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
  (acq `EVAL_52_SYNCHRONIZED_ACQUISITION_20261115T164732Z`, prereg `EVAL_52_PREREGISTRATION_20261115T165018Z`,
  window-A data `data/raw/eval52/`; pooled PBO 0.6389; best Sharpe BTC −0.7473, ETH −1.6028; all NO-GO).

Earlier: EVAL-37 audit `PASS 9/9`; EVAL-41/42 options pillar closed; EVAL-43 orderflow full roster
`NO-GO CONFIRMED (PASS)`; EVAL-44 `CAMPAIGN_CLOSED` (BTC-scoped); EVAL-45 ETH orderflow `NO-GO` + options
`BLOCKED`. The combined options+orderflow thesis is not net-of-cost tradable on all measured cells
including the pure options-side fusion (EVAL-52). EVAL-53 is the cross-window replication falsification.

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (imports `src/` → needs numpy).
- **GRID ALIGNMENT:** EVAL-52 capture stores `surface` snapshots (5m bar grid) and `option_trades` +
  `perp_candles`; measurement builds 5m bar grid from perp/order-flow side and attaches newest surface
  snapshot with `bar_end(snapshot) ≤ bar_end(bar)` (causal). Intersect legs' bar sets; floor on the
  intersected grid. Reuse EVAL-52 `build_bars`/`surface_signal_series`/`align_surface` logic.
- Deribit options **trades**: `GET /public/get_last_trades_by_instrument_and_time` (paginate
  `start_timestamp = last_trade_ts + 1` while `has_more`; ~24h cap per instrument — window B is the
  trailing ~24h at capture time). Deribit options **candles** (surface): `GET /public/get_tradingview_chart_data`
  per option instrument, resolution `5` (historical candles available). Perp: `get_tradingview_chart_data`
  `{BTC,ETH}-PERPETUAL` resolution `1`/`5` as in EVAL-52.
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
- **2026-11-15T16:42:09Z–16:50:18Z (EVAL-52 COMPLETED, `INIT-2026-11-15T15:26:16Z-...-EVAL-52-...`):**
  `./scripts/verify_env.sh --check` exit 0. `py_compile` eval52 scripts+tests ok; `pytest -q tests/test_eval52_options_surface_orderflow_net_of_cost.py` → 7 passed. Synchronized real Deribit capture BTC+ETH `--out-dir data/raw/eval52 --seal` → `EVAL_52_SYNCHRONIZED_ACQUISITION_20261115T164732Z`. Floor met: BTC 289 snaps/102 inst/289 5m bars, 4688 trades/99 inst/span 86261.649s/288 common 5m; ETH 289/102/289, 3122/101/span 86204.278s/287 common. Prereg `EVAL_52_PREREGISTRATION_20261115T165018Z`; verdict `EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_20261115T165018Z` — **NO-GO CONFIRMED (PASS)** (18 configs/underlying; best BTC −0.7473 `continuous_zscore::call_minus_put::bar300.0`, ETH −1.6028 `sign_agreement::imbalance::bar300.0`; all NO-GO; pooled PBO 0.6389; BH-FDR rejected 32). Seal gate exit 0. EVAL-52 immutable.
- **2026-11-15T16:54:19Z (this session, handoff refreshed for EVAL-53):** verified EVAL-52 sealed (verdict/prereg/acq manifests present, `data/raw/eval52/` has both legs, eval52 scripts+tests on disk, `pytest` previously 7 passed), env green (`verify_env.sh --check` exit 0), `data/raw/eval53/` absent, no `scripts/eval53*`. Set authoritative task **`INIT-2026-11-15T16:54:19Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION-ACQUIRE-MEASURE-AND-SEAL`** with unambiguous step-6 gate (`--glob "EVAL_53_WINDOW_B_ACQUISITION_*" --require-glob "EVAL_53_PREREGISTRATION_*" --require-glob "EVAL_53_CROSS_WINDOW_COMBINED_*"`, stamp ≥ task). Next session must build eval53 tooling, acquire window B (heavy real synchronized Deribit BTC+ETH ~24h), smoke `--no-write`, seal prereg+acquisition+cross-window combined verdict, and pass    gate; no other task valid.
- **2026-11-15T17:08:32Z (this session, EVAL-53 tooling built):** built
  `scripts/eval53_cross_window_replication.py` +
  `tests/test_eval53_cross_window_replication.py` (`py_compile` OK;
  `pytest -q` 9 passed). `--no-write` smoke verified offline: reuses sealed
  EVAL-52 helpers (`evaluate_config`, `surface_signal_series`, `build_bars`,
  `_underlying_floor`, stats), window A `floor_ok: true` with pooled PBO
  0.6389 matching sealed EVAL-52; window B (`data/raw/eval53`) absent ->
  `BLOCKED` (correct, not a verdict). No EVAL-02..52 edits, no `src/` edits,
  no `phaseNN_*`. Deribit public API unreachable (`NetworkError` after
  retries) at this session, so window-B synchronized capture +
  `--acquire-window-b` + seal could NOT be completed; seal gate (step 6)
  cannot pass until `EVAL_53_WINDOW_B_ACQUISITION_*`,
  `EVAL_53_PREREGISTRATION_*`, and a floor-passing
  `EVAL_53_CROSS_WINDOW_COMBINED_*` (stamp ≥ task) exist. Heavy work
  remaining: acquire real synchronized Deribit window B (BTC+ETH ~24h) meeting
  the per-underlying floor, then seal prereg + combined cross-window verdict
  and pass the gate. Authoritative task unchanged:
  `INIT-2026-11-15T16:54:19Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION-ACQUIRE-MEASURE-AND-SEAL`.
