# EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_PREREGISTRATION — cross-sectional term-ratio basis -> relative-value straddle spread net-of-cost

- Generated: `2026-11-20T07:32:26Z`
- Task: `EVAL137-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VALUE-STRADDLE-SPREAD-NET-OF-COST`
- Hypothesis: The causal cross-sectional near-to-far ATM implied-vol term-ratio basis (term_ratio_ETH - term_ratio_BTC, expanding-z-scored) timed a cross-sectional relative-value delta-hedged ATM straddle spread (long the cheap-term leg, short the rich-term leg) has a positive net-of-cost mean return on the real on-disk captures, independent of any trading wrapper; tested at the sealed EVAL-64 feasible floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-125 (identical cross-sectional BTC-vs-ETH term-ratio basis GO signal, reused verbatim) and EVAL-80 (identical relative-value ATM straddle-spread trade construction) and EVAL-62 (identical correct mark-path net-of-cost delta-hedged P&L + permutation/bootstrap inference) and EVAL-64 (sealed feasible floor, verbatim, NOT weakened); a distinct, on-charter traded-form monetization cell consuming EVAL-125's GO; no new acquisition

## Pre-declared protocol

- Basis signals: ['term_ratio']
- Bar grid (s): [60.0, 300.0]
- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_k = term_ratio[ETH](k) - term_ratio[BTC](k)
- Position: side_k = sign(rel_z_k) on the BTC leg and -side_k on the ETH leg (long the relatively-cheap-term underlying, short the relatively-rich-term underlying); exposure_k = min(|rel_z_k|, size_cap)
- Combination: ret_rel_k = ret_BTC_k + ret_ETH_k (equal-notional sum of the two spot-normalized EVAL-62 mark-path leg returns)
- Traded form: two-leg cross-sectional relative-value ATM straddle spread (each leg: front expiry, common strike nearest spot, IV backed out of the real mark via EVAL-57 helpers) with the EVAL-62 mark-path net-of-cost P&L per leg: delta-hedge + half real 2-leg spread + hedge fee, spot-normalized, then summed
- Statistic: net-of-cost mean_return > 0 with directional permutation p < 0.05 (H1: mean > 0) and block-bootstrap 95% CI lower > 0
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow None / size_cap 1.0 / min states per config 100

## Pre-declared GO bar

GO only if at least one config (basis signal x bar grid) has net-of-cost mean_return > 0, directional permutation p < 0.05 (H1: mean > 0), block-bootstrap 95% CI lower > 0 on the mean, nonzero positions > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered floor (sealed EVAL-64 verbatim, NOT weakened)

- Sealed EVAL-64 feasible floor verbatim (heaviest floor the free Deribit/OKX public API can deliver; NOT weakened): per underlying surface >= 1000 snapshots / >= 100 instruments / >= 1000 5m bars / >= 600000 s span; perp >= 1000 5m bars / >= 300000 s span; Deribit option trades >= 2000 / >= 150 instruments / >= 82000 s span / >= 240 5m bars; roster >= 2 underlyings. Below the floor the campaign seals BLOCKED, never NO-GO. The EVAL-64 floor governing the EVAL-67/68/69 ladder is untouched.
- Min underlyings: 2
- Min states per config: 100
