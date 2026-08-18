"""Load and persist the trained sklearn pipeline and metrics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
from sklearn.pipeline import Pipeline

from src.paths import METRICS_PATH, MODEL_PATH


class ModelNotFoundError(FileNotFoundError):
    """Raised when the serialized pipeline is missing."""


def save_pipeline(pipeline: Pipeline, path: Path = MODEL_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path, compress=True)
    return path


def load_pipeline(path: Path = MODEL_PATH) -> Pipeline:
    if not path.exists():
        raise ModelNotFoundError(f"Model artifact not found: {path}")
    return joblib.load(path)


def save_json(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_metrics(path: Path = METRICS_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Metrics file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
