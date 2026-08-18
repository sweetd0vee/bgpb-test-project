"""Resolved filesystem locations for the ML task."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
DATA_PATH = ARTIFACTS_DIR / "data.csv"
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"
CONFIG_PATH = ARTIFACTS_DIR / "training_config.json"

HOLDOUT_SETS = (
    (ARTIFACTS_DIR / "data_test_1.csv", ARTIFACTS_DIR / "y_test_1.csv"),
    (ARTIFACTS_DIR / "data_test_2.csv", ARTIFACTS_DIR / "y_test_2.csv"),
)
