# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## STATUS (verified 2026-11-16T03:21:05Z)

- **EVAL-02..62 are sealed.** EVAL-61 sealed `NO-GO CONFIRMED (PASS)` but was a **measurement artifact** (un-normalized dollar P&L treated as returns → spurious max-DD=1.0 on all configs); it never honestly tested the namesake hypothesis. EVAL-61 artifacts remain immutable and superseded by EVAL-62.
- **EVAL-62 (correct replacement) is SEALED `NO-GO CONFIRMED (PASS)`** on real data, mark-path P&L (EVAL-57 formula) driven by options order-flow toxicity side/exposure.
  - Task: `INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL`
  - Prereg: `research_state/EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION_20261116T032105Z.{json,md}`
  - Combined: `research_state/EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_20261116T032105Z.{json,md}`
  - Seal gate: `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL" --glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION_*" --require-glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_*"` → **exit 0** (stamp 20261116T032105Z).
  - Capture (reused, real): `data/raw/eval61/three_way_BTC_20261116T005923Z.json`, `data/raw/eval61/three_way_BTC_20261116T011441Z.json`, `data/raw/eval61/three_way_ETH_20261116T022541Z.json`. Floor met (BTC+ETH).
  - Measured: `floor_ok=true`, `overall_pbo=0.375`. Kill-switch breaches GONE (max-DD 0.03–0.12, not 1.0).
    - BTC best: `imbalance::bar300.0` Sharpe **−0.044300** (any_pass=false).
    - ETH best: `imbalance::bar300.0` Sharpe **+0.616252** (any_pass=false; fails GO bar on replication/permutation/bootstrap criteria across both underlyings).
  - **Conclusion:** real options order-flow toxicity → realized-vol signal, traded via signal-timed delta-hedged ATM straddle (mark-path, net-of-cost), is **not net-of-cost tradable** on real BTC or ETH with this capture/floor. Namesake rung honestly closed (NO-GO).
- Env (verified): `./scripts/verify_env.sh --check` OK; `.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED` unset.

## AUTHORITATIVE NEXT TASK (timestamped)

**Campaign state: NO FURTHER UNSEALED MANDATORY RUNG.** EVAL-02..62 sealed; the options+orderflow fusion/smile/standalone and namesake vol-trade ladders are complete on available real BTC/ETH data.

```
INIT-2026-11-16T03:21:05Z-CAMPAIGN-HOLD-NO-UNSEALED-RUNG
```

**Mandatory for any future session that does new research work (heavy, non-optional if opened):**
1. Define exactly ONE new, on-charter, pre-registered hypothesis not already falsified by EVAL-02..62 (must state why it differs from all sealed rungs and how it uses real options+orderflow). Do **not** re-run/re-litigate/re-seal EVAL-02..62.
2. Acquire/point to **heavy real** data meeting an explicit pre-registered floor (reuse `scripts/eval60_acquire_three_way.py` for Deribit+OKX capture patterns if applicable; never synthetic; never weaken floor). Record acquisition/seal artifacts in `research_state/` with a new timestamped task ID.
3. Pre-register (task, hypothesis, exact formula incl. return normalization by spot / mark-path P&L, grid, costs, GO/NO-GO bar, floor, kill-switches) → run measurement → seal `PREREGISTRATION_*` + `COMBINED_*` (or `BLOCKED_*` only on genuine floor failure) with `scripts/check_session_sealed.py` **exit 0**.
4. Update this handoff **in place** with verified facts/paths/commands/numbers and the sealed verdict. Timestamp-only edits without sealing = failed session.

**If no new on-charter hypothesis with acquirable real data is identified:** session must leave this handoff unchanged except to append a dated session-log note stating "no new falsifiable on-charter rung identified beyond EVAL-02..62" with evidence (checked sealed roster + data availability). Do not invent work, do not weaken floors, do not use synthetic.

## REPRO / KEY COMMANDS

```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
# verify env
./scripts/verify_env.sh --check
# (sealed) re-verify EVAL-62 seal
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL" \
  --glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION_*" \
  --require-glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_*"
# inspect combined
python3 -m json.tool research_state/EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_20261116T032105Z.json | head -120
```

## BOTTLENECKS

- **Cleared:** EVAL-62 tooling/tests built (`scripts/eval62_orderflow_realized_vol_markpath.py`, `tests/test_eval62_orderflow_realized_vol_markpath.py`), EVAL-61 P&L artifact corrected (mark-path, spot-normalized), seal complete (gate exit 0).
- **Current:** No unsealed mandatory rung. Any new rung requires a genuinely new on-charter hypothesis + heavy real data + prereg+seal; absence of such a hypothesis/data is a legitimate hold (not a blocker to fabricate).

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal EVAL-02..62; do not edit sealed artifacts or `src/`.
- Never synthetic fallback; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement. Public read-only network only, polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`; no `phaseNN_*` wrappers.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies (root retired pointers stay retired). Update this file in place with verified facts only.
- Any new P&L must be spot-normalized and use mark-path/realized costed returns (regression-guard pattern as in EVAL-62); never reintroduce the EVAL-61 dollar-as-return artifact.

## SEALED STATE (immutable; append only)

EVAL-02..62 sealed. EVAL-46..60 and EVAL-62: **NO-GO CONFIRMED (PASS)**, gate exit 0. EVAL-61: **NO-GO CONFIRMED (PASS)** but measurement-artifact (superseded by EVAL-62). Re-running/re-sealing prohibited.

## SESSION LOG (append-only)

- 2026-11-14→2026-11-15: EVAL-41..59 sealed NO-GO (gate exit 0).
- 2026-11-15T22:44:10Z: EVAL-60 tooling built + smoke.
- 2026-11-16T00:34:26Z: EVAL-60 heavy BTC+ETH sealed NO-GO (gate exit 0).
- 2026-11-16T02:41:37Z: EVAL-61 sealed NO-GO (gate exit 0) — later found to be a P&L artifact.
- 2026-11-16T03:17:05Z: EVAL-62 tooling/tests built; real `--no-write` verified (artifact gone, NO-GO on merits).
- **2026-11-16T03:21:05Z (this session):** Sealed EVAL-62 `NO-GO CONFIRMED (PASS)` (`EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_{PREREGISTRATION,COMBINED}_20261116T032105Z`, floor_ok, overall_pbo 0.375, BTC best −0.0443 / ETH +0.6163, kill-switch breaches gone). Seal gate exit 0. Namesake rung honestly closed; no unsealed mandatory rung — campaign on hold pending a genuinely new on-charter, real-data, pre-registered hypothesis beyond EVAL-02..62.
