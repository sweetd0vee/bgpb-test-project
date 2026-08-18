import pandas as pd
import pytest

from src.data import DataValidationError, encode_target, prepare_features
from src.features import CATEGORICAL, FEATURES, ID_COLUMN


def test_encode_target_maps_labels():
    encoded = encode_target(pd.Series(["good", "bad", "good"]))
    assert encoded.tolist() == [1, 0, 1]


def test_encode_target_rejects_unknown_labels():
    with pytest.raises(DataValidationError):
        encode_target(pd.Series(["good", "unknown"]))


def test_prepare_features_requires_columns():
    with pytest.raises(DataValidationError, match="Missing required columns"):
        prepare_features(pd.DataFrame({ID_COLUMN: [1]}))


def test_prepare_features_handles_unknown_and_string_categories(tiny_frame):
    frame = tiny_frame.drop(columns=["Marker"]).copy()
    frame.loc[0, CATEGORICAL[0]] = "brand-new-category"
    prepared = prepare_features(frame)
    assert list(prepared.columns) == FEATURES
    assert str(prepared.iloc[0][CATEGORICAL[0]]) == "brand-new-category"
