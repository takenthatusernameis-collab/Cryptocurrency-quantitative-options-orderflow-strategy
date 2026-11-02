from src.attribution.phase43_pnl_attribution import Phase43PnLAttribution, AttributionConfig43


def test_phase43_attribution_deterministic():
    cfg = AttributionConfig43(seed=4343, paper_only=True)
    a = Phase43PnLAttribution(cfg)
    attrs = a.attribute_pnl(0)
    assert len(attrs) > 0
    for x in attrs:
        assert x.delta_pnl is not None


def test_phase43_var_es_stress():
    cfg = AttributionConfig43(seed=4343, paper_only=True)
    a = Phase43PnLAttribution(cfg)
    var = a.compute_var_es(1)
    assert var.portfolio_var_usd >= 0
    assert var.portfolio_cvar_es_usd >= var.portfolio_var_usd
    stress = a.run_stress_scenarios(2)
    assert len(stress) == 4
    camp = a.run_campaign(4)
    assert camp["gates_ok"] is True
    assert camp["n_attributions"] > 0
