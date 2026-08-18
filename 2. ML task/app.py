"""FastAPI service that scores credit applications from a CSV upload."""

from __future__ import annotations

import io
from contextlib import asynccontextmanager
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.data import DataValidationError, prepare_features
from src.log import logger
from src.model_io import ModelNotFoundError, load_pipeline
from src.paths import MODEL_PATH
from src.predict import predict_frame

CONTENT_TYPE_CSV = {"text/csv", "application/vnd.ms-excel", "application/octet-stream", ""}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.pipeline = load_pipeline(MODEL_PATH)
        logger.info("Loaded pipeline from %s", MODEL_PATH)
    except ModelNotFoundError:
        app.state.pipeline = None
        logger.warning("Model artifact is missing; /predict will return 503")
    yield


app = FastAPI(
    title="Credit default model API",
    description="Upload a CSV of applications and receive default-risk scores.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


def _read_csv(upload: UploadFile, raw: bytes) -> pd.DataFrame:
    filename = (upload.filename or "").lower()
    content_type = (upload.content_type or "").split(";")[0].strip().lower()
    if filename and not filename.endswith(".csv") and content_type not in CONTENT_TYPE_CSV:
        raise HTTPException(status_code=400, detail="File must be a CSV")
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from exc
    try:
        frame = pd.read_csv(io.StringIO(text))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not parse CSV") from exc
    if frame.empty:
        raise HTTPException(status_code=400, detail="CSV has no data rows")
    return frame


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict[str, Any]:
    if getattr(app.state, "pipeline", None) is None:
        raise HTTPException(status_code=503, detail="Model is not available")

    logger.info("predict request filename=%s", file.filename)
    raw = await file.read()
    frame = _read_csv(file, raw)
    try:
        features = prepare_features(frame)
    except DataValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    predictions = predict_frame(app.state.pipeline, features)
    return {"n_rows": len(predictions), "predictions": predictions}


@app.get("/health")
@app.get("/")
async def health() -> dict[str, Any]:
    ready = getattr(app.state, "pipeline", None) is not None
    return {
        "message": "XGBoost Model API is running",
        "model_loaded": ready,
        "status": "ok" if ready else "model_missing",
    }
