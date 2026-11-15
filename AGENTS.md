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
strategy is **not net-of-cost tradable on dense real BTC**. **Next required task is EVAL-47 — the ETH
COMBINED (fused) options+orderflow net-of-cost cross-asset replication** (see
`research_state/durable_handoff.md`, task
`INIT-2026-11-15T06:12:24Z-EVAL-47-ETH-COMBINED-CROSS-ASSET-REPLICATION-FALSIFY-AND-SEAL`):
this is the natural cross-asset replication of EVAL-46 (does the combined thesis work on ETH?),
and it needs **new data** — the 5 ETH orderflow tapes are git-ignored and were wiped on a reset
(re-acquire with cursor chaining from the trade-id ranges in
`EVAL_45_ETH_TAPE_ACQUISITION_20261115T012656Z.json`, persist to git-tracked `data/raw/eval45/`),
and ETH options must be backfilled (`options_candle_backfill.py` `underlying="ETH"`;
`fetch_live_option_instruments("ETH", session=..., min_moneyness=0.7, max_moneyness=1.3)` → 858 live
instruments; `fetch_option_candles(..., after=..., before=..., max_pages=...)` verified).
Reuse the working `scripts/eval46_integrated_options_orderflow_audit.py` (12/12 tests, full run 3.4 s
via a bit-identical bisect fast signal; accepts `symbol`, `OPTIONS_DIR`, 3 fusion rules, walk-forward,
full stat battery, seal) — parametrize `symbol="ETH"` + an ETH options dir or thin-wrap it (do NOT edit
sealed eval41/42/43/46 or any `src/` module). Pre-register `EVAL_47_PREREGISTRATION_*`, seal
`EVAL_47_*`, and pass
`python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-15T06:12:24Z-EVAL-47-ETH-COMBINED-CROSS-ASSET-REPLICATION-FALSIFY-AND-SEAL" --glob "EVAL_47_*"`.
ETH data is on disk and git-tracked in `data/raw/eval45/` (5 orderflow tapes, 207,600 trades; 201
option snapshots) — use it (no re-acquisition/backfill required unless alignment proves insufficient).
This is mandatory heavy work: a NO-OP, handoff-only, BTC re-run, or partial/unsealed session is a
failed session. **EVAL-48 (cross-venue) and EVAL-49 (L2 OFI) are the queued follow-on rungs.**

**Do not** run the full test suite (~5k tests / ~75k state files) as a discovery loop; run only checks
specific to the work item.

## Hard constraints / invariants (non-negotiable)
- **Paper-only.** `.env` must stay absent; `LIVE_TRADING_ENABLED=false`. No live enablement,
  venue/config/credential mutation, or order placement.
- **Never fall back to synthetic data.** Real loaders raise `RealDataUnavailable`. Never relabel
  synthetic as real. Never emit `{"valid": true}`.
- **Sealed artifacts are immutable.** EVAL-02..45 are sealed; append new timestamped artifacts only.
  Do not modify sealed artifacts to make a check pass.
- Network is public read-only market data only, with polite rate limiting, if truly required.
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`
  rather than writing new orchestrator wrappers (`phaseNN_*` wrappers are prohibited).

## Current measured state
Campaign is **TERMINATED on BTC/OKX** (sealed EVAL-36 `TERMINATE_NO_GO`). The options+orderflow strategy
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
the fused options+orderflow strategy is **not net-of-cost tradable on dense real BTC**. The **ETH
combined** thesis (does the combined strategy work on ETH?) is the only untested extension — **EVAL-47
is the active mandatory rung**: re-acquire the ETH orderflow tapes (git-ignored, wiped) + backfill dense
ETH options + fuse under 3 rules + full-tape net-of-cost walk-forward + full stats + seal `EVAL_47_*`.
See `research_state/durable_handoff.md`.