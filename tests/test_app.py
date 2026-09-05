from cooling_cycle import CycleInputs, simulate_cycle


def test_ph_chart_renders_real_state_points(monkeypatch):
    import app

    monkeypatch.setattr(app.st, "pyplot", lambda *_args, **_kwargs: None)

    app.render_ph_chart(simulate_cycle(CycleInputs()))
