# EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY_COMBINED — causal near-ATM implied vol -> forward return tail asymmetry predictiveness (Spearman rank IC) falsification

- Generated: `2026-11-18T00:54:36Z`
- Task: `EVAL87-SURFACE-ATM-IV-FORWARD-RETURN-TAIL-ASYMMETRY`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between causal near-ATM implied vol and forward return tail asymmetry on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | n option trades | n near-ATM | n perp candles | span (s) | ok |
|---|---|---|---|---|---|

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.2170 | atm_iv::bar60.0::h72 | 1 | True |
| ETH | 6 | 0.3116 | atm_iv::bar300.0::h72 | 1 | True |

## Pooled

- BH-FDR rejected: ['BTC::atm_iv::bar60.0::h72', 'ETH::atm_iv::bar300.0::h72']
- All underlyings pass: True
- Campaign state: EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY
