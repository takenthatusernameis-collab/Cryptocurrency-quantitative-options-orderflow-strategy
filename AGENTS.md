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
**Next required task is EVAL-45 cross-asset ETH falsification** (see `research_state/durable_handoff.md`,
task `INIT-2026-11-14T23:41:41Z-EVAL-45-CROSS-ASSET-ETH-FALSIFY-AND-SEAL`): acquire real read-only ETH
data, pre-register, run the ETH orderflow + options legs net-of-cost with full statistics, seal
`EVAL_45_*`, and pass
`python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-14T23:41:41Z-EVAL-45-CROSS-ASSET-ETH-FALSIFY-AND-SEAL" --glob "EVAL_45_*"`.
This is mandatory heavy work: a NO-OP, handoff-only, or BTC-re-run session is a failed session.

**Do not** run the full test suite (~5k tests / ~75k state files) as a discovery loop; run only checks
specific to the work item.

## Hard constraints / invariants (non-negotiable)
- **Paper-only.** `.env` must stay absent; `LIVE_TRADING_ENABLED=false`. No live enablement,
  venue/config/credential mutation, or order placement.
- **Never fall back to synthetic data.** Real loaders raise `RealDataUnavailable`. Never relabel
  synthetic as real. Never emit `{"valid": true}`.
- **Sealed artifacts are immutable.** EVAL-02..44 are sealed; append new timestamped artifacts only.
  Do not modify sealed artifacts to make a check pass.
- Network is public read-only market data only, with polite rate limiting, if truly required.
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`
  rather than writing new orchestrator wrappers (`phaseNN_*` wrappers are prohibited).

## Current measured state
Campaign is **TERMINATED on BTC/OKX** (sealed EVAL-36 `TERMINATE_NO_GO`). The options+orderflow strategy
is **not net-of-cost tradable** on the available real BTC/OKX data. EVAL-37 post-termination audit
sealed **PASS 9/9**. EVAL-41/42 sealed the options pillar closed; EVAL-43 sealed the orderflow
pillar closed across the full roster (`NO-GO CONFIRMED (PASS)`,
`research_state/EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z.{json,md}`). EVAL-44 sealed
BTC-scoped `CAMPAIGN_CLOSED`. **The repo charter is multi-asset, so ETH is unmeasured: EVAL-45
cross-asset ETH falsification is the active mandatory rung** — see `research_state/durable_handoff.md`.