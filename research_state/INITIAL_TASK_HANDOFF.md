# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T02:40:19Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main. Working tree clean (pycache de-tracked from index). Do NOT end the GitHub Actions workflow.

## Initial Task Message

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, ZERO PLACEHOLDERS**

You are continuing in the SAME active run. Scaffolding exists (30 tests pass). Deribit + OKX + Binance connectors implemented. CLI wires all three venues end-to-end. Bottlenecks removed; remaining heavy work is backtest correctness, alpha depth, pipeline robustness.

**START HERE (GATE):**
- Harden `src/backtest/engine.py`: short equity math, SL/TP enforcement, risk limits, non-finite-safe metrics.
- Wire `src/main.py` pipeline fully: no silent exception swallowing, normalization on every ingested object, `--symbols` override, valid JSON output.
- Harden `src/features/*.py`: GEX formula, PCR, IV skew, max pain, CVD, orderflow imbalance — quantitatively correct.

## Immediate Objectives
- [CRITICAL] Fix backtest short-position equity; enforce stop-loss/take-profit on price ticks; enforce max_position_pct and max_drawdown_limit from config; profit_factor must not collapse inf to 0.
- [HIGH] Eliminate silent `except Exception: pass` in `src/main.py`; surface ingestion/feature/backtest errors in results.
- [HIGH] Apply `normalize_options_chain`/`normalize_orderflow` on every ingested object; cross-venue symbol/timestamp consistency.
- [HIGH] Verify GEX/PCR/skew/max-pain/CVD math with edge-case guards (zero division, non-finite).
- [MED] Add numeric tests for backtest shorts/sizing/SLTP/metrics and feature correctness; keep all passing.

## Next Focus Campaign
Phase 1: Backtest Engine Correctness — **short equity, SL/TP, risk limits, metrics, non-finite safety.**
Phase 2: Pipeline Robustness — **no silent swallows, normalization everywhere, --symbols, valid JSON.**
Phase 3: Alpha Features — **GEX/PCR/skew/max-pain/CVD quantitatively correct.**
Phase 4: Tests + Validation — **numeric tests, CI green, no placeholders.**
Phase 5: Hygiene — **clean commits, no pycache tracked, working tree clean.**

## MANDATE
Heavy engineering only. No scaffolding-only "done". Mathematical correctness matters. Vectorize where sensible. Never deflect from implementation. Future agents must do substantial work.

## BOTTLENECKS REMOVED
- Bytecode de-tracked from index; .gitignore excludes __pycache__/*.pyc.
- CI tests restored (30 passing).
- Deribit/OKX/Binance connectors implemented.
- CLI entrypoint wiring all three venues implemented.
- Normalization hardened (`src/data/normalization.py`).

## BLOCKERS / NOTES
- Backtest short equity math incorrect (get_equity subtracts qty*price without crediting short proceeds). **FIX IMMEDIATELY (Phase 1).**
- Pipeline swallows exceptions silently. **FIX IMMEDIATELY (Phase 2).**
- Alpha features need quantitative hardening. **Phase 3.**

**NEXT ACTION:** Edit `src/backtest/engine.py` to fix short equity, enforce SL/TP and risk limits, and produce non-finite-safe metrics. Then proceed to pipeline and feature hardening.
