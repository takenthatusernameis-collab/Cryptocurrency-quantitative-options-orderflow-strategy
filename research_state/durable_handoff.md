# SINGLE DURABLE HANDOFF — INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (SUPERSEDED)

**Timestamp:** 2026-11-09T07:34:46Z
**Repository:** Cryptocurrency-quantitative-options-orderflow-strategy
**Status:** STALE / SUPERSEDED by `HANDOFF_NEXT_AGENT.md` (the single durable handoff). Do not use the Phase 110 campaign below as the active focus.

## ⚠️ ACTIVE MANDATORY FOCUS (single durable handoff governs)

The repository name (`Cryptocurrency-quantitative-options-orderflow-strategy`) priorities Chain B post-attribution seal depth in `src/hedging`. The next agentic work session MUST execute:

**`INIT-20261109T092200Z-PHASE140-POST-ATTRIBUTION-SEAL-DEPTH`**

See `HANDOFF_NEXT_AGENT.md` READ FIRST block for the full timestamped, mandatory, heavy initial task message (Phase140: mirror Phase111–139, compose PHASE139→32, 12 venue×symbol coverage rows, paper-only, full deliverables + verification + artifact + handoff update). Phase140 is **unstarted** (0 `*phase140*` files). **No other work takes priority.**

---

## CONTEXT & PRIORITIZATION

This repository implements a **cryptocurrency quantitative options orderflow strategy** targeting multi-venue (Deribit, OKX, Binance) options trading with:
- Orderflow microstructure analytics (gamma exposure, IV skew, put/call ratio, max pain, liquidity)
- Cross-venue smart order routing (SOR) with delta-neutral execution
- Adaptive toxicity resilience and post-trade attribution/seal orchestration
- Real-time hardening, autonomous recovery, and compliance/governance loops

**Highest-impact phase currently active:** **Phase 110** (v89-v156+ variants) — Live execution real-time hardening with ultra-deep cross-venue SOR, post-trade finality, and autonomy. This phase has the most test coverage (15+ test files) and represents the production-readiness frontier.

---

## BOTTLENECKS REMOVED / UNBLOCKED

1. **Missing durable handoff artifact** — This file now exists, unblocking `test_durable_handoff_exists` and `test_durable_handoff_is_source_of_truth`.
2. **Campaign orchestration CLI** — `scripts/run_campaign.py` exists and is wired to `src/campaign/core.py` with atomic checkpointing.
3. **Test infrastructure** — 3,897 tests collected; only the handoff file was missing. Core pipeline (ingestion → features → signals → backtest) is functional.

---

## NEXT AGENTIC WORK SESSION — INITIAL TASK MESSAGE

**MANDATORY FOCUS:** Execute the **Phase 110 campaign** to production-readiness by completing the following weighted priorities:

### PRIORITY 1 — Harden Phase 110 Live Execution Loop (Weight: 40%)
- Run `scripts/run_campaign.py run --campaign-id phase110_live_execution --checkpoint-dir research_state/campaign_checkpoints --seed 42`
- Validate all Phase 110 test variants (`test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v*.py`) pass deterministically
- Ensure cross-venue SOR fragmentation, gamma inventory hedging, regime-aware MM, margin/collateral, liquidation buffer, stress gates, autonomous failover, compliance, and post-trade hardening all integrate without NaN/Inf propagation

### PRIORITY 2 — Close Adaptive Toxicity Attribution/Seal Gaps (Weight: 30%)
- Execute `scripts/generate_phase110_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` to produce paper evidence
- Verify `test_phase110_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` passes
- Ensure attribution seal orchestrator handles: cross-venue custody/clearing reconciliation, live readiness stress gates, autonomous failover, compliance, and post-trade hardening

### PRIORITY 3 — Eliminate Remaining Test Flakiness / Non-finite Propagation (Weight: 20%)
- Run full suite: `python -m pytest -x --tb=short` — target **zero failures**
- Pay special attention to: `test_nonfinite_result_serialization.py`, `test_artifact_serialization.py`, `test_backtest_stress_adversarial.py`
- All JSON serialization must use `allow_nan=False` strictly (enforced by `serialize_metrics`)

### PRIORITY 4 — Campaign Resume/Checkpoint Integrity (Weight: 10%)
- Verify `test_campaign_resume.py` passes completely (idempotent resume, failed-step rerun, atomic checkpoint integrity, strict serialization)
- Ensure `research_state/campaign_checkpoints/` persists valid checkpoints across interruptions

---

## ACCEPTANCE CRITERIA FOR THIS SESSION

| Check | Command | Must Pass |
|-------|---------|-----------|
| Durable handoff exists | `test -f research_state/durable_handoff.md` | ✅ |
| Phase 110 campaign completes | `python scripts/run_campaign.py run --campaign-id phase110_live_execution --checkpoint-dir research_state/campaign_checkpoints --seed 42` | Exit 0, state=COMPLETED |
| All 3,897 tests pass | `python -m pytest -q` | 0 failed, 0 error |
| No NaN/Inf in artifacts | `grep -r "NaN\|Infinity" research_state/*.json` | No matches |
| Campaign resume idempotent | `python scripts/run_campaign.py resume --campaign-id phase110_live_execution --checkpoint-dir research_state/campaign_checkpoints` | Exit 0, no duplicate work |

---

## ESCALATION / HANDOFF NOTES

- **Do not** create new root-level handoff files (`HANDOFF_NEXT_AGENT.md`). This `durable_handoff.md` is the **single source of truth**.
- If Phase 110 campaign completes, advance to **Phase 111+** (adaptive toxicity resilient post-attribution seal orchestrator variants) per the test matrix.
- If any test fails with `SerializationError` (non-finite values), fix the upstream numerical guard in `src/utils/numerical_guards.py` or the emitting module.
- The GitHub Actions workflow (`.github/workflows/main.yml`) runs the Kilo agent loop on a 5-minute schedule — ensure checkpoints are committed so subsequent runs resume cleanly.

---

**END OF INITIAL TASK MESSAGE** — Next agent must execute the above priorities in order, report completion against acceptance criteria, and update this file with a new timestamped entry upon session close.