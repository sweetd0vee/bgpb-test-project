"""Train an XGBoost default-risk pipeline and persist artifacts."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split

from src.data import load_training_frame
from src.log import logger
from src.model_io import save_json, save_pipeline
from src.paths import CONFIG_PATH, DATA_PATH, METRICS_PATH, MODEL_PATH
from src.pipeline import DEFAULT_PARAM_GRID, QUICK_PARAM_GRID, SEED, build_pipeline, compute_scale_pos_weight


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH, help="Training CSV with Marker")
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    parser.add_argument("--metrics-path", type=Path, default=METRICS_PATH)
    parser.add_argument("--config-path", type=Path, default=CONFIG_PATH)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--cv", type=int, default=3)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use a tiny hyperparameter grid (for tests and smoke runs)",
    )
    return parser.parse_args()


def train(
    *,
    data_path: Path = DATA_PATH,
    model_path: Path = MODEL_PATH,
    metrics_path: Path = METRICS_PATH,
    config_path: Path = CONFIG_PATH,
    test_size: float = 0.2,
    cv: int = 3,
    quick: bool = False,
    random_state: int = SEED,
) -> dict:
    x, y = load_training_frame(data_path)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    scale_pos_weight = compute_scale_pos_weight(y_train)
    pipeline = build_pipeline(scale_pos_weight=scale_pos_weight, random_state=random_state)
    param_grid = QUICK_PARAM_GRID if quick else DEFAULT_PARAM_GRID

    search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
        refit=True,
    )
    logger.info("Fitting GridSearchCV: grid=%s cv=%s train_rows=%s", param_grid, cv, len(x_train))
    search.fit(x_train, y_train)
    best_pipeline = search.best_estimator_

    y_proba = best_pipeline.predict_proba(x_test)[:, 1]
    y_pred = best_pipeline.predict(x_test)
    metrics = {
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "average_precision": float(average_precision_score(y_test, y_proba)),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
        "class_balance_train": {
            "good": int((y_train == 1).sum()),
            "bad": int((y_train == 0).sum()),
        },
        "best_params": search.best_params_,
        "best_cv_roc_auc": float(search.best_score_),
        "scale_pos_weight": scale_pos_weight,
        "classification_report": classification_report(
            y_test, y_pred, target_names=["bad", "good"], output_dict=True
        ),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    logger.info("Holdout ROC-AUC=%.4f AP=%.4f accuracy=%.4f", metrics["roc_auc"], metrics["average_precision"], metrics["accuracy"])

    save_pipeline(best_pipeline, model_path)
    save_json(metrics, metrics_path)
    save_json(
        {
            "data_path": str(data_path),
            "seed": random_state,
            "test_size": test_size,
            "cv": cv,
            "quick": quick,
            "param_grid": param_grid,
            "target": "Marker (good=1, bad=0). probability_default = 1 - P(good)",
        },
        config_path,
    )
    logger.info("Saved model to %s", model_path)
    return metrics


def main() -> None:
    args = parse_args()
    train(
        data_path=args.data,
        model_path=args.model_path,
        metrics_path=args.metrics_path,
        config_path=args.config_path,
        test_size=args.test_size,
        cv=args.cv,
        quick=args.quick,
    )


if __name__ == "__main__":
    main()
