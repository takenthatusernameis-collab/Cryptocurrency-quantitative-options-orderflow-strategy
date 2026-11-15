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
`EVAL_45_OPTIONS_ETH_BLOCKED_20261115T012906Z`). **Next required task is EVAL-46 ETH options
net-of-cost** (see `research_state/durable_handoff.md`,
task `INIT-2026-11-15T01:30:08Z-EVAL-46-OPTIONS-ETH-NET-OF-COST-FALSIFY-AND-SEAL`): backfill a
dense real ETH-USD option snapshot series (reuse `src/data/options_candle_backfill.py` with
`underlying="ETH"`; 836–1422 live ETH option instruments; `history-candles` verified working)
aligned to a matching real ETH orderflow window (tapes `orderflow_okx_ETH_w01..w05_*.json` on
disk, `2026-11-14 15:01→23:48`), pre-register, run the sealed EVAL-42 audit on ETH via a thin
`scripts/eval46_options_eth_audit.py` (eval42 hard-codes `symbol="BTC"` — do not edit the sealed
script), seal `EVAL_46_*`, and pass
`python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-15T01:30:08Z-EVAL-46-OPTIONS-ETH-NET-OF-COST-FALSIFY-AND-SEAL" --glob "EVAL_46_*"`.
This is mandatory heavy work: a NO-OP, handoff-only, or BTC-re-run session is a failed session.

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
BTC-scoped `CAMPAIGN_CLOSED`. **EVAL-45 (this session)** measured ETH: orderflow `NO-GO CONFIRMED (PASS)`
(5 disjoint real ETH tapes / 172,100 trades; 3/5 positive Sharpe but 2 kill-switch breaches →
replicates BTC), options `BLOCKED` (no real ETH option series). **The ETH options pillar remains OPEN:
EVAL-46 is the active mandatory rung** — see `research_state/durable_handoff.md`.