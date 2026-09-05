import pytest

from cooling_cycle import CycleInputs, InputValidationError, simulate_cycle


@pytest.mark.parametrize("refrigerant", ["R134a", "R410A", "R32"])
def test_supported_refrigerants_return_valid_cycle(refrigerant):
    result = simulate_cycle(CycleInputs(refrigerant=refrigerant))

    assert [state.number for state in result.states] == [1, 2, 3, 4]
    assert result.states[1].pressure_pa > result.states[0].pressure_pa
    assert result.states[2].enthalpy_j_kg == result.states[3].enthalpy_j_kg
    assert result.states[1].enthalpy_j_kg > result.states[0].enthalpy_j_kg
    assert result.cooling_capacity_w > 0
    assert result.compressor_power_w > 0
    assert result.cop > 0


def test_mass_flow_changes_total_outputs_only():
    base = simulate_cycle(CycleInputs(mass_flow_kg_s=0.01))
    doubled = simulate_cycle(CycleInputs(mass_flow_kg_s=0.02))

    assert doubled.cooling_capacity_w == pytest.approx(2 * base.cooling_capacity_w)
    assert doubled.compressor_power_w == pytest.approx(2 * base.compressor_power_w)
    assert doubled.specific_refrigeration_effect_j_kg == pytest.approx(base.specific_refrigeration_effect_j_kg)
    assert doubled.specific_compressor_work_j_kg == pytest.approx(base.specific_compressor_work_j_kg)
    assert doubled.cop == pytest.approx(base.cop)


def test_same_inputs_are_deterministic():
    inputs = CycleInputs()

    first = simulate_cycle(inputs)
    second = simulate_cycle(inputs)

    assert first == second


@pytest.mark.parametrize(
    "inputs, message",
    [
        (CycleInputs(refrigerant="R22"), "请选择"),
        (CycleInputs(evaporating_temperature_c=40, condensing_temperature_c=35), "冷凝温度"),
        (CycleInputs(superheat_k=-1), "过热度"),
        (CycleInputs(subcooling_k=-1), "过冷度"),
        (CycleInputs(mass_flow_kg_s=0), "质量流量"),
        (CycleInputs(compressor_isentropic_efficiency=0), "效率"),
        (CycleInputs(compressor_isentropic_efficiency=1.01), "效率"),
    ],
)
def test_invalid_inputs_are_rejected(inputs, message):
    with pytest.raises(InputValidationError, match=message):
        simulate_cycle(inputs)
