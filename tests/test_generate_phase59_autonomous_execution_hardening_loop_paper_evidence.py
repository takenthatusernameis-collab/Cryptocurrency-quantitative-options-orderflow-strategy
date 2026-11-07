import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.generate_phase59_autonomous_execution_hardening_loop_paper_evidence import (  # noqa: E402
    ARTIFACT_TYPE,
    SYMBOLS,
    UNDERLYINGS,
    VENUES,
    _strip_timestamps,
    generate,
    validate_artifact,
)

SEED = 59061
CYCLES = 20


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
    assert d["hardening_surface"]["paper_only"] is True
    assert d["hardening_surface"]["deterministic_replay_equal"] is True
    assert d["hardening_surface"]["bounds_ok"] is True
    assert d["hardening_surface"]["coverage_pairs"] == len(VENUES) * len(SYMBOLS)
    assert d["risk_posture"]["paper_only"] is True
    assert d["risk_posture"]["next9_unblocked"] is False
    assert d["risk_posture"]["live_trading_enabled"] is False
    json.dumps(d, allow_nan=False)


def test_rejects_live_and_next9_unblock_and_paper_only_false():
    for key, value in (
        ("live_trading_enabled", True),
        ("next9_unblocked", True),
        ("paper_only", False),
        ("advisory", False),
        ("no_external_venue_mutation", False),
    ):
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


def test_venue_symbol_coverage_and_finite_probes():
    d = generate(cycles=CYCLES, seed=SEED)
    pairs = {(x["venue"], x["symbol"]) for x in d["venue_symbol_coverage"]}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    assert pairs == expected
    assert all(x["paper_only"] is True for x in d["venue_symbol_coverage"])
    assert all(x.get("deterministic_probe_hardening_id") for x in d["venue_symbol_coverage"])
    assert all(bool(x.get("probe_finite")) for x in d["venue_symbol_coverage"])
    assert all(bool(x.get("probe_gates_ok")) for x in d["venue_symbol_coverage"])
    assert all(bool(x.get("probe_posttrade_pass_rate") >= 0.0) for x in d["venue_symbol_coverage"])
    assert set(d["hardening_surface"]["venues"]) == set(VENUES)
    assert set(d["hardening_surface"]["symbols"]) == set(SYMBOLS)


def test_hardening_surface_and_risk_posture():
    d = generate(cycles=CYCLES, seed=SEED)
    surf = d["hardening_surface"]
    assert int(surf["n_failovers"]) >= 0
    assert int(surf["n_posttrade_validations"]) > 0
    assert 0.0 <= float(surf["posttrade_pass_rate"]) <= 1.0
    assert int(surf["n_containments"]) >= 0
    assert int(surf["n_rollbacks"]) >= 0
    assert int(surf["cb_breaches"]) >= 0
    bounds = d["determinism"]["bounds"]
    assert all(bool(v) for v in bounds.values())
    rp = d["risk_posture"]
    assert rp["kill_switch_slo_posture"] in ("armed_paper", "observed_paper", "paper_guarded")
    assert rp["all_coverage_gates_ok"] is True
    assert rp["all_composed_phase_ok"] is True


def test_cli_no_write_mode():
    res = subprocess.run(
        [
            sys.executable,
            "scripts/generate_phase59_autonomous_execution_hardening_loop_paper_evidence.py",
            "--cycles",
            str(CYCLES),
            "--seed",
            str(SEED),
            "--no-write",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["valid"] is True
    assert payload["paper_only"] is True
    assert payload["live_trading_enabled"] is False
    assert payload["next9_unblocked"] is False
    assert payload["deterministic"] is True


def test_cross_refs_reference_phase59_hardening_and_previous_phases():
    d = generate(cycles=CYCLES, seed=SEED)
    joined = " ".join(d["evidence_refs"] + d["cross_refs"])
    assert "phase59_autonomous_execution_hardening_loop.py" in joined
    assert "Phase59AutonomousExecutionHardeningLoop" in joined
    assert "PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION_PAPER_EVIDENCE" in joined
    assert "PHASE58_ADAPTIVE_OPTIONS_SMART_ORDER_ROUTER_PAPER_EVIDENCE" in joined
    assert "PHASE59_FRAGMENTATION_TOXICITY_ARB_PAPER_EVIDENCE" in joined
    assert "PHASE58_FLOW_TOXICITY_MITIGATOR_PAPER_EVIDENCE" in joined
    assert "PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE" in joined
    assert "PAPER_OPS_SESSION_GATE" in joined
