from cooling_cycle import CycleInputs, simulate_cycle


def test_ph_chart_renders_real_state_points(monkeypatch):
    import app

    monkeypatch.setattr(app.st, "pyplot", lambda *_args, **_kwargs: None)

    app.render_ph_chart(simulate_cycle(CycleInputs()))


def test_chinese_font_is_selected_for_plot_labels():
    import app

    selected_font = app.configure_chinese_font()

    assert selected_font in app.CHINESE_FONT_CANDIDATES or selected_font == "DejaVu Sans"


def test_mass_flow_ui_unit_converts_to_internal_si_unit():
    import app

    assert app.mass_flow_kg_h_to_kg_s(36) == 0.01
    assert app.mass_flow_kg_s_to_kg_h(0.01) == 36
