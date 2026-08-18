import pandas as pd
import pytest

from src.features import CATEGORICAL, ID_COLUMN, NUMERICAL, TARGET_COLUMN
from src.pipeline import SEED, build_pipeline, compute_scale_pos_weight
from src.data import encode_target, prepare_features


@pytest.fixture
def tiny_frame() -> pd.DataFrame:
    rows = []
    for i in range(40):
        row = {ID_COLUMN: str(i), TARGET_COLUMN: "good" if i % 5 else "bad"}
        for column in NUMERICAL:
            row[column] = float((i % 7) + 1)
        for column in CATEGORICAL:
            row[column] = "A" if i % 2 == 0 else "B"
        rows.append(row)
    return pd.DataFrame(rows)


@pytest.fixture
def fitted_pipeline(tiny_frame: pd.DataFrame):
    y = encode_target(tiny_frame[TARGET_COLUMN])
    x = prepare_features(tiny_frame.drop(columns=[TARGET_COLUMN]))
    pipeline = build_pipeline(
        scale_pos_weight=compute_scale_pos_weight(y),
        random_state=SEED,
        n_jobs=1,
    )
    pipeline.set_params(model__n_estimators=10, model__max_depth=2, model__learning_rate=0.3)
    pipeline.fit(x, y)
    return pipeline, x, y
