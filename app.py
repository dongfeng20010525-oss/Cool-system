"""制冷系统仿真软件 MVP Streamlit 页面。"""

import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import font_manager

from cooling_cycle import (
    REFRIGERANTS,
    CycleInputs,
    CycleResult,
    InputValidationError,
    PropertyCalculationError,
    simulate_cycle,
)


CHINESE_FONT_CANDIDATES = (
    "Microsoft YaHei",
    "SimHei",
    "Microsoft JhengHei",
    "Noto Sans CJK SC",
    "Source Han Sans CN",
)
MASS_FLOW_KG_H_TO_KG_S = 1 / 3600


st.set_page_config(page_title="制冷系统仿真", page_icon="❄️", layout="wide")

st.markdown(
    """
    <style>
    .block-container { max-width: 1400px; padding-top: 2rem; }
    .hero { padding: 1.4rem 1.6rem; border-radius: 16px; background: linear-gradient(135deg, #0f3557, #1877a8); color: white; margin-bottom: 1rem; }
    .hero h1 { margin: 0; font-size: 2rem; }
    .hero p { margin: .45rem 0 0; color: #dceffd; }
    .demo-badge { display: inline-block; padding: .25rem .65rem; border-radius: 999px; background: #dff5e8; color: #17663a; font-size: .8rem; font-weight: 700; }
    .empty-state { padding: 2.2rem; border: 1px dashed #a7bfd1; border-radius: 14px; text-align: center; background: #f7fbfd; color: #547083; }
    </style>
    """,
    unsafe_allow_html=True,
)


def configure_chinese_font() -> str:
    """选择当前环境中可用的中文字体，避免图表中文显示为方框。"""

    installed_fonts = {font.name for font in font_manager.fontManager.ttflist}
    selected_font = next(
        (font for font in CHINESE_FONT_CANDIDATES if font in installed_fonts),
        "DejaVu Sans",
    )
    plt.rcParams["font.sans-serif"] = [selected_font, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    return selected_font


def mass_flow_kg_h_to_kg_s(mass_flow_kg_h: float) -> float:
    return mass_flow_kg_h * MASS_FLOW_KG_H_TO_KG_S


def mass_flow_kg_s_to_kg_h(mass_flow_kg_s: float) -> float:
    return mass_flow_kg_s / MASS_FLOW_KG_H_TO_KG_S


def render_ph_chart(result: CycleResult) -> None:
    configure_chinese_font()
    cycle = (*result.states, result.states[0])
    fig, ax = plt.subplots(figsize=(10, 5.2))
    enthalpy = [state.enthalpy_j_kg / 1000 for state in cycle]
    pressure = [state.pressure_pa / 1000 for state in cycle]
    ax.plot(enthalpy, pressure, color="#1683a8", linewidth=2.5, marker="o", markersize=7)
    for state in result.states:
        ax.annotate(
            f"{state.number} {state.name}",
            (state.enthalpy_j_kg / 1000, state.pressure_pa / 1000),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=9,
        )
    ax.set_title("P-h 循环图")
    ax.set_xlabel("比焓 (kJ/kg)")
    ax.set_ylabel("压力 (kPa)")
    ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_result(result: CycleResult) -> None:
    st.subheader("仿真结果")
    metric_columns = st.columns(3)
    metric_columns[0].metric("制冷量", f"{result.cooling_capacity_w / 1000:.2f} kW")
    metric_columns[1].metric("压缩机功率", f"{result.compressor_power_w / 1000:.2f} kW")
    metric_columns[2].metric("COP", f"{result.cop:.2f}")

    detail_columns = st.columns(3)
    detail_columns[0].metric("比制冷量", f"{result.specific_refrigeration_effect_j_kg / 1000:.1f} kJ/kg")
    detail_columns[1].metric("比压缩功", f"{result.specific_compressor_work_j_kg / 1000:.1f} kJ/kg")
    detail_columns[2].metric("制冷剂", result.inputs.refrigerant)

    st.subheader("本次输入")
    st.dataframe(
        [
            {"参数": "蒸发温度", "数值": result.inputs.evaporating_temperature_c, "单位": "°C"},
            {"参数": "冷凝温度", "数值": result.inputs.condensing_temperature_c, "单位": "°C"},
            {"参数": "过热度", "数值": result.inputs.superheat_k, "单位": "K"},
            {"参数": "过冷度", "数值": result.inputs.subcooling_k, "单位": "K"},
            {"参数": "质量流量", "数值": mass_flow_kg_s_to_kg_h(result.inputs.mass_flow_kg_s), "单位": "kg/h"},
            {
                "参数": "压缩机等熵效率",
                "数值": result.inputs.compressor_isentropic_efficiency * 100,
                "单位": "%",
            },
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("状态点")
    rows = []
    for state in result.states:
        rows.append(
            {
                "编号": state.number,
                "位置": state.name,
                "压力 (kPa)": round(state.pressure_pa / 1000, 1),
                "温度 (°C)": round(state.temperature_k - 273.15, 1),
                "焓 (kJ/kg)": round(state.enthalpy_j_kg / 1000, 1),
                "熵 (kJ/kg·K)": round(state.entropy_j_kg_k / 1000, 3),
                "干度": "—" if state.quality is None else f"{state.quality:.2f}",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.subheader("循环过程")
    render_ph_chart(result)


st.markdown(
    '<div class="hero"><span class="demo-badge">MVP · CoolProp 物性</span>'
    '<h1>制冷系统仿真</h1><p>输入基础工况，计算单级稳态蒸汽压缩制冷循环。</p></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("运行参数")
    refrigerant = st.selectbox("制冷剂", REFRIGERANTS, index=0)
    evaporating_temperature = st.number_input("蒸发温度 (°C)", value=0.0, step=1.0)
    condensing_temperature = st.number_input("冷凝温度 (°C)", value=40.0, step=1.0)
    superheat = st.number_input("过热度 (K)", min_value=0.0, value=5.0, step=1.0)
    subcooling = st.number_input("过冷度 (K)", min_value=0.0, value=5.0, step=1.0)
    mass_flow_kg_h = st.number_input("质量流量 (kg/h)", min_value=0.1, value=36.0, step=1.0, format="%.1f")
    efficiency = st.slider("压缩机等熵效率 (%)", min_value=1.0, max_value=100.0, value=75.0, step=1.0)
    run_simulation = st.button("运行仿真", type="primary", use_container_width=True)

    st.divider()
    st.caption("采用 CoolProp 计算物性；结果用于早期估算，不替代完整设备选型或实验验证。")

if run_simulation:
    inputs = CycleInputs(
        refrigerant=refrigerant,
        evaporating_temperature_c=evaporating_temperature,
        condensing_temperature_c=condensing_temperature,
        superheat_k=superheat,
        subcooling_k=subcooling,
        mass_flow_kg_s=mass_flow_kg_h_to_kg_s(mass_flow_kg_h),
        compressor_isentropic_efficiency=efficiency / 100,
    )
    try:
        st.session_state.cycle_result = simulate_cycle(inputs)
        st.session_state.cycle_error = None
    except (InputValidationError, PropertyCalculationError) as error:
        st.session_state.cycle_result = None
        st.session_state.cycle_error = str(error)

if st.session_state.get("cycle_error"):
    st.error(st.session_state.cycle_error)

if st.session_state.get("cycle_result"):
    render_result(st.session_state.cycle_result)
else:
    st.markdown(
        '<div class="empty-state"><h3>准备开始一次仿真</h3>'
        '<p>在左侧调整运行参数，点击“运行仿真”查看物性计算结果、状态点和 P-h 循环图。</p></div>',
        unsafe_allow_html=True,
    )
