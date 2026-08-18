"""Prediction helpers used by the API and offline evaluation."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.pipeline import Pipeline

from src.features import POSITIVE_CLASS


def predict_frame(pipeline: Pipeline, features: pd.DataFrame) -> list[dict[str, Any]]:
    """Return one scored row per input index."""
    class_labels = list(pipeline.classes_)
    positive_index = class_labels.index(POSITIVE_CLASS) if POSITIVE_CLASS in class_labels else -1

    predicted = pipeline.predict(features)
    probabilities = pipeline.predict_proba(features)

    rows: list[dict[str, Any]] = []
    for row_id, label, proba in zip(features.index.astype(str), predicted, probabilities):
        probability_good = float(proba[positive_index])
        rows.append(
            {
                "id": row_id,
                "prediction": int(label),
                "probability_good": probability_good,
                "probability_default": 1.0 - probability_good,
            }
        )
    return rows
