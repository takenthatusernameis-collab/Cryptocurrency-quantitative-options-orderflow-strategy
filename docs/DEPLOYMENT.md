# Deployment Guide - Live Trading Readiness

## Overview
This document outlines the deployment procedures for the crypto options + orderflow strategy in paper and live trading modes.

## Pre-Live Checklist
- [ ] All tests pass (>=500 tests, 0 failures)
- [ ] Exchange adapters hardened with auth/rate-limit/retry/reconnect
- [ ] Live/paper trading engine tested
- [ ] Secrets/config properly configured
- [ ] Reconciliation and margin checks validated
- [ ] Risk limits configured and tested
- [ ] Pre-live gates pass
- [ ] Monitoring and alerts configured
- [ ] Rollback procedures tested

## Paper Trading Mode
1. Set `TRADING_MODE=paper` in environment
2. Configure exchange API keys (read-only or paper trading keys)
3. Run pre-live gates: `python scripts/run_paper_trading_campaign.py --mode paper --gates-only`
4. Start paper trading: `python scripts/run_paper_trading_campaign.py --mode paper`
5. Monitor for at least 24-48 hours
6. Validate reconciliation matches

## Live Trading Mode (PRODUCTION)
**WARNING: Only proceed if all pre-live gates pass and you have tested thoroughly in paper mode.**

1. Review and sign off on pre-live checklist
2. Set `TRADING_MODE=live` and `LIVE_TRADING_ENABLED=true`
3. Use production API keys with appropriate permissions
4. Run full pre-live validation: `python scripts/run_paper_trading_campaign.py --mode live --strict-gates`
5. Start with minimal capital (canary)
6. Monitor continuously
7. Have rollback plan ready

## Rollback Procedures
1. **Immediate Halt**: Set kill switch or call halt endpoints
2. **Cancel All Orders**: Use order management to cancel open orders
3. **Flatten Positions**: Close all positions if necessary
4. **Disable Trading**: Set `LIVE_TRADING_ENABLED=false`
5. **Investigate**: Review logs and reconciliation reports
6. **Post-Mortem**: Document issues before resuming

## Health Checks
- Exchange connectivity
- API authentication
- Risk limits status
- Margin/collateral levels
- Position reconciliation
- Order flow health
- System latency

## Monitoring
- Real-time PnL and drawdown
- Greeks exposure
- VaR/ES metrics
- Circuit breaker status
- Kill switch status
- Alert notifications

## Secrets Management
- Never commit secrets to version control
- Use environment variables or secure vault
- Rotate API keys regularly
- Use read-only keys where possible
- Enable IP whitelisting on exchanges

## Emergency Contacts
- Risk team: [configured via alerts]
- DevOps: [configured via alerts]
- Trading desk: [configured via alerts]
