#!/usr/bin/env python3
"""EVAL-36: Final termination memo for the options+orderflow campaign (paper-only).

Consolidates the sealed EVAL-23..35 evidence into one final decision. EVAL-34
proved the options leg carries no net-of-cost alpha and provisionally selected
orderflow-only; EVAL-35 then failed to replicate orderflow-only on a second
independent real OKX window and breached the kill switches. The only defensible
decision is TERMINATE_NO_GO.

Seals research_state/FINAL_TERMINATION_MEMO_36_<UTC>.{json,md}.
Never emits {"valid": true}. Never falls back to synthetic data.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval34_final_strategy_falsification import (
    _find_artifact,
    _load_json,
    _num,
    _safe_get,
    build_consolidated_evidence_table as build_eval23_33_table,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

OUT_DIR = Path("research_state")
REPORT_ID = "FINAL_TERMINATION_MEMO_36"
EVAL34_REPORT_ID = "FINAL_STRATEGY_FALSIFICATION_34"
EVAL35_REPORT_ID = "ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35"

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _stamp_for_filename(iso_ts: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return dt.strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _fmt_num(value: Any, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def _fmt_cost(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"${float(value):.2f}"
    except (TypeError, ValueError):
        return str(value)


def _load_sealed(report_id: str) -> tuple[Path, Dict[str, Any]]:
    path = _find_artifact(report_id)
    if path is None:
        raise FileNotFoundError(f"sealed artifact not found for {report_id}")
    return path, _load_json(path)


def load_eval34() -> tuple[Path, Dict[str, Any]]:
    path, data = _load_sealed(EVAL34_REPORT_ID)
    if data.get("verdict") != "NO-GO":
        raise ValueError(f"{EVAL34_REPORT_ID} must be NO-GO")
    if data.get("final_falsification_statement", {}).get("combined_strategy_net_of_cost_tradable") is not False:
        raise ValueError("EVAL-34 must state combined strategy is not net-of-cost tradable")
    return path, data


def load_eval35() -> tuple[Path, Dict[str, Any]]:
    path, data = _load_sealed(EVAL35_REPORT_ID)
    if data.get("verdict") != "NO-GO":
        raise ValueError(f"{EVAL35_REPORT_ID} must be NO-GO")
    pc = _safe_get(data, "portfolio_certification", default={})
    if pc.get("decision") != "TERMINATE_NO_GO":
        raise ValueError("EVAL-35 portfolio certification must be TERMINATE_NO_GO")
    if pc.get("non_degenerate") is not False:
        raise ValueError("EVAL-35 must record non_degenerate=False")
    if pc.get("within_eval34_band") is not False:
        raise ValueError("EVAL-35 must record within_eval34_band=False")
    return path, data


def build_consolidated_evidence_table() -> List[Dict[str, Any]]:
    """Return the full EVAL-23..35 evidence table using sealed artifacts only."""
    rows: List[Dict[str, Any]] = list(build_eval23_33_table())

    p34, d34 = load_eval34()
    fs34 = _safe_get(d34, "final_falsification_statement", default={})
    rows.append({
        "eval": "EVAL-34",
        "report_id": d34.get("report_id", EVAL34_REPORT_ID),
        "artifact": str(p34),
        "generated_at": d34.get("generated_at"),
        "verdict": d34.get("verdict"),
        "verdict_reason": d34.get("verdict_reason"),
        "symbol": d34.get("symbol", "BTC"),
        "venue": d34.get("venue", "okx"),
        "data_provenance": d34.get("data_provenance"),
        "n_bars": 1553.0,
        "n_trades_total": None,
        "combined_ic_mean": None,
        "combined_ic_tstat": None,
        "combined_ic_bootstrap_ci_lo": None,
        "combined_ic_bootstrap_ci_hi": None,
        "options_ic_mean": None,
        "options_leg_degenerate": None,
        "orderflow_ic_mean": None,
        "orderflow_only_sharpe": _num(fs34.get("orderflow_only_held_out_sharpe")),
        "orderflow_only_trades": _num(fs34.get("orderflow_only_held_out_trades")),
        "orderflow_only_cost_usd": _num(fs34.get("orderflow_only_held_out_cost_usd")),
        "combined_sharpe": _num(fs34.get("combined_held_out_sharpe")),
        "combined_trades": _num(fs34.get("combined_held_out_trades")),
        "combined_cost_usd": _num(fs34.get("combined_held_out_cost_usd")),
        "options_only_sharpe": 0.0,
        "options_only_trades": 0.0,
        "options_only_cost_usd": 0.0,
        "flat_sharpe": 0.0,
        "permutation_p_value": _num(_safe_get(d34, "consolidated_evidence_table", default=[])[7].get("permutation_p_value") if len(_safe_get(d34, "consolidated_evidence_table", default=[])) > 7 else None),
        "key_reason": (
            "Final consolidated falsification NO-GO: options+orderflow combined is not net-of-cost "
            "tradable; options leg is a zero-alpha cost center; EVAL-34 provisionally selected "
            "orderflow-only with caveats, pending independent replication."
        ),
    })

    p35, d35 = load_eval35()
    wf = _safe_get(d35, "walkforward", default={})
    pc = _safe_get(d35, "portfolio_certification", default={})
    ks = _safe_get(d35, "kill_switch", default={})
    rows.append({
        "eval": "EVAL-35",
        "report_id": d35.get("report_id", EVAL35_REPORT_ID),
        "artifact": str(p35),
        "generated_at": d35.get("generated_at"),
        "verdict": d35.get("verdict"),
        "verdict_reason": d35.get("verdict_reason"),
        "symbol": d35.get("symbol", "BTC"),
        "venue": d35.get("venue", "okx"),
        "data_provenance": d35.get("data_provenance"),
        "n_bars": _num(_safe_get(d35, "tape", default={}).get("n_bars")),
        "n_trades_total": _num(_safe_get(d35, "tape", default={}).get("n_trades_total")),
        "combined_ic_mean": None,
        "combined_ic_tstat": None,
        "combined_ic_bootstrap_ci_lo": None,
        "combined_ic_bootstrap_ci_hi": None,
        "options_ic_mean": None,
        "options_leg_degenerate": None,
        "orderflow_ic_mean": None,
        "orderflow_only_sharpe": _num(wf.get("oos_sharpe")),
        "orderflow_only_trades": _num(wf.get("num_trades")),
        "orderflow_only_cost_usd": _num(wf.get("total_cost_usd")),
        "combined_sharpe": None,
        "combined_trades": None,
        "combined_cost_usd": None,
        "options_only_sharpe": 0.0,
        "options_only_trades": 0.0,
        "options_only_cost_usd": 0.0,
        "flat_sharpe": 0.0,
        "permutation_p_value": None,
        "key_reason": (
            "Second independent real orderflow window NO-GO: Sharpe -18.1777 vs ~4.8115 band, "
            "1255 trades vs ~129, $184.93 cost vs ~$157.02, max-DD 0.9662; kill-switch breached "
            "[max_drawdown,cost_bps,toxicity]; non_degenerate=False, within_band=False."
        ),
    })
    return rows


def build_final_decision(evidence_table: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build the final termination decision from sealed measured evidence."""
    _, d35 = load_eval35()
    wf = _safe_get(d35, "walkforward", default={})
    pc = _safe_get(d35, "portfolio_certification", default={})
    ks = _safe_get(d35, "kill_switch", default={})

    eval35_sharpe = _num(wf.get("oos_sharpe"))
    eval35_trades = _num(wf.get("num_trades"))
    eval35_cost = _num(wf.get("total_cost_usd"))
    eval35_max_dd = _num(wf.get("oos_max_drawdown"))
    eval35_triggers = list(_safe_get(ks, "triggers", default=[]))

    if (
        pc.get("decision") != "TERMINATE_NO_GO"
        or pc.get("non_degenerate") is not False
        or pc.get("within_eval34_band") is not False
        or pc.get("kill_switch_breach") is not True
    ):
        raise ValueError("EVAL-36 requires a sealed EVAL-35 failed-replication NO-GO with kill-switch breach")

    rationale = (
        "TERMINATE / NO-GO. The options+orderflow campaign is not net-of-cost tradable on the "
        "available real data. EVAL-23..33 proved the options leg has no net-of-cost alpha "
        "(all options-only variants flat; parity is additive only). EVAL-34 provisionally "
        "selected orderflow-only with caveats, but EVAL-35 failed to replicate it on a second "
        "independent real OKX BTC-USD-SWAP window (2026-11-14T08:08:15Z to 14:39:17Z, 57,600 "
        f"trades, 1565 bars): Sharpe {eval35_sharpe:.4f} vs EVAL-34 band ~4.8115, "
        f"{int(eval35_trades)} trades vs ~129, ${eval35_cost:.2f} cost vs ~$157.02, "
        f"max-DD {eval35_max_dd:.4f}, kill-switch triggers {eval35_triggers}. "
        "No paper rollout certification is granted. No live enablement. No further queue."
    )

    return {
        "decision": "TERMINATE_NO_GO",
        "verdict": "NO-GO",
        "rationale": rationale,
        "pre_declared_options": ["TERMINATE_NO_GO"],
        "campaign_status": "TERMINATED",
        "paper_rollout_certified": False,
        "live_trading_enabled": False,
        "options_leg_zero_alpha_confirmed": True,
        "options_leg_terminated": True,
        "orderflow_only_replication_failed": True,
        "orderflow_only_certified": False,
        "eval35_second_window": {
            "tape_path": _safe_get(d35, "tape", default={}).get("tape_path"),
            "n_trades_total": _num(_safe_get(d35, "tape", default={}).get("n_trades_total")),
            "n_bars": _num(_safe_get(d35, "tape", default={}).get("n_bars")),
            "start_timestamp": _safe_get(d35, "tape", default={}).get("start_timestamp"),
            "end_timestamp": _safe_get(d35, "tape", default={}).get("end_timestamp"),
            "oos_sharpe": eval35_sharpe,
            "num_trades": int(eval35_trades),
            "total_cost_usd": eval35_cost,
            "oos_max_drawdown": eval35_max_dd,
            "kill_switch_triggers": eval35_triggers,
            "non_degenerate": False,
            "within_eval34_band": False,
        },
        "eval34_reference": {
            "orderflow_only_sharpe": 4.811462185754629,
            "orderflow_only_trades": 129,
            "orderflow_only_cost_usd": 157.0180100586245,
            "combined_sharpe": 5.019467339381368,
        },
    }


def build_lessons_learned() -> List[str]:
    return [
        "A second independent real window invalidated the EVAL-34 orderflow-only deployment candidate: Sharpe -18.1777 vs +4.8115, 1255 trades vs 129, max-DD 0.9662.",
        "The options leg produced zero net-of-cost alpha across EVAL-23..33; parity calibration is additive only and cannot carry a trading strategy.",
        "Single-window or single-tape results are not sufficient for deployment certification; independent replication must be a hard gate.",
        "The toxicity gate engaged 80.3% of bars and the kill-switch still breached; risk controls cannot rescue a negative-expectancy signal.",
        "No synthetic fallback and no live enablement were used; the negative result is sealed as trustworthy evidence.",
    ]


def build_infrastructure_disposition() -> Dict[str, Any]:
    return {
        "options_leg": "TERMINATED",
        "orderflow_only": "NOT_CERTIFIED",
        "combined_strategy": "TERMINATED",
        "paper_rollout": False,
        "live_trading_enabled": False,
        "env_file_present": Path(".env").exists(),
        "data_retention": "Keep real public exports and sealed artifacts; do not delete evidence.",
        "real_loaders": "Must raise RealDataUnavailable; no synthetic fallback.",
        "next_actions": "NONE — campaign terminated.",
        "never_valid_true": True,
    }


def build_report() -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    evidence_table = build_consolidated_evidence_table()
    decision = build_final_decision(evidence_table)

    report = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-EVAL-36-FINAL-TERMINATION-MEMO",
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "authenticity_verified": False,
        "data_provenance": "real_public_exchange_export",
        "symbol": "BTC",
        "venue": "okx",
        "provenance_caveats": [
            "Public read-only OKX exports; no signed venue attestation.",
            "Inverse BTC-USD-SWAP orderflow tape vs spot option snapshots.",
            "Paper-only; no live trading; .env absent.",
            "authenticity_verified=false.",
        ],
        "eval_chain": [
            "EVAL-23", "EVAL-24", "EVAL-27", "EVAL-28", "EVAL-29",
            "EVAL-30", "EVAL-31", "EVAL-32", "EVAL-33", "EVAL-34", "EVAL-35",
        ],
        "consolidated_evidence_table": evidence_table,
        "final_decision": decision,
        "lessons_learned": build_lessons_learned(),
        "infrastructure_disposition": build_infrastructure_disposition(),
        "caveats": [
            "authenticity_verified=false; public exports have no signed venue attestation.",
            "Available real data covers BTC/OKX only; no claim is made for other venues or assets.",
            "The second independent window is still a single historical period; no forward deployment follows.",
        ],
        "verdict": "NO-GO",
        "verdict_reason": decision["rationale"],
        "commands": [
            "python3 -m py_compile scripts/eval36_final_termination_memo.py tests/test_eval36_final_termination_memo.py",
            "python3 -m pytest -q tests/test_eval36_final_termination_memo.py",
            "python3 scripts/eval36_final_termination_memo.py",
        ],
        "code_paths": [
            "scripts/eval36_final_termination_memo.py",
            "tests/test_eval36_final_termination_memo.py",
            "research_state/FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.json",
            "research_state/ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z.json",
        ],
    }

    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)
    return serialized


def build_md(r: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {r['report_id']} — Final termination memo (EVAL-36, paper-only)")
    lines.append("")
    lines.append(f"- **Report ID:** `{r['report_id']}`")
    lines.append(f"- **Generated:** {r['generated_at']}")
    lines.append(f"- **Task ID:** `{r['task_id']}`")
    lines.append(f"- **Verdict:** **{r['verdict']}**")
    lines.append(f"- **Decision:** **{r['final_decision']['decision']}**")
    lines.append(f"- **Campaign status:** {r['final_decision']['campaign_status']}")
    lines.append(f"- **Provenance:** {r['data_provenance']} (authenticity_verified={r['authenticity_verified']})")
    lines.append(f"- **Trading mode:** {r['trading_mode']} (live enabled: {r['live_trading_enabled']})")
    for c in r["provenance_caveats"]:
        lines.append(f"- Caveat: {c}")
    lines.append("")

    lines.append("## Final Decision")
    lines.append("")
    lines.append(r["final_decision"]["rationale"])
    lines.append("")
    lines.append(f"- Paper rollout certified: {r['final_decision']['paper_rollout_certified']}")
    lines.append(f"- Options leg zero alpha confirmed: {r['final_decision']['options_leg_zero_alpha_confirmed']}")
    lines.append(f"- Orderflow-only replication failed: {r['final_decision']['orderflow_only_replication_failed']}")
    lines.append(f"- Live trading enabled: {r['final_decision']['live_trading_enabled']}")
    lines.append("")

    lines.append("## Consolidated Evidence (EVAL-23 through EVAL-35)")
    lines.append("")
    lines.append("| Eval | Report ID | Verdict | Sharpe | Trades | Cost USD | Key Reason |")
    lines.append("|------|-----------|---------|--------|--------|----------|------------|")
    for row in r["consolidated_evidence_table"]:
        sharpe = row["combined_sharpe"] if row["combined_sharpe"] is not None else row["orderflow_only_sharpe"]
        trades = row["combined_trades"] if row["combined_trades"] is not None else row["orderflow_only_trades"]
        cost = row["combined_cost_usd"] if row["combined_cost_usd"] is not None else row["orderflow_only_cost_usd"]
        lines.append(
            f"| {row['eval']} | {row['report_id']} | {row['verdict']} | "
            f"{_fmt_num(sharpe)} | {_fmt_num(trades, 0)} | {_fmt_cost(cost)} | {row['key_reason']} |"
        )
    lines.append("")

    ev35 = r["final_decision"]["eval35_second_window"]
    lines.append("## EVAL-35 Independent Replication Result")
    lines.append("")
    lines.append(f"- Tape: `{ev35['tape_path']}`")
    lines.append(f"- Trades: {ev35['n_trades_total']}; Bars: {ev35['n_bars']}")
    lines.append(f"- Span: {ev35['start_timestamp']} -> {ev35['end_timestamp']}")
    lines.append(f"- Sharpe: {ev35['oos_sharpe']:.4f} (EVAL-34 band ~4.8115)")
    lines.append(f"- Trades: {ev35['num_trades']} (EVAL-34 band ~129)")
    lines.append(f"- Cost: ${ev35['total_cost_usd']:.2f} (EVAL-34 band ~$157.02)")
    lines.append(f"- Max drawdown: {ev35['oos_max_drawdown']:.4f}")
    lines.append(f"- Kill-switch triggers: {ev35['kill_switch_triggers']}")
    lines.append(f"- Non-degenerate: {ev35['non_degenerate']}; within EVAL-34 band: {ev35['within_eval34_band']}")
    lines.append("")

    lines.append("## Lessons Learned")
    for item in r["lessons_learned"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Infrastructure Disposition")
    for k, v in r["infrastructure_disposition"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## Caveats")
    for item in r["caveats"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Commands")
    for cmd in r["commands"]:
        lines.append(f"```bash\n{cmd}\n```")

    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-36 final termination memo (paper-only)")
    ap.add_argument("--no-write", action="store_true", help="compute without writing artifacts")
    args = ap.parse_args(argv)

    report = build_report()
    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "decision": report["final_decision"]["decision"],
        "campaign_status": report["final_decision"]["campaign_status"],
        "eval35_sharpe": report["final_decision"]["eval35_second_window"]["oos_sharpe"],
        "eval35_trades": report["final_decision"]["eval35_second_window"]["num_trades"],
        "eval35_cost_usd": report["final_decision"]["eval35_second_window"]["total_cost_usd"],
        "artifact_paths": report.get("artifact_paths", {}),
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())