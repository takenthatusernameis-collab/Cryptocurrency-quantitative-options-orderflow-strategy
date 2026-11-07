import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.generate_phase39_live_readiness_paper_evidence import (  # noqa: E402
    ARTIFACT_TYPE, VENUES, SYMBOLS, _strip_timestamps, generate, validate_artifact,
)

SEED = 39039
CYCLES = 12


def _tampered(**overrides):
    d = generate(cycles=CYCLES, seed=SEED)
    for k, v in overrides.items():
        d[k] = v
    return d


def test_generate_artifact_guards_and_schema():
    d = generate(cycles=CYCLES, seed=SEED)
    assert d["artifact_type"] == ARTIFACT_TYPE
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["advisory"] is True
    assert d["no_external_venue_mutation"] is True
    assert d["validation"]["valid"] is True
    assert d["validation"]["issues"] == []
    assert d["venues"] == list(VENUES)
    assert d["symbols"] == list(SYMBOLS)
    assert d["underlyings"] == ["BTC", "ETH"]
    assert int(d["cycles"]) > 0
    assert d["risk_summary"]["paper_only"] is True
    assert d["risk_summary"]["gates_ok"] is True
    assert d["risk_summary"]["next9_unblocked"] is False
    assert d["risk_summary"]["live_trading_enabled"] is False
    assert d["risk_summary"]["venues_covered"] == list(VENUES)
    assert d["risk_summary"]["symbols_covered"] == list(SYMBOLS)
    assert d["kill_switch_slo_posture"]["paper_only"] is True
    assert d["validation_surface"]["paper_only"] is True
    assert d["reconciliation_freshness"]["paper_only"] is True
    assert d["margin_settlement_audit"]["paper_only"] is True
    assert d["margin_settlement_audit"]["deterministic"] is True
    # artifact must be JSON-valid with allow_nan=False
    json.dumps(d, allow_nan=False)


def test_rejects_live_and_next9_unblock_and_paper_only_false():
    for key, value in (("live_trading_enabled", True), ("next9_unblocked", True),
                       ("paper_only", False), ("advisory", False),
                       ("no_external_venue_mutation", False)):
        d = _tampered(**{key: value})
        ok, issues = validate_artifact(d)
        assert ok is False, f"expected invalid for {key}={value}: {issues}"
        assert len(issues) > 0


def test_deterministic_seed_reproduces_surfaces():
    a = generate(cycles=CYCLES, seed=SEED)
    b = generate(cycles=CYCLES, seed=SEED)
    assert a["determinism"]["deterministic_seeded"] is True
    assert a["determinism"]["same_seed_cycles_reproduce_surfaces"] is True
    assert json.dumps(_strip_timestamps(a), sort_keys=True) == json.dumps(
        _strip_timestamps(b), sort_keys=True
    )
    c = generate(cycles=CYCLES, seed=99999)
    assert json.dumps(_strip_timestamps(c), sort_keys=True) != json.dumps(
        _strip_timestamps(a), sort_keys=True
    )


def test_venue_symbol_coverage_and_validation_rows():
    d = generate(cycles=CYCLES, seed=SEED)
    ks = d["kill_switch_slo_posture"]
    assert set(ks["venues"]) == set(VENUES)
    assert set(ks["symbols"]) == set(SYMBOLS)
    pairs = {(x["venue"], x["symbol"]) for x in ks["venue_symbol_coverage"]}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    assert pairs == expected
    assert all(x["paper_only"] is True for x in ks["venue_symbol_coverage"])
    rows = d["validation_surface"]["rows"]
    assert len(rows) == CYCLES
    assert all(r["paper_only"] is True for r in rows)
    assert all(r["venue"] in VENUES for r in rows)
    assert all(r["symbol"] in SYMBOLS for r in rows)
    assert d["validation_surface"]["all_rows_passed"] is True


def test_margin_settlement_audit_determinism_and_restore():
    d = generate(cycles=CYCLES, seed=SEED)
    ms = d["margin_settlement_audit"]
    assert ms["paper_only"] is True
    assert ms["deterministic"] is True
    assert ms["all_valid"] is True
    assert ms["all_restored_ok"] is True
    assert ms["no_external_venue_mutation"] is True
    assert len(ms["checkpoints"]) == CYCLES
    assert len(ms["restores"]) == CYCLES


def test_cross_refs_reference_existing_phase39_reports():
    d = generate(cycles=CYCLES, seed=SEED)
    refs = d["evidence_refs"] + d["cross_refs"]
    joined = " ".join(refs)
    assert "phase39_live_readiness_loop.py" in joined
    assert "phase39_prepost_trade_validation.py" in joined
    assert "PHASE39_LIVE_READINESS_LOOP_REPORT.json" in joined
    assert "PHASE39_CAMPAIGN_SUMMARY.json" in joined
    assert "PHASE39_KILL_SWITCH_REPORT.json" in joined


def test_cli_writes_no_write_mode():
    res = subprocess.run(
        [sys.executable, "scripts/generate_phase39_live_readiness_paper_evidence.py",
         "--cycles", str(CYCLES), "--seed", str(SEED), "--no-write"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert res.returncode == 0, f"stdout={res.stdout}\nstderr={res.stderr}"
    payload = json.loads(res.stdout)
    assert payload["valid"] is True
    assert payload["paper_only"] is True
    assert payload["next9_unblocked"] is False
    assert payload["live_trading_enabled"] is False
    assert payload["advisory"] is True
    assert payload["no_external_venue_mutation"] is True
    assert payload["deterministic"] is True
    assert payload["gates_ok"] is True
    assert payload["venues"] == list(VENUES)
    assert payload["symbols"] == list(SYMBOLS)
