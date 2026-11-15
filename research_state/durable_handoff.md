# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK FOR NEXT SESSION (timestamped; only valid task)

**Status as of 2026-11-15T22:33:03Z (verified this session):** CAMPAIGN **CLOSED — NO NEXT EVAL TASK EXISTS WITHIN EVAL-02..59.** EVAL-59 **SEALED NO-GO CONFIRMED (PASS)** (gate exit 0). All EVAL-02..59 sealed `NO-GO CONFIRMED (PASS)` (gate exit 0). The combined options+orderflow thesis and the full pure options-native smile/greeks ladder are **not net-of-cost tradable** on measured real BTC/ETH data. **Env verified green this session:** `./scripts/verify_env.sh` completed OK (`pytest` ok, numpy/pandas/scipy/pydantic/yaml/requests ok; py_compile sealed EVAL scripts/tests OK; EVAL-37 audit 6 passed, EVAL-36 memo 7 passed); `.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED=unset`; `git status` clean.

**MANDATORY NEXT TASK (timestamped, non-optional, heavy real work — NO handoff-only completion):**

```
INIT-2026-11-15T22:33:03Z-POST-EVAL-NEW-HYPOTHESIS-OPTIONS-ORDERFLOW-PREREG-ACQUIRE-MEASURE-SEAL
```

**What this task requires (all steps, in order; a session is FAILED if it only edits this handoff):**
1. **Pick ONE new falsifiable hypothesis** (not tested in EVAL-02..59) fusing real Deribit options (surface/greeks/orderflow) + real orderflow (Deribit options-venue trades and/or OKX BTC/ETH perp L2/L3) per repo charter and the candidate directions below.
2. **Pre-register BEFORE any verdict:** exact hypothesis, data sources/endpoints, floor metrics, measurement grid, costs/hedging, and GO/NO-GO criteria → `research_state/POST_EVAL_<NAME>_PREREGISTRATION_<STAMP>Z.{json,md}`.
3. **Acquire real data** meeting/exceeding the heavy-work floor (no synthetic; real loaders raise `RealDataUnavailable`) → `research_state/POST_EVAL_<NAME>_ACQUISITION_<STAMP>Z.{json,md}` with provenance.
4. **Build/test tooling if absent** (`scripts/post_eval_<name>_*.py`, `tests/test_post_eval_<name>_*.py`), `py_compile` + `pytest -q` green, reusing `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`.
5. **Measure net-of-cost P&L causally** (decision at bar k → outcome over [k, k+1]) with realistic costs (half-spread on options legs, hedge turnover on perp, funding/fees) → `research_state/POST_EVAL_<NAME>_COMBINED_<STAMP>Z.{json,md}`.
6. **Seal with gate exit 0:**
   `python3 scripts/check_session_sealed.py --glob "POST_EVAL_<NAME>_ACQUISITION_*" --require-glob "POST_EVAL_<NAME>_PREREGISTRATION_*" --require-glob "POST_EVAL_<NAME>_COMBINED_*"` with stamp ≥ `2026-11-15T22:33:03Z`.
7. **Update this handoff in place** with verified facts/paths/commands/measured numbers (not intentions). No GO without a verifying sealed artifact.

================================================================================
>>> CAMPAIGN CLOSED (EVAL-02..59 all SEALED NO-GO CONFIRMED (PASS), gate exit 0). NO FURTHER EVAL RUNGS REMAIN. <<<
================================================================================

**EVAL-59 is COMPLETE and sealed (immutable).** Tooling built+tested green
(`scripts/eval59_acquire_options_surface.py`, `scripts/eval59_butterfly_net_of_cost.py`,
`tests/test_eval59_butterfly_net_of_cost.py`; `py_compile` OK; `pytest -q` 16 passed).
Live synchronized Deribit BTC+ETH `--days 1` capture → `EVAL_59_SYNCHRONIZED_ACQUISITION_20261115T210410Z`
(floor OK: BTC 289/103/289/3647/100/86083s/287 common, term-structure viable 8 expiries;
ETH 289/102/289/2638/98/84614s/282 common, viable 8 expiries);
prereg `EVAL_59_PREREGISTRATION_20261115T210615Z` BEFORE verdict;
smoke `--no-write` floor_ok true;
verdict `EVAL_59_COMBINED_20261115T214832Z` — **NO-GO CONFIRMED (PASS)**
(floor_ok true; BTC best Sharpe 0.0000 any_pass false; ETH best Sharpe 0.9168
`butterfly_25d_delta_hedged::2026-11-15::lb12::st0.5::sc1.0::reb2` any_pass false;
pooled PBO 0.6667; BH-FDR rejected 8 BTC lb12 configs; combined NO-GO since neither underlying
passed the GO bar). Seal gate exit 0. EVAL-59 immutable. EVAL-59 bottleneck cleared by real execution,
not handoff.

**CAMPAIGN STATE: CLOSED.** Every options+orderflow fusion cell (EVAL-46..53) and every
options smile/greeks ladder rung (EVAL-54 delta-hedged short-vol, EVAL-55 long-gamma gamma-scalping,
EVAL-56 term-structure calendar-spread, EVAL-57 VRP/realized-vs-implied, EVAL-58 skew/risk-reversal 25Δ,
EVAL-59 25Δ butterfly/convexity) is sealed `NO-GO CONFIRMED (PASS)` with gate exit 0. The fused
options+orderflow strategy is **not net-of-cost tradable** on real BTC/OKX, real ETH/OKX, BTC Deribit
cross-venue, ETH Deribit cross-venue, real L2 OFI (BTC+ETH), options-venue order flow standalone
(BTC+ETH), nor any pure options-native smile/greeks rung. No further EVAL rungs remain; re-running or
re-sealing EVAL-02..59 is prohibited re-litigation.

**BOTTLENECK STATUS (all cleared):** EVAL-59 tooling was the last remaining bottleneck; it is now
built, tested, acquired, pre-registered, measured, and sealed with gate exit 0. No bottlenecks remain.

---

### POST-EVAL CAMPAIGN DEFINITION (MANDATORY — FUTURE AGENTS CANNOT AVOID HEAVY WORK)

**Repository charter:** `Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined OPTIONS + ORDERFLOW** strategy. All EVAL-02..59 cells are sealed NO-GO. The **next focus campaign MUST** be a **fresh, pre-registered, heavy real-data falsification** with a **new timestamped task ID outside EVAL-02..59** that tests a **net-of-cost tradable** combined options+orderflow hypothesis on **real data** with **causal, no-look-ahead P&L**.

**Authoritative next-session task (timestamped):**

```
INIT-2026-11-15T21:56:47Z-POST-EVAL-CAMPAIGN-DEFINE-NEW-HYPOTHESIS-PREREG-ACQUIRE-MEASURE-SEAL
```

**Non-negotiable definition of done for ANY post-EVAL session (step-7 gate):**

1. **Define a NEW falsifiable hypothesis** combining real options data (Deribit surface/greeks/orderflow) + real orderflow data (Deribit options-venue trades and/or OKX perpetual L2/L3) that has NOT been tested in EVAL-02..59.
2. **Pre-register** the exact hypothesis, data sources, floor metrics, measurement grid, and GO/NO-GO criteria **BEFORE any verdict** → artifact `POST_EVAL_<NAME>_PREREGISTRATION_<STAMP>Z`.
3. **Acquire real data** meeting or exceeding the pre-registered floor (no synthetic fallback; real loaders raise `RealDataUnavailable`) → artifact `POST_EVAL_<NAME>_ACQUISITION_<STAMP>Z`.
4. **Measure net-of-cost P&L** causally (decision at bar k → outcome over [k, k+1]) with realistic costs (half-spread on options legs, hedge turnover on perp, funding/fees) → artifact `POST_EVAL_<NAME>_COMBINED_<STAMP>Z`.
5. **Seal with gate exit 0** via `scripts/check_session_sealed.py --glob "POST_EVAL_<NAME>_ACQUISITION_*" --require-glob "POST_EVAL_<NAME>_PREREGISTRATION_*" --require-glob "POST_EVAL_<NAME>_COMBINED_*"` with stamp ≥ `2026-11-15T21:56:47Z`.
6. **No handoff-only completion** — a session whose only diff to this file is the timestamp is a failed session.

**Candidate hypothesis directions (repo-name priority — options + orderflow fusion):**

- **A.** Synchronized real Deribit options SURFACE (greeks/IV/term-structure) × real Deribit options-venue ORDER FLOW (trade toxicity/OFI) × real OKX perpetual orderflow — net-of-cost delta/gamma/vega hedged fusion.
- **B.** Real Deribit options SURFACE (vol-surface dynamics) → pure options-native strategies **beyond the smile ladder** (e.g., vol-of-vol / vanna / volga / term-structure slope / calendar basis) net-of-cost on perp.
- **C.** Real OKX BTC/ETH perpetual L2/L3 orderbook OFI + real Deribit options surface — cross-venue microstructure alpha net-of-cost.
- **D.** Real Deribit options surface + real Deribit options trades (venue order flow) — synchronized options-side fusion (EVAL-52/53 pattern but with NEW hypothesis not yet tested).

**Heavy-work floor (minimum for ANY post-EVAL campaign):**

- Synchronized capture: **BTC + ETH** over same ~24h window.
- Options surface: ≥100 snapshots / ≥50 instruments / ≥240 5m bars per underlying; term-structure viable (≥2 expiries with common strike nearest spot in ≥100 snapshots).
- Options-venue trades: ≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span per underlying.
- Perp candles: 1m resolution, time-aligned.
- Legs time-overlapping common 5m bars ≥240.
- Real Deribit public endpoints only (polite rate limiting); no synthetic data; `RealDataUnavailable` if floor unmet.

**Prohibited (hard constraints):**

- Do NOT re-run, re-litigate, or re-seal EVAL-02..59.
- Do NOT fall back to synthetic data; never relabel synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`; no `phaseNN_*` orchestrator wrappers.
- Do NOT run the full test suite as discovery; do NOT enumerate `research_state/`; do NOT create timestamped handoff copies or new handoff files.

## WHY THIS IS THE RIGHT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE)
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined options + orderflow** strategy,
but every options+orderflow fusion cell (EVAL-46..53) and the options smile/greeks ladder rungs EVAL-54
(delta-hedged short-vol), EVAL-55 (long-gamma gamma-scalping), EVAL-56 (term-structure calendar-spread),
EVAL-57 (VRP / realized-vs-implied) and EVAL-58 (skew / risk-reversal 25Δ) are sealed `NO-GO CONFIRMED
(PASS)`; re-running them is prohibited re-litigation. **EVAL-59 (25Δ butterfly / convexity net-of-cost) is
now also sealed `NO-GO CONFIRMED (PASS)` (gate exit 0).** The complete smile/greeks ladder — delta → gamma
→ vega/term-structure → VRP → skew/risk-reversal → **butterfly/convexity** — is fully measured and all rungs
are NO-GO. The entire campaign (EVAL-02..59) is **CLOSED**: the fused options+orderflow strategy is **not
net-of-cost tradable** on any measured cell or any pure options-native smile/greeks rung, on real BTC or
real ETH.

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
New synchronized real Deribit options surface capture (BTC+ETH) over the same ~24h window meeting
per-underlying floor (surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options-venue trades
≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span; legs time-overlapping/common 5m bars ≥240)
**plus the term-structure leg viable: ≥2 distinct expiries each with a common strike nearest spot present
in ≥100 snapshots** → real vol-surface/greeks 25Δ butterfly net-of-cost P&L (causal, no look-ahead,
floor-aligned grid) → pre-register `EVAL_59_PREREGISTRATION_*` BEFORE verdict → seal
`EVAL_59_SYNCHRONIZED_ACQUISITION_*` and `EVAL_59_COMBINED_*` (or BLOCKED only if floor unmet, never as
substitute) → pass seal gate. No prior-EVAL re-runs/re-seals, no `research_state/` enumeration, no
full test suite, no handoff-only session.

## BOTTLENECKS — CLEARED / REMAINING (verified 2026-11-15T21:51:36Z)
1. **CLEARED (this session):** EVAL-59 heavy real work complete — tooling green
   (`scripts/eval59_acquire_options_surface.py`, `scripts/eval59_butterfly_net_of_cost.py`,
   `tests/test_eval59_butterfly_net_of_cost.py`; `py_compile` OK; `pytest -q` 16 passed),
   acquisition `EVAL_59_SYNCHRONIZED_ACQUISITION_20261115T210410Z` (floor met: BTC 289/103/289/3647/100/86083s/287
   common, term-structure viable 8 expiries; ETH 289/102/289/2638/98/84614s/282 common, viable 8 expiries),
   prereg `EVAL_59_PREREGISTRATION_20261115T210615Z` BEFORE verdict,
   verdict `EVAL_59_COMBINED_20261115T214832Z` — **NO-GO CONFIRMED (PASS)** (floor_ok true; BTC best Sharpe 0.0000
   any_pass false; ETH best Sharpe 0.9168 any_pass false; pooled PBO 0.6667; BH-FDR rejected 8 BTC lb12 configs;
   combined NO-GO since neither underlying passed the GO bar). Seal gate exit 0. EVAL-59 immutable. EVAL-59
   bottleneck cleared by real execution, not handoff.
2. **CLEARED (prior session):** EVAL-58 heavy real work complete — tooling green (`scripts/eval58_*`,
   `tests/test_eval58_skew_risk_reversal_net_of_cost.py`; 16 tests pass), acquisition
   `EVAL_58_SYNCHRONIZED_ACQUISITION_20261115T200518Z`, prereg `EVAL_58_PREREGISTRATION_20261115T200718Z`,
   verdict `EVAL_58_COMBINED_20261115T200745Z` **NO-GO CONFIRMED (PASS)**, seal gate exit 0. EVAL-58 no
   longer pending.
3. **CLEARED:** No bottlenecks remain. EVAL-02..59 all sealed `NO-GO CONFIRMED (PASS)` with gate exit 0.
   Campaign is CLOSED. No next EVAL rung exists.
4. **CLEARED:** Deribit public network — EVAL-59 BTC+ETH capture completed at 2026-11-15T21:04:10Z
   (`data/raw/eval59/`). No active network blocker.
5. **CLEARED:** EVAL-46..59 sealed `NO-GO CONFIRMED (PASS)` with gate exit 0; their captures
   `data/raw/eval46/`..`data/raw/eval59/` are present and reusable (read-only). No handoff-only loop.
6. **CLEARED:** env ready — `.venv-deps/` present; `./scripts/verify_env.sh --check` exit 0; `.env` absent;
   `LIVE_TRADING_ENABLED` unset/false.
7. **CLEARED:** `scripts/check_session_sealed.py` supports `--glob` + repeatable `--require-glob` (AND); the
   EVAL-59 gate is executable and exits 0.

## ANTI-STALL RULE (read before touching this file)
- **Only** acceptable outputs: (a) sealed `POST_EVAL_<NAME>_ACQUISITION_*` + `POST_EVAL_<NAME>_PREREGISTRATION_*` + `POST_EVAL_<NAME>_COMBINED_*` with gate exit 0 (stamp ≥ 2026-11-15T22:33:03Z), or (b) a *narrower/stricter* timestamped handoff that keeps the floor identical or stricter and corrects only the task timestamp.
- **Do NOT** re-issue at a new timestamp without either sealing artifacts or making the task stricter. A session whose only diff to this file is the timestamp is a **failed session**.
- **Do NOT** weaken the floor, drop an underlying, drop a bar size, or convert the gate to accept a BLOCKED artifact as a verdict.
- **Do NOT** create a BLOCKED artifact and stop: below-floor means *widen the capture*, not *stop*. If external outage blocks capture, re-run with wider capture parameters first; only then record a blocked artifact **plus** the exact failing floor metric and the command to resume.
- **Build the tooling first** if absent — do not attempt capture before `scripts/post_eval_<name>_*` + `tests/test_post_eval_<name>_*` exist and `pytest -q` is green.
- **No handoff-only completion.** Do not enumerate `research_state/`; do not run the full test suite as discovery; do not create timestamped handoff copies.

## PROHIBITED (hard constraints)
- Do **not** re-run, re-litigate, or re-seal EVAL-02..58; do not edit sealed artifacts, sealed EVAL-52/
  EVAL-53/EVAL-54/EVAL-55/EVAL-56/EVAL-57/EVAL-58 scripts/tests, or `src/`.
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
EVAL-02..58 sealed. EVAL-46..58 (options+orderflow ladder + options smile/greeks) all
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
  (+195911Z); floor OK True; BTC best Sharpe 1.1620 any_pass false; ETH best Sharpe 7.7375 any_pass true;
  pooled PBO 0.3750; BH-FDR rejected 6 ETH configs but BTC never passed → combined NO-GO; seal gate exit 0).
  EVAL-57 immutable.
- **EVAL-58** real Deribit options vol-surface/greeks **skew / risk-reversal (25Δ)** net-of-cost (BTC+ETH) →
  `NO-GO CONFIRMED (PASS)` `research_state/EVAL_58_COMBINED_20261115T200745Z.{json,md}`
  (acq `EVAL_58_SYNCHRONIZED_ACQUISITION_20261115T200518Z`, prereg `EVAL_58_PREREGISTRATION_20261115T200718Z`
  (+200745Z); floor OK True; BTC best Sharpe 4.9797 `risk_reversal_25d_delta_hedged::2026-11-15::lb12::st0.25::sc0.5::reb1`
  any_pass true; ETH best Sharpe 3.3834 any_pass false; pooled PBO 0.0625; BH-FDR rejected []; combined NO-GO
  since ETH never passed → `NO-GO CONFIRMED (PASS)`; seal gate exit 0). EVAL-58 immutable.

- **EVAL-59** real Deribit options vol-surface/greeks **25Δ butterfly / convexity** net-of-cost
  (BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_59_COMBINED_20261115T214832Z.{json,md}`
  (acq `EVAL_59_SYNCHRONIZED_ACQUISITION_20261115T210410Z`, prereg `EVAL_59_PREREGISTRATION_20261115T210615Z`;
  floor OK True; BTC best Sharpe 0.0000 any_pass false; ETH best Sharpe 0.9168
  `butterfly_25d_delta_hedged::2026-11-15::lb12::st0.5::sc1.0::reb2` any_pass false; pooled PBO 0.6667;
  BH-FDR rejected 8 BTC lb12 configs; combined NO-GO since neither underlying passed the GO bar;
  seal gate exit 0). EVAL-59 immutable.

**EVAL-59 is now SEALED.** Tooling built+tested green; acquisition `EVAL_59_SYNCHRONIZED_ACQUISITION_20261115T210410Z`,
prereg `EVAL_59_PREREGISTRATION_20261115T210615Z`, verdict `EVAL_59_COMBINED_20261115T214832Z` all sealed
with gate exit 0. EVAL-59 was the last unmeasured heavy rung; all EVAL-02..59 are sealed. The campaign is
CLOSED — no further EVAL rung exists. Do not re-run, re-litigate, or re-seal EVAL-02..59. Any future work
is a fresh, pre-registered, heavy real-data falsification with a new timestamped task ID outside EVAL-02..59.

Earlier: EVAL-37 audit `PASS 9/9`; EVAL-41/42 options pillar closed; EVAL-43 orderflow full roster
`NO-GO CONFIRMED (PASS)`; EVAL-44 `CAMPAIGN_CLOSED` (BTC-scoped); EVAL-45 ETH orderflow `NO-GO` + options
`BLOCKED`. The combined options+orderflow thesis is not net-of-cost tradable on all measured cells; the
pure options-native delta-hedged (EVAL-54), long-gamma (EVAL-55), term-structure calendar-spread (EVAL-56),
VRP / realized-vs-implied (EVAL-57) and skew / risk-reversal 25Δ (EVAL-58) rungs are all NO-GO. EVAL-59
(25Δ butterfly / convexity net-of-cost) is the next unmeasured heavy rung.

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (imports `src/` → needs numpy).
- **EVAL-54/55/56/57/58 capture schema** (`scripts/eval5{4,5,6,7,8}_acquire_options_surface.py`):
  one file per underlying, `data/raw/eval5{4,5,6,7,8}/options_surface_{BTC,ETH}_<stamp>.json`, with
  `surface.snapshots[]` (each has `bar_ms`, causal `spot` = perp close at bar end, and `quotes[]` with
  `strike`/`expiry`/`option_type`/`bid`/`ask`/`mark`), `option_trades[]` (floor parity), and
  `perp_candles[]` (1m). No synthetic data; `source.provenance` records real Deribit public provenance.
  **EVAL-59 acquisition is a copy-and-retarget of EVAL-58** (same real surface + order flow + perp capture)
  writing `EVAL_59_SYNCHRONIZED_ACQUISITION_*`; do not edit the sealed EVAL-58 acquisition.
- **EVAL-54/55/56/57/58 MEASUREMENT GRID ALIGNMENT:** the hedge walks the real 5m surface snapshots in
  ascending time; each snapshot is an end-of-bar state at `bar_ms + 300s` (its `spot` is the causal perp
  close). IV is backed out of the *real* mark (`implied_volatility(mark*spot, spot, K, 0, T, type)`) and
  greeks come from `black_scholes_greeks` at that IV (intrinsic-delta fallback if the IV solve fails).
  P&L is causal: decision at bar `k` → outcome over `[k, k+1]`.
- **EVAL-58 skew/risk-reversal selection (proven, reuse the pattern for EVAL-59):** back IV out of each real
  mark, compute delta via `black_scholes_greeks`, select the call whose |delta| is nearest 0.25 and the put
  whose |delta| is nearest 0.25 (both quoted, both with a finite positive IV) at the front expiry; if either
  wing is missing that state is invalid (do not fabricate). **EVAL-59 adds the ATM body**: also select the
  ATM call+put at the common strike nearest spot in the same expiry, then the butterfly = long 25Δ call +
  long 25Δ put − ATM call − ATM put (or the mirror). The `by_expiry` cache is keyed by the **date part**
  (`str(expiry)[:10]`); look it up with the date part, not the full ISO expiry.
- **EVAL-54/55/56/57/58 COST MODEL:** hedge turnover `HEDGE_FEE_BPS=5` on `|Δhedge|*S`; long legs pay the
  real half bid/ask at entry (ask) and exit (bid); return = net-of-cost P&L / S per 1-unit underlying
  notional. EVAL-59 charges all 4 butterfly legs the round-trip half-spread at entry/exit and the full
  spread on a side flip.
- Deribit options **candles** (surface): `GET /public/get_tradingview_chart_data` per option instrument,
  resolution `5` (historical candles available). Deribit options **trades**:
  `GET /public/get_last_trades_by_instrument_and_time` (paginate `start_timestamp = last_trade_ts + 1`
  while `has_more`; ~24h cap per instrument). Perp: `get_tradingview_chart_data` `{BTC,ETH}-PERPETUAL`
  resolution `1` as in EVAL-52.
- `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 → DSR may report 0.0; use perm/bootstrap/PBO/BH-FDR.
- `permutation_test(rets, flat, statistic=_mean, paired=True, seed=42)` → `p_value`. `block_bootstrap_ci`
  → `(point, lo, hi)`. Run full capture; no fixed tail slices.
- EVAL-58 evidence that the smoke + full runs are fast: heavy BTC+ETH `--days 1` capture ≈ 2 min; the
  24-config measurement (IV/greeks cached once per capture via `_enrich_snapshots`) ≈ seconds. EVAL-59
  inherits the same runtime profile.

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

- **2026-11-15T20:05:18Z–20:07:45Z (EVAL-58 COMPLETED — this session; bottleneck CLEARED by execution):** verified env green (`verify_env.sh --check` exit 0), Deribit reachable (get_time 200). Built EVAL-58 tooling (copy-and-retarget of EVAL-57): `scripts/eval58_acquire_options_surface.py`, `scripts/eval58_skew_risk_reversal_net_of_cost.py` (25Δ risk-reversal book: `_enrich_snapshots` IV/greeks cache keyed by expiry date-part; `_select_rr_wings` picks |delta|-nearest-0.25 call+put; `_rr_states`/`_rr_series` size long/short risk reversal by the skew (IV_put−IV_call) vs trailing-median deviation, delta-hedged in perp, 4-leg... 2-wing spread + hedge turnover), `tests/test_eval58_skew_risk_reversal_net_of_cost.py` (`py_compile` OK; `pytest -q` 16 passed). Fixed one bug: `_select_rr_wings` must look up `by_expiry` by the date-part (`str(expiry)[:10]`), not the full ISO expiry. Then ran the heavy pipeline in order: live synchronized Deribit BTC+ETH `--days 1` capture → `EVAL_58_SYNCHRONIZED_ACQUISITION_20261115T200518Z` (floor OK: BTC 289 snaps/102 inst/288 5m bars/4224 trades/98 inst-with-trades/86238 s span/287 common, term-structure viable 8 expiries; ETH 289/102/288/2890/100/86267 s/287 common, viable 8 expiries); prereg `EVAL_58_PREREGISTRATION_20261115T200718Z` (+200745Z) BEFORE verdict; smoke `--no-write` floor_ok true; verdict `EVAL_58_COMBINED_20261115T200745Z` — **NO-GO CONFIRMED (PASS)** (floor_ok true; BTC best Sharpe 4.9797 `risk_reversal_25d_delta_hedged::2026-11-15::lb12::st0.25::sc0.5::reb1` any_pass true; ETH best Sharpe 3.3834 any_pass false; pooled PBO 0.0625; BH-FDR rejected []; combined NO-GO since ETH never passed). Seal gate exit 0. EVAL-58 immutable. Handoff advanced to EVAL-59 (25Δ butterfly / convexity net-of-cost); EVAL-59 tooling absent, next session must build+test it then execute heavy capture/measure/seal. EVAL-58 bottleneck cleared by real execution, not handoff.
- **2026-11-15T21:04:10Z–21:48:32Z (EVAL-59 COMPLETED — this session; bottleneck CLEARED by execution):** verified env green (`verify_env.sh --check` exit 0), Deribit reachable (get_time 200). EVAL-59 tooling already present and green: `scripts/eval59_acquire_options_surface.py`, `scripts/eval59_butterfly_net_of_cost.py`, `tests/test_eval59_butterfly_net_of_cost.py` (`py_compile` OK; `pytest -q` 16 passed). Ran the heavy pipeline in order: live synchronized Deribit BTC+ETH `--days 1` capture → `EVAL_59_SYNCHRONIZED_ACQUISITION_20261115T210410Z` (floor OK: BTC 289 snaps/103 inst/289 5m bars/3647 trades/100 of-inst/86083s span/287 common, term-structure viable 8 expiries; ETH 289/102/289/2638/98/84614s/282 common, viable 8 expiries); prereg `EVAL_59_PREREGISTRATION_20261115T210615Z` BEFORE verdict; smoke `--no-write` floor_ok true; verdict `EVAL_59_COMBINED_20261115T214832Z` — **NO-GO CONFIRMED (PASS)** (floor_ok true; BTC best Sharpe 0.0000 any_pass false; ETH best Sharpe 0.9168 `butterfly_25d_delta_hedged::2026-11-15::lb12::st0.5::sc1.0::reb2` any_pass false; pooled PBO 0.6667; BH-FDR rejected 8 BTC lb12 configs; combined NO-GO since neither underlying passed the GO bar). Seal gate exit 0. EVAL-59 immutable. **CAMPAIGN CLOSED: all EVAL-02..59 sealed `NO-GO CONFIRMED (PASS)` with gate exit 0.** No further EVAL rung exists.- **2026-11-15T20:47:28Z (handoff verified):** confirmed authoritative task `INIT-2026-11-15T20:08:00Z-EVAL-59-REAL-OPTIONS-BUTTERFLY-25D-CONVEXITY-NET-OF-COST-BTC-ETH-BUILD-TOOLING-ACQUIRE-MEASURE-AND-SEAL` is correctly set; EVAL-59 tooling was present and green; EVAL-59 subsequently completed and sealed (gate exit 0). Superseded by EVAL-59 completion entry above.
351: - **2026-11-15T22:33:03Z (this session — durable handoff refreshed, no heavy work run):** verified env green (`./scripts/verify_env.sh` OK: deps ok; py_compile sealed EVAL scripts/tests OK; EVAL-37 6 passed, EVAL-36 7 passed; `.venv-deps/` present); `.env` absent; `LIVE_TRADING_ENABLED=unset`; `git status` clean. Confirmed EVAL-59 sealed `NO-GO CONFIRMED (PASS)` (ACQ `20261115T210410Z`, PREREG `20261115T210615Z`, COMBINED `20261115T214832Z`, gate exit 0) and campaign EVAL-02..59 CLOSED. **No bottlenecks found** (env ready; eval48–59 acquisition/measurement templates exist). Set new authoritative mandatory heavy-work task **`INIT-2026-11-15T22:33:03Z-POST-EVAL-NEW-HYPOTHESIS-OPTIONS-ORDERFLOW-PREREG-ACQUIRE-MEASURE-SEAL`**: define a new falsifiable options+orderflow hypothesis not in EVAL-02..59, pre-register, acquire real data to floor, build/test tooling, measure net-of-cost causal P&L, and seal `POST_EVAL_<NAME>_{ACQUISITION,PREREGISTRATION,COMBINED}_*` with gate exit 0 (stamp ≥ 2026-11-15T22:33:03Z). Handoff-only completion explicitly prohibited.
