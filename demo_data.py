"""制冷系统 MVP 界面演示用的确定性模拟数据。"""

from dataclasses import dataclass


REFRIGERANTS = ("R134a", "R410A", "R32")


class DemoValidationError(ValueError):
    """用户输入不满足演示流程约束时抛出。"""


@dataclass(frozen=True)
class DemoInputs:
    refrigerant: str = "R134a"
    evaporating_temperature_c: float = 0.0
    condensing_temperature_c: float = 40.0
    superheat_k: float = 5.0
    subcooling_k: float = 5.0
    mass_flow_kg_s: float = 0.01
    compressor_efficiency_pct: float = 75.0


@dataclass(frozen=True)
class DemoStatePoint:
    number: int
    name: str
    pressure_kpa: float
    temperature_c: float
    enthalpy_kj_kg: float
    entropy_kj_kg_k: float
    quality: float | None


@dataclass(frozen=True)
class DemoResult:
    inputs: DemoInputs
    states: tuple[DemoStatePoint, ...]
    specific_refrigeration_effect_kj_kg: float
    specific_compressor_work_kj_kg: float
    cooling_capacity_kw: float
    compressor_power_kw: float
    cop: float


def validate_inputs(inputs: DemoInputs) -> None:
    if inputs.refrigerant not in REFRIGERANTS:
        raise DemoValidationError("请选择 R134a、R410A 或 R32。")
    if inputs.condensing_temperature_c <= inputs.evaporating_temperature_c:
        raise DemoValidationError("冷凝温度必须高于蒸发温度。")
    if inputs.superheat_k < 0 or inputs.subcooling_k < 0:
        raise DemoValidationError("过热度和过冷度不能为负数。")
    if inputs.mass_flow_kg_s <= 0:
        raise DemoValidationError("质量流量必须大于 0 kg/s。")
    if not 0 < inputs.compressor_efficiency_pct <= 100:
        raise DemoValidationError("压缩机等熵效率必须在 0% 到 100% 之间。")


def simulate_demo(inputs: DemoInputs) -> DemoResult:
    """根据输入生成稳定、可解释的演示结果，不调用真实物性库。"""

    validate_inputs(inputs)

    temperature_lift = inputs.condensing_temperature_c - inputs.evaporating_temperature_c
    specific_refrigeration_effect = max(
        95.0,
        165.0 - 0.9 * temperature_lift + 0.35 * inputs.superheat_k + 0.2 * inputs.subcooling_k,
    )
    specific_compressor_work = max(
        18.0,
        42.0 + 0.55 * temperature_lift + (75.0 - inputs.compressor_efficiency_pct) * 0.28,
    )
    cooling_capacity = inputs.mass_flow_kg_s * specific_refrigeration_effect
    compressor_power = inputs.mass_flow_kg_s * specific_compressor_work

    low_pressure = 290.0 + 5.5 * (inputs.evaporating_temperature_c + 10.0)
    high_pressure = 900.0 + 12.0 * (inputs.condensing_temperature_c - 30.0)
    h1 = 405.0 + 0.8 * inputs.evaporating_temperature_c + 0.7 * inputs.superheat_k
    h4 = h1 - specific_refrigeration_effect
    h2 = h1 + specific_compressor_work

    states = (
        DemoStatePoint(1, "压缩机入口", low_pressure, inputs.evaporating_temperature_c + inputs.superheat_k, h1, 1.75, None),
        DemoStatePoint(2, "压缩机出口", high_pressure, inputs.condensing_temperature_c + 18.0, h2, 1.82, None),
        DemoStatePoint(3, "冷凝器出口", high_pressure, inputs.condensing_temperature_c - inputs.subcooling_k, h4, 1.15, 0.0),
        DemoStatePoint(4, "节流阀出口", low_pressure, inputs.evaporating_temperature_c - 2.0, h4, 1.21, 0.24),
    )
    return DemoResult(
        inputs=inputs,
        states=states,
        specific_refrigeration_effect_kj_kg=specific_refrigeration_effect,
        specific_compressor_work_kj_kg=specific_compressor_work,
        cooling_capacity_kw=cooling_capacity,
        compressor_power_kw=compressor_power,
        cop=specific_refrigeration_effect / specific_compressor_work,
    )

