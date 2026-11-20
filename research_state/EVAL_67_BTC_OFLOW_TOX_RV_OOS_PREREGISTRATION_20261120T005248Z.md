# EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION — BTC OOS replication of suggestive EVAL-65 slice (tox/imbalance::bar60::h72, wrapper-free Spearman rank IC)

- Generated: `2026-11-20T00:52:48Z`
- Task: `EVAL67-BTC-OFLOW-TOX-RV-OOS`
- Hypothesis: The suggestive EVAL-65 BTC slice (tox/imbalance, bar60, horizon 72) replicates out-of-sample on a fresh disjoint real BTC window: Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and BH-FDR rejects, at the sealed EVAL-64 feasible floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval67`
- Extends: EVAL-65/EVAL-66 (identical signal/statistic/floor reused; restricted to the single BTC predictive slice on a fresh disjoint real window)
- Disjoint from: data/raw/eval63/three_way_BTC_20261116T064816Z.json (window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)

## Pre-declared protocol

- Underlyings: ['BTC']
- Tox signals: ['tox', 'imbalance']
- Bar grid (s): [60.0]
- Forward horizons (bars): [72]
- Signal: signal_z_k = expanding-zscore of per-bar options order-flow toxicity (tox) / signed-aggressor imbalance (imbalance), reused verbatim from EVAL-61/EVAL-62 (causal, end-of-bar k)
- Target: rv_{k+1..k+H} = sqrt(mean(log-return^2)) over the next H perp 1m/5m bars (forward realized vol, strictly after the decision at k)
- Statistic: Spearman rank correlation IC = rho(signal_z_k, rv_forward_k)
- Stats: perm 1000 (directional (H1: IC>0), shuffle realized-vol series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42

## Pre-declared disjointness + capture-window rule

A capture is usable only if [window_start, window_end] does not overlap [2026-11-09T06:48:16Z, 2026-11-16T06:48:16Z]. Because the free Deribit perp 1m endpoint returns at most 5001 candles (300000 s), the capture must also span >=300000 s. The earliest floor-compliant end is 2026-11-19T18:08:16Z (sealed end + 300000 s); for margin use 2026-11-20T00:00:00Z or later. A naive trailing --days 7 capture before the sealed window has cleared will overlap and must seal BLOCKED.

At/after 2026-11-20T00:00:00Z: --underlying BTC --days 3.7 --end <now-ISO> --out-dir data/raw/eval67 --seal. At end 2026-11-20T00:00:00Z this gives start 2026-11-16T07:12:00Z (disjoint from 2026-11-16T06:48:16Z; span 319680 s). If running later, start moves later and stays disjoint. Do not weaken the EVAL-64 floor.

## Pre-declared GO bar

GO only if, on BTC and at least one of the pre-registered configs (tox::bar60::h72, imbalance::bar60::h72), Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, pooled BH-FDR rejects that config, the EVAL-64 floor is met, and the capture window is disjoint from the sealed BTC window; else NO-GO CONFIRMED (PASS) when floor+disjoint but not predictive, or BLOCKED when floor/disjoint fails.

## Pre-registered feasible floor (reused verbatim from sealed EVAL-64)

- min surface snapshots/underlying: 1000
- min surface 5m bars/underlying: 1000
- min Deribit option trades/underlying: 2000
- min perp 5m bars/underlying: 1000
- min perp span seconds/underlying: 300000.0
- min common 5m bars/underlying: 240
- min underlyings (BTC-only): 1
