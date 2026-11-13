# SAMPLE_ADEQUACY_ACQUISITION_21 — GO

- Generated: `2026-11-13T16:51:08.037643Z`
- Trading mode: `paper` (live=False)
- never `{"valid": true}`: `True`
- **data_provenance: `synthetic`** — source_path=`None`, seed=`42`, reason=`no_real_tape_meets_adequacy_floors`
- ⚠ SYNTHETIC tape: the net-of-cost verdict on this sample is on synthetic data and MUST be re-confirmed on a real tape before any capital decision.

## Sample adequacy
- bars: **3400** / returns: **3399** / walk-forward windows: **82** / trades: **40800**
- return mean **-1.2120 bps/bar**, std **20.0460 bps**, t **-3.5250**
- floors: n_returns >= 1000, n_windows >= 20 -> **sample_adequate = True**
- minimum detectable |IC| at n_returns=3 (IC-horizon count): **1.617496** (80% power, 5% two-sided; sealed-helper quirk)
- minimum detectable |IC| at n_returns=3399: **0.048054**; min |horizon IC| **0.235529** vs max horizon MDE **0.048189**; IC mean **0.375126** (t **6.5444**)

## Degenerate pillars
- **options**: unique=1 degenerate=**True** values=[0.3333333333333333]
- **orderflow**: unique=3345 degenerate=**False** values=[-1.0, -0.9906985921169285, -0.989317201026739, -0.9892238045031495, -0.9887640674418053, -0.9886485715810176, -0.9871462994599984, -0.9863225750085819]
- **toxicity**: unique=2167 degenerate=**False** values=[0.0002084635226674557, 0.00043072492917824667, 0.002170215341168391, 0.0032584470917395685, 0.003364438707293245, 0.003744509992114699, 0.0039007091091102413, 0.0044420073930105915]

## Net-of-cost by pillar (per-bar returns, annualisation from bar duration)

| pillar | n_ret | gross total | net total | gross Sharpe | net Sharpe | cost bps | turnover | rejections |
|---|---|---|---|---|---|---|---|---|
| combined | 3399 | 0.300476 | 0.300366 | 154.5406 | 154.4828 | 1.1031 | 0.9965 | 0 |
| options_only | 3399 | -0.411963 | -0.412073 | -87.6673 | -87.6926 | 1.1091 | 1.0000 | 0 |
| orderflow_only | 3399 | 2.624589 | 2.624479 | 639.6301 | 639.6137 | 1.1091 | 1.0000 | 0 |
| flat | 3399 | 0.000000 | 0.000000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 |

- Sharpe basis: per-bar, annualisation **2102400.00** (expected 2102400.00); window-level Sharpe **842.8424** over **84** windows.

## Sizing consistency
- requested max_position_pct **0.2** vs RiskConfig **0.2**; rejections **0** -> consistent **True**

## Cost sensitivity (one-way spread bps)

| spread bps | net total | net Sharpe | mean cost bps |
|---|---|---|---|
| 0 | 0.300416 | 154.5091 | 0.0002 |
| 0.5 | 0.300366 | 154.4828 | 0.0003 |
| 1 | 0.300316 | 154.4564 | 0.0005 |
| 5 | 0.299936 | 154.2499 | 0.0016 |

## Verdict checks
- **GO** — 9/9 checks passed
- [PASS] `measurement_reproducible` observed=True threshold=True
- [PASS] `sample_adequate_declared` observed={'n_returns': 3399, 'n_windows': 82} threshold={'min_returns': 1000, 'min_windows': 20}
- [PASS] `causal_no_lookahead` observed=True threshold=True
- [PASS] `sizing_consistent` observed={'risk_config_max_position_pct': 0.2, 'rejections': 0} threshold={'risk_config_max_position_pct': 0.2, 'swallowed_rejections': 0}
- [PASS] `sharpe_basis_valid` observed={'annualisation': 2102400.0, 'sharpe': 154.4828182076907, 'abs_error': 0.0} threshold={'annualisation': 2102400.0, 'max_abs_error': 1e-09}
- [PASS] `non_degenerate_pillars_reported` observed={'options_leg_degenerate': True, 'orderflow_leg_degenerate': False} threshold=True
- [PASS] `net_of_cost_honest` observed={'complete': True, 'non_negative': True} threshold={'complete': True, 'non_negative': True}
- [PASS] `ic_reported_with_power` observed={'ic_mean': 0.3751261392184914, 'min_detectable_ic_at_n_returns': 0.04805385736967488, 'min_abs_horizon_ic': 0.23552916253509623, 'max_horizon_mde': 0.0481887307112244, 'ic_tstat': 6.544352554413802, 'n_ic_observations': 3, 'n_returns': 3399} threshold={'max_min_detectable_ic_at_n_returns': 0.05, 'detectable_all_horizons': True}
- [PASS] `strict_serialization` observed={'never_valid_true': True} threshold={'allow_nan': False}
