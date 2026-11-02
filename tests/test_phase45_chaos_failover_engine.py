from src.errors import RiskLimitError
from src.resilience.phase45_chaos_failover_engine import (
    ChaosFaultType,
    ChaosFailoverConfig,
    FailoverState,
    Phase45ChaosFailoverEngine,
    VenueHealth,
)


def test_phase45_engine_constructs_paper_only():
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=7, cycles=12, paper_only=True))
    assert eng.paper_only is True
    assert eng.state == FailoverState.NOMINAL
    assert eng.primary_venue in eng.venues


def test_phase45_engine_live_path_hard_gated():
    try:
        Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=7, cycles=12, paper_only=False))
    except (ValueError, RiskLimitError):
        pass
    else:
        raise AssertionError("live path must be hard-gated")


def test_phase45_run_campaign_gates_ok():
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=11, cycles=20, paper_only=True))
    rep = eng.run_campaign()
    assert rep["phase"] == "PHASE45_CHAOS_FAILOVER_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles_run"] == 20
    assert rep["final_active_venue"] in eng.venues
    assert rep["n_failovers"] >= 0
    assert rep["n_venues"] == 4
    assert isinstance(rep["n_slo_burn_alerts"], int)


def test_phase45_active_faults_scheduled():
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=3, cycles=50, paper_only=True))
    act = eng.active_faults(10)
    assert all(sc.inject_at_cycle <= 10 < sc.recover_at_cycle for sc in act)
    for sc in act:
        assert sc.fault_type in ChaosFaultType
        assert sc.severity in {"low", "medium", "high", "critical"}


def test_phase45_inject_fault_adds_scenario():
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=5, cycles=20, paper_only=True))
    before = len(eng.scenarios)
    sc = eng.inject_fault(cycle=3, fault_type=ChaosFaultType.VENUE_OUTAGE,
                           venue="okx", symbol="BTC-PERP", severity="critical")
    assert sc.scenario_id in {s.scenario_id for s in eng.scenarios}
    assert len(eng.scenarios) == before + 1
    assert sc.inject_at_cycle == 3


def test_phase45_should_failover_circuit_and_critical():
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=5, cycles=20, paper_only=True))
    from src.resilience.phase45_chaos_failover_engine import VenueHealth
    healthy = VenueHealth(venue="deribit", cycle=1, timestamp="t", healthy=True,
                          circuit_state="closed", error_rate=0.01)
    assert eng.should_failover("deribit", healthy) == (False, "nominal")
    open_cb = VenueHealth(venue="deribit", cycle=1, timestamp="t", healthy=True,
                          circuit_state="open", error_rate=0.01)
    assert eng.should_failover("deribit", open_cb)[0] is True
    crit = VenueHealth(venue="deribit", cycle=1, timestamp="t", healthy=True,
                       circuit_state="closed", error_rate=0.01,
                       fault_severity="critical")
    assert eng.should_failover("deribit", crit)[0] is True


def test_phase45_execute_failover_changes_active_venue():
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=5, cycles=20, paper_only=True))
    start = eng.active_venue
    ev = eng.execute_failover(cycle=1, from_venue=start, to_venue="okx",
                              reason="test", trigger="circuit_open")
    assert ev.executed is True
    assert ev.paper_only is True
    assert eng.active_venue == "okx"
    assert eng.active_venue != start
    assert eng.state == FailoverState.FAILED_OVER


def test_phase45_attempt_recovery_failbacks():
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=5, cycles=20, paper_only=True))
    eng.execute_failover(cycle=1, from_venue="deribit", to_venue="okx",
                         reason="r", trigger="circuit_open")
    assert eng.state == FailoverState.FAILED_OVER
    # force primary healthy so recovery succeeds
    eng.venue_health["deribit"] = VenueHealth(
        venue="deribit", cycle=5, timestamp="t", healthy=True, circuit_state="closed", error_rate=0.01)
    ev = eng.attempt_recovery(cycle=5)
    assert ev is not None
    assert ev.trigger == "automated_recovery"
    assert eng.active_venue == "deribit"
    assert eng.state == FailoverState.NOMINAL


def test_phase45_snapshot_restore_deterministic():
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=9, cycles=30, paper_only=True))
    eng.run_cycle(1)
    eng.run_cycle(2)
    snap = eng.snapshot()
    import json
    json.dumps(snap, allow_nan=False)
    # mutate state
    eng.halt()
    eng.active_venue = "bybit"
    eng.restore(snap)
    assert eng.active_venue == "deribit"
    assert eng.state == FailoverState.NOMINAL
    assert eng._halted is False
    # venue health restored
    assert "deribit" in eng.venue_health


def test_phase45_all_artifacts_finite_jsonable():
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=2, cycles=15, paper_only=True))
    rep = eng.run_campaign()
    import json
    json.dumps(rep, allow_nan=False)
    for cyc in eng.cycles_run:
        json.dumps(cyc, allow_nan=False)
    for ev in eng.failover_events:
        json.dumps(ev.to_dict(), allow_nan=False)
    for a in eng.slo_alerts:
        json.dumps(a.to_dict(), allow_nan=False)


def test_phase45_generate_reports_writes_artifacts(tmp_path):
    eng = Phase45ChaosFailoverEngine(ChaosFailoverConfig(seed=4, cycles=10, paper_only=True,
                                                         outdir=str(tmp_path)))
    paths = eng.generate_reports()
    import json, os
    assert os.path.exists(paths["json"])
    assert os.path.exists(paths["md"])
    assert os.path.exists(paths["campaign_json"])
    assert os.path.exists(paths["campaign_md"])
    data = json.loads(open(paths["json"]).read())
    assert data["gates_ok"] is True
    json.dumps(data, allow_nan=False)
