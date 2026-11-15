# AGENTS.md — working agreement for this repository

## What this repo is
`Cryptocurrency-quantitative-options-orderflow-strategy` — a **cryptocurrency quantitative
OPTIONS + ORDERFLOW strategy** research repository: real options pricing/greeks/vol-surface,
orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and **net-of-cost evaluation**.

## Single durable handoff (read first, every session)
`research_state/durable_handoff.md` is the **only** actionable handoff. Root
`HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and
`NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers with **no task IDs**.
Do not create new handoff files or timestamped handoff copies. Update the durable handoff in place.

## Verification commands (use these, in this order)
The checkout ships **no** third-party packages. Bootstrap the runtime first:

```bash
./scripts/verify_env.sh            # installs deps into .venv-deps/ (git-ignored) and runs checks
```

That script installs `requirements.txt`, then runs `py_compile` on the sealed EVAL scripts and
`pytest` on the EVAL-37 audit and EVAL-36 memo. Use `./scripts/verify_env.sh --check` to run
against already-installed deps.

Targeted checks (after `source`/export `PYTHONPATH`):
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m py_compile scripts/eval37_final_termination_audit.py tests/test_eval37_final_termination_audit.py
python3 -m pytest -q tests/test_eval37_final_termination_audit.py
python3 scripts/eval37_final_termination_audit.py        # seals a new PASS/FAIL artifact
```

EVAL-44 (BTC-scoped campaign closure certification) is sealed at
`research_state/EVAL_44_CAMPAIGN_CLOSURE_20261114T232641Z.{json,md}` (`CAMPAIGN_CLOSED`).
EVAL-45 (ETH orderflow + options cross-asset falsification) is sealed: ETH orderflow
`NO-GO CONFIRMED (PASS)` (`EVAL_45_ETH_ORDERFLOW_META_20261115T012707Z`, 5 disjoint real ETH
tapes / 172,100 trades) and ETH options `BLOCKED` (no real ETH option series,
`EVAL_45_OPTIONS_ETH_BLOCKED_20261115T012906Z`). EVAL-46 (the integrated/fused options+orderflow
net-of-cost falsification on the FULL dense real BTC dataset — the repo's **core thesis**) is sealed:
**`NO-GO CONFIRMED (PASS)`** at `research_state/EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z.{json,md}`
(prereg `EVAL_46_PREREGISTRATION_20261115T041621Z`; 101 BTC snapshots × 2 real tapes × 3 pre-registered
fusion rules, all NO-GO; pooled PBO 0.833; BH-FDR rejected nothing). The fused options+orderflow
strategy is **not net-of-cost tradable on dense real BTC**. EVAL-47 (ETH combined cross-asset
replication) is sealed: **`NO-GO CONFIRMED (PASS)`** at
`research_state/EVAL_47_ETH_COMBINED_20261115T071330Z.{json,md}` (5 ETH tapes × 3 fusion rules, all
NO-GO; seal gate exit 0). The fused options+orderflow strategy is **not net-of-cost tradable on real
BTC or real ETH**. EVAL-48 (BTC cross-venue replication: **Deribit BTC options + OKX BTC orderflow**) is
sealed: **`NO-GO CONFIRMED (PASS)`** at
`research_state/EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z.{json,md}` (prereg
`EVAL_48_PREREGISTRATION_20261115T081951Z`; acquisition `EVAL_48_DERIBIT_ACQUISITION_20261115T081709Z`;
133 real Deribit BTC snapshots × 2 OKX BTC tapes × 3 fusion rules, all NO-GO; pooled PBO 0.667; BH-FDR
rejected 5 configs; the single-tape midday sign_agreement +5.71 does not replicate on 41d_fresh; seal
gate exit 0). **The chronic "no Deribit data / no acquisition tooling" bottleneck is GONE:**
`scripts/eval48_acquire_deribit_options.py` reconstructs real Deribit option snapshots (reusable for ETH
via `--underlying ETH`) and `scripts/eval48_cross_venue_replication.py` is the tested copy-and-retarget
wrapper. **EVAL-49 (ETH cross-venue), EVAL-50 (real L2 OFI), EVAL-51 (real Deribit options-venue order flow),
EVAL-52/53 (synchronized options SURFACE × options-venue ORDER FLOW), EVAL-54 (delta-hedged short-vol),
EVAL-55 (long-gamma gamma-scalping), EVAL-56 (term-structure calendar-spread), EVAL-57 (VRP /
realized-vs-implied) and EVAL-58 (skew / risk-reversal 25Δ) are ALL SEALED `NO-GO CONFIRMED (PASS)` — see
"Current measured state" below. The options greeks/smile ladder (EVAL-54..58) is COMPLETE, and the next
focus campaign is now DEFINED as EVAL-59 (synchronized real Deribit options SURFACE → 25Δ BUTTERFLY /
CONVEXITY net-of-cost on the underlying BTC/ETH perpetual, the one pure options-native smile rung not yet
measured: EVAL-58 measured the smile SLOPE / risk-reversal, EVAL-59 measures the smile CURVATURE /
butterfly). EVAL-58 tooling (`scripts/eval58_acquire_options_surface.py`,
`scripts/eval58_skew_risk_reversal_net_of_cost.py`, `tests/test_eval58_*`) is sealed/immutable; EVAL-59
tooling does not yet exist and must be built (`scripts/eval59_acquire_options_surface.py`,
`scripts/eval59_butterfly_net_of_cost.py`, `tests/test_eval59_*`).** Do not re-run, re-litigate, or
re-seal EVAL-02..58. Any future work is a fresh, pre-registered, heavy real-data falsification with a new
timestamped task ID; see `research_state/durable_handoff.md` for the authoritative EVAL-59 task.

**Do not** run the full test suite (~5k tests / ~75k state files) as a discovery loop; run only checks
specific to the work item.

## Hard constraints / invariants (non-negotiable)
- **Paper-only.** `.env` must stay absent; `LIVE_TRADING_ENABLED=false`. No live enablement,
  venue/config/credential mutation, or order placement.
- **Never fall back to synthetic data.** Real loaders raise `RealDataUnavailable`. Never relabel
  synthetic as real. Never emit `{"valid": true}`.
- **Sealed artifacts are immutable.** EVAL-02..48 are sealed; append new timestamped artifacts only.
  Do not modify sealed artifacts to make a check pass.
- Network is public read-only market data only, with polite rate limiting, if truly required.
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`
  rather than writing new orchestrator wrappers (`phaseNN_*` wrappers are prohibited).

## Current measured state
Campaign is **CLOSED (EVAL-46..50 all sealed NO-GO CONFIRMED (PASS))**. The options+orderflow strategy
is **not net-of-cost tradable** on the available real BTC/OKX data. EVAL-37 post-termination audit
sealed **PASS 9/9**. EVAL-41/42 sealed the BTC options pillar closed; EVAL-43 sealed the BTC orderflow
pillar closed across the full roster (`NO-GO CONFIRMED (PASS)`,
`research_state/EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z.{json,md}`). EVAL-44 sealed
BTC-scoped `CAMPAIGN_CLOSED`. EVAL-45 measured ETH: orderflow `NO-GO CONFIRMED (PASS)`
(5 disjoint real ETH tapes / 172,100 trades; 3/5 positive Sharpe but 2 kill-switch breaches →
replicates BTC), options `BLOCKED` (no real ETH option series). **EVAL-46 sealed the combined (fused)
options+orderflow thesis on the full dense real BTC data: `NO-GO CONFIRMED (PASS)`**
(`research_state/EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z.{json,md}`; 101 BTC snapshots ×
2 real tapes × 3 pre-registered fusion rules, all NO-GO; pooled PBO 0.833; BH-FDR rejected nothing) —
the fused options+orderflow strategy is **not net-of-cost tradable on dense real BTC**. **EVAL-47 sealed
the ETH combined thesis: `NO-GO CONFIRMED (PASS)`** at
`research_state/EVAL_47_ETH_COMBINED_20261115T071330Z.{json,md}` (5 ETH tapes × 3 fusion rules, all NO-GO;
seal gate exit 0) — the fused options+orderflow strategy is **not net-of-cost tradable on real ETH**.
**EVAL-48 sealed the BTC cross-venue cell (Deribit options + OKX BTC orderflow): `NO-GO CONFIRMED (PASS)`**
at `research_state/EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z.{json,md}` (133 real Deribit BTC snapshots ×
2 OKX BTC tapes × 3 fusion rules, all NO-GO; pooled PBO 0.667; the midday sign_agreement +5.71 does not
replicate on 41d_fresh; seal gate exit 0). **EVAL-49 sealed the ETH cross-venue cell (Deribit ETH options +
OKX ETH orderflow): `NO-GO CONFIRMED (PASS)`** at
`research_state/EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z.{json,md}` (109 Deribit ETH snapshots ×
5 ETH tapes × 3 fusion rules, all NO-GO; seal gate exit 0). **EVAL-50 sealed the real L2 order-book OFI
campaign: `NO-GO CONFIRMED (PASS)`** at
`research_state/EVAL_50_L2_OFI_COMBINED_20261115T134705Z.{json,md}` (acquisition
`EVAL_50_L2_DEPTH_ACQUISITION_20261115T134456Z`; prereg `EVAL_50_PREREGISTRATION_20261115T134705Z`;
floor met: BTC 443 snaps/999.6s, ETH 444 snaps/999.6s; 4 configs/instrument, all NO-GO; pooled PBO 0.5000;
BH-FDR rejected 4 configs; seal gate exit 0). **EVAL-51 sealed the real Deribit options-venue order flow
(BTC+ETH): `NO-GO CONFIRMED (PASS)`** at
`research_state/EVAL_51_OPTIONS_ORDERFLOW_COMBINED_20261115T152005Z.{json,md}` (prereg
`EVAL_51_PREREGISTRATION_20261115T152005Z`; acquisition `EVAL_51_OPTIONS_ORDERFLOW_ACQUISITION_20261115T151843Z`
— BTC 5347 trades / 98 instruments / 289 bars / 86010 s, ETH 3429 trades / 102 instruments / 289 bars /
86381 s; 6 configs/underlying; best Sharpe BTC −1.864, ETH −1.897; pooled PBO 0.5000; seal gate exit 0).
The combined options+orderflow thesis is **NOT net-of-cost tradable on BTC/OKX, ETH/OKX, BTC
Deribit-cross-venue, ETH Deribit-cross-venue, nor on real L2 order-book OFI (BTC+ETH)**, and the
options-venue order flow standalone is **NOT net-of-cost tradable on BTC or ETH**. **The ladder EVAL-46..58
is COMPLETE; the next focus campaign is EVAL-59 (25Δ butterfly / convexity net-of-cost on the real Deribit
options SURFACE, BTC+ETH), the one pure options-native smile rung not yet measured (EVAL-58 measured the
smile SLOPE / risk-reversal; EVAL-59 measures the smile CURVATURE / butterfly).** Do not re-run,
re-litigate, or re-seal EVAL-02..58. Any future work is a fresh, pre-registered, heavy real-data
falsification with a new timestamped task ID. See `research_state/durable_handoff.md`.