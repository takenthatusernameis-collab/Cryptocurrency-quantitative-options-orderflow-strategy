# Incident triage (paper-only) — 2026-11-06T17:20:16Z

## r_drawdown_pct (alert_6863a5540ff6) — drawdown_pct=0.12 > 0.1 (warning)
- Source: CONTINUOUS_VALIDATION_20261101T004750Z.json
- Decision (paper-only): **ACKNOWLEDGE + EXPECTED for synthetic stress scenarios**. The 12% drawdown appears in synthetic validation runs; it does not represent live capital loss. Do not escalate to live gates.
- Required before live readiness: replay with real/recorded venue data; require max_drawdown < configured live threshold and resolved=true with evidence.

## slo_reconciliation_freshness — current 0.0 vs target 0.99
- Source: HEALTH_SLO_REPORT / continuous validation.
- Root cause (inferred): no reconciliation heartbeat/freshness sample emitted in the validation path; metric defaults to 0.0.
- Required fix: wire reconciliation freshness emission in the end-to-end pipeline/campaign runner and add a regression asserting SLO met when reconciliation ran within window. Until fixed, treat as a **hard gate blocker** for live-trading readiness.
