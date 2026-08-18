"""Sklearn pipeline: impute + ordinal-encode categoricals, then XGBoost."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from src.features import CATEGORICAL, NUMERICAL

SEED = 42

DEFAULT_PARAM_GRID: dict[str, list[Any]] = {
    "model__n_estimators": [50, 100],
    "model__learning_rate": [0.05, 0.1],
    "model__max_depth": [3, 5],
    "model__min_child_weight": [1, 3],
}

QUICK_PARAM_GRID: dict[str, list[Any]] = {
    "model__n_estimators": [20],
    "model__learning_rate": [0.1],
    "model__max_depth": [3],
}


def compute_scale_pos_weight(y: pd.Series) -> float:
    n_positive = int((y == 1).sum())
    n_negative = int((y == 0).sum())
    if n_positive == 0:
        return 1.0
    return n_negative / n_positive


def build_pipeline(
    *,
    scale_pos_weight: float = 1.0,
    random_state: int = SEED,
    n_jobs: int = -1,
) -> Pipeline:
    from xgboost import XGBClassifier

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            (
                "encoder",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    dtype=np.int32,
                ),
            ),
        ]
    )
    numeric_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_transformer, CATEGORICAL),
            ("num", numeric_transformer, NUMERICAL),
        ],
        remainder="drop",
    )
    model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="auc",
        scale_pos_weight=scale_pos_weight,
        random_state=random_state,
        n_jobs=n_jobs,
        tree_method="hist",
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )
