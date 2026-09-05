"""单级稳态蒸汽压缩制冷循环的 CoolProp 计算模块。"""

from dataclasses import dataclass

from CoolProp.CoolProp import PropsSI


REFRIGERANTS = ("R134a", "R410A", "R32")


class InputValidationError(ValueError):
    """输入参数不满足循环计算的基础约束。"""


class PropertyCalculationError(ValueError):
    """CoolProp 无法为当前输入生成有效物性状态。"""


@dataclass(frozen=True)
class CycleInputs:
    refrigerant: str = "R134a"
    evaporating_temperature_c: float = 0.0
    condensing_temperature_c: float = 40.0
    superheat_k: float = 5.0
    subcooling_k: float = 5.0
    mass_flow_kg_s: float = 0.01
    compressor_isentropic_efficiency: float = 0.75


@dataclass(frozen=True)
class StatePoint:
    number: int
    name: str
    pressure_pa: float
    temperature_k: float
    enthalpy_j_kg: float
    entropy_j_kg_k: float
    quality: float | None


@dataclass(frozen=True)
class CycleResult:
    inputs: CycleInputs
    states: tuple[StatePoint, StatePoint, StatePoint, StatePoint]
    specific_refrigeration_effect_j_kg: float
    specific_compressor_work_j_kg: float
    specific_condenser_rejection_j_kg: float
    cooling_capacity_w: float
    compressor_power_w: float
    cop: float


def validate_inputs(inputs: CycleInputs) -> None:
    if inputs.refrigerant not in REFRIGERANTS:
        raise InputValidationError("请选择 R134a、R410A 或 R32。")
    if inputs.condensing_temperature_c <= inputs.evaporating_temperature_c:
        raise InputValidationError("冷凝温度必须高于蒸发温度，请提高冷凝温度或降低蒸发温度。")
    if inputs.superheat_k < 0:
        raise InputValidationError("过热度不能为负数，请输入不小于 0 K 的值。")
    if inputs.subcooling_k < 0:
        raise InputValidationError("过冷度不能为负数，请输入不小于 0 K 的值。")
    if inputs.mass_flow_kg_s <= 0:
        raise InputValidationError("质量流量必须大于 0 kg/s。")
    if not 0 < inputs.compressor_isentropic_efficiency <= 1:
        raise InputValidationError("压缩机等熵效率必须在 0% 到 100% 之间。")


def _property(output: str, input_1: str, value_1: float, input_2: str, value_2: float, refrigerant: str) -> float:
    try:
        return float(PropsSI(output, input_1, value_1, input_2, value_2, refrigerant))
    except Exception as error:
        raise PropertyCalculationError(
            "当前参数组合无法计算有效物性状态，请调整蒸发温度、冷凝温度、过热度或过冷度。"
        ) from error


def _quality(pressure_pa: float, enthalpy_j_kg: float, refrigerant: str) -> float | None:
    try:
        value = float(PropsSI("Q", "P", pressure_pa, "H", enthalpy_j_kg, refrigerant))
    except Exception:
        return None
    return value if 0 <= value <= 1 else None


def simulate_cycle(inputs: CycleInputs) -> CycleResult:
    """根据输入计算四状态点和稳态循环性能。"""

    validate_inputs(inputs)
    refrigerant = inputs.refrigerant
    evaporating_temperature_k = inputs.evaporating_temperature_c + 273.15
    condensing_temperature_k = inputs.condensing_temperature_c + 273.15

    low_pressure = _property("P", "T", evaporating_temperature_k, "Q", 0, refrigerant)
    high_pressure = _property("P", "T", condensing_temperature_k, "Q", 0, refrigerant)

    t1 = evaporating_temperature_k + inputs.superheat_k
    h1 = _property("H", "P", low_pressure, "T", t1, refrigerant)
    s1 = _property("S", "P", low_pressure, "T", t1, refrigerant)

    h2s = _property("H", "P", high_pressure, "S", s1, refrigerant)
    h2 = h1 + (h2s - h1) / inputs.compressor_isentropic_efficiency
    t2 = _property("T", "P", high_pressure, "H", h2, refrigerant)
    s2 = _property("S", "P", high_pressure, "H", h2, refrigerant)

    t3 = condensing_temperature_k - inputs.subcooling_k
    h3 = _property("H", "P", high_pressure, "T", t3, refrigerant)
    s3 = _property("S", "P", high_pressure, "T", t3, refrigerant)

    h4 = h3
    t4 = _property("T", "P", low_pressure, "H", h4, refrigerant)
    s4 = _property("S", "P", low_pressure, "H", h4, refrigerant)

    states = (
        StatePoint(1, "压缩机入口", low_pressure, t1, h1, s1, None),
        StatePoint(2, "压缩机出口", high_pressure, t2, h2, s2, None),
        StatePoint(3, "冷凝器出口", high_pressure, t3, h3, s3, None),
        StatePoint(4, "节流阀出口", low_pressure, t4, h4, s4, _quality(low_pressure, h4, refrigerant)),
    )

    specific_refrigeration_effect = h1 - h4
    specific_compressor_work = h2 - h1
    specific_condenser_rejection = h2 - h3
    cooling_capacity = inputs.mass_flow_kg_s * specific_refrigeration_effect
    compressor_power = inputs.mass_flow_kg_s * specific_compressor_work
    cop = specific_refrigeration_effect / specific_compressor_work

    if specific_refrigeration_effect <= 0 or specific_compressor_work <= 0 or cop <= 0:
        raise PropertyCalculationError("当前参数组合得到的循环性能无效，请调整运行温度或压缩机效率。")

    return CycleResult(
        inputs=inputs,
        states=states,
        specific_refrigeration_effect_j_kg=specific_refrigeration_effect,
        specific_compressor_work_j_kg=specific_compressor_work,
        specific_condenser_rejection_j_kg=specific_condenser_rejection,
        cooling_capacity_w=cooling_capacity,
        compressor_power_w=compressor_power,
        cop=cop,
    )
