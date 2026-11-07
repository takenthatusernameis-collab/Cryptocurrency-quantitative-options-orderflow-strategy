# Paper Trading Runbook (Operator, Paper-Only)

**Campaign:** `PAPER_RUNBOOK_DRILL_AND_GO_NO_GO` / NEXT7
**Mode:** paper-only. **No live capital.** `LIVE_TRADING_ENABLED` must remain `false`. `TRADING_MODE=paper` / `--mode paper`.

## Guardrails
- Never set `LIVE_TRADING_ENABLED=true`.
- Never use live venue credentials for capital deployment as part of this runbook.
- All evidence is additive, timestamped, under `research_state/`.
- GO/NO-GO recommendation is **GO for continued paper operations / NO-GO for live capital enablement** unless a separate explicitly approved live-enablement campaign is completed.

## Environment (verified)
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
. .venv/bin/activate
PYTHONPATH=. python -c "import pydantic,pytest,pandas,numpy,yaml,scipy,mypy; print('deps ok')"
# expected: deps ok
```

## Required prerequisite gates (must be cited)
| Gate/campaign | Checkpoint/artifact |
|---|---|
| END2END_LIVE_TRADING_READINESS | `research_state/campaign_checkpoints/END2END_LIVE_TRADING_READINESS_latest.json` |
| PAPER_TRADING_PRE_LIVE_READINESS | `research_state/campaign_checkpoints/PAPER_TRADING_PRE_LIVE_READINESS_latest.json` |
| CONTINUOUS_VALIDATION_AND_MONITORING | `research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json` (5/5 strict, 0 failed, recon freshness >=0.99 met with measurements `[1,1,1,1,1]`) |

## CLI commands (paper)
```bash
# Continuous validation (strict, paper-only)
PYTHONPATH=. python scripts/run_continuous_validation.py --iterations 5 --strict --symbols BTC,ETH --seed 42

# Paper trading campaign (strict gates) — run 3+ times / collect 3+ indexed artifacts
PYTHONPATH=. python scripts/run_paper_trading_campaign.py --mode paper --strict-gates

# Integrated campaign (as needed)
PYTHONPATH=. python scripts/run_integrated_campaign.py run --help
```

## Artifact locations
- Campaign checkpoints: `research_state/campaign_checkpoints/*_latest.json` (+ immutable timestamped copies)
- Paper runs: `research_state/PAPER_TRADING_CAMPAIGN_<UTC>.json` (+ `PRE_LIVE_GATE_REPORT_*`, `RECONCILIATION_AUDIT_*`)
- Continuous validation: `research_state/CONTINUOUS_VALIDATION_<UTC>.json`, `OBSERVABILITY_REPORT_*`, `ALERT_AUDIT_*`, `HEALTH_SLO_REPORT_*`, `RESILIENCE_AUDIT_*`
- Incident drills: `research_state/INCIDENT_DRILL_<UTC>.json`
- GO/NO-GO: `research_state/GO_NO_GO_REPORT_<UTC>.json`

## Gate thresholds
- Paper critical gates: **all critical passed, `failed==0`** (18/18 in current campaign shape; verify `summary.all_critical_passed==true`).
- Reconciliation freshness SLO: **`target_gte 0.99` met with measurements** in latest CV evidence (no synthetic pass without measurement).
- Continuous validation strict: **iterations 5/5, 0 failed**, paper-only, `live_trading_enabled=false`.

## Incident response / ack (paper drill)
1. **Detection:** reconciliation position mismatch (critical) auto-halts via `ReconciliationEngine(auto_halt_on_critical=True)`; drawdown/risk triggers `RiskManager` kill-switch when limits breached.
2. **Containment:** trading remains paper-gated; no live orders; `CircuitBreaker`/risk integrator signals reviewed.
3. **Ack:** operator records `acknowledged_by`, UTC timestamp, and action in drill artifact.
4. **Resolution:** controlled paper-only reset/verification; document root cause and confirm gates before next run.
5. **Evidence:** `INCIDENT_DRILL_<UTC>.json` with injected condition, detection, ack, resolution, timestamps.

## No live enablement
This runbook does **not** authorize live trading. Live capital enablement requires a separate, explicitly approved campaign (NEXT8 review-only proposal). `LIVE_TRADING_ENABLED` must remain `false`.
