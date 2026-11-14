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
**Do not** run the full test suite (~5k tests / ~75k state files) as a discovery loop; run the
specific sealed tests for the work item.

## Hard constraints / invariants (non-negotiable)
- **Paper-only.** `.env` must stay absent; `LIVE_TRADING_ENABLED=false`. No live enablement,
  venue/config/credential mutation, or order placement.
- **Never fall back to synthetic data.** Real loaders raise `RealDataUnavailable`. Never relabel
  synthetic as real. Never emit `{"valid": true}`.
- **Sealed artifacts are immutable.** EVAL-02..37 are sealed; append new timestamped artifacts only.
  Do not modify sealed EVAL-34/35/36/37 to make a check pass.
- Network is public read-only market data only, with polite rate limiting, if truly required.
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`
  rather than writing new orchestrator wrappers (`phaseNN_*` wrappers are prohibited).

## Current measured state
Campaign is **TERMINATED** (sealed EVAL-36 `TERMINATE_NO_GO`). The options+orderflow strategy is
**not net-of-cost tradable** on the available real BTC/OKX data. EVAL-37's independent
post-termination audit was re-run after fixing a checker schema bug and now seals **PASS 9/9**.
This is a full success: a trustworthy NO-GO with sealed measurement.