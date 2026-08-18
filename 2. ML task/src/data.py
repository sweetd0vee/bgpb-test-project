"""Loading, validation and target encoding for tabular credit data."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from src.features import (
    CATEGORICAL,
    FEATURES,
    ID_COLUMN,
    NUMERICAL,
    REQUIRED_INPUT_COLUMNS,
    TARGET_COLUMN,
    TARGET_MAP,
)


class DataValidationError(ValueError):
    """Raised when an input frame does not match the expected schema."""


def encode_target(series: pd.Series) -> pd.Series:
    """Map `good`/`bad` labels to 1/0; leave already-encoded values as-is."""
    if series.dtype == object or series.dtype.name == "string":
        mapped = series.map(TARGET_MAP)
        if mapped.isna().any():
            unknown = sorted(series[mapped.isna()].astype(str).unique().tolist())
            raise DataValidationError(f"Unknown target values: {unknown}")
        return mapped.astype(int)
    return series.astype(int)


def missing_columns(frame: pd.DataFrame, required: Iterable[str]) -> list[str]:
    return [column for column in required if column not in frame.columns]


def prepare_features(frame: pd.DataFrame, *, require_id: bool = True) -> pd.DataFrame:
    """Return a copy with categorical columns as strings and a stable column order."""
    required = REQUIRED_INPUT_COLUMNS if require_id else FEATURES
    missing = missing_columns(frame, required)
    if missing:
        raise DataValidationError(f"Missing required columns: {missing}")

    prepared = frame.copy()
    if require_id:
        prepared[ID_COLUMN] = prepared[ID_COLUMN].astype(str)
        prepared = prepared.set_index(ID_COLUMN)

    for column in CATEGORICAL:
        prepared[column] = prepared[column].astype("string")
    for column in NUMERICAL:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce")

    return prepared[FEATURES]


def load_training_frame(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    raw = pd.read_csv(path)
    missing = missing_columns(raw, REQUIRED_INPUT_COLUMNS + [TARGET_COLUMN])
    if missing:
        raise DataValidationError(f"Training file is missing columns: {missing}")
    if raw.empty:
        raise DataValidationError("Training file is empty")

    y = encode_target(raw[TARGET_COLUMN])
    x = prepare_features(raw.drop(columns=[TARGET_COLUMN]))
    return x, y


def load_feature_frame(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    if raw.empty:
        raise DataValidationError("Input file is empty")
    return prepare_features(raw)


def load_labels(path: Path) -> pd.Series:
    raw = pd.read_csv(path)
    missing = missing_columns(raw, [ID_COLUMN, TARGET_COLUMN])
    if missing:
        raise DataValidationError(f"Label file is missing columns: {missing}")
    labels = encode_target(raw[TARGET_COLUMN])
    labels.index = raw[ID_COLUMN].astype(str)
    labels.name = TARGET_COLUMN
    return labels
