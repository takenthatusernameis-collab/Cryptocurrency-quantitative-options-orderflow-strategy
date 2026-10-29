# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T14:07:41Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 253 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | ZERO PLACEHOLDERS | PORTFOLIO WALK-FORWARD/CORRELATION CAMPAIGN COMPLETE | RE-VERIFIED 2026-10-29T14:07:41Z

Session start: 2026-10-29T14:07:41Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Phases 1-5 complete (dealer positioning/gamma, orderflow microstructure, vol surface, regime-aware signals, stress + walk-forward/OOS robustness hardened). **Portfolio-level walk-forward/OOS with cross-symbol correlation constraints + regime-dependent costs/slippage + strict serialization/stability invariants is ALSO COMPLETE** (implementation in src/backtest/engine.py:1522-2008; tests in tests/test_portfolio_walkforward_correlation_adversarial.py — all 253 tests green).

**BASELINE (VERIFIED):** 253 tests passing, mypy clean (--disallow-untyped-defs --warn-return-any), working tree clean, zero TODO/FIXME/PLACEHOLDER/HACK/XXX. Bottlenecks: none detected; imports, types, and deps all resolve cleanly. Previous edit-tool invalid-argument bottlenecks from earlier sessions are resolved; no active blockers.

## Immediate Objectives (FIRST ACTIONS)
1. **Verify green baseline**: `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` >=253 passing. `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean. `git status` clean. Grep for TODO/FIXME/PLACEHOLDER/HACK/XXX in src/tests/scripts returns zero.
2. **Execute the next heavy campaign below end-to-end.** Do not stop at scaffolding. Complete fully with tests + mypy + serialization invariants.
3. **Handoff if stopping**: Update BOTH handoff files with fresh UTC timestamp, concrete summary, exact remaining targets with file paths, and next steps. Keep byte-for-byte identical.

## Next Focus Campaign (MANDATORY - EXECUTE IN ORDER, HEAVY QUANT ONLY)
**CAMPAIGN: OPTIONS PRICING & GREEKS ENGINE WITH IMPLIED VOLATILITY SURFACE CALIBRATION + DELTA-HEDGED P&L ATTRIBUTION + STRICT SERIALIZATION/STABILITY INVARIANTS**

### Phase 1: Black-Scholes Options Pricing Engine
- Implement Black-Scholes-Merton analytical pricing for European calls/puts with numerical stability guards.
- Greeks: delta, gamma, vega, theta, rho with analytic formulas and finite-difference cross-checks.
- Implied volatility solver (bisection + Newton refinement) with convergence guards, bracket protection, and deterministic seeding.
- Extend `src/data/schemas.py` to carry pricing inputs/outputs with serialization invariants.

### Phase 2: Implied Volatility Surface Construction & Calibration
- Build IV surface from options chain quotes across strikes and expiries with time-to-maturity interpolation.
- Arbitrage guards: calendar spread, butterfly, and strike-arbitrage enforcement; surface smoothing.
- Deterministic calibration routine with residual reporting and finite/serialization invariants.
- Unit tests for IV solver convergence, surface arbitrage-freeness, and calibration stability.

### Phase 3: Delta-Hedged Options Backtesting & P&L Attribution
- Extend `src/backtest/engine.py` (or new backtest module) with delta-hedged options P&L: entry, dynamic rebalancing, hedge P&L, theta/gamma P&L decomposition.
- Attribution: P&L explained by delta, gamma, vega, theta, and residual; finite metrics only.
- Integration with existing regime detection for regime-dependent hedging frequency/costs.
- Add unit tests for hedge P&L, attribution sums, and edge cases (deep ITM/OTM, near-expiry).

### Phase 4: Adversarial Testing & Hardening
- Create `tests/test_options_pricing_greeks_adversarial.py` with adversarial cases (IV solver non-convergence, surface arbitrage, extreme strikes/expiries, zero/division guards, determinism twice->byte-identical).
- Verify serialization with `allow_nan=False`, finite metrics, edge cases.
- Full verification pass (>=253+N tests, mypy clean, clean tree).

### Concrete Targets (exact files)
- `src/features/options_pricing.py` (new) - Black-Scholes pricing, Greeks (analytic + finite-difference), IV solver (bisection+Newton), deterministic seeding, numerical stability guards, finite/serialization invariants.
- `src/features/iv_surface.py` (new) - IV surface construction from chain quotes, arbitrage guards (calendar/butterfly/strike), surface smoothing, calibration with residuals, deterministic.
- `src/backtest/engine.py` - Extend with delta-hedged options backtest path and P&L attribution (delta/gamma/vega/theta/residual decomposition), or new `src/backtest/options_hedging.py`.
- `src/data/schemas.py` - Extend to carry pricing inputs/outputs and IV surface with serialization invariants.
- `tests/test_options_pricing_greeks_adversarial.py` (new) - Adversarial tests: IV solver, surface arbitrage, hedge P&L, attribution sums, determinism, serialization allow_nan=False, edge cases.

### Acceptance Criteria
- New tests pass; total tests >= 253 + N (all green).
- `mypy src/ --disallow-untyped-defs --warn-return-any` clean.
- `git status` clean, no placeholders.
- All pricing/Greeks/IV outputs pass `serialize_metrics_strict`/`allow_nan=False`; no NaN/Inf propagation.
- IV solver converges deterministically; surface is arbitrage-free; hedge P&L attribution sums reconcile.
- No lookahead in surface construction; time-ordered calibration.

### Execution Notes
- Keep API backward compatible where possible; extend existing types.
- Prefer vectorized/numerically stable ops; guard divisions and square roots (variance >= 0).
- Determinism via existing seed mechanism.
- Complete fully end-to-end (implementation + tests + verification). If blocked by missing deps/imports/types, fix immediately (bottlenecks removed).

## Verification (REQUIRED BEFORE HANDOFF)
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` → all passing (>=253).
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
