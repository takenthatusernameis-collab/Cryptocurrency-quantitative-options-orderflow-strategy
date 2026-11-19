# EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION — cross-sectional term_ratio basis (ETH - BTC) -> forward relative realized return tail-asymmetry spread (Spearman rank IC)

- Generated: `2026-11-19T23:10:35Z`
- Task: `EVAL131-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-RETURN-TAIL-ASYMMETRY-SPREAD`
- Task ID: `INIT-2026-11-19T18:15:00Z-EVAL131-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-TAIL-ASYMMETRY-SPREAD`
- Task ID floor stamp: `20261119T181500Z`
- Hypothesis: The causal cross-sectional near-to-far ATM implied-vol term-ratio basis (term_ratio_ETH - term_ratio_BTC, expanding-z-scored) has a positive monotone (Spearman rank) relationship with the subsequent forward relative realized return tail-asymmetry spread (tail_asym_BTC - tail_asym_ETH over the next H perp log returns), independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-77 surface basis floor.
- Surface signals: ['term_ratio']
- Bar seconds grid: [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Min usable pairs per config: 120
- Data availability: no new acquisition; no network
