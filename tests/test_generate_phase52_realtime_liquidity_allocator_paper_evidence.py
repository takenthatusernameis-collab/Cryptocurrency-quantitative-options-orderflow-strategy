import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.generate_phase52_realtime_liquidity_allocator_paper_evidence import (  # noqa: E402
    ARTIFACT_TYPE, VENUES, SYMBOLS, UNDERLYINGS, _strip_timestamps, generate, validate_artifact,
)

SEED = 52052
CYCLES = 60


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
    assert d["underlyings"] == list(UNDERLYINGS)
    assert int(d["cycles"]) > 0
    assert d["campaign"]["paper_only"] is True
    assert d["campaign"]["gates_ok"] is True
    assert d["allocation_surface"]["paper_only"] is True
    assert d["allocation_surface"]["gates_ok"] is True
    assert d["slicing_tca_summary"]["paper_only"] is True
    assert d["slicing_tca_summary"]["slice_alloc_linked"] is True
    assert d["risk_posture"]["paper_only"] is True
    assert d["risk_posture"]["next9_unblocked"] is False
    assert d["risk_posture"]["live_trading_enabled"] is False
    assert isinstance(d.get("p1_blocker"), str) and "phase50" in d["p1_blocker"].lower()
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
    assert a["determinism"]["bounds_ok"] is True
    assert json.dumps(_strip_timestamps(a), sort_keys=True) == json.dumps(
        _strip_timestamps(b), sort_keys=True
    )
    c = generate(cycles=CYCLES, seed=999)
    assert json.dumps(_strip_timestamps(c), sort_keys=True) != json.dumps(
        _strip_timestamps(a), sort_keys=True
    )


def test_venue_symbol_coverage_and_determinism_rows():
    d = generate(cycles=CYCLES, seed=SEED)
    pairs = {(x["venue"], x["symbol"]) for x in d["venue_symbol_coverage"]}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    assert pairs == expected
    assert all(x["paper_only"] is True for x in d["venue_symbol_coverage"])
    assert all(x.get("deterministic_probe_alloc_id") for x in d["venue_symbol_coverage"])
    assert all(bool(x.get("probe_alloc_finite")) for x in d["venue_symbol_coverage"])
    assert all(int(x.get("campaign_n_allocations", -1)) >= 0 for x in d["venue_symbol_coverage"])
    assert set(d["allocation_surface"]["venues"]) == set(VENUES)
    assert set(d["allocation_surface"]["underlyings"]) == set(UNDERLYINGS)


def test_slicing_tca_bounds_and_linkage():
    d = generate(cycles=CYCLES, seed=SEED)
    tca = d["slicing_tca_summary"]
    assert int(tca["n_slices"]) > 0
    assert int(tca["n_tca"]) == int(d["campaign"]["cycles"])
    assert float(tca["avg_est_slippage_bps"]) >= 0.0
    assert float(tca["avg_slice_usd"]) >= 0.0
    assert tca["slice_alloc_linked"] is True
    bounds = d["determinism"]["bounds"]
    assert all(bool(v) for v in bounds.values())


def test_cross_refs_reference_phase52_and_phase50_context():
    d = generate(cycles=CYCLES, seed=SEED)
    joined = " ".join(d["evidence_refs"] + d["cross_refs"])
    assert "phase52_realtime_liquidity_allocator.py" in joined
    assert "phase50_toxicity_aware_options_mm.py" in joined
    assert "PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE" in joined


def test_cli_no_write_mode():
    res = subprocess.run(
        [sys.executable, "scripts/generate_phase52_realtime_liquidity_allocator_paper_evidence.py",
         "--cycles", str(CYCLES), "--seed", str(SEED), "--no-write"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["valid"] is True
    assert payload["paper_only"] is True
    assert payload["next9_unblocked"] is False
    assert payload["deterministic"] is True
    assert payload["gates_ok"] is True
    assert payload["venues"] == list(VENUES)
    assert payload["symbols"] == list(SYMBOLS)
    assert payload["p1_blocker_documented"] is True
