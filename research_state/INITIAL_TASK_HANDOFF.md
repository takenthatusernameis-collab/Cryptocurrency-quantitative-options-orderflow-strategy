# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T13:10:08Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 239 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T13:10:08Z

Session start: 2026-10-29T13:10:08Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Phases 1-5 complete (dealer positioning/gamma, orderflow microstructure, vol surface, regime-aware signals, stress + walk-forward/OOS robustness hardened). Baseline verified green.

**BASELINE (VERIFIED):** 239 tests passing, mypy clean, working tree clean, zero TODO/FIXME/PLACEHOLDER/HACK/XXX. Bottlenecks: none detected; imports, types, and deps all resolve cleanly.

## Immediate Objectives (FIRST ACTIONS)
1. **Verify green baseline**: `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` >=239 passing. `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean. `git status` clean. Grep for TODO/FIXME/PLACEHOLDER/HACK/XXX in src/tests/scripts returns zero.
2. **Execute the next heavy campaign below end-to-end.** Do not stop at scaffolding. Complete fully with tests + mypy + serialization invariants.
3. **Handoff if stopping**: Update BOTH handoff files with fresh UTC timestamp, concrete summary, exact remaining targets with file paths, and next steps. Keep byte-for-byte identical.

## Next Focus Campaign (MANDATORY - EXECUTE IN ORDER, HEAVY QUANT ONLY)
**CAMPAIGN: PORTFOLIO-LEVEL WALK-FORWARD/OOS WITH CROSS-SYMBOL CORRELATION CONSTRAINTS + REGIME-DEPENDENT COSTS/SLIPPAGE + STRICT SERIALIZATION/STABILITY INVARIANTS**

### Phase 1: Correlation Estimation Infrastructure
- Implement rolling/expanding cross-symbol correlation estimation with time alignment and lookahead guards.
- Add numerical stability (eigenvalue clipping/PSD enforcement), tz-normalization, and deterministic seeding.
- Extend types/schemas to carry correlation matrices with serialization invariants.

### Phase 2: Correlation-Constrained Portfolio Sizing
- Integrate correlation constraints into allocation/sizing with breach prevention and risk-parity style guards.
- Enforce finite metrics, diversification breakdown handling, and constraint validation.
- Add unit tests for constraint enforcement and numerical stability.

### Phase 3: Regime-Dependent Costs/Slippage
- Map regime states to transaction costs/slippage with deterministic regime detection integration.
- Apply regime-dependent costs across all portfolio paths with no lookahead.
- Add tests for cost shock scenarios and invariants.

### Phase 4: Portfolio Walk-Forward/OOS Orchestration
- Extend `src/backtest/engine.py` with portfolio walk-forward/orchestrator across symbols.
- Respect purge/embargo, time ordering, positions-flatten invariants, and portfolio-level OOS aggregation.
- Extend `WalkForwardResults`/add `PortfolioWalkForwardResults` with `serialize_oos`/`assert_oos_finite` parity.

### Phase 5: Adversarial Testing & Hardening
- Create `tests/test_portfolio_walkforward_correlation_adversarial.py` with adversarial cases (correlation spike, diversification breakdown, constraint breaches, tz-aware ordering, determinism).
- Verify serialization with `allow_nan=False`, finite metrics, edge cases.
- Full verification pass (>=239+N tests, mypy clean, clean tree).

### Concrete Targets (exact files)
- `src/backtest/engine.py` - Add portfolio walk-forward/orchestrator: cross-symbol correlation estimation (rolling/expanding, time-aligned, no lookahead), correlation-constrained sizing/allocation, regime-dependent costs/slippage mapping, portfolio-level OOS aggregation with equity/trades across symbols, strict finite/serialization invariants (extend `WalkForwardResults`/add `PortfolioWalkForwardResults` with `serialize_oos`/`assert_oos_finite` parity), purge/embargo respected, tz-normalized time ordering, determinism.
- `tests/test_portfolio_walkforward_correlation_adversarial.py` (new) - Adversarial tests: correlation spike/diversification breakdown, regime-dependent cost shocks, cross-symbol constraint breach prevention, purge/embargo correctness across symbols, strict time ordering across tz-aware/naive, determinism (twice -> byte-identical), serialization with allow_nan=False, finite metrics, positions-flatten invariants, edge cases (empty/short series, single symbol).

### Acceptance Criteria
- New tests pass; total tests >= 239 + N (all green).
- `mypy src/ --disallow-untyped-defs --warn-return-any` clean.
- `git status` clean, no placeholders.
- Portfolio results pass `serialize_oos`/strict serialization with no NaN/Inf; `assert_oos_finite` enforced.
- Correlation constraints enforced with numerical stability; regime-dependent costs/slippage applied deterministically.
- No lookahead: time ordering validated, purge/embargo applied per-window across symbols.

### Execution Notes
- Keep API backward compatible where possible; extend existing types.
- Prefer vectorized/numerically stable ops; guard divisions.
- Determinism via existing seed mechanism.
- Complete fully end-to-end (implementation + tests + verification). If blocked by missing deps/imports/types, fix immediately (bottlenecks removed).

## Verification (REQUIRED BEFORE HANDOFF)
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` → all passing (>=239).
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean.
- `git status` → clean working tree.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero.

## MANDATE (Non-Negotiable)
- **Heavy engineering only.** Mathematical correctness mandatory.
- **Numerical stability required.** Defend all public paths; no NaN/Inf propagation.
- **No placeholders/TODOs/FIXMEs/HACKs/XXX.** Production-grade only.
- **Complete ONE major item fully end-to-end.** Leave concrete instructions if handing off.
- **Never stop at scaffolding.** Never avoid heavy quantitative work.
- **Bottlenecks removed by default.** Fix imports/types/tests immediately.
- **Determinism where relevant.** No hidden global state breaking reproducibility.
- **Working tree must remain clean.** No untracked junk.

## Execution Rules
- Read this handoff first. Treat both canonical files as identical.
- Work only in service of project priority.
- After any change: run verification commands above.
- Keep changes minimal and correct. Prefer hardening over refactoring.
- If you must hand off mid-campaign, update BOTH files with timestamp + concrete next steps before stopping.
