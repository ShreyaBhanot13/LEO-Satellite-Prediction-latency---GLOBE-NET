"""Phase 3C for the India-first workflow: classify high-latency risk with binary targets."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs" / "india_model_dataset.csv"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

TARGET = "avg_lat_ms"
RANDOM_STATE = 42
TEST_SIZE = 0.2
THRESHOLD_LEVELS = [0.90, 0.95]
CLASS_LABELS = ["normal_latency", "high_latency"]


def load_dataset() -> tuple[pd.DataFrame, pd.Series]:
    dataset = pd.read_csv(DATASET_PATH)
    X = dataset.drop(columns=[TARGET]).copy().astype(float)
    y = dataset[TARGET].copy()
    return X, y


def split_data(X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def to_high_latency_target(y: pd.Series, cutoff: float) -> pd.Series:
    return (y >= cutoff).astype(int)


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
            objective="binary:logistic",
            eval_metric="logloss",
            scale_pos_weight=9,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbosity=0,
        ),
        "CatBoostClassifier": CatBoostClassifier(
            depth=8,
            iterations=350,
            learning_rate=0.08,
            random_state=RANDOM_STATE,
            loss_function="Logloss",
            verbose=0,
            auto_class_weights="Balanced",
        ),
    }


def evaluate_model(model: object, X_test: pd.DataFrame, y_test: pd.Series) -> tuple[np.ndarray, dict[str, float]]:
    y_pred = np.asarray(model.predict(X_test)).reshape(-1).astype(int)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "high_latency_f1": float(f1_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "high_latency_precision": float(precision_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "high_latency_recall": float(recall_score(y_test, y_pred, pos_label=1, zero_division=0)),
    }
    return y_pred, metrics


def evaluate_threshold(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train_raw: pd.Series,
    y_test_raw: pd.Series,
    quantile_level: float,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, np.ndarray], pd.Series, pd.Series]:
    cutoff = float(y_train_raw.quantile(quantile_level))
    y_train_target = to_high_latency_target(y_train_raw, cutoff)
    y_test_target = to_high_latency_target(y_test_raw, cutoff)

    scale_pos_weight = max(float((y_train_target == 0).sum()) / max((y_train_target == 1).sum(), 1), 1.0)

    results: list[dict[str, float | str]] = []
    trained_models: dict[str, object] = {}
    predictions: dict[str, np.ndarray] = {}

    for model_name, model in get_models().items():
        if model_name == "XGBoostClassifier":
            model.set_params(scale_pos_weight=scale_pos_weight)

        model.fit(X_train, y_train_target)
        y_pred, metrics = evaluate_model(model, X_test, y_test_target)
        results.append(
            {
                "threshold_name": f"P{int(quantile_level * 100)}",
                "threshold_ms": cutoff,
                "positive_rate_train": float(y_train_target.mean()),
                "positive_rate_test": float(y_test_target.mean()),
                "model": model_name,
                "features": X_train.shape[1],
                **metrics,
            }
        )
        trained_models[model_name] = model
        predictions[model_name] = y_pred

    results_df = pd.DataFrame(results).sort_values(
        ["high_latency_f1", "balanced_accuracy", "accuracy"],
        ascending=False,
    ).reset_index(drop=True)
    best_model_name = str(results_df.iloc[0]["model"])
    payload = {
        "name": best_model_name,
        "model": trained_models[best_model_name],
        "features": list(X_train.columns),
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "target_type": "binary_high_latency_classification",
        "threshold_name": f"P{int(quantile_level * 100)}",
        "threshold_ms": cutoff,
        "class_labels": CLASS_LABELS,
        "positive_rate_train": float(y_train_target.mean()),
        "positive_rate_test": float(y_test_target.mean()),
    }
    return results_df, payload, predictions, y_train_target, y_test_target


def write_outputs(
    all_results: pd.DataFrame,
    best_payload: dict[str, object],
    best_predictions: np.ndarray,
    y_test_raw: pd.Series,
    y_test_target: pd.Series,
    X_train: pd.DataFrame,
    y_train_target: pd.Series,
    X_test: pd.DataFrame,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    confusion = confusion_matrix(y_test_target, best_predictions, labels=[0, 1])
    confusion_df = pd.DataFrame(confusion, index=CLASS_LABELS, columns=CLASS_LABELS)
    class_report = classification_report(
        y_test_target,
        best_predictions,
        target_names=CLASS_LABELS,
        digits=4,
        zero_division=0,
    )

    all_results.to_csv(OUTPUT_DIR / "india_high_latency_classifier_results.csv", index=False)
    confusion_df.to_csv(OUTPUT_DIR / "india_high_latency_confusion_matrix.csv")
    joblib.dump(best_payload, OUTPUT_DIR / "india_best_high_latency_classifier.pkl")
    joblib.dump((X_train, y_train_target), OUTPUT_DIR / "india_high_latency_train_data.pkl")
    joblib.dump((X_test, y_test_target), OUTPUT_DIR / "india_high_latency_test_data.pkl")

    prediction_frame = pd.DataFrame(
        {
            "actual_latency_ms": y_test_raw.values,
            "actual_label": pd.Series(y_test_target).map({0: CLASS_LABELS[0], 1: CLASS_LABELS[1]}).values,
            "predicted_label": pd.Series(best_predictions).map({0: CLASS_LABELS[0], 1: CLASS_LABELS[1]}).values,
        },
        index=X_test.index,
    )
    prediction_frame.to_csv(OUTPUT_DIR / "india_high_latency_predictions.csv", index_label="row_index")

    best_row = (
        all_results[
            (all_results["threshold_name"] == best_payload["threshold_name"])
            & (all_results["model"] == best_payload["name"])
        ]
        .iloc[0]
    )
    report_lines = [
        "PHASE 3C REPORT: INDIA HIGH-LATENCY BINARY CLASSIFICATION",
        "=" * 80,
        f"Train rows: {len(X_train):,}",
        f"Test rows: {len(X_test):,}",
        f"Feature count: {X_train.shape[1]}",
        f"Target type: {best_payload['target_type']}",
        f"Selected threshold: {best_payload['threshold_name']} ({float(best_payload['threshold_ms']):.4f} ms)",
        f"Train positive rate: {float(best_payload['positive_rate_train']):.4f}",
        f"Test positive rate: {float(best_payload['positive_rate_test']):.4f}",
        "",
        "Model comparison across thresholds:",
    ]

    for threshold_name, threshold_frame in all_results.groupby("threshold_name", sort=False):
        threshold_ms = float(threshold_frame.iloc[0]["threshold_ms"])
        positive_rate = float(threshold_frame.iloc[0]["positive_rate_test"])
        report_lines.append(f"- {threshold_name} threshold ({threshold_ms:.4f} ms), test positive rate={positive_rate:.4f}")
        for _, row in threshold_frame.iterrows():
            report_lines.append(
                f"  {row['model']}: accuracy={row['accuracy']:.4f}, balanced_accuracy={row['balanced_accuracy']:.4f}, macro_f1={row['macro_f1']:.4f}, high_latency_f1={row['high_latency_f1']:.4f}, precision={row['high_latency_precision']:.4f}, recall={row['high_latency_recall']:.4f}"
            )

    report_lines.extend(
        [
            "",
            "Best model:",
            f"- {best_payload['name']}",
            f"- Threshold: {best_payload['threshold_name']}",
            f"- Accuracy: {best_row['accuracy']:.4f}",
            f"- Balanced accuracy: {best_row['balanced_accuracy']:.4f}",
            f"- Macro F1: {best_row['macro_f1']:.4f}",
            f"- High-latency F1: {best_row['high_latency_f1']:.4f}",
            f"- High-latency precision: {best_row['high_latency_precision']:.4f}",
            f"- High-latency recall: {best_row['high_latency_recall']:.4f}",
            "",
            "Best-model classification report:",
            class_report,
            "Confusion matrix:",
            confusion_df.to_string(),
        ]
    )

    (REPORT_DIR / "phase3c_india_high_latency_classification.txt").write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    X, y = load_dataset()
    X_train, X_test, y_train_raw, y_test_raw = split_data(X, y)

    threshold_results: list[pd.DataFrame] = []
    threshold_payloads: list[dict[str, object]] = []
    threshold_predictions: list[dict[str, np.ndarray]] = []
    threshold_targets: list[tuple[pd.Series, pd.Series]] = []

    for quantile_level in THRESHOLD_LEVELS:
        results_df, payload, predictions, y_train_target, y_test_target = evaluate_threshold(
            X_train,
            X_test,
            y_train_raw,
            y_test_raw,
            quantile_level,
        )
        threshold_results.append(results_df)
        threshold_payloads.append(payload)
        threshold_predictions.append(predictions)
        threshold_targets.append((y_train_target, y_test_target))

    all_results = pd.concat(threshold_results, ignore_index=True)
    best_overall_row = all_results.sort_values(
        ["high_latency_f1", "balanced_accuracy", "accuracy"],
        ascending=False,
    ).iloc[0]

    best_index = next(
        index
        for index, payload in enumerate(threshold_payloads)
        if payload["threshold_name"] == best_overall_row["threshold_name"] and payload["name"] == best_overall_row["model"]
    )

    best_payload = threshold_payloads[best_index]
    best_predictions = threshold_predictions[best_index][best_payload["name"]]
    y_train_target, y_test_target = threshold_targets[best_index]

    write_outputs(
        all_results,
        best_payload,
        best_predictions,
        y_test_raw,
        y_test_target,
        X_train,
        y_train_target,
        X_test,
    )

    print("India Phase 3C high-latency classification complete.")
    print(all_results.to_string(index=False))
    print(f"Saved best classifier: {OUTPUT_DIR / 'india_best_high_latency_classifier.pkl'}")


if __name__ == "__main__":
    main()