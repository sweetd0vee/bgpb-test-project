"""Offline evaluation of a trained pipeline on holdout CSV pairs."""

from __future__ import annotations

import argparse
from pathlib import Path

from sklearn.metrics import accuracy_score, average_precision_score, roc_auc_score

from src.data import load_feature_frame, load_labels
from src.log import logger
from src.model_io import load_pipeline, save_json
from src.paths import ARTIFACTS_DIR, HOLDOUT_SETS, MODEL_PATH
from src.predict import predict_frame


def evaluate_pair(pipeline, features_path: Path, labels_path: Path) -> dict:
    features = load_feature_frame(features_path)
    labels = load_labels(labels_path)
    aligned_labels = labels.reindex(features.index.astype(str))
    if aligned_labels.isna().any():
        missing = aligned_labels[aligned_labels.isna()].index.tolist()
        raise ValueError(f"Labels missing for IDs: {missing[:10]}")

    scored = predict_frame(pipeline, features)
    y_true = aligned_labels.astype(int)
    y_prob = [row["probability_good"] for row in scored]
    y_pred = [row["prediction"] for row in scored]
    return {
        "features": str(features_path.name),
        "labels": str(labels_path.name),
        "n_rows": int(len(features)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "average_precision": float(average_precision_score(y_true, y_prob)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
    }


def evaluate(
    *,
    model_path: Path = MODEL_PATH,
    output_path: Path | None = None,
) -> dict:
    pipeline = load_pipeline(model_path)
    reports = [evaluate_pair(pipeline, features, labels) for features, labels in HOLDOUT_SETS]
    payload = {"model_path": str(model_path), "holdout": reports}
    if output_path is not None:
        save_json(payload, output_path)
    for report in reports:
        logger.info(
            "%s ROC-AUC=%.4f AP=%.4f accuracy=%.4f (n=%s)",
            report["features"],
            report["roc_auc"],
            report["average_precision"],
            report["accuracy"],
            report["n_rows"],
        )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTIFACTS_DIR / "holdout_metrics.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    evaluate(model_path=args.model_path, output_path=args.output)


if __name__ == "__main__":
    main()
