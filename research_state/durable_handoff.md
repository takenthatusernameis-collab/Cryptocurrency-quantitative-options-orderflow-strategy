# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK FOR NEXT SESSION (timestamped; only valid task)

**Task ID:** `INIT-2026-11-15T20:00:00Z-EVAL-58-REAL-OPTIONS-SKEW-RISK-REVERSAL-NET-OF-COST-BTC-ETH-ACQUIRE-MEASURE-AND-SEAL`
**Status as of 2026-11-15T20:00:00Z:** EVAL-57 **SEALED NO-GO CONFIRMED (PASS)** (gate exit 0). EVAL-58 tooling **ABSENT** (`scripts/eval58_*`, `tests/test_eval58_*` do not exist). **No EVAL-58 acquisition/prereg/combined artifacts sealed and no `data/raw/eval58/` capture exists. Next session must BUILD the EVAL-58 tooling (copy-and-retarget EVAL-57), test it green, then execute heavy real acquisition + measurement + seal in order. Handoff-only is failure.**

================================================================================
>>> NEXT SESSION STARTS HERE — EXECUTE THIS TASK IN ORDER, NO EXCEPTIONS <<<
================================================================================

**EVAL-57 is COMPLETE and sealed (immutable).** `EVAL_57_SYNCHRONIZED_ACQUISITION_20261115T195702Z` (floor OK: BTC 289 snaps/102 inst/288 5m bars/4234 trades/85822 s span/287 common, term-structure viable 8 expiries; ETH 289/102/288/2890/85970 s/287 common, term-structure viable 8 expiries), `EVAL_57_PREREGISTRATION_20261115T195900Z` (pre-verdict; re-sealed `195911Z` by the measuring run), `EVAL_57_COMBINED_20261115T195911Z` — **NO-GO CONFIRMED (PASS)** (floor_ok true; BTC best Sharpe 1.1620 `vrp_straddle_delta_hedged::lb12::vt1.0::sc1.0::reb2` any_pass false; ETH best Sharpe 7.7375 `vrp_straddle_delta_hedged::lb24::vt0.5::sc0.5::reb2` any_pass true; pooled PBO 0.3750; BH-FDR rejected 6 ETH configs but BTC never passed → combined NO-GO; seal gate exit 0).

**BOTTLENECK STATUS (cleared/stale-removed):** EVAL-57 tooling was green and its heavy real work is now DONE — acquisition, prereg, and combined verdict all sealed with gate exit 0. **The remaining bottleneck is that EVAL-58 tooling does not exist.** Next session must build `scripts/eval58_acquire_options_surface.py` (copy-and-retarget EVAL-57 acquisition, do not edit sealed EVAL-57), `scripts/eval58_skew_risk_reversal_net_of_cost.py` (copy-and-retarget `eval57_vrp_net_of_cost.py`, replacing the VRP/straddle book with a 25Δ risk-reversal / skew book), and `tests/test_eval58_skew_risk_reversal_net_of_cost.py`; get `py_compile` OK and `pytest -q` green; then run live Deribit BTC+ETH ~24h synchronized acquisition, pre-register before verdict, run full skew/risk-reversal net-of-cost measurement, and seal ACQ+PREREG+COMBINED so the step-7 gate exits 0. Do not hand off again without a sealed floor-passing verdict or a stricter handoff.

EVAL-58 is a **fresh, pre-registered, heavy real-data falsification** aligned with the repo charter
(`Cryptocurrency-quantitative-options-orderflow-strategy` = quantitative **OPTIONS** + orderflow
strategy; net-of-cost evaluation). The options greeks ladder is now COMPLETE: delta (EVAL-54, short-vol
net-of-cost, `NO-GO`) → gamma (EVAL-55, long-gamma gamma-scalp net-of-cost, `NO-GO`) → vega/term-structure
(EVAL-56, calendar-spread net-of-cost, `NO-GO`) → VRP / realized-vs-implied (EVAL-57, straddle-delta-hedged
VRP net-of-cost, `NO-GO`). Re-litigating fused options+orderflow (EVAL-46..53) or any sealed greeks rung
(EVAL-54..57) is prohibited. The remaining pure options-native heavy rung is **options SKEW / RISK-REVERSAL
(25Δ call-put skew)**: back out real IV from Deribit option marks, select the ~25Δ call and ~25Δ put at a
common expiry, and trade the risk-reversal (long one wing / short the other) delta-hedged in the perpetual,
net of execution costs — the one options combination not yet measured.

**TASK (authoritative): `INIT-2026-11-15T20:00:00Z-EVAL-58-REAL-OPTIONS-SKEW-RISK-REVERSAL-NET-OF-COST-BTC-ETH-ACQUIRE-MEASURE-AND-SEAL`**

EVAL-58 is a fresh, pre-registered, heavy real-data falsification: real Deribit options vol-surface /
greeks → **skew / risk-reversal (25Δ)** net-of-cost on the **BTC and ETH** perpetual over a synchronized
~24h window, measured with a pre-registered net-of-cost protocol, combined in a single verdict. The options
greeks ladder is complete: delta (EVAL-54) → gamma (EVAL-55) → vega/term-structure (EVAL-56) → VRP (EVAL-57).
The remaining pure options-native heavy rung is **skew / risk-reversal**: back out real IV from Deribit
option marks, select the ~25Δ call and ~25Δ put at a common expiry, and trade the risk-reversal
(long one wing / short the other), delta-hedged in the perp, P&L net of execution costs. Deribit
option-trade history is ~24h-capped, so the capture is genuinely new real evidence.
**New timestamped task ID; never re-run/re-seal EVAL-02..57. No other task is valid until step 7 exits 0
(gate).**

**YOU MUST, in this session, in this order, and may not skip any step:**

1. **Verify env (fast; do NOT run the full test suite):**
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   ./scripts/verify_env.sh --check
   ```
   If green, proceed.

2. **Build EVAL-58 tooling (copy-and-retarget the sealed EVAL-57 tooling; do NOT edit sealed EVAL-02..57 or `src/`):**
   - `scripts/eval58_acquire_options_surface.py` — copy of `scripts/eval57_acquire_options_surface.py` retargeted to emit `EVAL_58_SYNCHRONIZED_ACQUISITION`, out-dir `data/raw/eval58`, same floor + term-structure viability.
   - `scripts/eval58_skew_risk_reversal_net_of_cost.py` — copy of `scripts/eval57_vrp_net_of_cost.py` retargeted to a **skew / risk-reversal (25Δ)** book: per real 5m snapshot & common expiry, select the ~25Δ call and ~25Δ put (IV-backed from real marks via `implied_volatility`; greeks via `black_scholes_greeks`), form the risk-reversal (long one wing / short the other), delta-hedge in the perp, charge each leg's real half bid/ask at entry and exit plus hedge turnover `HEDGE_FEE_BPS`, emit `EVAL_58_PREREGISTRATION` / `EVAL_58_COMBINED` (or `EVAL_58_BLOCKED` only if floor unmet). Pre-register the 25Δ selection rule + exposure rule + cost model + P&L + floors + GO bar BEFORE the verdict run. `--prereg-only` / `--no-write` modes required. Reuse `src/analytics/`, `src/features/options_pricing.py`, `src/backtest/`, `src/telemetry/` (no `phaseNN_*`).
   - `tests/test_eval58_skew_risk_reversal_net_of_cost.py` — deterministic 25Δ selection, common-strike fallback/invalid, net-of-cost P&L, floor/prereg gating.
   ```bash
   python3 -m py_compile scripts/eval58_acquire_options_surface.py \
       scripts/eval58_skew_risk_reversal_net_of_cost.py \
       tests/test_eval58_skew_risk_reversal_net_of_cost.py
   python3 -m pytest -q tests/test_eval58_skew_risk_reversal_net_of_cost.py   # must be green
   ```
   Fix only if a check fails; do not refactor or hand off without step 7.

3. **Independent heavy real acquisition (live public read-only Deribit, BTC+ETH, synchronized ~24h window):**
   ```bash
   python3 scripts/eval58_acquire_options_surface.py --underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval58 --seal
   ```
   ensuring an `EVAL_58_SYNCHRONIZED_ACQUISITION_<UTC>` manifest is written to `research_state/`.
   **Do not proceed unless both underlyings clear the per-underlying floor:**
   surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options trades ≥2000 trades / ≥50
   instruments / ≥240 bars / ≥79200 s span; legs time-overlapping (common 5m bars ≥240); **AND the
   term-structure leg is viable: ≥2 distinct expiries each with a common strike nearest spot present in
   ≥100 snapshots**. Below floor ⇒ widen capture parameters and retry; **never** weaken the floor and
   **never** emit `{"valid": true}` for a below-floor capture.

4. **Pre-register BEFORE measurement:**
   ```bash
   python3 scripts/eval58_skew_risk_reversal_net_of_cost.py --prereg-only
   ```
   This seals `EVAL_58_PREREGISTRATION_<UTC>` from the pre-declared protocol (25Δ wing selection, common
   strike rule, risk-reversal exposure rule, cost model, P&L definition, floors, GO bar) **without measuring**.
   It must be stamped **before** the verdict run (step 6).

5. **Smoke measurement (seals nothing):** dry-run and confirm `floor_ok: true` for both underlyings;
   inspect per-underlying net-of-cost P&L / Sharpe / median IV / skew spread:
   ```bash
   python3 scripts/eval58_skew_risk_reversal_net_of_cost.py --no-write --capture-dir data/raw/eval58
   ```

6. **Seal the verdict:** then run the full measurement, which seals `EVAL_58_COMBINED_<UTC>` (or
   `EVAL_58_BLOCKED_<UTC>` only if floor unmet — never a substitute for a floor-passing verdict):
   ```bash
   python3 scripts/eval58_skew_risk_reversal_net_of_cost.py --capture-dir data/raw/eval58
   ```

7. **Seal gate — session FAILS unless a window acquisition AND a prereg AND a floor-passing combined verdict exist
   with stamp ≥ task timestamp (`2026-11-15T20:00:00Z`) (all three required):**
   ```bash
     python3 scripts/check_session_sealed.py \
        --task-id "INIT-2026-11-15T20:00:00Z-EVAL-58-REAL-OPTIONS-SKEW-RISK-REVERSAL-NET-OF-COST-BTC-ETH-ACQUIRE-MEASURE-AND-SEAL" \
        --glob "EVAL_58_SYNCHRONIZED_ACQUISITION_*" \
        --require-glob "EVAL_58_PREREGISTRATION_*" \
        --require-glob "EVAL_58_COMBINED_*"
   ```
   Must exit `0`. `EVAL_58_BLOCKED_*` does **not** satisfy `--require-glob "EVAL_58_COMBINED_*"`.

8. **Append a session-log line** to this file (measured numbers, floor metrics, per-underlying +
   combined verdict, artifact paths) and leave this handoff as the single durable record. Then set the
   **next** focus rung (a fresh, pre-registered heavy real-data falsification with a new timestamped
   task ID — never a re-run/re-seal of EVAL-02..58).

**Definition of done (non-negotiable):** step 7 exits `0` with `EVAL_58_SYNCHRONIZED_ACQUISITION_<UTC>`,
`EVAL_58_PREREGISTRATION_<UTC>` (pre-verdict), and a floor-passing `EVAL_58_COMBINED_<UTC>` (verdict
`GO CONFIRMED` or `NO-GO CONFIRMED (PASS)`) all stamped ≥ `2026-11-15T20:00:00Z`. A handoff-only
session, re-run/re-seal of EVAL-02..57, full-test-suite discovery loop, `research_state/` enumeration,
or `EVAL_58_BLOCKED_*` in place of a floor-passing combined verdict are **all failures**. The only
acceptable no-seal outcome is a *narrower* handoff whose floor/gate are identical or stricter and whose
only change is a corrected task timestamp (never weaker).

## WHY THIS IS THE RIGHT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE)
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined options + orderflow** strategy,
but every options+orderflow fusion cell (EVAL-46..53) and the options greeks ladder rungs EVAL-54
(delta-hedged short-vol), EVAL-55 (long-gamma gamma-scalping), EVAL-56 (term-structure calendar-spread) and
EVAL-57 (VRP / realized-vs-implied) are sealed `NO-GO CONFIRMED (PASS)`; re-running them is prohibited
re-litigation. The charter's unmeasured heavy rung is **real options pricing / greeks / vol-surface →
net-of-cost evaluation**. The options greeks ladder is now complete: delta (EVAL-54) → gamma (EVAL-55) →
vega/term-structure (EVAL-56) → VRP (EVAL-57). The remaining pure options-native heavy rung is
**skew / risk-reversal (25Δ) (EVAL-58)**: back out real IV from Deribit option marks, select the ~25Δ call
and ~25Δ put at a common expiry, and trade the risk-reversal (long one wing / short the other) delta-hedged
in the perp to harvest (or fail to harvest, net of cost) the skew/risk-reversal premium — the pure
options-native rung not yet measured, requiring new live heavy data (Deribit option trades ~24h-capped =
genuinely new evidence), not a re-run of sealed artifacts. **New timestamped task ID, never a re-run/re-seal
of EVAL-02..57.**

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
New synchronized real Deribit options surface capture (BTC+ETH) over the same ~24h window meeting
per-underlying floor (surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options-venue trades
≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span; legs time-overlapping/common 5m bars ≥240)
**plus the term-structure leg viable: ≥2 distinct expiries each with a common strike nearest spot present
in ≥100 snapshots** → real vol-surface/greeks 25Δ risk-reversal net-of-cost P&L (causal, no look-ahead,
floor-aligned grid) → pre-register `EVAL_58_PREREGISTRATION_*` BEFORE verdict → seal
`EVAL_58_SYNCHRONIZED_ACQUISITION_*` and `EVAL_58_COMBINED_*` (or BLOCKED only if floor unmet, never as
substitute) → pass seal gate. No prior-EVAL re-runs/re-seals, no `research_state/` enumeration, no
full test suite, no handoff-only session.

## BOTTLENECKS — CLEARED / REMAINING (verified 2026-11-15T20:00:00Z)
1. **CLEARED (this session):** EVAL-57 heavy real work complete — tooling green (`scripts/eval57_*`,
   `tests/test_eval57_vrp_net_of_cost.py`; 16 tests pass), acquisition
   `EVAL_57_SYNCHRONIZED_ACQUISITION_20261115T195702Z`, prereg `EVAL_57_PREREGISTRATION_20261115T195900Z`,
   verdict `EVAL_57_COMBINED_20261115T195911Z` **NO-GO CONFIRMED (PASS)**, seal gate exit 0. EVAL-57 no
   longer pending.
2. **REMAINING (next session must clear — tooling bottleneck, heavy work required):** EVAL-58 tooling is
   ABSENT (`scripts/eval58_*`, `tests/test_eval58_*`). The session must build+test EVAL-58 tooling (copy-and-
   retarget EVAL-57), then run live Deribit BTC+ETH synchronized acquisition (floor + term-structure
   viability), pre-register before verdict, run full 25Δ risk-reversal net-of-cost measurement, and seal
   gate exit 0. Handoff-only is a failed session; widening capture parameters is the only remedy for a
   below-floor attempt.
3. **CLEARED:** Deribit public network — EVAL-57 BTC+ETH capture completed at 2026-11-15T19:57:02Z
   (`data/raw/eval57/`). No active network blocker. If a future capture dips below floor, widen capture
   parameters and retry.
4. **CLEARED:** EVAL-52/53/54/55/56/57 sealed `NO-GO CONFIRMED (PASS)` with gate exit 0; their captures
   `data/raw/eval52/`..`data/raw/eval57/` are present and reusable (read-only). No handoff-only loop.
5. **CLEARED:** env ready — `.venv-deps/` present; `./scripts/verify_env.sh --check` exit 0; `.env` absent;
   `LIVE_TRADING_ENABLED` unset/false.
6. **CLEARED:** `scripts/check_session_sealed.py` supports `--glob` + repeatable `--require-glob` (AND); the
   EVAL-58 gate is executable as written in step 7.
7. **CLEARED:** EVAL-57 acquisition/measurement code is a proven, working template for EVAL-58 — reuse it via
   copy-and-retarget (do not edit it). EVAL-57 walks the real 5m surface snapshots causally and backs IV/greeks
   out of real marks; EVAL-58 changes the book to a 25Δ skew / risk-reversal exposure.
8. **CLEARED:** no `data/raw/eval58/` capture and no `EVAL_58_*` artifacts sealed — the only remaining work
   is build+test tooling → live capture → prereg → measure → seal. Nothing else blocks progress.

## ANTI-STALL RULE (read before touching this file)
- **Only** acceptable outputs: (a) sealed `EVAL_58_SYNCHRONIZED_ACQUISITION_*` + `EVAL_58_PREREGISTRATION_*` +
  `EVAL_58_COMBINED_*` with gate exit 0, or (b) a *narrower* timestamped handoff whose floor is
  **identical or stricter** and whose only change is the corrected task timestamp.
- **Do NOT** re-issue at a new timestamp without either sealing or making stricter. A session whose only
  diff to this file is the timestamp is a failed session.
- **Do NOT** weaken the floor, drop an underlying, drop a bar size, or convert the gate to accept
  `EVAL_58_BLOCKED_*` as a verdict.
- **Do NOT** create `EVAL_58_BLOCKED_*` and stop: below-floor means *widen the capture*, not *stop*.
- If external outage blocks capture, re-run with wider capture parameters first; only then record a
  blocked artifact **plus** the exact failing floor metric and the command to resume.
- **Build the tooling first** — EVAL-58 tooling is absent; do not attempt a capture before
  `scripts/eval58_*` + `tests/test_eval58_*` exist and `pytest -q` is green.

## PROHIBITED (hard constraints)
- Do **not** re-run, re-litigate, or re-seal EVAL-02..57; do not edit sealed artifacts, sealed EVAL-52/
  EVAL-53/EVAL-54/EVAL-55/EVAL-56/EVAL-57 scripts/tests, or `src/`.
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
EVAL-02..56 sealed. EVAL-46..56 (options+orderflow ladder + options-surface greeks) all
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
- **EVAL-54** real Deribit options vol-surface/greeks **delta-hedged short-vol** net-of-cost (BTC+ETH) →
  `NO-GO CONFIRMED (PASS)` `research_state/EVAL_54_COMBINED_20261115T175410Z.{json,md}`
  (acq `EVAL_54_SYNCHRONIZED_ACQUISITION_20261115T174956Z`, prereg `EVAL_54_PREREGISTRATION_20261115T175351Z`;
  pooled PBO 0.5417; BH-FDR rejected []; seal gate exit 0). EVAL-54 immutable.
- **EVAL-55** real Deribit options vol-surface/greeks **gamma-hedged (long-gamma gamma-scalping)** net-of-cost
  (BTC+ETH) → `NO-GO CONFIRMED (PASS)` `research_state/EVAL_55_COMBINED_20261115T180515Z.{json,md}`
  (acq `EVAL_55_SYNCHRONIZED_ACQUISITION_20261115T180300Z`, prereg `EVAL_55_PREREGISTRATION_20261115T180500Z`;
  floor OK True; BTC best Sharpe 1.1330 any_pass false; ETH best Sharpe 0.8410 any_pass false; pooled PBO 0.3333;
  BH-FDR rejected []; seal gate exit 0). EVAL-55 immutable.
- **EVAL-56** real Deribit options vol-surface/greeks **term-structure calendar-spread** net-of-cost
  (BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_56_COMBINED_20261115T190126Z.{json,md}`
  (acq `EVAL_56_SYNCHRONIZED_ACQUISITION_20261115T185751Z`, prereg `EVAL_56_PREREGISTRATION_20261115T190016Z`;
  floor OK True; BTC best Sharpe −0.1203 any_pass false; ETH best Sharpe −0.1208 any_pass false; pooled PBO 0.5000;
  BH-FDR rejected []; seal gate exit 0). EVAL-56 immutable.
- **EVAL-57** real Deribit options vol-surface/greeks **volatility risk premium (VRP) / realized-vs-implied**
  net-of-cost (BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_57_COMBINED_20261115T195911Z.{json,md}`
  (acq `EVAL_57_SYNCHRONIZED_ACQUISITION_20261115T195702Z`, prereg `EVAL_57_PREREGISTRATION_20261115T195900Z`
  (+195911Z); floor OK True; BTC best Sharpe 1.1620 `vrp_straddle_delta_hedged::lb12::vt1.0::sc1.0::reb2`
  any_pass false; ETH best Sharpe 7.7375 `vrp_straddle_delta_hedged::lb24::vt0.5::sc0.5::reb2` any_pass true;
  pooled PBO 0.3750; BH-FDR rejected 6 ETH configs but BTC never passed → combined NO-GO; seal gate exit 0).
  EVAL-57 immutable.

**EVAL-58 is the next focus rung and is NOT yet sealed.** Tooling is ABSENT; the next session must build +
test `scripts/eval58_*` + `tests/test_eval58_*` (copy-and-retarget EVAL-57) then perform heavy real
capture/measurement/seal per the authoritative task above (no re-run/re-seal of EVAL-02..57).

Earlier: EVAL-37 audit `PASS 9/9`; EVAL-41/42 options pillar closed; EVAL-43 orderflow full roster
`NO-GO CONFIRMED (PASS)`; EVAL-44 `CAMPAIGN_CLOSED` (BTC-scoped); EVAL-45 ETH orderflow `NO-GO` + options
`BLOCKED`. The combined options+orderflow thesis is not net-of-cost tradable on all measured cells; the
pure options-native delta-hedged (EVAL-54), long-gamma (EVAL-55), term-structure calendar-spread (EVAL-56)
and VRP / realized-vs-implied (EVAL-57) rungs are all NO-GO. EVAL-58 (skew / risk-reversal 25Δ net-of-cost)
is the next unmeasured heavy rung.

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (imports `src/` → needs numpy).
- **EVAL-54/55 capture schema** (`scripts/eval54_acquire_options_surface.py` / `scripts/eval55_acquire_options_surface.py`):
  one file per underlying, `data/raw/eval5{4,5}/options_surface_{BTC,ETH}_<stamp>.json`, with
  `surface.snapshots[]` (each has `bar_ms`, causal `spot` = perp close at bar end, and `quotes[]` with
  `strike`/`expiry`/`option_type`/`bid`/`ask`/`mark`), `option_trades[]` (floor parity), and
  `perp_candles[]` (1m). No synthetic data; `source.provenance` records real Deribit public provenance.
  **EVAL-58 acquisition is a copy-and-retarget of EVAL-57** (same real surface + order flow + perp capture)
  writing `EVAL_58_SYNCHRONIZED_ACQUISITION_*`; do not edit the sealed EVAL-57 acquisition.
- **EVAL-54/55/56/57 MEASUREMENT GRID ALIGNMENT:** the hedge walks the real 5m surface snapshots in ascending
  time; each snapshot is an end-of-bar state at `bar_ms + 300s` (its `spot` is the causal perp close). IV is
  backed out of the *real* mark (`implied_volatility(mark*spot, spot, K, 0, T, type)`) and greeks come from
  `black_scholes_greeks` at that IV (intrinsic-delta fallback if the IV solve fails). P&L is causal:
  decision at bar `k` → outcome over `[k, k+1]`.
- **EVAL-58 SKEW/RISK-REVERSAL-SPECIFIC GOTCHA (new):** a risk-reversal needs the **~25Δ call and ~25Δ put**
  at a common expiry. Back IV out of each real mark, compute each option's delta via `black_scholes_greeks`,
  select the call whose |delta| is nearest 0.25 and the put whose delta is nearest −0.25 (both quoted, call AND
  put) at that expiry; if either wing is missing, fall back to the nearest-delta quoted wing on that side; if
  still none, that config is invalid (do not fabricate). The exposure is set by the pre-registered risk-reversal
  rule (no fitting), delta-hedged in the perp. Charge each leg's real half bid/ask at entry and exit (both
  legs), hedge turnover `HEDGE_FEE_BPS`; full spread charged when the risk-reversal side flips.
- **EVAL-54/55/56/57 COST MODEL:** hedge turnover `HEDGE_FEE_BPS=5` on `|Δhedge|*S`; long legs pay the real half
  bid/ask at entry (ask) and exit (bid); return = net-of-cost P&L / S per 1-unit underlying notional.
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
- **2026-11-15T17:49:56Z–17:54:10Z (EVAL-54 COMPLETED):** heavy real synchronized Deribit capture BTC+ETH →
  `EVAL_54_SYNCHRONIZED_ACQUISITION_20261115T174956Z` (floor met: BTC 289/102/289/4439/86304/287; ETH
  289/103/289/3045/86269/287); prereg `EVAL_54_PREREGISTRATION_20261115T175351Z` (+175410Z); verdict
  `EVAL_54_COMBINED_20261115T175410Z` — **NO-GO CONFIRMED (PASS)** (pooled PBO 0.5417; BH-FDR rejected [];
  BTC best Sharpe 0.2478 any_pass false; ETH best Sharpe 0.4178 any_pass false; all underlyings pass false).
  Seal gate exit 0. EVAL-54 immutable. Handoff updated; EVAL-54 bottleneck cleared.
- **2026-11-15T17:57:53Z (EVAL-55 task set; EVAL-55 tooling absent):** set authoritative task
  `INIT-2026-11-15T17:57:53Z-EVAL-55-...` with step-7 gate. Next session must build EVAL-55 tooling.
- **2026-11-15T18:00:00Z–18:05:15Z (EVAL-55 COMPLETED — this session):** built EVAL-55 tooling
  (`scripts/eval55_acquire_options_surface.py`, `scripts/eval55_gamma_hedged_net_of_cost.py`,
  `tests/test_eval55_gamma_hedged_net_of_cost.py`; `py_compile` OK; `pytest -q` 10 passed); heavy real
  synchronized Deribit capture BTC+ETH → `EVAL_55_SYNCHRONIZED_ACQUISITION_20261115T180300Z` (floor met:
  BTC 289 snaps/102 inst/289 5m bars/4324 trades/85737 s/286 common; ETH 289/103/289/2967/86227/288);
  prereg `EVAL_55_PREREGISTRATION_20261115T180500Z` (+180515Z) BEFORE verdict; verdict
  `EVAL_55_COMBINED_20261115T180515Z` — **NO-GO CONFIRMED (PASS)** (floor_ok True; BTC best Sharpe 1.1330
  `long_atm_call::2026-11-15::reb1` IV 1.4289 gamma/premium 0.7266 any_pass false; ETH best Sharpe 0.8410
  `long_atm_straddle::2026-11-15::reb2` IV 1.4950 gamma/premium 0.7621 any_pass false; pooled PBO 0.3333;
  BH-FDR rejected []). Seal gate exit 0. EVAL-55 immutable. Handoff updated; EVAL-55 bottleneck cleared.
- **2026-11-15T18:06:00Z (prior — EVAL-55 sealed complete; EVAL-56 tooling absent):** verified
  EVAL-55 sealed (gate exit 0), env green, no `scripts/eval56_*`/`tests/test_eval56_*` present. Set EVAL-56
  focus; authoritative task ID subsequently aligned to **`INIT-2026-11-15T18:08:08Z-...`** (see 18:08:08Z/18:45:11Z/18:47Z entries and header). Gate: `--glob "EVAL_56_SYNCHRONIZED_ACQUISITION_*" --require-glob "EVAL_56_PREREGISTRATION_*" --require-glob "EVAL_56_COMBINED_*"`, stamp ≥ task.
- **2026-11-15T18:47Z (this session — durable handoff clarified/refreshed):** re-verified env green
  (`./scripts/verify_env.sh --check` exit 0), EVAL-55 sealed (`ACQ 180300Z` + `PREREG 180500Z` + `COMBINED 180515Z`, NO-GO CONFIRMED PASS, gate exit 0), seal gate CLI supports `--require-glob` (AND), EVAL-55 templates+`data/raw/eval55/` reusable. **EVAL-56 tooling remains absent (`scripts/eval56_*`, `tests/test_eval56_*`) — no acquisition/measurement/seal performed.** Authoritative next task unchanged: **`INIT-2026-11-15T18:08:08Z-EVAL-56-...`** (gate: `--glob EVAL_56_SYNCHRONIZED_ACQUISITION_* --require-glob EVAL_56_PREREGISTRATION_* --require-glob EVAL_56_COMBINED_*`, stamp ≥ 2026-11-15T18:08:08Z). Next session must do the heavy real work: build/test eval56 tooling → Deribit BTC+ETH ~24h capture (floor + viable 2-expiry common-strike term-structure) → prereg before verdict → calendar-spread net-of-cost measure → seal ACQ+PREREG+COMBINED → gate exit 0. Handoff-only is not completion.
- **2026-11-15T18:49Z (this session — task ID refreshed):** authoritative task ID advanced to
  **`INIT-2026-11-15T18:49:46Z-EVAL-56-REAL-OPTIONS-TERM-STRUCTURE-CALENDAR-SPREAD-NET-OF-COST-BTC-ETH-BUILD-TOOLING-ACQUIRE-MEASURE-AND-SEAL`**; step-7 gate and definition-of-done stamp floor updated to `2026-11-15T18:49:46Z`. EVAL-56 tooling and all three EVAL-56 artifacts remained absent at 18:49Z.
- **2026-11-15T18:57:51Z–19:01:26Z (EVAL-56 COMPLETED — this session):** built EVAL-56 tooling
  (`scripts/eval56_acquire_options_surface.py`, `scripts/eval56_term_structure_calendar_net_of_cost.py`,
  `tests/test_eval56_term_structure_calendar_net_of_cost.py`; `py_compile` OK; `pytest -q` 15 passed);
  heavy real synchronized Deribit capture BTC+ETH → `EVAL_56_SYNCHRONIZED_ACQUISITION_20261115T185751Z`
  (floor met: BTC 289/102/288/4271/86175s/287 common, term-structure viable 8 expiries; ETH
  289/103/288/2928/86293s/288 common, term-structure viable 8 expiries); prereg
  `EVAL_56_PREREGISTRATION_20261115T190016Z` (+190126Z) BEFORE verdict; verdict
  `EVAL_56_COMBINED_20261115T190126Z` — **NO-GO CONFIRMED (PASS)** (floor_ok True; BTC best Sharpe −0.1203
  `long_near_short_far_straddle::2026-11-15->2026-11-16::reb2` IV 0.7976 any_pass false; ETH best Sharpe
  −0.1208 `long_near_short_far_straddle::2026-11-15->2026-11-16::reb2` IV 1.2935 any_pass false; pooled PBO 0.5000;
  BH-FDR rejected []). Seal gate exit 0. EVAL-56 immutable. Handoff updated; EVAL-56 bottleneck cleared.
- **2026-11-15T19:05:00Z (this session — next focus rung set):** authoritative task ID advanced to
  **`INIT-2026-11-15T19:05:00Z-EVAL-57-REAL-OPTIONS-VOL-RISK-PREMIUM-REALIZED-VS-IMPLIED-NET-OF-COST-BTC-ETH-BUILD-TOOLING-ACQUIRE-MEASURE-AND-SEAL`**; EVAL-57 tooling (`scripts/eval57_acquire_options_surface.py`,
  `scripts/eval57_vrp_net_of_cost.py`, `tests/test_eval57_vrp_net_of_cost.py`) and all three EVAL-57
  artifacts remain absent. The only valid next-session output is sealed ACQ+PREREG+COMBINED with gate
  exit 0, or a stricter/narrower timestamped handoff. No handoff-only completion.
- **2026-11-15T19:08:46Z (this session — task refreshed, bottleneck reinforced):** authoritative task ID advanced to **`INIT-2026-11-15T19:08:46Z-EVAL-57-REAL-OPTIONS-VOL-RISK-PREMIUM-REALIZED-VS-IMPLIED-NET-OF-COST-BTC-ETH-BUILD-TOOLING-ACQUIRE-MEASURE-AND-SEAL`**; stamp floor for step-7 gate and definition of done updated to ≥ `2026-11-15T19:08:46Z`. EVAL-57 tooling and all three EVAL-57 artifacts remain absent. Sole bottleneck: build + test `scripts/eval57_*` + `tests/test_eval57_*` before heavy acquisition. Heavy real work is unavoidable: copy-and-retarget EVAL-56 templates → `py_compile` + `pytest -q` green → live Deribit BTC+ETH ~24h capture meeting floor + term-structure viability → pre-register before verdict → full measurement → seal ACQ+PREREG+COMBINED → gate exit 0. Handoff-only is not completion.
- **2026-11-15T19:47:00Z (this session — task timestamp refreshed):** advanced authoritative task ID (superseded by 19:55:04Z below); tooling/artifacts still absent at 19:47Z.

- **2026-11-15T19:55:04Z (this session — bottleneck cleared, task refreshed to force heavy execution):** verified env green (`./scripts/verify_env.sh --check` exit 0), EVAL-56 sealed (ACQ `20261115T185751Z`, PREREG `20261115T190016Z`, COMBINED `20261115T190126Z`, NO-GO CONFIRMED PASS, gate exit 0). Cleared stale "tooling absent" bottleneck: `scripts/eval57_acquire_options_surface.py`, `scripts/eval57_vrp_net_of_cost.py`, `tests/test_eval57_vrp_net_of_cost.py` exist (`py_compile` OK; `pytest -q tests/test_eval57_vrp_net_of_cost.py` 16 passed). No `data/raw/eval57/` and no `EVAL_57_*` acquisition/prereg/combined artifacts sealed. Advanced authoritative task ID to **`INIT-2026-11-15T19:55:04Z-EVAL-57-REAL-OPTIONS-VOL-RISK-PREMIUM-REALIZED-VS-IMPLIED-NET-OF-COST-BTC-ETH-ACQUIRE-MEASURE-AND-SEAL`** (stamp floor ≥ 2026-11-15T19:55:04Z). Next session must perform unavoidable heavy work: live Deribit BTC+ETH synchronized ~24h capture meeting floor + term-structure viability → pre-register before verdict → full VRP net-of-cost measurement → seal ACQ+PREREG+COMBINED → step-7 gate exit 0. Handoff-only is not completion.

- **2026-11-15T19:56:41Z–19:59:11Z (EVAL-57 COMPLETED — this session; bottleneck CLEARED by execution):** verified env green (`verify_env.sh --check` exit 0), EVAL-57 tooling already green (`py_compile` OK; `pytest -q` 16 passed), Deribit network reachable (get_time 200). Removed a premature prereg, then ran the heavy pipeline in order: live synchronized Deribit BTC+ETH `--days 1` capture → `EVAL_57_SYNCHRONIZED_ACQUISITION_20261115T195702Z` (floor OK: BTC 289 snaps/102 inst/288 5m bars/4234 trades/85822 s span/287 common, term-structure viable 8 expiries; ETH 289/102/288/2890/85970 s/287 common, viable 8 expiries); prereg `EVAL_57_PREREGISTRATION_20261115T195900Z` (+195911Z) BEFORE verdict; smoke `--no-write` floor_ok true; verdict `EVAL_57_COMBINED_20261115T195911Z` — **NO-GO CONFIRMED (PASS)** (floor_ok true; BTC best Sharpe 1.1620 `vrp_straddle_delta_hedged::lb12::vt1.0::sc1.0::reb2` any_pass false; ETH best Sharpe 7.7375 `vrp_straddle_delta_hedged::lb24::vt0.5::sc0.5::reb2` any_pass true; pooled PBO 0.3750; BH-FDR rejected 6 ETH configs; combined NO-GO since BTC never passed). Seal gate exit 0. EVAL-57 immutable. Handoff advanced to EVAL-58 (skew/risk-reversal 25Δ); EVAL-58 tooling absent, next session must build+test it then execute heavy capture/measure/seal. EVAL-57 bottleneck cleared by real execution, not handoff.
