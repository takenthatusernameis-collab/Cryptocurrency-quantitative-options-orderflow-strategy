# EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_PREREGISTRATION — pooled BTC+ETH OOS traded-form net-of-cost monetization of suggestive EVAL-65 slice (tox/imbalance::bar60, pooled-sample Sharpe)

- Generated: `2026-11-16T22:55:49Z`
- Task: `EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS`
- Hypothesis: Pooled across BTC and ETH, the suggestive EVAL-65 slice (tox/imbalance, bar60) is monetizable net-of-cost out-of-sample on a fresh disjoint real forward window (reused from EVAL-68): pooled Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, >=790 pooled returns (80% power), and BH-FDR rejects, at the sealed EVAL-64 floor on both underlyings.
- Capture dir: `data/raw/eval68` (reused from EVAL-68; no new acquisition)
- Extends: EVAL-65/EVAL-67/EVAL-68 (identical signal/P&L/floor reused; BTC and ETH traded-form returns pooled into one sample on the same disjoint real forward window EVAL-68 acquires)
- Disjoint from: data/raw/eval63/three_way_{BTC,ETH}_20261116T064816Z.json (window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)

## Pre-declared protocol

- Underlyings: ['BTC', 'ETH']
- Tox signals: ['tox', 'imbalance']
- Bar grid (s): [60.0]
- Target: signal-timed delta-hedged ATM straddle mark-path net-of-cost P&L (EVAL-62/64 traded form), pooled across BTC+ETH
- Statistic: Pooled Sharpe / max-drawdown / directional permutation p / block-bootstrap 95% CI of the concatenated per-bar net-of-cost traded-form returns across BTC and ETH, per config
- Stats: perm 1000 (directional (H1: IC>0), shuffle realized-vol series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42
- Power adequacy: pooled returns >= 790

## Pre-declared disjointness + capture-window rule

A capture is usable only if [window_start, window_end] does not overlap [2026-11-09T06:48:16Z, 2026-11-16T06:48:16Z]. Because the free Deribit perp 1m endpoint returns at most 5001 candles (300000 s), each capture must also span >=300000 s. EVAL-69 reuses EVAL-68's capture, which EVAL-68's gate already enforces to be disjoint; EVAL-69 re-checks it here.

EVAL-69 does NOT acquire. It reads EVAL-68's disjoint forward capture at data/raw/eval68 (three_way_BTC_*.json + three_way_ETH_*.json), acquired by scripts/eval68_phaseb_gate.py --execute at/after 2026-11-20T00:00:00Z. Do not weaken the EVAL-64 floor.

## Pre-declared GO bar

GO only if, pooled across BTC+ETH and at least one of the pre-registered configs (tox::bar60, imbalance::bar60), the pooled Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, nonzero positions > 0, pooled returns >= 790 (power), pooled BH-FDR rejects that config, the EVAL-64 floor is met on BOTH underlyings, and both capture windows are disjoint from the sealed window; else NO-GO CONFIRMED (PASS) when floor+disjoint+power but not monetizable, INCONCLUSIVE (UNDERPOWERED) when floor+disjoint but pooled returns < 790, or BLOCKED when floor/disjoint fails.

## Pre-registered feasible floor (reused verbatim from sealed EVAL-64)

- min surface snapshots/underlying: 1000
- min surface 5m bars/underlying: 1000
- min Deribit option trades/underlying: 2000
- min perp 5m bars/underlying: 1000
- min perp span seconds/underlying: 300000.0
- min common 5m bars/underlying: 240
- min underlyings (BTC+ETH): 2
