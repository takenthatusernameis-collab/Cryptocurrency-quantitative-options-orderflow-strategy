# EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_PREREGISTRATION — term-structure signal -> signal-timed delta-hedged ATM straddle net-of-cost monetization falsification

- Generated: `2026-11-17T09:56:28Z`
- Task: `EVAL75-TERM-STRUCTURE-STRADDLE-MONETIZATION`
- Hypothesis: The causal options implied-volatility TERM STRUCTURE (EVAL-74 near-dated minus far-dated near-ATM IV slope, and its ratio) can be monetized net-of-cost by a signal-timed delta-hedged ATM straddle on the BTC/ETH perpetual, on the already-acquired real on-disk captures at the composed floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-72 (identical correct mark-path net-of-cost delta-hedged ATM straddle traded form) but a different, on-charter signal source: EVAL-74's term-structure slope (near-minus-far near-ATM IV) rather than the EVAL-71 level/skew; no new acquisition

## Pre-declared protocol

- Term signals: ['term_slope', 'term_ratio']
- Signal window (s): 900.0
- Bar grid (s): [60.0, 300.0]
- Position: side_k = sign(z_k); exposure_k = min(|z_k|, SIZE_CAP); causal decision at bar k; z_k = expanding-z of the causal EVAL-74 term-structure signal
- Traded form: ATM straddle (front expiry, common strike nearest spot, IV backed out of the real mark via EVAL-57 helpers) with the EVAL-62 mark-path net-of-cost P&L: delta-hedge + half real 2-leg spread + hedge fee, spot-normalized
- Stats: perm 1000 (True) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / size_cap 1.0
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one grid config, net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, nonzero positions > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (both sealed floors; neither weakened)

- EVAL-75 consumes both the traded-instrument data (surface snapshots / perp candles; EVAL-61/62 floor) and the term-structure signal data (per-expiry near-ATM option trade tape; EVAL-74 term-structure floor, which itself reuses the sealed EVAL-71 trade-tape IV floor verbatim). Both sealed floors are reused verbatim and BOTH must pass; neither is weakened. This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Composed of: ['EVAL-61/62 traded-instrument floor', 'EVAL-74 term-structure floor (EVAL-71 trade-tape floor + term adequacy)']
- Min underlyings: 2
