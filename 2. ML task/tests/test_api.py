import io

from fastapi.testclient import TestClient

from src.data import encode_target, prepare_features
from src.pipeline import SEED, build_pipeline, compute_scale_pos_weight


def _client_with_pipeline(tiny_frame):
    from app import app

    y = encode_target(tiny_frame["Marker"])
    x = prepare_features(tiny_frame.drop(columns=["Marker"]))
    pipeline = build_pipeline(
        scale_pos_weight=compute_scale_pos_weight(y),
        random_state=SEED,
        n_jobs=1,
    )
    pipeline.set_params(model__n_estimators=10, model__max_depth=2, model__learning_rate=0.3)
    pipeline.fit(x, y)

    client = TestClient(app)
    app.state.pipeline = pipeline
    return client, tiny_frame.drop(columns=["Marker"])


def test_health_ok(tiny_frame):
    client, _ = _client_with_pipeline(tiny_frame)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["model_loaded"] is True


def test_predict_batch_csv(tiny_frame):
    client, features = _client_with_pipeline(tiny_frame)
    csv_buffer = io.BytesIO(features.to_csv(index=False).encode("utf-8"))
    response = client.post("/predict", files={"file": ("batch.csv", csv_buffer, "text/csv")})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["n_rows"] == len(features)
    assert len(payload["predictions"]) == len(features)


def test_predict_rejects_missing_columns(tiny_frame):
    client, _ = _client_with_pipeline(tiny_frame)
    response = client.post(
        "/predict",
        files={"file": ("bad.csv", b"ID\n1\n", "text/csv")},
    )
    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]


def test_predict_rejects_non_csv(tiny_frame):
    client, _ = _client_with_pipeline(tiny_frame)
    response = client.post(
        "/predict",
        files={"file": ("notes.txt", b"not a csv", "text/plain")},
    )
    assert response.status_code == 400


def test_predict_rejects_empty_file(tiny_frame):
    client, _ = _client_with_pipeline(tiny_frame)
    response = client.post(
        "/predict",
        files={"file": ("empty.csv", b"", "text/csv")},
    )
    assert response.status_code == 400
