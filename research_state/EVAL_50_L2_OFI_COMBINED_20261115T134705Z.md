# EVAL_50_L2_OFI_COMBINED — Real L2 order-book OFI net-of-cost falsification

- Generated: `2026-11-15T13:47:05Z`
- Task: `EVAL-50-L2-OFI-NET-OF-COST`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (total snapshots 887, max span 999.6s; per-instrument floor 400 snaps / 900s)
- Instruments: BTC-USD-SWAP, ETH-USD-SWAP

## Per-instrument (best config)

| instrument | configs | best Sharpe | best config | any pass |
|---|---|---|---|---|
| BTC-USD-SWAP | 4 | -2.6831 | bar10.0::z2.0 | False |
| ETH-USD-SWAP | 4 | -1.0061 | bar10.0::z1.0 | False |

## Per-config (Sharpe / max-DD / perm p / CI / breach / pass)

- BTC-USD-SWAP bar5.0 z1.0: Sharpe -4.2390 / DD 0.0070 / p 0.0020 / CI [-6.538, -2.280] / breach False / pass False
- BTC-USD-SWAP bar5.0 z2.0: Sharpe -4.5226 / DD 0.0047 / p 0.0010 / CI [-6.627, -2.518] / breach False / pass False
- BTC-USD-SWAP bar10.0 z1.0: Sharpe -2.7922 / DD 0.0036 / p 0.0799 / CI [-6.112, 0.565] / breach False / pass False
- BTC-USD-SWAP bar10.0 z2.0: Sharpe -2.6831 / DD 0.0022 / p 0.0989 / CI [-5.643, 0.334] / breach False / pass False
- ETH-USD-SWAP bar5.0 z1.0: Sharpe -4.7874 / DD 0.0106 / p 0.0010 / CI [-7.228, -2.507] / breach False / pass False
- ETH-USD-SWAP bar5.0 z2.0: Sharpe -4.2376 / DD 0.0068 / p 0.0010 / CI [-6.943, -1.710] / breach False / pass False
- ETH-USD-SWAP bar10.0 z1.0: Sharpe -1.0061 / DD 0.0044 / p 0.5235 / CI [-4.518, 2.112] / breach False / pass False
- ETH-USD-SWAP bar10.0 z2.0: Sharpe -1.0906 / DD 0.0029 / p 0.5125 / CI [-4.482, 2.169] / breach False / pass False

## Pooled

- Overall PBO: 0.5000
- BH-FDR rejected: ['BTC-USD-SWAP::bar5.0::z2.0', 'ETH-USD-SWAP::bar5.0::z1.0', 'ETH-USD-SWAP::bar5.0::z2.0', 'BTC-USD-SWAP::bar5.0::z1.0']
- All instruments pass: False
