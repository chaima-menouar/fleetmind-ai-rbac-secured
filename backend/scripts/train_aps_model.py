"""Train and evaluate the FleetMind APS failure classifier.

The script downloads the official UCI archive when --archive is not supplied,
uses only the supplied training split for fitting/calibration/threshold choice,
and evaluates exactly once on the official held-out test split.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

DATASET_URL = (
    "https://archive.ics.uci.edu/static/public/421/"
    "aps%2Bfailure%2Bat%2Bscania%2Btrucks.zip"
)
DATASET_SHA256 = "5504d0402f54faaf97ac0ca085a621645763f5cfea2eb29c592b057d43d4db89"
DATASET_DOI = "https://doi.org/10.24432/C51S51"
TRAIN_MEMBER = "aps_failure_training_set.csv"
TEST_MEMBER = "aps_failure_test_set.csv"
FALSE_POSITIVE_COST = 10
FALSE_NEGATIVE_COST = 500
RANDOM_STATE = 42

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = BACKEND_ROOT / ".data" / "aps-failure-scania.zip"
ARTIFACT_DIR = BACKEND_ROOT / "app" / "ml" / "artifacts"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_archive(path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".download")
        print(f"Downloading the official dataset to {path} ...")
        urllib.request.urlretrieve(DATASET_URL, temporary)
        temporary.replace(path)
    actual_hash = sha256(path)
    if actual_hash != DATASET_SHA256:
        raise ValueError(
            f"Dataset SHA-256 mismatch: expected {DATASET_SHA256}, received {actual_hash}"
        )
    return path


def read_split(archive: Path, member: str) -> tuple[pd.DataFrame, np.ndarray]:
    with zipfile.ZipFile(archive) as bundle, bundle.open(member) as source:
        frame = pd.read_csv(source, skiprows=20, na_values="na", low_memory=False)
    if "class" not in frame.columns:
        raise ValueError(f"The expected class column is missing from {member}.")
    labels = (frame.pop("class") == "pos").to_numpy(dtype=np.int8)
    features = frame.apply(pd.to_numeric, errors="coerce").astype(np.float32)
    return features, labels


def prediction_cost(labels: np.ndarray, predictions: np.ndarray) -> tuple[int, int, int]:
    false_positives = int(np.sum((predictions == 1) & (labels == 0)))
    false_negatives = int(np.sum((predictions == 0) & (labels == 1)))
    total = false_positives * FALSE_POSITIVE_COST + false_negatives * FALSE_NEGATIVE_COST
    return total, false_positives, false_negatives


def choose_threshold(labels: np.ndarray, scores: np.ndarray) -> tuple[float, int]:
    best_threshold = 0.5
    best_cost = sys.maxsize
    for threshold in np.linspace(0.001, 0.999, 999):
        predictions = (scores >= threshold).astype(np.int8)
        cost, _, _ = prediction_cost(labels, predictions)
        if cost < best_cost:
            best_threshold = float(threshold)
            best_cost = cost
    return best_threshold, best_cost


def serializable_features(row: pd.Series) -> dict[str, float | None]:
    return {
        name: None if pd.isna(value) else float(value)
        for name, value in row.items()
    }


def select_evaluation_samples(
    features: pd.DataFrame,
    labels: np.ndarray,
    predictions: np.ndarray,
) -> list[dict[str, Any]]:
    groups = [
        (np.flatnonzero((labels == 1) & (predictions == 1)), 4),
        (np.flatnonzero((labels == 1) & (predictions == 0)), 2),
        (np.flatnonzero((labels == 0) & (predictions == 1)), 2),
        (np.flatnonzero((labels == 0) & (predictions == 0)), 4),
    ]
    selected: list[dict[str, Any]] = []
    for indices, limit in groups:
        for index in indices[:limit]:
            selected.append(
                {
                    "sample_id": f"test-example-{len(selected) + 1:02d}",
                    "actual_label": "aps_failure" if labels[index] else "other_failure",
                    "features": serializable_features(features.iloc[index]),
                }
            )
    return selected


def train(archive: Path) -> dict[str, Any]:
    print("Reading official training and test splits ...")
    full_train, full_labels = read_split(archive, TRAIN_MEMBER)
    test_features, test_labels = read_split(archive, TEST_MEMBER)
    if list(full_train.columns) != list(test_features.columns):
        raise ValueError("Training and test feature columns do not match.")

    fit_features, holdout_features, fit_labels, holdout_labels = train_test_split(
        full_train,
        full_labels,
        test_size=0.30,
        stratify=full_labels,
        random_state=RANDOM_STATE,
    )
    calibration_features, threshold_features, calibration_labels, threshold_labels = (
        train_test_split(
            holdout_features,
            holdout_labels,
            test_size=0.50,
            stratify=holdout_labels,
            random_state=RANDOM_STATE,
        )
    )

    print("Fitting class-balanced histogram gradient boosting model ...")
    estimator = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=260,
        max_leaf_nodes=31,
        min_samples_leaf=24,
        l2_regularization=0.15,
        class_weight="balanced",
        early_stopping=True,
        validation_fraction=0.12,
        random_state=RANDOM_STATE,
    )
    estimator.fit(fit_features.to_numpy(), fit_labels)

    print("Calibrating model scores and choosing a cost-sensitive threshold ...")
    calibrated_model = CalibratedClassifierCV(
        FrozenEstimator(estimator),
        method="sigmoid",
    )
    calibrated_model.fit(calibration_features.to_numpy(), calibration_labels)
    validation_scores = calibrated_model.predict_proba(threshold_features.to_numpy())[:, 1]
    threshold, validation_cost = choose_threshold(threshold_labels, validation_scores)

    print("Evaluating once on the official test split ...")
    test_scores = calibrated_model.predict_proba(test_features.to_numpy())[:, 1]
    test_predictions = (test_scores >= threshold).astype(np.int8)
    tn, fp, fn, tp = confusion_matrix(test_labels, test_predictions, labels=[0, 1]).ravel()
    official_cost, _, _ = prediction_cost(test_labels, test_predictions)
    all_negative_cost = int(np.sum(test_labels == 1)) * FALSE_NEGATIVE_COST

    metadata: dict[str, Any] = {
        "model_version": "aps-hgb-1.0.0",
        "trained_at": datetime.now(UTC).isoformat(),
        "algorithm": "Calibrated HistGradientBoostingClassifier",
        "dataset": {
            "name": "APS Failure at Scania Trucks",
            "source": DATASET_URL,
            "doi": DATASET_DOI,
            "archive_sha256": DATASET_SHA256,
            "license_catalog": "CC BY 4.0",
            "train_rows": int(len(full_train)),
            "test_rows": int(len(test_features)),
            "features": int(full_train.shape[1]),
            "train_positive_rows": int(np.sum(full_labels == 1)),
            "test_positive_rows": int(np.sum(test_labels == 1)),
        },
        "training": {
            "random_state": RANDOM_STATE,
            "fit_rows": int(len(fit_features)),
            "calibration_rows": int(len(calibration_features)),
            "threshold_rows": int(len(threshold_features)),
            "decision_threshold": threshold,
            "validation_cost": validation_cost,
            "false_positive_cost": FALSE_POSITIVE_COST,
            "false_negative_cost": FALSE_NEGATIVE_COST,
        },
        "metrics": {
            "precision": float(precision_score(test_labels, test_predictions, zero_division=0)),
            "recall": float(recall_score(test_labels, test_predictions, zero_division=0)),
            "f1": float(f1_score(test_labels, test_predictions, zero_division=0)),
            "balanced_accuracy": float(balanced_accuracy_score(test_labels, test_predictions)),
            "roc_auc": float(roc_auc_score(test_labels, test_scores)),
            "average_precision": float(average_precision_score(test_labels, test_scores)),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
            "official_cost": official_cost,
            "all_negative_baseline_cost": all_negative_cost,
            "cost_reduction_percent": float(
                100 * (all_negative_cost - official_cost) / all_negative_cost
            ),
        },
        "runtime": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        "limitations": [
            "The 170 operational features are anonymized by the dataset owner.",
            "The score estimates APS-related failure risk, not general vehicle failure.",
            "Performance is measured on the supplied historical test split.",
            "The model is a portfolio demonstration and not approved for safety decisions.",
        ],
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    model_path = ARTIFACT_DIR / "aps_failure_model.joblib"
    joblib.dump(
        {
            "model": calibrated_model,
            "feature_names": list(full_train.columns),
            "threshold": threshold,
            "model_version": metadata["model_version"],
        },
        model_path,
        compress=3,
    )
    metadata["artifact_sha256"] = sha256(model_path)
    samples = select_evaluation_samples(test_features, test_labels, test_predictions)
    (ARTIFACT_DIR / "evaluation_samples.json").write_text(
        json.dumps(samples, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    (ARTIFACT_DIR / "metadata.json").write_text(
        json.dumps(metadata, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive",
        type=Path,
        default=DEFAULT_ARCHIVE,
        help="Path to the official UCI zip archive; downloaded when missing.",
    )
    args = parser.parse_args()
    archive = ensure_archive(args.archive.expanduser().resolve())
    metadata = train(archive)
    print(json.dumps(metadata["metrics"], indent=2))
    print(f"Artifacts written to {ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
