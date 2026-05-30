"""Phase 3B for the India-first workflow: classify latency bands instead of regressing raw latency."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs" / "india_model_dataset.csv"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

TARGET = "avg_lat_ms"
RANDOM_STATE = 42
TEST_SIZE = 0.2
CLASS_LABELS = ["low_latency", "medium_latency", "high_latency"]


def load_dataset() -> tuple[pd.DataFrame, pd.Series]:
    dataset = pd.read_csv(DATASET_PATH)
    X = dataset.drop(columns=[TARGET]).copy().astype(float)
    y = dataset[TARGET].copy()
    return X, y


def split_data(X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def derive_thresholds(y_train: pd.Series) -> tuple[float, float]:
    low_high_cutoffs = y_train.quantile([1 / 3, 2 / 3]).to_list()
    return float(low_high_cutoffs[0]), float(low_high_cutoffs[1])


def to_latency_bands(y: pd.Series, low_cutoff: float, high_cutoff: float) -> pd.Series:
    bins = [-np.inf, low_cutoff, high_cutoff, np.inf]
    return pd.cut(y, bins=bins, labels=[0, 1, 2], include_lowest=True).astype(int)


def get_models() -> dict[str, object]:
    return {
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=300,
            max_depth=20,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=RANDOM_STATE,
            class_weight="balanced_subsample",
        ),
        "XGBoostClassifier": XGBClassifier(
            n_estimators=400,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbosity=0,
        ),
        "CatBoostClassifier": CatBoostClassifier(
            depth=8,
            iterations=350,
            learning_rate=0.08,
            random_state=RANDOM_STATE,
            loss_function="MultiClass",
            verbose=0,
        ),
    }


def evaluate_model(model: object, X_test: pd.DataFrame, y_test: pd.Series) -> tuple[np.ndarray, dict[str, float]]:
    y_pred = model.predict(X_test)
    y_pred = np.asarray(y_pred).reshape(-1).astype(int)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro")),
        "weighted_f1": float(f1_score(y_test, y_pred, average="weighted")),
    }
    return y_pred, metrics


def train_and_compare(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train_band: pd.Series,
    y_test_band: pd.Series,
    thresholds: tuple[float, float],
) -> tuple[pd.DataFrame, dict[str, object], dict[str, np.ndarray]]:
    results: list[dict[str, float | str]] = []
    trained_models: dict[str, object] = {}
    predictions: dict[str, np.ndarray] = {}

    for model_name, model in get_models().items():
        model.fit(X_train, y_train_band)
        y_pred, metrics = evaluate_model(model, X_test, y_test_band)
        results.append(
            {
                "model": model_name,
                "features": X_train.shape[1],
                **metrics,
            }
        )
        trained_models[model_name] = model
        predictions[model_name] = y_pred

    results_df = pd.DataFrame(results).sort_values(["macro_f1", "accuracy"], ascending=False).reset_index(drop=True)
    best_model_name = str(results_df.iloc[0]["model"])
    best_payload = {
        "name": best_model_name,
        "model": trained_models[best_model_name],
        "features": list(X_train.columns),
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "target_type": "three_band_latency_classification",
        "class_labels": CLASS_LABELS,
        "thresholds_ms": {
            "low_cutoff": thresholds[0],
            "high_cutoff": thresholds[1],
        },
    }
    return results_df, best_payload, predictions


def band_distribution(y_band: pd.Series) -> dict[str, int]:
    counts = y_band.value_counts().sort_index()
    return {CLASS_LABELS[index]: int(counts.get(index, 0)) for index in range(len(CLASS_LABELS))}


def write_outputs(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train_raw: pd.Series,
    y_test_raw: pd.Series,
    y_train_band: pd.Series,
    y_test_band: pd.Series,
    results_df: pd.DataFrame,
    best_payload: dict[str, object],
    predictions: dict[str, np.ndarray],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    best_name = str(best_payload["name"])
    best_predictions = predictions[best_name]
    report = classification_report(
        y_test_band,
        best_predictions,
        target_names=CLASS_LABELS,
        digits=4,
        zero_division=0,
    )
    matrix = confusion_matrix(y_test_band, best_predictions, labels=[0, 1, 2])
    confusion_df = pd.DataFrame(matrix, index=CLASS_LABELS, columns=CLASS_LABELS)

    comparison_path = OUTPUT_DIR / "india_latency_classifier_results.csv"
    confusion_path = OUTPUT_DIR / "india_latency_classifier_confusion_matrix.csv"
    predictions_path = OUTPUT_DIR / "india_latency_classifier_predictions.csv"
    classifier_path = OUTPUT_DIR / "india_best_latency_classifier.pkl"

    results_df.to_csv(comparison_path, index=False)
    confusion_df.to_csv(confusion_path)
    joblib.dump((X_train, y_train_band), OUTPUT_DIR / "india_classification_train_data.pkl")
    joblib.dump((X_test, y_test_band), OUTPUT_DIR / "india_classification_test_data.pkl")
    joblib.dump(best_payload, classifier_path)

    prediction_frame = pd.DataFrame(
        {
            "actual_latency_ms": y_test_raw.values,
            "actual_band": pd.Series(y_test_band).map(dict(enumerate(CLASS_LABELS))).values,
            "predicted_band": pd.Series(best_predictions).map(dict(enumerate(CLASS_LABELS))).values,
        },
        index=X_test.index,
    )
    prediction_frame.to_csv(predictions_path, index_label="row_index")

    best_row = results_df.iloc[0]
    low_cutoff = float(best_payload["thresholds_ms"]["low_cutoff"])
    high_cutoff = float(best_payload["thresholds_ms"]["high_cutoff"])
    report_lines = [
        "PHASE 3B REPORT: INDIA LATENCY BAND CLASSIFICATION",
        "=" * 80,
        f"Train rows: {len(X_train):,}",
        f"Test rows: {len(X_test):,}",
        f"Feature count: {X_train.shape[1]}",
        f"Target type: {best_payload['target_type']}",
        f"Low/medium cutoff: <= {low_cutoff:.4f} ms",
        f"Medium/high cutoff: > {high_cutoff:.4f} ms",
        "",
        f"Train class distribution: {band_distribution(y_train_band)}",
        f"Test class distribution: {band_distribution(y_test_band)}",
        "",
        "Model comparison:",
    ]

    for _, row in results_df.iterrows():
        report_lines.append(
            f"- {row['model']}: accuracy={row['accuracy']:.4f}, balanced_accuracy={row['balanced_accuracy']:.4f}, macro_f1={row['macro_f1']:.4f}, weighted_f1={row['weighted_f1']:.4f}"
        )

    report_lines.extend(
        [
            "",
            "Best model:",
            f"- {best_row['model']}",
            f"- Accuracy: {best_row['accuracy']:.4f}",
            f"- Balanced accuracy: {best_row['balanced_accuracy']:.4f}",
            f"- Macro F1: {best_row['macro_f1']:.4f}",
            f"- Weighted F1: {best_row['weighted_f1']:.4f}",
            "",
            "Best-model classification report:",
            report,
            "Confusion matrix:",
            confusion_df.to_string(),
        ]
    )

    (REPORT_DIR / "phase3b_india_latency_classification.txt").write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    X, y = load_dataset()
    X_train, X_test, y_train, y_test = split_data(X, y)
    low_cutoff, high_cutoff = derive_thresholds(y_train)
    y_train_band = to_latency_bands(y_train, low_cutoff, high_cutoff)
    y_test_band = to_latency_bands(y_test, low_cutoff, high_cutoff)

    results_df, best_payload, predictions = train_and_compare(
        X_train,
        X_test,
        y_train_band,
        y_test_band,
        (low_cutoff, high_cutoff),
    )
    write_outputs(X_train, X_test, y_train, y_test, y_train_band, y_test_band, results_df, best_payload, predictions)

    print("India Phase 3B latency classification complete.")
    print(results_df.to_string(index=False))
    print(f"Saved best classifier: {OUTPUT_DIR / 'india_best_latency_classifier.pkl'}")


if __name__ == "__main__":
    main()