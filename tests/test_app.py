from cooling_cycle import CycleInputs, simulate_cycle


def test_ph_chart_renders_real_state_points(monkeypatch):
    import app

    monkeypatch.setattr(app.st, "pyplot", lambda *_args, **_kwargs: None)

    app.render_ph_chart(simulate_cycle(CycleInputs()))


def test_chinese_font_is_selected_for_plot_labels():
    import app

    selected_font = app.configure_chinese_font()

    assert selected_font in app.CHINESE_FONT_CANDIDATES or selected_font == "DejaVu Sans"
