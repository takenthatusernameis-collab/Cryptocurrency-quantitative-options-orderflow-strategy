# EVAL_184_SURFACE_TRADED_NETFCOST_OOS_PREREGISTRATION — surface-line traded-form net-of-cost OOS monetization of the EVAL-177/168/169 surface GOs (pooled-sample Sharpe)

- Generated: `2026-11-22T06:50:50Z`
- Task: `EVAL184-SURFACE-TRADED-NETOFCOST-OOS`
- Hypothesis: Pooled across BTC and ETH, the surface-line signals (skew -> forward variance, atm_iv/term_slope -> forward CVaR) are monetizable net-of-cost out-of-sample on a fresh disjoint real forward window (data/raw/eval84cap): pooled Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, >=790 pooled returns (power), and BH-FDR rejects, at the sealed EVAL-64 floor on both underlyings.
- Capture dir: `data/raw/eval84cap` (fresh disjoint forward capture)
- Extends: EVAL-69 (identical pooled traded-form + BH-FDR + EVAL-64 floor reused verbatim) with a surface signal source instead of the order-flow toxicity; fresh disjoint forward capture at data/raw/eval84cap
- Disjoint from: [2026-11-09T06:48:16Z, 2026-11-16T06:48:16Z]

## Pre-declared protocol

- Underlyings: 2 (BTC+ETH)
- Surface signals: ['skew', 'atm_iv', 'term_slope']
- Signal targets: {'skew': 'forward_variance', 'atm_iv': 'forward_cvar', 'term_slope': 'forward_cvar'}
- Signal builders: {'skew': 'e71.build_surface_bars', 'atm_iv': 'e71.build_surface_bars', 'term_slope': 'e74._term_bars'}
- Bar grid (s): [60.0, 300.0]
- Signal window (s): 900.0
- Target: signal-timed delta-hedged ATM straddle mark-path net-of-cost P&L, pooled across BTC+ETH
- Statistic: {'permutation_perms': 1000, 'permutation_paired': True, 'bootstrap_resamples': 1000, 'bootstrap_block': 2, 'fdr_alpha': 0.1, 'seed': 42}
- Power adequacy: pooled returns >= 790

## Pre-declared disjointness + capture-window rule

A capture is usable only if [window_start, window_end] does not overlap [2026-11-09T06:48:16Z, 2026-11-16T06:48:16Z] (sealed EVAL-64/65 window); the surface-line traded-form must consume a forward capture disjoint from it, at/after 2026-11-20T00:00:00Z.

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one grid config, net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, nonzero positions > 0, pooled returns >= 790 (power), pooled BH-FDR rejects that config, the EVAL-64 floor is met on BOTH underlyings, and both capture windows are disjoint from the sealed window; else NO-GO CONFIRMED (PASS) when floor+disjoint+power but not monetizable, INCONCLUSIVE (UNDERPOWERED) when floor+disjoint but pooled returns < 790, or BLOCKED when floor/disjoint fails.

## Pre-registered feasible floor (reused verbatim from sealed EVAL-64)

- min underlyings (BTC+ETH): 2
- Floor checks: snapshots_ok, surface_instruments_ok, surface_bars_ok, trades_ok, of_instruments_ok, of_span_ok, of_bars_ok, perp_bars_ok, perp_span_ok, common_overlap_ok
