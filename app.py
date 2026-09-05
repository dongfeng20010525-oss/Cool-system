"""制冷系统仿真软件 MVP 界面 Demo。结果为模拟数据，仅用于验证界面和流程。"""

import matplotlib.pyplot as plt
import streamlit as st

from demo_data import DemoInputs, DemoResult, DemoValidationError, REFRIGERANTS, simulate_demo


st.set_page_config(page_title="制冷系统仿真 Demo", page_icon="❄️", layout="wide")

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


def render_ph_chart(result: DemoResult) -> None:
    cycle = (*result.states, result.states[0])
    fig, ax = plt.subplots(figsize=(10, 5.2))
    enthalpy = [state.enthalpy_kj_kg for state in cycle]
    pressure = [state.pressure_kpa for state in cycle]
    ax.plot(enthalpy, pressure, color="#1683a8", linewidth=2.5, marker="o", markersize=7)
    for state in result.states:
        ax.annotate(
            f"{state.number} {state.name}",
            (state.enthalpy_kj_kg, state.pressure_kpa),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=9,
        )
    ax.set_title("P-h 循环图（模拟数据）")
    ax.set_xlabel("比焓 (kJ/kg)")
    ax.set_ylabel("压力 (kPa)")
    ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_result(result: DemoResult) -> None:
    st.subheader("仿真结果")
    metric_columns = st.columns(3)
    metric_columns[0].metric("制冷量", f"{result.cooling_capacity_kw:.2f} kW")
    metric_columns[1].metric("压缩机功率", f"{result.compressor_power_kw:.2f} kW")
    metric_columns[2].metric("COP", f"{result.cop:.2f}")

    detail_columns = st.columns(3)
    detail_columns[0].metric("比制冷量", f"{result.specific_refrigeration_effect_kj_kg:.1f} kJ/kg")
    detail_columns[1].metric("比压缩功", f"{result.specific_compressor_work_kj_kg:.1f} kJ/kg")
    detail_columns[2].metric("制冷剂", result.inputs.refrigerant)

    st.subheader("状态点")
    rows = []
    for state in result.states:
        rows.append(
            {
                "编号": state.number,
                "位置": state.name,
                "压力 (kPa)": round(state.pressure_kpa, 1),
                "温度 (°C)": round(state.temperature_c, 1),
                "焓 (kJ/kg)": round(state.enthalpy_kj_kg, 1),
                "熵 (kJ/kg·K)": round(state.entropy_kj_kg_k, 3),
                "干度": "—" if state.quality is None else f"{state.quality:.2f}",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.subheader("循环过程")
    render_ph_chart(result)


st.markdown(
    '<div class="hero"><span class="demo-badge">MVP Demo · 模拟数据</span>'
    '<h1>制冷系统仿真</h1><p>用一组基础参数，快速查看单级稳态制冷循环的界面和操作流程。</p></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("运行参数")
    refrigerant = st.selectbox("制冷剂", REFRIGERANTS, index=0)
    evaporating_temperature = st.number_input("蒸发温度 (°C)", value=0.0, step=1.0)
    condensing_temperature = st.number_input("冷凝温度 (°C)", value=40.0, step=1.0)
    superheat = st.number_input("过热度 (K)", min_value=0.0, value=5.0, step=1.0)
    subcooling = st.number_input("过冷度 (K)", min_value=0.0, value=5.0, step=1.0)
    mass_flow = st.number_input("质量流量 (kg/s)", min_value=0.001, value=0.01, step=0.001, format="%.3f")
    efficiency = st.slider("压缩机等熵效率 (%)", min_value=1.0, max_value=100.0, value=75.0, step=1.0)
    run_simulation = st.button("运行仿真", type="primary", use_container_width=True)

    st.divider()
    st.caption("当前为产品流程演示。数据由本地模拟逻辑生成，不代表真实物性计算结果。")

if run_simulation:
    inputs = DemoInputs(
        refrigerant=refrigerant,
        evaporating_temperature_c=evaporating_temperature,
        condensing_temperature_c=condensing_temperature,
        superheat_k=superheat,
        subcooling_k=subcooling,
        mass_flow_kg_s=mass_flow,
        compressor_efficiency_pct=efficiency,
    )
    try:
        st.session_state.demo_result = simulate_demo(inputs)
        st.session_state.demo_error = None
    except DemoValidationError as error:
        st.session_state.demo_result = None
        st.session_state.demo_error = str(error)

if st.session_state.get("demo_error"):
    st.error(st.session_state.demo_error)

if st.session_state.get("demo_result"):
    render_result(st.session_state.demo_result)
else:
    st.markdown(
        '<div class="empty-state"><h3>准备开始一次仿真</h3>'
        '<p>在左侧调整运行参数，点击“运行仿真”查看指标、状态点和 P-h 循环图。</p></div>',
        unsafe_allow_html=True,
    )

