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
BTC or real ETH**. **Next required task is EVAL-48 — cross-venue combined options+orderflow net-of-cost
replication** (see `research_state/durable_handoff.md`, task
`INIT-2026-11-15T07:23:17Z-EVAL-48-CROSS-VENUE-REPLICATION-FALSIFY-AND-SEAL`): test venue-specificity —
does the combined thesis produce a net-of-cost GO on another venue pair (Deribit options +
Bybit/OKX orderflow)? **This is mandatory heavy work: a NO-OP, handoff-only, BTC/ETH re-run, or
partial/unsealed session is a failed session.** Seal `EVAL_48_*` then pass
`python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-15T07:23:17Z-EVAL-48-CROSS-VENUE-REPLICATION-FALSIFY-AND-SEAL" --glob "EVAL_48_*"`. **EVAL-49 (L2 OFI) is the queued follow-on rung.**

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
the fused options+orderflow strategy is **not net-of-cost tradable on dense real BTC**. **EVAL-47 sealed
the ETH combined thesis: `NO-GO CONFIRMED (PASS)`** at
`research_state/EVAL_47_ETH_COMBINED_20261115T071330Z.{json,md}` (5 ETH tapes × 3 fusion rules, all NO-GO;
seal gate exit 0) — the fused options+orderflow strategy is **not net-of-cost tradable on real ETH**. The
combined thesis is NOT net-of-cost tradable on real BTC or real ETH (both OKX single-venue). Venue-
specificity is the only untested extension — **EVAL-48 is the active mandatory rung**: acquire Deribit
options + Bybit/OKX orderflow tapes, fuse under 3 pre-registered rules, full-tape net-of-cost walk-forward,
full stats, seal `EVAL_48_*`. See `research_state/durable_handoff.md`.