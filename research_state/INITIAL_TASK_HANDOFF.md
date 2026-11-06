# POINTER — SINGLE DURABLE HANDOFF (AUTHORITATIVE)
**Timestamp (UTC): 2026-11-06T00:58:30Z**

The **only** source of truth for the next agent session is:
- `research_state/durable_handoff.md` (same directory)

Gate: **GREEN** (phase-scoped, re-verified 2026-11-06T00:58:30Z; v82–v95 = 14 ok, `PHASE_QUICK_VERIFY=1`). No blocked sessions. No bottlenecks. `research_state/` writable. v95 shipped+green/finite. **v96 ABSENT — MANDATORY: ship `PHASE_110..._V96` next with real src+tests+deterministic artifacts.** Read `durable_handoff.md` for the full task message.
