# EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_PREREGISTRATION — surface-line traded-form ROBUSTNESS GRID (is the EVAL-184 surface NO-GO a monetization/horizon artifact?)

- Generated: `2026-11-22T09:22:35Z`
- Task: `EVAL185-SURFACE-TRADED-ROBUSTNESS-GRID`
- Hypothesis: The EVAL-184 surface-line NO-GO is NOT a monetization/horizon artifact: no signal/horizon config in the pre-registered 3x5x3 cost x horizon grid yields a pooled BH-FDR rejection with net-of-cost Sharpe>0 + bootstrap CI lower>0 + nonzero positions + >=790 pooled returns at >=2 of 3 cost haircuts (cost-robust), at the sealed EVAL-64 floor on both underlyings. If such a config exists, the surface line is monetizable and EVAL-184's NO-GO was horizon/cost-specific (GO CONFIRMED).
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval84cap` (same disjoint forward capture as EVAL-184)
- Extends: EVAL-184 (identical surface signals, EVAL-62 mark-path net-of-cost P&L, EVAL-64 feasible floor, and EVAL-67 disjointness reused verbatim) with a pre-registered cost x horizon grid: 3 signals x horizons {60,120,240,300,360}s x cost haircuts {0.5x,1x,2x} = 45 pooled configs
- Disjoint from: [2026-11-09T06:48:16Z, 2026-11-16T06:48:16Z]

## Pre-declared protocol

- Underlyings: 2 (BTC+ETH)
- Surface signals: ['skew', 'atm_iv', 'term_slope']
- Signal targets: {'skew': 'forward_variance', 'atm_iv': 'forward_cvar', 'term_slope': 'forward_cvar'}
- Signal builders: {'skew': 'e71.build_surface_bars', 'atm_iv': 'e71.build_surface_bars', 'term_slope': 'e74._term_bars'}
- Horizon grid (s): [60.0, 120.0, 240.0, 300.0, 360.0]
- Cost haircuts: [0.5, 1.0, 2.0]
- Grid config count: 45
- Signal window (s): 900.0
- Target: signal-timed delta-hedged ATM straddle mark-path net-of-cost P&L, pooled across BTC+ETH; cost haircut scales BOTH hedge fee and real spread
- Statistic: {'permutation_perms': 1000, 'permutation_paired': True, 'bootstrap_resamples': 1000, 'bootstrap_block': 2, 'fdr_alpha': 0.1, 'seed': 42}
- Power adequacy: pooled returns >= 790
- Cost-robustness: a (signal,horizon) passes at >= 2 of 3 cost haircuts

## Pre-declared disjointness + capture-window rule

A capture is usable only if [window_start, window_end] does not overlap [2026-11-09T06:48:16Z, 2026-11-16T06:48:16Z] (sealed EVAL-64/65 window); the robustness grid consumes the same disjoint forward capture as EVAL-184, at/after 2026-11-20T00:00:00Z.

## Pre-declared GO bar

GO only if >=1 grid config yields a pooled BH-FDR rejection (across the FULL 45-config grid) AND net-of-cost Sharpe > 0 AND no kill-switch breach (max-DD <= 0.20) AND directional permutation p < 0.05 AND block-bootstrap 95% CI lower > 0 AND nonzero positions > 0 AND pooled returns >= 790 (power), AND the same (signal, horizon) passes at >= 2 of 3 cost haircuts (robust to cost), AND the EVAL-64 floor is met on BOTH underlyings AND both capture windows are disjoint from the sealed window; else NO-GO CONFIRMED (PASS) when floor+disjoint+power but not monetizable (the surface NO-GO is robust to monetization/horizon), INCONCLUSIVE (UNDERPOWERED) when floor+disjoint but pooled returns < 790, or BLOCKED when floor/disjoint fails.

## Pre-registered feasible floor (reused verbatim from sealed EVAL-64)

- min underlyings (BTC+ETH): 2
- Floor checks: snapshots_ok, surface_instruments_ok, surface_bars_ok, trades_ok, of_instruments_ok, of_span_ok, of_bars_ok, perp_bars_ok, perp_span_ok, common_overlap_ok
