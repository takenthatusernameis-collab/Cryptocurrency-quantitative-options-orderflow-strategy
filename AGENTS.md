# AGENTS.md — working agreement for this repository

**On-charter ladder EVAL-02..66 is CLOSED** (EVAL-66 sealed `BLOCKED`, gate exit 0; EVAL-63 was never sealed). Do not re-run, re-litigate, or re-seal sealed EVAL-02..62 or EVAL-64..66 artifacts or `src/`.

**Active heavy campaigns (repo priority: crypto options surface + options order-flow → tradeable, net-of-cost alpha on REAL public data):** EVAL-67/68/69 are SEALED (EVAL-67/68 predictive GO; EVAL-69 traded-form `NO-GO CONFIRMED (PASS)`), EVAL-70..183 are SEALED, and EVAL-184 + EVAL-185 are SEALED (`NO-GO CONFIRMED (PASS)`, `20261122T081750Z` / `20261122T092235Z`): both signal families now fail to monetize net-of-cost. Run the full heavy-work driver every session: `python3 scripts/eval67_prethreshold_progress.py --execute` (env + 2430 targeted + 27 diagnostics tests + all arbiters/seal gates + readiness refresh; require exit 0). Never synthetic data, never weaken the EVAL-64 floor, paper-only.

**The single authoritative handoff is `research_state/durable_handoff.md`.** All predictiveness rungs EVAL-02..183 are sealed (EVAL-63 never sealed), as is the surface traded-form rung EVAL-184. There is no unsealed predictiveness rung and no missing-capture excuse in this checkout: `data/raw/eval84cap` is present, floor-compliant, and disjoint. Do not invent a substitute rung.

**Anti-avoidance:** a green driver plus EVAL-184/EVAL-185 SEALED is NOT completion. EVAL-185 is SEALED (`NO-GO CONFIRMED (PASS)`, `20261122T092235Z`, 0/45 grid configs pass). The current mandated queue is **EVAL-186 — TRACK A fresh-window replication**: run `python3 scripts/eval186_phaseb_gate.py` every session; it reports `WAIT_CAPTURE` (exit 10) until `data/raw/eval185cap` exists, then `WAIT_RUNNER` (exit 20) until `--no-write` is green, then `DUE` (exit 30) — re-run with `--execute` to seal EVAL-186 and pass the seal-gate. Under-floor or non-disjoint data is `BLOCKED`, never `NO-GO`. Do not re-run, re-litigate, or re-seal sealed artifacts EVAL-02..185 or `src/`.

See `research_state/durable_handoff.md` (the single durable handoff) for the authoritative timestamped initial task message and completion contract.
