from src.predict import predict_frame


def test_predict_frame_returns_one_row_per_input(fitted_pipeline):
    pipeline, features, _ = fitted_pipeline
    scored = predict_frame(pipeline, features)
    assert len(scored) == len(features)
    row = scored[0]
    assert set(row) == {"id", "prediction", "probability_good", "probability_default"}
    assert 0.0 <= row["probability_good"] <= 1.0
    assert abs(row["probability_good"] + row["probability_default"] - 1.0) < 1e-6


def test_unknown_category_does_not_break_inference(fitted_pipeline, tiny_frame):
    pipeline, features, _ = fitted_pipeline
    features = features.copy()
    features.iloc[0, features.columns.get_loc("SEX")] = "something-unseen"
    scored = predict_frame(pipeline, features)
    assert len(scored) == len(features)
