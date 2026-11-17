# EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION_PREREGISTRATION — cross-sectional relative-value delta-hedged ATM straddle spread net-of-cost monetization falsification

- Generated: `2026-11-17T13:44:47Z`
- Task: `EVAL80-CROSS-SECTIONAL-RV-STRADDLE-MONETIZATION`
- Hypothesis: The causal cross-sectional options implied-volatility basis (EVAL-77 BTC-vs-ETH relative near-ATM IV / put-call skew, from the real Deribit option trade tapes) can be monetized net-of-cost by a signal-timed cross-sectional relative-value delta-hedged ATM straddle spread (long the relatively-cheap-vol underlying's straddle, short the relatively-rich-vol underlying's) on the BTC/ETH perpetual, on the already-acquired real on-disk captures at the composed floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-77 (identical cross-sectional BTC-vs-ETH relative near-ATM IV / skew basis and Spearman-rank-IC predictiveness GO) and EVAL-62/EVAL-72/EVAL-75/EVAL-76 (identical correct mark-path net-of-cost delta-hedged traded form) but a different, on-charter traded structure: a two-leg cross-sectional relative-value ATM straddle spread rather than a single-underlying straddle or risk reversal; no new acquisition

## Pre-declared protocol

- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_k = signal[ETH](k) - signal[BTC](k)
- Position: side_k = sign(rel_z_k) on the BTC leg and -side_k on the ETH leg (long the relatively-cheap-vol underlying, short the relatively-rich-vol underlying); exposure_k = min(|rel_z_k|, size_cap)
- Combination: ret_rel_k = ret_BTC_k + ret_ETH_k (equal-notional sum of the two spot-normalized EVAL-62 mark-path leg returns)
- Basis signals: ['atm_iv', 'skew']
- Signal window (s): 900.0
- Bar grid (s): [60.0, 300.0]
- Traded form: two-leg cross-sectional relative-value ATM straddle spread (each leg: front expiry, common strike nearest spot, IV backed out of the real mark via EVAL-57 helpers) with the EVAL-62 mark-path net-of-cost P&L per leg: delta-hedge + half real 2-leg spread + hedge fee, spot-normalized, then summed
- Stats: perm 1000 (True) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / size_cap 1.0 / min states per config 100
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if at least one config (basis signal x bar grid) has net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, nonzero positions > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (all sealed floors + alignment; none weakened)

- EVAL-80 consumes both underlyings' traded-instrument data (surface snapshots / perp candles / option trades; EVAL-61/62 floor), both underlyings' near-ATM trade-tape IV (EVAL-71 surface floor), and their cross-sectional alignment. All sealed floors are reused verbatim for each underlying and BOTH must pass, plus >= min_aligned_common_straddle_bars bar-ends where both underlyings carry a priced ATM straddle on the coarsest grid; none is weakened. This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Composed of: ['EVAL-61/62 traded-instrument floor', 'EVAL-71 surface floor', 'cross-sectional straddle alignment floor']
- Min underlyings: 2
- Min aligned common straddle bars (coarsest grid): 200
