from pathlib import Path

from src.data import load_feature_frame, load_labels
from src.paths import HOLDOUT_SETS
from train import train


def test_train_quick_writes_artifacts(tiny_frame, tmp_path: Path):
    data_path = tmp_path / "data.csv"
    tiny_frame.to_csv(data_path, index=False)
    model_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "metrics.json"
    config_path = tmp_path / "training_config.json"

    metrics = train(
        data_path=data_path,
        model_path=model_path,
        metrics_path=metrics_path,
        config_path=config_path,
        test_size=0.3,
        cv=2,
        quick=True,
    )
    assert model_path.exists()
    assert metrics_path.exists()
    assert config_path.exists()
    assert 0.0 <= metrics["roc_auc"] <= 1.0


def test_holdout_files_align():
    for features_path, labels_path in HOLDOUT_SETS:
        features = load_feature_frame(features_path)
        labels = load_labels(labels_path)
        assert set(features.index.astype(str)) == set(labels.index.astype(str))
