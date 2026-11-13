# MEASUREMENT_VALIDITY_EVAL_20 — NO-GO

- Generated: `2026-11-13T12:52:27.463340Z`
- Trading mode: `paper` (live=False)
- never `{"valid": true}`: `True`

## Sample adequacy
- bars: **240** / returns: **239** / walk-forward windows: **3**
- return mean **0.1972 bps/bar**, std **31.2602 bps**, t **0.0975**
- floors: n_returns >= 1000, n_windows >= 20 -> **sample_adequate = False**
- minimum detectable |IC| at n=3: **1.617496** (80% power, 5% two-sided)

## Degenerate pillars
- **options**: unique=1 degenerate=**True** values=[0.3333333333333333]
- **orderflow**: unique=240 degenerate=**False** values=[-0.883906171452577, -0.8056435973230786, -0.745834533455962, -0.7255322891548605, -0.7224813107165926, -0.6986862451710706, -0.6951593176894636, -0.6477113168224979]
- **toxicity**: unique=223 degenerate=**False** values=[0.0014025695931477425, 0.004316155371964529, 0.005754527690713812, 0.012456288128238539, 0.01392909354888944, 0.016494338502678625, 0.0181001095546022, 0.020431455978749822]

## Net-of-cost by pillar (per-bar returns, annualisation from bar duration)

| pillar | n_ret | gross total | net total | gross Sharpe | net Sharpe | cost bps | turnover | rejections |
|---|---|---|---|---|---|---|---|---|
| combined | 239 | -0.033720 | -0.033831 | -130.3944 | -130.8247 | 1.1071 | 0.9833 | 0 |
| options_only | 239 | 0.004714 | 0.004603 | 9.1490 | 8.9341 | 1.1091 | 1.0000 | 0 |
| orderflow_only | 239 | -0.009785 | -0.009896 | -22.3345 | -22.5864 | 1.1091 | 1.0000 | 0 |
| flat | 239 | 0.000000 | 0.000000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 |

- Sharpe basis: per-bar, annualisation **2102400.00** (expected 2102400.00); window-level Sharpe **-1173.0862** over **5** windows.

## Sizing consistency
- requested max_position_pct **0.2** vs RiskConfig **0.2**; rejections **0** -> consistent **True**

## Cost sensitivity (one-way spread bps)

| spread bps | net total | net Sharpe | mean cost bps |
|---|---|---|---|
| 0 | -0.033781 | -130.6307 | 0.0025 |
| 0.5 | -0.033831 | -130.8247 | 0.0046 |
| 1 | -0.033881 | -131.0181 | 0.0067 |
| 5 | -0.034260 | -132.4691 | 0.0226 |

## Verdict checks
- **NO-GO** — 7/8 checks passed
- [PASS] `measurement_reproducible` observed=True threshold=True
- [FAIL] `sample_adequate_declared` observed={'n_returns': 239, 'n_windows': 3} threshold={'min_returns': 1000, 'min_windows': 20}
- [PASS] `sizing_consistent` observed={'risk_config_max_position_pct': 0.2, 'rejections': 0} threshold={'risk_config_max_position_pct': 0.2, 'swallowed_rejections': 0}
- [PASS] `sharpe_basis_valid` observed={'annualisation': 2102400.0, 'sharpe': -130.82465671653728, 'abs_error': 0.0} threshold={'annualisation': 2102400.0, 'max_abs_error': 1e-09}
- [PASS] `non_degenerate_pillars_reported` observed={'options_leg_degenerate': True, 'orderflow_leg_degenerate': False} threshold=True
- [PASS] `net_of_cost_honest` observed={'complete': True, 'non_negative': True} threshold={'complete': True, 'non_negative': True}
- [PASS] `ic_reported_with_power` observed={'keys': ['ic_mean', 'min_detectable_ic_at_n']} threshold={'keys': ['ic_mean', 'min_detectable_ic_at_n']}
- [PASS] `strict_serialization` observed={'never_valid_true': True} threshold={'allow_nan': False}
