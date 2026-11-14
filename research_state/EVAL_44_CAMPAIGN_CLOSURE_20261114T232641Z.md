# EVAL_44_CAMPAIGN_CLOSURE — 20261114T232641Z

- **Verdict:** `CAMPAIGN_CLOSED`
- **Campaign closed:** `True`
- **Task:** `INIT-2026-11-14T23:14:32Z-EVAL-44-CLOSURE-CERTIFY-AND-SEAL`
- **Generated:** `2026-11-14T23:26:41.119565Z`
- **Re-runs performed:** `False` (recomputed from sealed hashes + pre-declared bars only)
- **Append-only verified:** `True`

## Recomputed termination verdict

- Status: **TERMINATED_NO_GO_CLOSED**
- Basis: recomputed from sealed artifact hashes and pre-declared bars only (no re-running)
- Options pillar: CLOSED (EVAL-41 Track B REPLICATION/NO-GO; EVAL-42 NO-GO CONFIRMED)
- Orderflow pillar: CLOSED (EVAL-41 Track A NO-GO/REPLICATION; EVAL-43 NO-GO CONFIRMED PASS)
- Net-of-cost tradable on available real BTC/OKX data: **False**
- New real data required for any further progress: **True**

## Pre-declared bar checks (sealed inputs)

| name | ok | hash match | verdict ok | observed verdict |
|---|---|---:|---:|---|
| `FINAL_TERMINATION_MEMO_36_20261114T145419Z` | True | True | True | `NO-GO` |
| `FINAL_TERMINATION_AUDIT_37_20261114T152849Z` | True | True | True | `PASS` |
| `ORDERFLOW_ROBUSTNESS_41_20261114T193836Z` | True | True | True | `NO-GO / REPLICATION` |
| `EVAL_41_TIMESERIES_NET_OF_COST_20261114T203006Z` | True | True | True | `REPLICATION/NO-GO` |
| `EVAL_42_OPTIONS_TIMESERIES_INDEPENDENT_AUDIT_20261114T221418Z` | True | True | True | `NO-GO CONFIRMED` |
| `EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z` | True | True | True | `NO-GO CONFIRMED (PASS)` |

## Artifact ledger (EVAL_* / FINAL_TERMINATION_*)

Total artifacts: **20**

| path | sha256 | stamp | bytes |
|---|---|---|---:|
| `research_state/EVAL_32_OOS_VALIDATION_20261114T124437Z.json` | `95feb93cde8067cd7d88c59203dc25df387e2724c9a9582c6f1685965a6089f1` | `20261114T124437Z` | 7694 |
| `research_state/EVAL_32_OOS_VALIDATION_20261114T124437Z.md` | `788dfbca045a4230817487ecc7edf1d51b833181b241fdc39d99a0aba16c5243` | `20261114T124437Z` | 3938 |
| `research_state/EVAL_40_MEASUREMENT_20261114T173912Z.json` | `400b6be1bcfb662066413f712edbe0f7ab9b212ff68056717f1ec6d8a3018039` | `20261114T173912Z` | 4869 |
| `research_state/EVAL_40_MEASUREMENT_20261114T173912Z.md` | `9d4f710eab59a0a6b0a9d90187fb92910c2c5157da8d8286284e02d622be0e23` | `20261114T173912Z` | 3166 |
| `research_state/EVAL_40_PREREGISTRATION_20261114T172130Z.json` | `eb326306fd772fc2025d41f3aa20c8a813247649fdaf1978a4195b139133b7e7` | `20261114T172130Z` | 3292 |
| `research_state/EVAL_40_PREREGISTRATION_20261114T172130Z.md` | `0bbca2cb4aebcbf7eeeef360815b67d5d571b5c1827fb9acf8a9999f815cb199` | `20261114T172130Z` | 2659 |
| `research_state/EVAL_41_TIMESERIES_NET_OF_COST_20261114T202641Z.json` | `6af7af0a17a88ee8402f7e6848548274c13df9314f72ef24c1c00c32461fbc4a` | `20261114T202641Z` | 60204 |
| `research_state/EVAL_41_TIMESERIES_NET_OF_COST_20261114T202641Z.md` | `188fcc6b847cc1aa745ec787da64c4e20586ae363c101d03df1998ca8c885ae0` | `20261114T202641Z` | 6537 |
| `research_state/EVAL_41_TIMESERIES_NET_OF_COST_20261114T203006Z.json` | `f8446f9088e69feb111a65ef7ac60fbe19e007822d2ccd4c74be9e72d00b5db4` | `20261114T203006Z` | 79062 |
| `research_state/EVAL_41_TIMESERIES_NET_OF_COST_20261114T203006Z.md` | `71485b184733dc1db0ca9651a1e2e87012d35f9e5b365597848c8ce18573cd36` | `20261114T203006Z` | 6568 |
| `research_state/EVAL_42_OPTIONS_TIMESERIES_INDEPENDENT_AUDIT_20261114T221418Z.json` | `fc913898398a7e208f6f8f70a75ad584929bc1e59698cc8170ed6ac305857157` | `20261114T221418Z` | 70211 |
| `research_state/EVAL_42_OPTIONS_TIMESERIES_INDEPENDENT_AUDIT_20261114T221418Z.md` | `f8099911a7fb3c45a72514cf44951284e116c7b328db36ef42df8b0fa7305fb6` | `20261114T221418Z` | 7963 |
| `research_state/EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z.json` | `a9eea6dc4ab5e82d4cb9b1d8abf7fcb567eb8f2c84528c38cde213fc244c4194` | `20261114T224516Z` | 22656 |
| `research_state/EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z.md` | `3f040782a307ac99b24436aaa06ce867da824a2e9922043f0a1998eb1c23dd18` | `20261114T224516Z` | 3094 |
| `research_state/FINAL_TERMINATION_AUDIT_37_20261114T151805Z.json` | `afab3760f113b8e2885cc023a69d4f05e58f142d8e614d2d3715bfe2424352d6` | `20261114T151805Z` | 5723 |
| `research_state/FINAL_TERMINATION_AUDIT_37_20261114T151805Z.md` | `ae37cdf994f8890b12086a59fa83c53cc94017b1806de365b6ad2cd2db29585c` | `20261114T151805Z` | 4141 |
| `research_state/FINAL_TERMINATION_AUDIT_37_20261114T152849Z.json` | `74a1869d62ea5f706e1ded359b0c1d6d1527bd9a455826a09e84011b83a2819c` | `20261114T152849Z` | 6181 |
| `research_state/FINAL_TERMINATION_AUDIT_37_20261114T152849Z.md` | `ca5cd7857ea6fd4eeb59abb98802cbdd07407ddebcac34d67c90e5a39220d754` | `20261114T152849Z` | 4409 |
| `research_state/FINAL_TERMINATION_MEMO_36_20261114T145419Z.json` | `e05da3950a32bc4344acdaeac7382dc298748a9ca8262ad6c39fa06e17af8d58` | `20261114T145419Z` | 21456 |
| `research_state/FINAL_TERMINATION_MEMO_36_20261114T145419Z.md` | `6ae23e9b5387837767a4ec54641281fac61af02bbd5e1b860780d51dc7ff396c` | `20261114T145419Z` | 6458 |

## Invariants

- paper_only: `True`
- live_trading_enabled: `False`
- env_absent: `True`
- re_runs_performed: `False`
- synthetic_fallback: `False`
- phaseNN_wrappers: `False`

## Commands

- `./scripts/verify_env.sh --check`
- `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`
- `python3 -m py_compile scripts/eval44_campaign_closure_certify.py`
- `python3 scripts/eval44_campaign_closure_certify.py`
- `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-14T23:14:32Z-EVAL-44-CLOSURE-CERTIFY-AND-SEAL" --glob "EVAL_44_*"`

## Closure

Campaign is closed pending new real data. No further artifacts unless new real data arrives.
The cryptocurrency quantitative options+orderflow strategy is definitively not net-of-cost tradable on the available real BTC/OKX data.
