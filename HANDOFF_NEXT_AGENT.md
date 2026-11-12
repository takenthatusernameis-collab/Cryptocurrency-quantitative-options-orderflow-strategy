# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy* — i.e. real pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **quantitative, statistically-defensible evaluation of the strategy**. The project value is the strategy and its measured performance — **not** the generation of more orchestrator wrapper files.
**Single durable handoff/task source:** this file only. `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/durable_handoff.md` are redirect stubs — do not action them or create new handoff files.
**Handoff refreshed:** 2026-11-12T13:39:14Z (UTC).

## P0 SAFETY — VERIFIED 2026-11-12T13:39:14Z — CLEAR
- `.env` **ABSENT**. `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- Runtime deps present: `pydantic, numpy, pandas, scipy, yaml, pytest` on Python 3.12.3. `python3 -m pytest` **works** (the old "pytest unavailable" caveat is stale — do not repeat it).
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO NEXT9 unblock.**

## VERIFIED STATE (ground truth, 2026-11-12T13:39:14Z)
- **Real pipeline works end-to-end (verified in-session):**
  - `PYTHONPATH=. python3 scripts/run_integrated_campaign.py run --campaign-id EVAL_VERIFY_20261112T1337 --checkpoint-dir /tmp/eval_verify_ckpt --seed 42 --n-points 40 --train-window 20 --test-window 10 --step-size 10 --allocation-mode risk_parity` → **exit 0**, `status=completed`, **7/7 steps**; emitted `INTEGRATED_CAMPAIGN_*`, `INTEGRATED_CAMPAIGN_SUMMARY_*`, `INTEGRATED_CAMPAIGN_REGIMES_*`, and six `INTEGRATED_STEP_*` artifacts. (Use the full command in the task below for the real campaign; this was a smoke run.)
  - `PYTHONPATH=. python3 scripts/run_backtest.py` → **exit 0**; wrote `research_state/BACKTEST_20261112T133901Z.json`.
  - `python3 -m pytest --collect-only -q` → **5017 tests collected in ~22s** (imports/deps are healthy).
- **Real code exists (do not rewrite from scratch):** `src/backtest/engine.py` (walk-forward/OOS, portfolio), `src/backtest/options_hedging.py` (delta-hedged PnL + attribution), `src/features/*` (orderflow, gamma exposure, IV surface, liquidity, vol, options pricing/greeks), `src/signals/*` (composite/regime), `src/campaign/integrated.py`, `src/analytics/*`, `src/orderflow/phase32_orderflow_alpha_integration.py`, `src/execution/*`, `src/risk/*`.
- **Phase272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` chain: ARCHIVED — LOW VALUE.** These are ~20 near-identical 259-line wrappers that each import the previous phase and re-emit a vacuous `valid=true issues=[]` evidence JSON. They added no strategy capability. **Do NOT re-implement, re-seal, extend, or "advance" this chain.**

## BOTTLENECKS REMOVED (this handoff)
| Bottleneck | Resolution |
|---|---|
| **Phase292+ clone treadmill** (each session re-seals a near-identical wrapper and hands off N+1) | **CLOSED.** Further `phaseNN_*_post_attribution_seal_orchestrator` files/evidence are rejected. Effort is redirected to the real evaluation campaign below. |
| Stale competing handoff stubs pointing at Phase289/290/286 | **CLEARED.** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/durable_handoff.md` are redirect stubs only. |
| Stale "missing pytest / missing deps" caveat | **CLEARED.** Deps and `pytest` verified working; 5017 tests collect. |
| `research_state/` is ~5 GB / 75k files and can stall naive globbing | **AVOID THE TRAP.** Do not enumerate `research_state/`; use explicit paths/globs. Generated step/phase dirs are disposable; do not mine them for strategy signal. |
| `run_backtest.py` produces a 2-trade, vacuous Sharpe (~6.3) on synthetic data | **ACKNOWLEDGED.** The new campaign must produce statistically meaningful, baseline-compared, multi-seed OOS metrics (not a single synthetic point). |

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, non-optional)

**`INIT-2026-11-12T13:39:14Z-STRATEGY-EVAL-01-FULLSTACK-BASELINE` — ACTIVE. START IMMEDIATELY.**

**Directive:** Execute this campaign **end-to-end in this session** (heavy work required). **No deferral, no stubs, no placeholders, no partial completion, no follow-up questions, and do NOT fall back to the archived phase-clone loop.** Record exact commands/results/caveats.

**Objective:** Build and run a **rigorous, paper-only, full-stack quantitative evaluation of the crypto options + orderflow strategy**, benchmarked against baselines, with confidence intervals, attribution, and an explicit GO/NO-GO. This is the repo's core deliverable.

### Required work (complete in-session — all of it)
1. **Evaluation engine — `src/analytics/strategy_evaluation.py`** (additive, deterministic, finite-guarded, strict serialization):
   - Metric suite from backtest equity/trade/position series: CAGR, annualized return & vol, Sharpe, Sortino, Calmar, max drawdown + duration, hit rate, profit factor, avg win/loss, exposure, turnover, capacity proxy.
   - **Block-bootstrap 95% CIs** (deterministic seed) for headline metrics.
   - **Attribution** by venue / underlying / regime / signal-family; must reconcile to total PnL within tolerance.
   - **Baseline comparison** API.
2. **Evaluation CLI — `scripts/evaluate_strategy.py`**:
   - Drive the real pipeline (`src/campaign/integrated.py` and/or `src/backtest/*`) across **≥5 seeds** and **≥3 allocation modes** (`equal_weight`, `risk_parity`, `vol_target`).
   - Compute **≥3 baselines**: (a) delta-hedged buy-and-hold / long-gamma, (b) naive orderflow-threshold with no hedge, (c) zero-signal / random.
   - Emit `research_state/STRATEGY_EVALUATION_<UTC>.json` **and** `research_state/STRATEGY_EVALUATION_<UTC>.md` with real numbers, per-gate pass/fail, and GO/NO-GO for paper continuation. Label data provenance (synthetic vs processed) explicitly.
3. **Tests — `tests/test_strategy_evaluation.py` + `tests/test_evaluate_strategy.py`**:
   - Assert **numeric invariants** (finite metrics; attribution sums to total within tol; bootstrap CI brackets point estimate; baselines computed; strategy vs baseline ordering computed; rerun determinism/byte-identical). **Not** merely `valid=true`.
   - Must pass under `python3 -m pytest`.
4. **End-to-end runs:** run `scripts/run_integrated_campaign.py run` (≥2 allocation modes) and `scripts/run_backtest.py`; cite the emitted artifacts in the report.

### Exact commands (run, record output)
```bash
python3 -m py_compile src/analytics/strategy_evaluation.py scripts/evaluate_strategy.py tests/test_strategy_evaluation.py tests/test_evaluate_strategy.py

PYTHONPATH=. python3 scripts/run_integrated_campaign.py run --campaign-id EVAL01_<UTC> --seed 42 \
  --n-points 120 --train-window 40 --test-window 20 --step-size 20 --allocation-mode risk_parity

PYTHONPATH=. python3 scripts/run_backtest.py

PYTHONPATH=. python3 -m pytest -q tests/test_strategy_evaluation.py tests/test_evaluate_strategy.py

PYTHONPATH=. python3 scripts/evaluate_strategy.py --seeds 1 2 3 4 5 \
  --allocation-modes equal_weight risk_parity vol_target --write
```

### Acceptance criteria (must be demonstrably met; no stubs)
- `src/analytics/strategy_evaluation.py` computes finite metrics on real pipeline output; unit tests assert numeric invariants and **pass under pytest**.
- ≥5 seeds × ≥3 allocation modes evaluated; bootstrap 95% CIs reported.
- ≥3 baselines computed and compared; attribution reconciles to total PnL within tolerance.
- `research_state/STRATEGY_EVALUATION_<UTC>.json` + `.md` written with **real numbers**, explicit quantitative gates, and a GO/NO-GO for paper continuation.
- Determinism: fixed-seed rerun is byte-identical.
- P0 intact (`.env` absent, `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`).

## HANDOFF DISCIPLINE
- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- After STRATEGY-EVAL-01 is sealed (report + tests green + artifacts), replace the active task with **`INIT-<UTC>-STRATEGY-EVAL-02-...`** advancing the *strategy* (e.g. regime-conditional sizing, capacity/liquidity-aware execution TCA optimization, or cross-venue netting) — **never** return to the archived phase-clone loop.
- Final responses must not ask follow-up questions.

## SCOPE & HARD GUARDS (non-negotiable)
- **Allowed:** `src/`, `scripts/`, `tests/`, `research_state/`. Additive, deterministic, bounded, paper-only, guarded.
- **Forbidden:** live trading, `.env` creation, venue/config/credential mutation, NEXT9 unblock, and any new `phaseNN_*_post_attribution_seal_orchestrator` wrapper.
- Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Do not refactor sealed legacy phases.