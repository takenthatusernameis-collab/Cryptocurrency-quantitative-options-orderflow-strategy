# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T13:18:17Z, verified):**
> **Repo priority (per name `Cryptocurrency-quantitative-options-orderflow-strategy`):** options + orderflow alpha, net-of-cost on real data. **On-charter ladder EVAL-02..66 is CLOSED** — EVAL-66 sealed `BLOCKED` (gate exit 0; ETH capture under-floor & not disjoint from EVAL-65); namesake options order-flow → realized-vol hypothesis not supported on real BTC/ETH in tested windows. Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/EVAL-64..66 artifacts or `src/`. Do not invent synthetic data or weaken floors.
>
> **NEXT FOCUS CAMPAIGN — EVAL-67 (MANDATORY heavy real-data falsification, off-charter but core-thesis-aligned): BTC options order-flow (toxicity/imbalance) → realized-vol OOS replication on a fresh, disjoint, floor-compliant real BTC capture.** Future agents must not avoid heavy work: execute this end-to-end; end only with a sealed COMBINED/BLOCKED/NO-GO artifact **+ seal gate exit 0**, or a genuinely live **persistent** acquisition with recorded PID/command/liveness. No timestamp-only refreshes, no planning-only stops.
>
> **Task ID:** `INIT-2026-11-16T122919Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION` (use this exact ID for prereg/seal/gate).
>
> **Unskippable heavy-work contract (execute in order):**
> 1. **Env/safety (must pass):** `.env` absent; `LIVE_TRADING_ENABLED` unset/false; paper-only. `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `./scripts/verify_env.sh --check`. Run targeted tests: `python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py` (EVAL-66 harness baseline, expect 9/9) and `python3 -m pytest -q tests/test_eval65_oflow_tox_rv_predictiveness.py` if present. Do **not** run full suite / do **not** enumerate `research_state/`.
> 2. **Pre-register before capture (append-only):** write `research_state/EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_<TS>.{json,md}` fixing hypothesis (replicate suggestive ETH 1m/72-bar `tox::bar60.0::h72`, `imbalance::bar60.0::h72` on **real BTC**, disjoint from sealed BTC windows), instrument=BTC, acquisition source/params, EVAL-64 floor (no weakening), disjointness rule vs sealed EVAL-64/65/66 BTC windows, metrics/gates, and `verdict ∈ {NO-GO CONFIRMED (PASS), BLOCKED}` (under-floor or non-disjoint non-empty real ⇒ `BLOCKED`).
> 3. **Heavy real capture (mandatory):** start **persistent** 7d BTC acquisition (survives session boundary) — `mkdir -p data/raw/eval67`; run with venv deps: `PYTHONUNBUFFERED=1 PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py --underlying BTC --days 7 --out-dir data/raw/eval67 --seal` as a **persistent** background process. Record PID/process id + command in this handoff before ending session if still running. Real loaders only (`RealDataUnavailable` on missing); **never synthetic, never relabel, never `{"valid": true}`**. If a capture exists, verify it is real and **disjoint** from sealed BTC windows and meets EVAL-64 floor before proceeding.
> 4. **Evaluate:** implement/reuse a tested BTC-targeted runner (copy-and-retarget `scripts/eval66_eth_oflow_tox_rv_oos.py`/tests to EVAL-67 BTC if needed, keeping floors/invariants) **or** run an equivalent pre-registered evaluation over `data/raw/eval67/` producing per-slice stats for the two pre-registered slices + BH-FDR/PBO as pre-registered. **Dry-run first** (no write/seal on bad state) → then `--seal` to emit `EVAL_67_BTC_OFLOW_TOX_RV_OOS_{COMBINED|BLOCKED}_<TS>.{json,md}`. Under-floor or non-disjoint non-empty real ⇒ `BLOCKED` (do not weaken floor).
> 5. **Seal gate (must be exit 0):** `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T122919Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"` → **exit 0**.
> 6. **Close session:** update this handoff with verified facts (artifact names, verdict, gate exit code, capture sha256/size/window/disjointness, PIDs if any). `data/raw/eval67/` is gitignored real data — do not commit. Paper-only preserved.
>
> **Completion contract:** session ends only with (a) sealed EVAL-67 artifact + gate exit 0, OR (b) a genuinely live **persistent** acquisition with recorded PID/command/liveness check noted here. No other stopping point is acceptable.

## STATUS (verified 2026-11-16T12:38:24Z)

- **On-charter campaign:** `CAMPAIGN_CLOSED`. EVAL-66 sealed `BLOCKED` (gate exit 0, rechecked this session) — `research_state/EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,BLOCKED}_20261116T121851Z.{json,md}` (task `INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`). ETH capture `data/raw/eval66/three_way_ETH_20261116T111833Z.json` (93,667,786 B, sha256 `d9873…d37e1`, 2026-11-09T11:18:33Z..2026-11-16T11:18:33Z) overlapped EVAL-65 and failed EVAL-64 floor ⇒ BLOCKED.
- **Bottlenecks:** **None blocking (rechecked).** No eval/acquisition processes running; `.env` absent; `LIVE_TRADING_ENABLED` unset; `data/raw/eval66/` present (gitignored); `data/raw/eval67/` not yet created. `.venv-deps` bootstrapped; existing EVAL-66/60 acquisition + harness tooling reusable. Secondary root handoff files are retired pointers (no task IDs); single durable handoff is authoritative. No bottlenecks removed this session.
- **Sealed (immutable):** EVAL-02..62, EVAL-64..66 sealed; **EVAL-63 never sealed**. EVAL-46..60,62,64,65 `NO-GO CONFIRMED (PASS)`; EVAL-61 `NO-GO` (artifact, superseded by 62); EVAL-66 `BLOCKED`.
- **Next required action:** execute **EVAL-67** per the heavy-work contract above (start with pre-reg + persistent 7d BTC acquisition). No other stopping point acceptable.

## AUTHORITATIVE NEXT TASK

**EVAL-67 — BTC options order-flow (tox/imbalance) → realized-vol OOS replication** (`INIT-2026-11-16T122919Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`). Heavy, pre-registered, real-data-only, floor-compliant, disjoint. Follow the 6-step contract in the initial task message. Do not stop at planning or timestamp bumps.

## REPRO / KEY COMMANDS

```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check
python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py

# immutable sealed checks
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"

# EVAL-67 seal gate (after prereg + sealed result exist)
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T122919Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"
```

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62 or EVAL-64..66 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real data; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor or non-disjoint non-empty real capture ⇒ `BLOCKED`, not `NO-GO`.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`, and existing `scripts/eval60_*`/`eval66_*` patterns; no `phaseNN_*` wrappers.
- `data/raw/eval66/`, `data/raw/eval67/` real captures are gitignored — do not commit/push.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only.

## SESSION LOG (append-only, recent)

- 2026-11-16T12:19:00Z: Sealed **EVAL-66 `BLOCKED`** (under-floor, non-disjoint ETH capture; gate exit 0). `CAMPAIGN_CLOSED`.
- 2026-11-16T12:23:50Z / 12:25:20Z / 12:26:20Z / 12:27:06Z: verification/timestamp refresh sessions; no sealed artifacts modified.
- **2026-11-16T12:29:19Z (this session):** Re-verified state (EVAL-66 BLOCKED gate exit 0, campaign closed, no running acquisition, `.env` absent, no bottlenecks). Refreshed this single durable handoff with a timestamped initial task and built **EVAL-67** as the mandatory next focus campaign: heavy 7d real BTC options+orderflow acquisition, pre-registered, disjoint/floor-compliant, dry-run→seal→gate-exit-0, no timestamp-only stops. No sealed artifacts modified; no synthetic data; paper-only.
- **2026-11-16T12:33:59Z (this session):** Re-verified state (EVAL-66 BLOCKED gate exit 0, campaign closed, no running acquisition, `.venv-deps` bootstrapped, `.env` absent, `LIVE_TRADING_ENABLED` unset, no bottlenecks). Refreshed the timestamped initial task message in this single durable handoff and confirmed **EVAL-67** remains the mandatory next focus campaign: heavy 7d real BTC options+orderflow acquisition, pre-registered, disjoint/floor-compliant, dry-run→seal→gate-exit-0, no timestamp-only stops. No sealed artifacts modified; no synthetic data; paper-only.
- **2026-11-16T12:35:17Z:** Re-verified repo state and handoff integrity: `research_state/durable_handoff.md` is the sole actionable handoff; other `*HANDOFF*` root files are retired pointers with no task IDs. Confirmed campaign closed, no running eval acquisition (`pgrep` negative), `.env` absent, `LIVE_TRADING_ENABLED` unset, `data/raw/eval67/` absent, `data/raw/eval66/` present (gitignored). No bottlenecks removed (none present). Preserved **EVAL-67** as the mandatory heavy real-data falsification campaign.
- **2026-11-16T12:36:59Z:** Re-verified (EVAL-66 seal gate exit 0, no running eval/acquisition procs, `.env` absent, `data/raw/eval67/` absent, `data/raw/eval66/` present, retired handoff pointers intact). No bottlenecks to remove. Refreshed initial task timestamp; **EVAL-67** (`INIT-2026-11-16T122919Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`) remained mandatory per contract.
- **2026-11-16T12:38:24Z (this session):** Re-verified EVAL-66 seal gate exit 0, no running eval/acquisition processes, `.env` absent, `LIVE_TRADING_ENABLED` unset, `data/raw/eval67/` absent, `data/raw/eval66/` present (gitignored), retired root handoffs are pointers. No bottlenecks found/removed. Refreshed the single durable handoff with this timestamped initial task message; **EVAL-67** remains the mandatory, unskippable heavy real-data falsification campaign — next session must execute pre-reg → persistent 7d BTC capture (`data/raw/eval67/`) → disjoint/floor-compliant eval → sealed artifact + seal gate exit 0, or leave a recorded live persistent acquisition (PID/command/liveness). No sealed artifacts or `src/` modified; no synthetic data; paper-only.
- **2026-11-16T13:18:17Z (this session):** Verified repo state and handoff integrity: `research_state/durable_handoff.md` is the sole actionable handoff; other `*HANDOFF*` root files are retired pointers with no task IDs. Confirmed campaign closed, no running eval acquisition (`pgrep` negative), `.env` absent, `LIVE_TRADING_ENABLED` unset, `data/raw/eval67/` absent, `data/raw/eval66/` present (gitignored). No bottlenecks to remove (none present). Refreshed initial task timestamp; **EVAL-67** (`INIT-2026-11-16T122919Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`) remains mandatory per heavy-work contract. Ready for next agentic session to execute pre-reg + persistent 7d BTC capture.

## SEALED STATE (immutable; append only)

EVAL-02..62,64..66 sealed. EVAL-63 never sealed. EVAL-46..60,62,64,65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`. On-charter campaign closed; EVAL-67 is the next authorized heavy falsification campaign.

(End of file)
