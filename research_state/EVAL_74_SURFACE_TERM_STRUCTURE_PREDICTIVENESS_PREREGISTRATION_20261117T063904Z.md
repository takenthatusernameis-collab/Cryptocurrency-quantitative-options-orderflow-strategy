# EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_PREREGISTRATION — options implied-vol term structure -> realized-vol predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-17T06:39:04Z`
- Task: `EVAL74-SURFACE-TERM-STRUCTURE-PREDICTIVENESS`
- Hypothesis: The causal options implied-volatility TERM STRUCTURE (near-dated minus far-dated near-ATM IV slope, and its ratio) has a positive monotone (Spearman rank) relationship with subsequent forward realized volatility of the BTC/ETH perpetual (a steeper/higher near-minus-far IV slope indicates near-term vol stress and predicts higher forward realized vol), independent of any trading wrapper; tested on the already-acquired real on-disk captures at the composed EVAL-71 + term-structure floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71 (identical Spearman rank-IC statistic, forward-rv target and causal expanding-zscore) but a DIFFERENT, distinct surface signal: the cross-expiry term-structure SLOPE (near-minus-far ATM IV), not the near-ATM level/skew EVAL-71 already sealed; no new acquisition

## Pre-declared protocol

- Term signals: ['term_slope', 'term_ratio']
- Signal window (s): 900.0
- Near-ATM band: 0.05
- Min trades per expiry bucket: 5
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar implied-vol term structure from the real Deribit option trade tape: near-ATM trades grouped by expiry; term_slope = IV(near expiry) - IV(far expiry) (vol points), term_ratio = IV(near)/IV(far) - 1; near = earliest and far = latest expiry each with >= min_expiry_trades near-ATM trades in the trailing window; both forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore)
- Target: rv = sqrt(mean(log-return^2)) over the next H perp bars (forward realized vol, strictly after the decision at k)
- Statistic: Spearman rank correlation IC = rho(signal_z_k, rv_forward_k); directional permutation H1: IC>0 (a steeper/higher near-minus-far IV slope predicts higher forward realized vol)
- Stats: perm 1000 (directional (H1: IC>0), shuffle realized-vol series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS) -- the term-structure slope does not add portable forward-vol predictiveness beyond EVAL-71's level/skew.

## Pre-registered feasible floor (EVAL-71 floor + term-structure adequacy; NOT EVAL-64)

- EVAL-74 reuses the sealed EVAL-71 trade-tape IV floor verbatim on the full capture (NOT weakened) and additionally requires a term-structure adequacy floor (>= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with >= MIN_EXPIRY_TRADES trades each, and >= MIN_BARS_WITH_TERM bars carrying a non-null term signal). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- min underlyings: 2
- min distinct near-ATM expiries: 2
- min trades per expiry bucket: 5
- min bars with a term signal: 40
