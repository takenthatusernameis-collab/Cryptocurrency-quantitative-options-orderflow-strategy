# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T15:08:04Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 288 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | ZERO PLACEHOLDERS | PORTFOLIO WALK-FORWARD/CORRELATION CAMPAIGN COMPLETE | OPTIONS PRICING PHASE 1 COMPLETE | IV SURFACE PHASE 2 CODE EXISTS (implementation src/features/iv_surface.py + schemas src/data/schemas.py IVPoint/IVSurfaceSnapshot) BUT ZERO TESTS | RE-VERIFIED 2026-10-29T15:08:04Z

Session start: 2026-10-29T15:08:04Z

## Progress this session (2026-10-29)
- Removed bottleneck: corrected stale handoff that marked Phase 2 (IV Surface) as "NEXT" when src/features/iv_surface.py and src/data/schemas.py (IVPoint/IVSurfaceSnapshot) already exist; real gap is Phase 2 has ZERO tests, blocking confident progress to Phase 3.
- Phase 1 (Black-Scholes Options Pricing Engine) COMPLETE end-to-end:
  - NEW src/features/options_pricing.py: Black-Scholes-Merton analytical pricing (call + put via put-call parity), analytic Greeks (delta/gamma/vega/theta/rho), finite-difference cross-check (greeks_match_analytic), deterministic IV solver (bisection bracket + Newton refinement, convergence guards, bracket protection, deterministic seeding), degenerate zero-vol/zero-time intrinsic handling, arbitrage boundary rejection, batch pricing, strict serialize_metrics_strict gating on every output.
  - EXTENDED src/data/schemas.py: PricingInputs and PricingOutputs pydantic models with field validators (finite/positive/non-negative/option_type invariants) for serialization safety.
  - NEW tests/test_options_pricing_greeks_adversarial.py: 35 adversarial tests (pricing ranges, put-call parity, intrinsic at zero vol/T, deep ITM/OTM, extreme strikes, Greeks signs/bounds, FD-vs-analytic match, IV round-trip, determinism twice->byte-identical, IV arbitrage violations, negative/non-finite/invalid inputs, strict serialization, schema validation invariants).
- Phase 2 (IV Surface Construction & Calibration): CODE EXISTS (src/features/iv_surface.py: build_iv_surface_from_chain, IVSurface with calendar/butterfly/strike-arbitrage guards, bilinear interpolation, calibrate_iv_surface with smoothing + residuals; src/data/schemas.py IVPoint/IVSurfaceSnapshot). NEEDS: adversarial unit tests + verification pass.
- Verification: 288 tests passing, mypy clean (31 source files), grep for TODO/FIXME/PLACEHOLDER/HACK/XXX = zero, git status clean.

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES. DO NOT RE-IMPLEMENT EXISTING CODE.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Phases 1-5 (dealer positioning/gamma, orderflow microstructure, vol surface, regime-aware signals, stress + walk-forward/OOS robustness hardened) complete. Portfolio-level walk-forward/OOS with cross-symbol correlation constraints + regime-dependent costs/slippage + strict serialization/stability invariants COMPLETE (src/backtest/engine.py:1522-2008; tests/test_portfolio_walkforward_correlation_adversarial.py). Options Pricing Phase 1 COMPLETE (src/features/options_pricing.py, src/data/schemas.py, tests/test_options_pricing_greeks_adversarial.py — 288 tests green). **IV Surface Phase 2 code EXISTS but has NO tests — this is the immediate gap.**

**BASELINE (VERIFIED):** 288 tests passing, mypy clean (--disallow-untyped-defs --warn-return-any), working tree clean, zero TODO/FIXME/PLACEHOLDER/HACK/XXX. Bottlenecks: none; stale Phase-2 "NEXT" marker corrected. No active blockers.

## Immediate Objectives (FIRST ACTIONS)
1. **Verify green baseline**: `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` >=288 passing. `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean. `git status` clean. Grep for TODO/FIXME/PLACEHOLDER/HACK/XXX in src/tests/scripts returns zero.
2. **Close Phase 2 gap**: Add adversarial unit tests for src/features/iv_surface.py (IV solver convergence, surface arbitrage-freeness, calibration stability/residuals, determinism twice->byte-identical, serialization allow_nan=False, edge cases empty chain/deep ITM/OTM/near-expiry). Do not re-implement iv_surface.py.
3. **Verify Phase 2 end-to-end**: full test pass >=288+N, mypy clean, clean tree, all outputs pass serialize_metrics_strict/allow_nan=False.
4. **Then Phase 3**: delta-hedged options backtesting & P&L attribution (src/backtest/engine.py or src/backtest/options_hedging.py).
5. **Handoff if stopping**: Update BOTH handoff files with fresh UTC timestamp, concrete summary, exact remaining targets with file paths, and next steps. Keep byte-for-byte identical.

## Next Focus Campaign (MANDATORY - EXECUTE IN ORDER, HEAVY QUANT ONLY)
**CAMPAIGN: OPTIONS PRICING & GREEKS ENGINE WITH IMPLIED VOLATILITY SURFACE CALIBRATION + DELTA-HEDGED P&L ATTRIBUTION + STRICT SERIALIZATION/STABILITY INVARIANTS**

### Phase 1: Black-Scholes Options Pricing Engine — COMPLETE
- src/features/options_pricing.py: pricing, Greeks (analytic + finite-difference), IV solver (bisection+Newton), deterministic seeding, numerical stability guards, finite/serialization invariants. DONE.
- src/data/schemas.py: PricingInputs / PricingOutputs with serialization invariants. DONE.
- tests/test_options_pricing_greeks_adversarial.py: adversarial tests. DONE.

### Phase 2: Implied Volatility Surface Construction & Calibration — CODE EXISTS, TESTS REQUIRED (CURRENT FOCUS)
- src/features/iv_surface.py: IV surface from options chain quotes across strikes/expiries with TTM interpolation; arbitrage guards (calendar, butterfly, strike); smoothing; deterministic calibration with residuals. CODE DONE — do not rewrite.
- tests/test_iv_surface.py (NEW, REQUIRED): unit tests for IV solver convergence, surface arbitrage-freeness, calibration stability, determinism twice->byte-identical, serialization allow_nan=False, edge cases.
- No lookahead in surface construction; time-ordered calibration.

### Phase 3: Delta-Hedged Options Backtesting & P&L Attribution (NEXT AFTER PHASE 2 TESTS)
- Extend src/backtest/engine.py (or new backtest module) with delta-hedged options P&L: entry, dynamic rebalancing, hedge P&L, theta/gamma P&L decomposition.
- Attribution: P&L explained by delta, gamma, vega, theta, and residual; finite metrics only.
- Integration with existing regime detection for regime-dependent hedging frequency/costs.
- Add unit tests for hedge P&L, attribution sums, and edge cases (deep ITM/OTM, near-expiry).

### Phase 4: Adversarial Testing & Hardening
- Extend tests/test_options_pricing_greeks_adversarial.py and tests/test_iv_surface.py with surface arbitrage, hedge P&L, attribution sums, determinism twice->byte-identical, serialization allow_nan=False, edge cases.
- Full verification pass (>=288+N tests, mypy clean, clean tree).

### Phase 5: Pipeline Integration & End-to-End Campaign Verification
- Wire src/features/options_pricing.py and src/features/iv_surface.py into src/main.py run_pipeline so options marks/Greeks/IV flow into signal generation.
- Integrate pricing/Greeks outputs with CompositeSignalGenerator for regime-dependent hedging frequency/costs (extend signal metadata with greeks/iv).
- Extend src/backtest/engine.py delta-hedged options backtest path to consume IV surface marks and produce attribution.
- End-to-end run: ingestion -> pricing -> signals -> backtest -> strict serialization; determinism check (run twice -> byte-identical JSON).
- Full verification pass (>=288+N tests all green, mypy clean, clean tree).

### Concrete Targets (exact files)
- `tests/test_iv_surface.py` (new, Phase 2 tests - IMMEDIATE) - IV solver convergence, surface arbitrage-freeness, calibration stability, determinism, serialization allow_nan=False, edge cases.
- `src/features/iv_surface.py` (Phase 2 code, EXISTS - do not rewrite) - IV surface construction, arbitrage guards, smoothing, calibration with residuals, deterministic.
- `src/backtest/engine.py` - Extend with delta-hedged options backtest path and P&L attribution (delta/gamma/vega/theta/residual decomposition), or new `src/backtest/options_hedging.py`.
- `src/data/schemas.py` - Already carries IVPoint/IVSurfaceSnapshot; extend if needed with serialization invariants.
- `tests/test_options_pricing_greeks_adversarial.py` - Extend with surface arbitrage, hedge P&L, attribution sums, determinism, serialization allow_nan=False, edge cases.

### Acceptance Criteria
- New tests pass; total tests >= 288 + N (all green).
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
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` → all passing (>=288).
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
