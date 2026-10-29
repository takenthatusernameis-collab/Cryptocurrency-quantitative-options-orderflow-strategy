# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH MIRROR) — LATEST
Timestamp (UTC): 2026-10-29T04:12:21Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 210 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION (PRIORITIZED - DO NOT DEVIATE)

"Cryptocurrency-quantitative-options-orderflow-strategy" — enforce this strict order of priority for every change:

1. **Dealer positioning / gamma exposure** (gamma, gamma flip, net GEX, notional by bands, pin/flip zones) — core edge. Must be numerically correct and vectorized.
2. **Orderflow microstructure** (signed volume, cumulative delta, VPIN/toxicity, absorption, aggressive/passive flow) — flow confirmation. Handle adversarial flows without NaN/Inf leakage.
3. **Volatility surface dynamics** (skew/term structure/RR, ATM term structure, calendar spreads, max pain) — regime/context. Guard against degenerate surfaces.
4. **Regime-aware signal engineering** (cross-features, calibration, normalization, feature leakage prevention) — actionable signals. Determinism required.
5. **Rigorous backtesting** (fills/slippage/costs/partial fills, round lots, walk-forward/OOS, stress, transaction costs) — ground truth. No lookahead. Metrics must be sanitized.

Everything must serve (1)-(5). Mathematical correctness > elegance. Numerical stability required. Vectorize where sensible. No shortcuts.

## BOTTLENECK REMOVAL (APPLIED)

- **Single source of truth enforced**: Both canonical handoff files mirror this content exactly.
- **Ambiguity eliminated**: exactly two canonical handoff files exist (INITIAL_TASK_HANDOFF.md, durable_handoff.md).
- **Mypy/type issues cleared**: Strict mypy with --disallow-untyped-defs passes cleanly.
- **Test suite current**: 210 passing, 1 warning (deprecation in test_schemas only). Do not rely on older numbers.
- **Workflow/test coverage**: All tests present and passing; no missing-test blockers remain.
- **No untracked junk, clean working tree**: Ready for immediate heavy engineering.

## VERIFIED STATE (2026-10-29T04:12:21Z — FROZEN SNAPSHOT)

- `python -m pytest -q` → 210 passed, 1 warning (deprecation in test_schemas only)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 28 source files
- `git status` → On branch main, working tree clean
- `grep -rn "TODO|FIXME|PLACEHOLDER|HACK|XXX" src/ tests/ scripts/` → no matches
- No untracked junk. No placeholder scaffolding.

## Initial Task Message — For Next Agentic Work Session (Mandatory, Non-Optional)
Session start: 2026-10-29T04:12:21Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP.**

### ABSOLUTE FIRST ACTION
**START AT: WIRE NUMERICAL GUARDS INTO data/normalization.py + END-TO-END PIPELINE SERIALIZATION TEST** (next highest-impact uncompleted item). Pick **EXACTLY ONE** highest-impact uncompleted item and **COMPLETE IT END-TO-END** (implementation + tests + mypy clean). Do **NOT** parallelize across multiple items. Leave remaining heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### JUST COMPLETED (END-TO-END)
- **[CRITICAL] Adversarial stress scenarios across ALL modules** — DONE.
- **[CRITICAL] Production telemetry/serialization guardrails** — PRESENT (serialize_metrics/strict with allow_nan=False, structured error logging). Telemetry end-to-end test exists and passing.
- **[HIGH] OOS & walk-forward robustness** — DONE (src/backtest/engine.py + tests/test_oos_walkforward.py). Purge/embargo windows, strict time ordering/no lookahead validation, RNG seed determinism (verify_determinism), allow_nan=False OOS serialization (serialize_oos/assert_oos_finite), stability SerializationError guards. Tests passing.
- **[HIGH] Numerical guards & config validation edge cases** — DONE (src/utils/numerical_guards.py + src/config.py cross-field validation + src/features/volatility.py inf-leak fixes). New module provides safe_divide/safe_log/safe_sqrt/safe_pct_change/ensure_finite/validate_finite/safe_mean/clamp; config rejects slippage>cap, fee_rate>0.1, stop_loss>=take_profit, options_interval<=0, max_position_qty<round_lot. Volatility PCR/Put-call-OI now return finite 0.0 instead of float("inf"). Tests: tests/test_numerical_guards.py + tests/test_config_validation.py (210 total passing). Mypy clean.

### Immediate Objectives (Strict Priority Order)
1. **[HIGH] Wire numerical guards into data/normalization.py + end-to-end pipeline serialization test — START HERE NOW**
   - **data/normalization.py**: `calculate_cumulative_delta` (no isfinite/None guards on trade.size/side), `compute_vwap` (no finiteness on price/size), `calculate_moneyness` (no finiteness on spot/strike) lack numerical guards — NaN/Inf can leak into the pipeline (serves Phase 2 orderflow + Phase 5 backtest). Apply safe_divide/safe_pct_change/validate_finite per existing project patterns.
   - **End-to-end pipeline serialization test**: Add a test that runs `src.main.run_pipeline` (or constructs a full chain→signal→backtest→serialize_metrics path) with adversarial/edge-case configs (zero volume, NaN prices, inverted stops, empty chains) and asserts `serialize_metrics`/`serialize_metrics_strict` never emits NaN/Inf and raises SerializationError on any leak.
   - **Every path** must be typed (mypy strict), logged where errors occur, and covered by tests.

2. **[HIGH] Telemetry coverage gaps (only if discovered while doing #1)**
   - Ensure all new error paths log via log_strategy_error with module/symbol/timestamp/operation.
   - Extend end-to-end serialization to cover any new aggregates if introduced.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` must be >= 210 passing (maintain/improve).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` must be clean.
- Working tree clean. No untracked junk. No TODO/FIXME/placeholder/HACK/XXX.
- If work remains after completing ONE item end-to-end, update **BOTH** handoff files with a new timestamped message and leave heavy work clearly specified with concrete next steps.

## Next Focus Campaign (Never Avoid Heavy Work)
Project-name priority order (derived from "Cryptocurrency-quantitative-options-orderflow-strategy"):
- **Phase 1: Dealer positioning / gamma exposure** (gamma, gamma flip, net GEX, notional by bands, pin/flip zones) — core edge. (IMPLEMENTED: src/features/gamma_exposure.py)
- **Phase 2: Orderflow microstructure** (signed volume, cumulative delta, VPIN/toxicity, absorption, aggressive/passive flow) — flow confirmation. (IMPLEMENTED: src/features/orderflow.py; guards pending in src/data/normalization.py)
- **Phase 3: Volatility surface dynamics** (skew/term structure/RR, ATM term structure, calendar spreads, max pain) — regime/context. (IMPLEMENTED: src/features/volatility.py; inf leaks fixed)
- **Phase 4: Regime-aware signal engineering** (cross-features, calibration, normalization, feature leakage prevention) — actionable signals. (IMPLEMENTED: src/signals/composite.py)
- **Phase 5: Rigorous backtesting** (phases 1-5 are the permanent priority backbone; every change must serve them in order. Phase 8 is the current production-hardening campaign.

**Remaining Phase 8 deliverables (COMPLETE ONE FULLY BEFORE MOVING ON):**
- [x] Stress scenarios across all modules *(COMPLETED)*
- [x] Telemetry/guardrails & serialization end-to-end *(COMPLETED/PRESENT)*
- [x] OOS & walk-forward robustness *(COMPLETED)*
- [x] Numerical guards & config validation edge cases *(COMPLETED)*
- [ ] Wire numerical guards into data/normalization.py + end-to-end pipeline serialization test *(NEXT - START HERE)*

## MANDATE (NON-NEGOTIABLE)
- Heavy engineering only. Mathematical correctness mandatory.
- Numerical stability required. Vectorize where sensible.
- No placeholders/TODOs/FIXMEs. Full implementation with code AND tests.
- Complete **ONE** major item fully end-to-end; leave heavy work for the next agent.
- Never stop at scaffolding. Prioritize strictly by project name order above (gamma/orderflow/vol/signal/backtest).
- Working tree clean. Do not create untracked junk.
- **DO NOT AVOID HEAVY WORK. EXECUTE IN ORDER WITHOUT SKIPPING.**

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes: `python -m pytest` (maintain >= 210 passing).
- Run static checks: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains (update BOTH files).
- DO NOT avoid heavy work. Execute in order without skipping.
