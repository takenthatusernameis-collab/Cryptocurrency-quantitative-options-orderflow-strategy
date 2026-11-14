# FINAL_TERMINATION_AUDIT_37 — Final termination audit (EVAL-37, paper-only)

- **Report ID:** `FINAL_TERMINATION_AUDIT_37`
- **Generated:** 2026-11-14T15:28:49.875428Z
- **Task ID:** `INIT-2026-11-14T15:28:49.875428Z-EVAL-37-FINAL-TERMINATION-AUDIT`
- **Verdict:** **PASS**
- **Checks passed:** 9/9
- **Trading mode:** paper (live enabled: False)
- **Never valid true:** True

## Audited Artifacts

- eval36_memo: `research_state/FINAL_TERMINATION_MEMO_36_20261114T145419Z.json`
- eval36_memo_md: `research_state/FINAL_TERMINATION_MEMO_36_20261114T145419Z.md`
- eval35_validation: `research_state/ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z.json`
- eval35_validation_md: `research_state/ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z.md`
- eval34_falsification: `research_state/FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.json`
- eval34_falsification_md: `research_state/FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.md`

## Checks

| Check | Passed | Detail |
|-------|--------|--------|
| artifacts_exist_nonempty | True | {"stems": ["FINAL_TERMINATION_MEMO_36_20261114T145419Z", "ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z", "FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z"]} |
| eval36_required_fields | True | {"final_decision_present": ["campaign_status", "paper_rollout_certified", "live_trading_enabled", "decision", "verdict"], "present": ["verdict", "final_decision", "live_trading_enabled", "never_valid_true", "authenticity_verified", "consolidated_evidence_table"]} |
| eval36_verdict_and_decision | True | {"campaign_status": "TERMINATED", "decision": "TERMINATE_NO_GO", "field_location": "final_decision", "verdict": "NO-GO"} |
| eval36_consolidated_evidence_table | True | {"evals": ["EVAL-23", "EVAL-24", "EVAL-27", "EVAL-28", "EVAL-29", "EVAL-30", "EVAL-31", "EVAL-32", "EVAL-33", "EVAL-34", "EVAL-35"], "n_rows": 11} |
| eval36_exact_eval35_measurements | True | {"kill_switch_triggers": ["max_drawdown", "cost_bps", "toxicity"], "non_degenerate": false, "num_trades": 1255, "oos_max_drawdown": 0.9662457344138068, "oos_sharpe": -18.17767893333353, "total_cost_usd": 184.9265410980795, "within_eval34_band": false} |
| eval35_artifact_consistency | True | {"decision": "TERMINATE_NO_GO", "kill_switch_any_breach": true} |
| eval34_artifact_consistency | True | {"combined_tradable": false, "verdict": "NO-GO"} |
| no_synthetic_no_valid_payload | True | {"checked": ["FINAL_TERMINATION_MEMO_36_20261114T145419Z", "ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z", "FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z"]} |
| env_absent_paper_only | True | {"all_paper": true, "env_present": false} |

## SHA-256 Digests

- `e05da3950a32bc4344acdaeac7382dc298748a9ca8262ad6c39fa06e17af8d58`  research_state/FINAL_TERMINATION_MEMO_36_20261114T145419Z.json
- `6ae23e9b5387837767a4ec54641281fac61af02bbd5e1b860780d51dc7ff396c`  research_state/FINAL_TERMINATION_MEMO_36_20261114T145419Z.md
- `f0d095482c846f54b93a46289cb61a838e6a4f2c017a4f67061a7b7ae17d408f`  research_state/ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z.json
- `a1d8c2ae2682f187d6285c67e87afcdfe339a4da78afe07a91efcca660f0dd61`  research_state/ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z.md
- `75bb0ac7e3ddd3eab07f9c32916cecb14dd9017d7c44ca9301cb282d03bb634a`  research_state/FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.json
- `2f6d4102efa2577145e11e7e82362fdd26161ce657cb58aa8b5bb4b2f05187bc`  research_state/FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.md

## Expected EVAL-35 Measurements (verified in EVAL-36)

- oos_sharpe: -18.17767893333353
- num_trades: 1255
- total_cost_usd: 184.9265410980795
- oos_max_drawdown: 0.9662457344138068
- kill_switch_triggers: ['max_drawdown', 'cost_bps', 'toxicity']
- non_degenerate: False
- within_eval34_band: False

## Caveats
- This is a post-termination assurance audit, not a new research campaign.
- authenticity_verified=false; public exports have no signed venue attestation.
- A PASS means the sealed EVAL-36 memo is internally consistent with its EVAL-34/35 inputs; it does not reopen deployment.

## Commands
```bash
python3 -m py_compile scripts/eval37_final_termination_audit.py tests/test_eval37_final_termination_audit.py
```
```bash
python3 -m pytest -q tests/test_eval37_final_termination_audit.py
```
```bash
python3 scripts/eval37_final_termination_audit.py
```
