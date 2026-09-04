"""Load the trusted bundled APS model and run reproducible demo predictions."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "aps_failure_model.joblib"
METADATA_PATH = ARTIFACT_DIR / "metadata.json"
SAMPLES_PATH = ARTIFACT_DIR / "evaluation_samples.json"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=1)
def load_artifacts() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Load only artifacts that are built and shipped with this repository."""
    if not all(path.is_file() for path in (MODEL_PATH, METADATA_PATH, SAMPLES_PATH)):
        raise FileNotFoundError("The APS model artifacts are not installed.")

    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    if file_sha256(MODEL_PATH) != metadata.get("artifact_sha256"):
        raise RuntimeError("The bundled APS model failed its integrity check.")
    bundle = joblib.load(MODEL_PATH)
    samples = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    return bundle, metadata, samples


def get_model_card() -> dict[str, Any]:
    _, metadata, _ = load_artifacts()
    return metadata


def list_evaluation_samples() -> list[dict[str, str]]:
    _, _, samples = load_artifacts()
    return [{"sample_id": str(sample["sample_id"])} for sample in samples]


def predict_evaluation_sample(sample_id: str) -> dict[str, Any]:
    bundle, _, samples = load_artifacts()
    sample = next((item for item in samples if item["sample_id"] == sample_id), None)
    if sample is None:
        raise KeyError(sample_id)

    feature_names = bundle["feature_names"]
    row = np.asarray(
        [[np.nan if sample["features"].get(name) is None else sample["features"][name]
          for name in feature_names]],
        dtype=np.float32,
    )
    score = float(bundle["model"].predict_proba(row)[0, 1])
    threshold = float(bundle["threshold"])
    predicted_label = "aps_failure" if score >= threshold else "other_failure"
    actual_label = str(sample["actual_label"])
    if score >= threshold:
        risk_level = "high"
    elif score >= threshold / 2:
        risk_level = "watch"
    else:
        risk_level = "low"

    return {
        "sample_id": sample_id,
        "aps_failure_score": score,
        "decision_threshold": threshold,
        "predicted_label": predicted_label,
        "actual_label": actual_label,
        "matches_actual": predicted_label == actual_label,
        "risk_level": risk_level,
        "model_version": str(bundle["model_version"]),
    }
