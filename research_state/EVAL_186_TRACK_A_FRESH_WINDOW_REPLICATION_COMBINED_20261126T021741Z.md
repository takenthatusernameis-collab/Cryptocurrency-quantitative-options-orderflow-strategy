# EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_COMBINED - TRACK A fresh-window replication of the dual traded-form NO-GO

- Generated: `2026-11-26T02:17:41Z`
- Task: `EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True
- Strictly-forward disjointness OK: True
- Missing underlyings: []
- GO families: []
- Both families power adequate: True

## Family replication

| family | verdict | floor | power | max pooled | pass configs |
|---|---|---|---|---|---|
| order_flow | NO-GO CONFIRMED (PASS) | True | True | 2000 | [] |
| surface | NO-GO CONFIRMED (PASS) | True | True | 2000 | [] |

## Forward disjointness

| underlying | ok | reason | capture window | previous overlap s | sealed overlap s |
|---|---|---|---|---|---|
| BTC | True | strictly_forward_disjoint | ['2026-11-22T08:22:56Z', '2026-11-26T01:10:56Z'] | 0.0 | 0.0 |
| ETH | True | strictly_forward_disjoint | ['2026-11-22T08:22:56Z', '2026-11-26T01:10:56Z'] | 0.0 | 0.0 |

## Per-underlying EVAL-64 floor

| underlying | snaps | surf inst | 5m bars | trades | of inst | perp bars | perp span s | common 5m | ok |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 1067 | 222 | 1001 | 8637 | 199 | 1000 | 300000 | 288 | True |
| ETH | 1067 | 221 | 1001 | 6808 | 181 | 1000 | 300000 | 282 | True |
