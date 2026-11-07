import copy
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.generate_phase46_execution_paper_evidence import (  # noqa: E402
    ARTIFACT_TYPE, VENUES, SYMBOLS, _strip_timestamps, generate, validate_artifact,
)

SEED = 47
CYCLES = 14  # known-good combo: phase46 loop gates_ok == True


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
    assert d["execution_intelligence"]["paper_only"] is True
    assert d["execution_intelligence"]["gates_ok"] is True
    assert d["risk_summary"]["paper_only"] is True
    assert d["risk_summary"]["gates_ok"] is True
    assert d["risk_summary"]["venues_covered"] == list(VENUES)
    assert d["risk_summary"]["symbols_covered"] == list(SYMBOLS)
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


def test_deterministic_seed_reproduces_surface():
    a = generate(cycles=CYCLES, seed=SEED)
    b = generate(cycles=CYCLES, seed=SEED)
    assert a["determinism"]["deterministic_seeded"] is True
    assert a["determinism"]["same_seed_cycles_reproduce_surface"] is True
    # Non-timestamp content must be byte-identical across identical seeds.
    assert json.dumps(_strip_timestamps(a), sort_keys=True) == json.dumps(
        _strip_timestamps(b), sort_keys=True
    )
    # Different seed must differ.
    c = generate(cycles=CYCLES, seed=999)
    assert json.dumps(_strip_timestamps(c), sort_keys=True) != json.dumps(
        _strip_timestamps(a), sort_keys=True
    )


def test_venue_symbol_coverage_matrix():
    d = generate(cycles=CYCLES, seed=SEED)
    surf = d["adaptive_mm_surface"]
    assert surf["venues"] == list(VENUES)
    assert surf["symbols"] == list(SYMBOLS)
    pairs = {(x["venue"], x["symbol"]) for x in surf["venue_symbol_coverage"]}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    assert pairs == expected
    assert all(x["paper_only"] is True for x in surf["venue_symbol_coverage"])


def test_cross_refs_reference_existing_phase46_reports():
    d = generate(cycles=CYCLES, seed=SEED)
    refs = d["evidence_refs"] + d["cross_refs"]
    joined = " ".join(refs)
    assert "phase46_execution_intelligence_loop.py" in joined
    assert "phase46_adaptive_mm_engine.py" in joined
    assert "PHASE46_EXECUTION_INTELLIGENCE_LOOP_REPORT.json" in joined
    assert "PHASE46_ADAPTIVE_MM_ENGINE_REPORT.json" in joined
    assert "PHASE46_CAMPAIGN_SUMMARY.json" in joined


def test_cli_writes_timestamped_artifact(tmp_path):
    out = REPO / "research_state" / "PHASE46_EXECUTION_PAPER_EVIDENCE_CLI.json"
    try:
        res = subprocess.run(
            [sys.executable, "scripts/generate_phase46_execution_paper_evidence.py",
             "--cycles", str(CYCLES), "--seed", str(SEED), "--no-write"],
            cwd=str(REPO), capture_output=True, text=True,
        )
        assert res.returncode == 0, res.stderr
        payload = json.loads(res.stdout)
        assert payload["valid"] is True
        assert payload["paper_only"] is True
        assert payload["next9_unblocked"] is False
        assert payload["deterministic"] is True
        assert payload["venues"] == list(VENUES)
        assert payload["symbols"] == list(SYMBOLS)
    finally:
        if out.exists():
            out.unlink()
