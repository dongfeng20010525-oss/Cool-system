from demo_data import DemoInputs, DemoValidationError, simulate_demo


def test_demo_returns_complete_result_for_default_inputs():
    result = simulate_demo(DemoInputs())

    assert len(result.states) == 4
    assert result.states[0].number == 1
    assert result.states[-1].number == 4
    assert result.cooling_capacity_kw > 0
    assert result.compressor_power_kw > 0
    assert result.cop > 0
    assert result.states[2].enthalpy_kj_kg == result.states[3].enthalpy_kj_kg


def test_mass_flow_changes_total_capacity_but_not_specific_result():
    base = simulate_demo(DemoInputs(mass_flow_kg_s=0.01))
    doubled = simulate_demo(DemoInputs(mass_flow_kg_s=0.02))

    assert doubled.cooling_capacity_kw == 2 * base.cooling_capacity_kw
    assert doubled.compressor_power_kw == 2 * base.compressor_power_kw
    assert doubled.cop == base.cop


def test_invalid_temperature_relation_is_explained():
    try:
        simulate_demo(DemoInputs(evaporating_temperature_c=40, condensing_temperature_c=35))
    except DemoValidationError as error:
        assert "冷凝温度" in str(error)
    else:
        raise AssertionError("expected DemoValidationError")


def test_invalid_mass_flow_is_rejected():
    try:
        simulate_demo(DemoInputs(mass_flow_kg_s=0))
    except DemoValidationError as error:
        assert "质量流量" in str(error)
    else:
        raise AssertionError("expected DemoValidationError")

