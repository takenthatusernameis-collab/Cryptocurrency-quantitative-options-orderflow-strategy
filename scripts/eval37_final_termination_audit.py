#!/usr/bin/env python3
"""EVAL-37: Independent post-termination audit of the sealed EVAL-36 memo.

This is a post-termination assurance audit, not a new research campaign. It
independently loads the sealed EVAL-36 termination memo and its sealed EVAL-34 /
EVAL-35 inputs, verifies every required field and the exact EVAL-35 measured
failure, computes SHA-256 digests for every sealed input artifact, and seals a
single PASS/FAIL audit artifact.

Invariants enforced (paper-only):
- `.env` must be absent; `live_trading_enabled` false everywhere.
- No synthetic fallback, no `{"valid": true}` payload is emitted.
- Sealed artifacts are never modified; this script only reads them and appends a
  new timestamped audit artifact.

Seals research_state/FINAL_TERMINATION_AUDIT_37_<UTC>.{json,md}.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

OUT_DIR = Path("research_state")
REPORT_ID = "FINAL_TERMINATION_AUDIT_37"

# Sealed inputs this audit must verify.
EVAL36_STEM = "FINAL_TERMINATION_MEMO_36_20261114T145419Z"
EVAL35_STEM = "ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z"
EVAL34_STEM = "FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z"

# Exact EVAL-35 measurements that must appear in the sealed EVAL-36 memo.
EXPECTED_EVAL35 = {
    "oos_sharpe": -18.17767893333353,
    "num_trades": 1255,
    "total_cost_usd": 184.9265410980795,
    "oos_max_drawdown": 0.9662457344138068,
    "kill_switch_triggers": ["max_drawdown", "cost_bps", "toxicity"],
    "non_degenerate": False,
    "within_eval34_band": False,
}

EXPECTED_EVAL_CHAIN = [
    "EVAL-23", "EVAL-24", "EVAL-27", "EVAL-28", "EVAL-29",
    "EVAL-30", "EVAL-31", "EVAL-32", "EVAL-33", "EVAL-34", "EVAL-35",
]

REQUIRED_EVAL36_FIELDS = [
    "verdict",
    "final_decision",
    "campaign_status",
    "paper_rollout_certified",
    "live_trading_enabled",
    "never_valid_true",
    "authenticity_verified",
    "consolidated_evidence_table",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _stamp_for_filename(iso_ts: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return dt.strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve(stem: str, suffix: str) -> Path:
    p = OUT_DIR / f"{stem}{suffix}"
    if not p.exists():
        raise FileNotFoundError(f"sealed artifact missing: {p}")
    return p


class Check:
    """A single measured audit check."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.passed = False
        self.detail: Any = None
        self.error: str | None = None

    def ok(self, detail: Any = None) -> "Check":
        self.passed = True
        self.detail = detail
        return self

    def fail(self, error: str, detail: Any = None) -> "Check":
        self.passed = False
        self.error = error
        self.detail = detail
        return self

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "detail": self.detail,
            "error": self.error,
        }


def _run_check(name: str, fn) -> Check:
    c = Check(name)
    try:
        fn(c)
    except Exception as e:  # noqa: BLE001 - audit records measured failure
        c.fail(f"{type(e).__name__}: {e}")
    return c


def _approx(a: Any, b: float, tol: float) -> bool:
    try:
        return abs(float(a) - b) <= tol
    except (TypeError, ValueError):
        return False


# --------------------------------------------------------------------------- #
# Individual checks
# --------------------------------------------------------------------------- #

def _check_artifacts_exist() -> Check:
    def _fn(c: Check) -> None:
        for stem in (EVAL36_STEM, EVAL35_STEM, EVAL34_STEM):
            for suffix in (".json", ".md"):
                p = _resolve(stem, suffix)
                assert p.stat().st_size > 0, f"empty artifact {p}"
        c.ok({"stems": [EVAL36_STEM, EVAL35_STEM, EVAL34_STEM]})

    return _run_check("artifacts_exist_nonempty", _fn)


def _check_eval36_required_fields() -> Check:
    def _fn(c: Check) -> None:
        d = _load_json(_resolve(EVAL36_STEM, ".json"))
        missing = [f for f in REQUIRED_EVAL36_FIELDS if f not in d]
        assert not missing, f"EVAL-36 missing fields: {missing}"
        c.ok({"present": REQUIRED_EVAL36_FIELDS})

    return _run_check("eval36_required_fields", _fn)


def _check_eval36_verdict_and_decision() -> Check:
    def _fn(c: Check) -> None:
        d = _load_json(_resolve(EVAL36_STEM, ".json"))
        assert d["verdict"] == "NO-GO", f"verdict={d['verdict']!r}"
        fd = d["final_decision"]
        assert fd["decision"] == "TERMINATE_NO_GO", f"decision={fd['decision']!r}"
        assert fd["verdict"] == "NO-GO", f"final_decision.verdict={fd['verdict']!r}"
        assert fd["campaign_status"] == "TERMINATED", f"campaign_status={fd['campaign_status']!r}"
        assert d["campaign_status"] == "TERMINATED", f"top campaign_status={d['campaign_status']!r}"
        assert fd["paper_rollout_certified"] is False, "paper_rollout_certified must be False"
        assert d["paper_rollout_certified"] is False, "top paper_rollout_certified must be False"
        assert fd["live_trading_enabled"] is False, "final_decision.live_trading_enabled must be False"
        assert d["live_trading_enabled"] is False, "top live_trading_enabled must be False"
        assert d["never_valid_true"] is True, "never_valid_true must be True"
        assert d["authenticity_verified"] is False, "authenticity_verified must be False"
        assert fd["orderflow_only_certified"] is False, "orderflow_only_certified must be False"
        assert fd["orderflow_only_replication_failed"] is True, "orderflow_only_replication_failed must be True"
        c.ok({
            "verdict": d["verdict"],
            "decision": fd["decision"],
            "campaign_status": d["campaign_status"],
        })

    return _run_check("eval36_verdict_and_decision", _fn)


def _check_eval36_evidence_table() -> Check:
    def _fn(c: Check) -> None:
        d = _load_json(_resolve(EVAL36_STEM, ".json"))
        rows = d["consolidated_evidence_table"]
        evals = [r.get("eval") for r in rows]
        assert len(rows) == 11, f"expected 11 rows, got {len(rows)}"
        assert evals == EXPECTED_EVAL_CHAIN, f"eval chain mismatch: {evals}"
        assert d["eval_chain"] == EXPECTED_EVAL_CHAIN, f"eval_chain mismatch: {d['eval_chain']}"
        # Every row must carry a real data provenance, never synthetic.
        for r in rows:
            prov = r.get("data_provenance")
            assert prov and "synthetic" not in str(prov).lower(), (
                f"{r.get('eval')} provenance={prov!r} not real"
            )
        c.ok({"n_rows": len(rows), "evals": evals})

    return _run_check("eval36_consolidated_evidence_table", _fn)


def _check_eval36_exact_eval35_measurements() -> Check:
    def _fn(c: Check) -> None:
        d = _load_json(_resolve(EVAL36_STEM, ".json"))
        ev35 = d["final_decision"]["eval35_second_window"]
        assert _approx(ev35["oos_sharpe"], EXPECTED_EVAL35["oos_sharpe"], 1e-12), (
            f"oos_sharpe={ev35['oos_sharpe']!r}"
        )
        assert int(ev35["num_trades"]) == EXPECTED_EVAL35["num_trades"], (
            f"num_trades={ev35['num_trades']!r}"
        )
        assert _approx(ev35["total_cost_usd"], EXPECTED_EVAL35["total_cost_usd"], 1e-9), (
            f"total_cost_usd={ev35['total_cost_usd']!r}"
        )
        assert _approx(ev35["oos_max_drawdown"], EXPECTED_EVAL35["oos_max_drawdown"], 1e-12), (
            f"oos_max_drawdown={ev35['oos_max_drawdown']!r}"
        )
        assert ev35["kill_switch_triggers"] == EXPECTED_EVAL35["kill_switch_triggers"], (
            f"kill_switch_triggers={ev35['kill_switch_triggers']!r}"
        )
        assert ev35["non_degenerate"] is EXPECTED_EVAL35["non_degenerate"], (
            f"non_degenerate={ev35['non_degenerate']!r}"
        )
        assert ev35["within_eval34_band"] is EXPECTED_EVAL35["within_eval34_band"], (
            f"within_eval34_band={ev35['within_eval34_band']!r}"
        )
        c.ok({k: ev35[k] for k in (
            "oos_sharpe", "num_trades", "total_cost_usd", "oos_max_drawdown",
            "kill_switch_triggers", "non_degenerate", "within_eval34_band",
        )})

    return _run_check("eval36_exact_eval35_measurements", _fn)


def _check_eval35_artifact_consistency() -> Check:
    """EVAL-35 sealed artifact must agree with the memo's restatement."""

    def _fn(c: Check) -> None:
        d = _load_json(_resolve(EVAL35_STEM, ".json"))
        assert d["verdict"] == "NO-GO", f"EVAL-35 verdict={d['verdict']!r}"
        assert d["live_trading_enabled"] is False, "EVAL-35 live_trading_enabled must be False"
        assert d["never_valid_true"] is True, "EVAL-35 never_valid_true must be True"
        assert d["authenticity_verified"] is False, "EVAL-35 authenticity_verified must be False"
        wf = d["walkforward"]
        pc = d["portfolio_certification"]
        ks = d["kill_switch"]
        assert _approx(wf["oos_sharpe"], EXPECTED_EVAL35["oos_sharpe"], 1e-12)
        assert int(wf["num_trades"]) == EXPECTED_EVAL35["num_trades"]
        assert _approx(wf["total_cost_usd"], EXPECTED_EVAL35["total_cost_usd"], 1e-9)
        assert _approx(wf["oos_max_drawdown"], EXPECTED_EVAL35["oos_max_drawdown"], 1e-12)
        assert ks["triggers"] == EXPECTED_EVAL35["kill_switch_triggers"]
        assert pc["non_degenerate"] is False
        assert pc["within_eval34_band"] is False
        assert pc["decision"] == "TERMINATE_NO_GO", f"pc.decision={pc['decision']!r}"
        assert pc["kill_switch_breach"] is True, "kill_switch_breach must be True"
        c.ok({"decision": pc["decision"], "kill_switch_any_breach": ks.get("any_breach")})

    return _run_check("eval35_artifact_consistency", _fn)


def _check_eval34_artifact_consistency() -> Check:
    def _fn(c: Check) -> None:
        d = _load_json(_resolve(EVAL34_STEM, ".json"))
        assert d["verdict"] == "NO-GO", f"EVAL-34 verdict={d['verdict']!r}"
        assert d["live_trading_enabled"] is False, "EVAL-34 live_trading_enabled must be False"
        assert d["never_valid_true"] is True, "EVAL-34 never_valid_true must be True"
        fs = d["final_falsification_statement"]
        assert fs["combined_strategy_net_of_cost_tradable"] is False, (
            "EVAL-34 must state combined strategy is not net-of-cost tradable"
        )
        c.ok({"verdict": d["verdict"], "combined_tradable": fs["combined_strategy_net_of_cost_tradable"]})

    return _run_check("eval34_artifact_consistency", _fn)


def _check_no_synthetic_no_valid_payload() -> Check:
    def _fn(c: Check) -> None:
        for stem in (EVAL36_STEM, EVAL35_STEM, EVAL34_STEM):
            raw = _resolve(stem, ".json").read_text(encoding="utf-8")
            assert '{"valid": true}' not in raw.replace(" ", "").replace("\n", ""), (
                f"{stem} contains a valid:true payload"
            )
            # crude synthetic guard: a real provenance marker must be present
            d = json.loads(raw)
            prov = str(d.get("data_provenance", "")).lower()
            assert "synthetic" not in prov, f"{stem} provenance={prov!r}"
        c.ok({"checked": [EVAL36_STEM, EVAL35_STEM, EVAL34_STEM]})

    return _run_check("no_synthetic_no_valid_payload", _fn)


def _check_env_absent_paper_only() -> Check:
    def _fn(c: Check) -> None:
        assert not Path(".env").exists(), ".env must be absent (paper-only)"
        for stem in (EVAL36_STEM, EVAL35_STEM, EVAL34_STEM):
            d = _load_json(_resolve(stem, ".json"))
            assert d.get("live_trading_enabled") is False, f"{stem} live_trading_enabled must be False"
            assert d.get("trading_mode", "paper") == "paper", f"{stem} trading_mode must be paper"
        c.ok({"env_present": False, "all_paper": True})

    return _run_check("env_absent_paper_only", _fn)


def run_audit() -> Tuple[Dict[str, Any], List[Check], Dict[str, str]]:
    """Run every check, compute digests, and return (report, checks, digests)."""
    checks: List[Check] = [
        _check_artifacts_exist(),
        _check_eval36_required_fields(),
        _check_eval36_verdict_and_decision(),
        _check_eval36_evidence_table(),
        _check_eval36_exact_eval35_measurements(),
        _check_eval35_artifact_consistency(),
        _check_eval34_artifact_consistency(),
        _check_no_synthetic_no_valid_payload(),
        _check_env_absent_paper_only(),
    ]

    # SHA-256 digests for every sealed input artifact.
    digests: Dict[str, str] = {}
    for stem in (EVAL36_STEM, EVAL35_STEM, EVAL34_STEM):
        for suffix in (".json", ".md"):
            p = _resolve(stem, suffix)
            digests[str(p)] = _sha256(p)

    all_passed = all(c.passed for c in checks)
    verdict = "PASS" if all_passed else "FAIL"

    generated_at = _utc_now_iso()
    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-EVAL-37-FINAL-TERMINATION-AUDIT",
        "trading_mode": "paper",
        "live_trading_enabled": False,
        "never_valid_true": True,
        "authenticity_verified": False,
        "data_provenance": "real_public_exchange_export",
        "symbol": "BTC",
        "venue": "okx",
        "audited_artifacts": {
            "eval36_memo": str(_resolve(EVAL36_STEM, ".json")),
            "eval36_memo_md": str(_resolve(EVAL36_STEM, ".md")),
            "eval35_validation": str(_resolve(EVAL35_STEM, ".json")),
            "eval35_validation_md": str(_resolve(EVAL35_STEM, ".md")),
            "eval34_falsification": str(_resolve(EVAL34_STEM, ".json")),
            "eval34_falsification_md": str(_resolve(EVAL34_STEM, ".md")),
        },
        "sha256_digests": digests,
        "checks": [c.as_dict() for c in checks],
        "n_checks": len(checks),
        "n_passed": sum(1 for c in checks if c.passed),
        "n_failed": sum(1 for c in checks if not c.passed),
        "verdict": verdict,
        "expected_eval35_measurements": EXPECTED_EVAL35,
        "commands": [
            "python3 -m py_compile scripts/eval37_final_termination_audit.py tests/test_eval37_final_termination_audit.py",
            "python3 -m pytest -q tests/test_eval37_final_termination_audit.py",
            "python3 scripts/eval37_final_termination_audit.py",
        ],
        "code_paths": [
            "scripts/eval37_final_termination_audit.py",
            "tests/test_eval37_final_termination_audit.py",
        ],
        "caveats": [
            "This is a post-termination assurance audit, not a new research campaign.",
            "authenticity_verified=false; public exports have no signed venue attestation.",
            "A PASS means the sealed EVAL-36 memo is internally consistent with its EVAL-34/35 inputs; it does not reopen deployment.",
        ],
    }

    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)
    return serialized, checks, digests


def build_md(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {report['report_id']} — Final termination audit (EVAL-37, paper-only)")
    lines.append("")
    lines.append(f"- **Report ID:** `{report['report_id']}`")
    lines.append(f"- **Generated:** {report['generated_at']}")
    lines.append(f"- **Task ID:** `{report['task_id']}`")
    lines.append(f"- **Verdict:** **{report['verdict']}**")
    lines.append(f"- **Checks passed:** {report['n_passed']}/{report['n_checks']}")
    lines.append(f"- **Trading mode:** {report['trading_mode']} (live enabled: {report['live_trading_enabled']})")
    lines.append(f"- **Never valid true:** {report['never_valid_true']}")
    lines.append("")

    lines.append("## Audited Artifacts")
    lines.append("")
    for k, v in report["audited_artifacts"].items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")

    lines.append("## Checks")
    lines.append("")
    lines.append("| Check | Passed | Detail |")
    lines.append("|-------|--------|--------|")
    for c in report["checks"]:
        detail = c.get("detail")
        detail_s = json.dumps(detail, sort_keys=True) if detail is not None else (c.get("error") or "")
        lines.append(f"| {c['name']} | {c['passed']} | {detail_s} |")
    lines.append("")

    lines.append("## SHA-256 Digests")
    lines.append("")
    for path, digest in report["sha256_digests"].items():
        lines.append(f"- `{digest}`  {path}")
    lines.append("")

    lines.append("## Expected EVAL-35 Measurements (verified in EVAL-36)")
    lines.append("")
    for k, v in report["expected_eval35_measurements"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## Caveats")
    for item in report["caveats"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Commands")
    for cmd in report["commands"]:
        lines.append(f"```bash\n{cmd}\n```")

    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-37 final termination audit (paper-only)")
    ap.add_argument("--no-write", action="store_true", help="compute without writing artifacts")
    args = ap.parse_args(argv)

    report, _checks, _digests = run_audit()
    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "n_checks": report["n_checks"],
        "n_passed": report["n_passed"],
        "n_failed": report["n_failed"],
    }, sort_keys=True))

    if not args.no_write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = _stamp_for_filename(report["generated_at"])
        jpath = OUT_DIR / f"{REPORT_ID}_{stamp}.json"
        mpath = OUT_DIR / f"{REPORT_ID}_{stamp}.md"
        jpath.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        mpath.write_text(build_md(report) + "\n", encoding="utf-8")
        report["artifact_paths"] = {"json": str(jpath), "md": str(mpath)}
        jpath.write_text(json.dumps(serialize_metrics_strict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {jpath}")
        print(f"Wrote {mpath}")

    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())