"""Train multiple classifiers to identify high-risk internet performance zones in India."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs" / "india_zone_risk_dataset.csv"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

RANDOM_STATE = 42
TEST_SIZE = 0.2
RISK_QUANTILES = [0.75, 0.80, 0.85]
CLASS_LABELS = ["normal_zone", "high_risk_zone"]
LABEL_SOURCE = "zone_p90_latency_ms"
EXCLUDE_COLUMNS = {
    "zone_mean_latency_ms",
    "zone_median_latency_ms",
    "zone_p90_latency_ms",
    "zone_latency_std_ms",
    "zone_high_latency_share",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=DATASET_PATH,
        help="Path to the zone-risk dataset CSV to train on.",
    )
    parser.add_argument(
        "--output-suffix",
        default="",
        help="Optional suffix appended to output artifact filenames.",
    )
    return parser.parse_args()


def load_dataset(dataset_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    dataset = pd.read_csv(dataset_path)
    feature_columns = [column for column in dataset.columns if column not in EXCLUDE_COLUMNS]
    X = dataset[feature_columns].copy().astype(float)
    y_source = dataset[LABEL_SOURCE].copy()
    return X, y_source


def split_data(X: pd.DataFrame, y_source: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(X, y_source, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def to_risk_target(y_source: pd.Series, cutoff: float) -> pd.Series:
    return (y_source >= cutoff).astype(int)


def get_models() -> dict[str, object]:
    return {
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=400,
            max_depth=18,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=RANDOM_STATE,
            class_weight="balanced_subsample",
        ),
        "ExtraTreesClassifier": ExtraTreesClassifier(
            n_estimators=500,
            max_depth=None,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=RANDOM_STATE,
            class_weight="balanced_subsample",
        ),
        "XGBoostClassifier": XGBClassifier(
            n_estimators=500,
            max_depth=7,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbosity=0,
        ),
        "CatBoostClassifier": CatBoostClassifier(
            depth=8,
            iterations=500,
            learning_rate=0.06,
            l2_leaf_reg=5,
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
        "high_risk_f1": float(f1_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "high_risk_precision": float(precision_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "high_risk_recall": float(recall_score(y_test, y_pred, pos_label=1, zero_division=0)),
    }
    return y_pred, metrics


def evaluate_quantile(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train_source: pd.Series,
    y_test_source: pd.Series,
    quantile_level: float,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, np.ndarray], pd.Series, pd.Series]:
    cutoff = float(y_train_source.quantile(quantile_level))
    y_train = to_risk_target(y_train_source, cutoff)
    y_test = to_risk_target(y_test_source, cutoff)
    scale_pos_weight = max(float((y_train == 0).sum()) / max((y_train == 1).sum(), 1), 1.0)

    results: list[dict[str, float | str]] = []
    trained_models: dict[str, object] = {}
    predictions: dict[str, np.ndarray] = {}

    for model_name, model in get_models().items():
        if model_name == "XGBoostClassifier":
            model.set_params(scale_pos_weight=scale_pos_weight)

        model.fit(X_train, y_train)
        y_pred, metrics = evaluate_model(model, X_test, y_test)
        results.append(
            {
                "risk_quantile": f"P{int(quantile_level * 100)}",
                "risk_cutoff_ms": cutoff,
                "positive_rate_train": float(y_train.mean()),
                "positive_rate_test": float(y_test.mean()),
                "model": model_name,
                "features": X_train.shape[1],
                **metrics,
            }
        )
        trained_models[model_name] = model
        predictions[model_name] = y_pred

    results_df = pd.DataFrame(results).sort_values(
        ["high_risk_f1", "balanced_accuracy", "accuracy"],
        ascending=False,
    ).reset_index(drop=True)
    best_model_name = str(results_df.iloc[0]["model"])
    payload = {
        "name": best_model_name,
        "model": trained_models[best_model_name],
        "features": list(X_train.columns),
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "target_type": "zone_level_high_risk_classification",
        "risk_quantile": f"P{int(quantile_level * 100)}",
        "risk_cutoff_ms": cutoff,
        "class_labels": CLASS_LABELS,
        "positive_rate_train": float(y_train.mean()),
        "positive_rate_test": float(y_test.mean()),
    }
    return results_df, payload, predictions, y_train, y_test


def write_outputs(
    all_results: pd.DataFrame,
    best_payload: dict[str, object],
    best_predictions: np.ndarray,
    y_test_source: pd.Series,
    y_test: pd.Series,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    output_suffix: str,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    suffix = output_suffix if not output_suffix or output_suffix.startswith("_") else f"_{output_suffix}"

    best_result = (
        all_results[
            (all_results["risk_quantile"] == best_payload["risk_quantile"])
            & (all_results["model"] == best_payload["name"])
        ]
        .iloc[0]
    )
    confusion = confusion_matrix(y_test, best_predictions, labels=[0, 1])
    confusion_df = pd.DataFrame(confusion, index=CLASS_LABELS, columns=CLASS_LABELS)
    class_report = classification_report(
        y_test,
        best_predictions,
        target_names=CLASS_LABELS,
        digits=4,
        zero_division=0,
    )

    all_results.to_csv(OUTPUT_DIR / f"india_zone_risk_model_results{suffix}.csv", index=False)
    confusion_df.to_csv(OUTPUT_DIR / f"india_zone_risk_confusion_matrix{suffix}.csv")
    joblib.dump(best_payload, OUTPUT_DIR / f"india_best_zone_risk_model{suffix}.pkl")
    joblib.dump((X_train, y_train), OUTPUT_DIR / f"india_zone_risk_train_data{suffix}.pkl")
    joblib.dump((X_test, y_test), OUTPUT_DIR / f"india_zone_risk_test_data{suffix}.pkl")

    prediction_frame = pd.DataFrame(
        {
            "zone_p90_latency_ms": y_test_source.values,
            "actual_label": pd.Series(y_test).map({0: CLASS_LABELS[0], 1: CLASS_LABELS[1]}).values,
            "predicted_label": pd.Series(best_predictions).map({0: CLASS_LABELS[0], 1: CLASS_LABELS[1]}).values,
        },
        index=X_test.index,
    )
    prediction_frame.to_csv(OUTPUT_DIR / f"india_zone_risk_predictions{suffix}.csv", index_label="row_index")

    report_lines = [
        "PHASE 8 REPORT: INDIA HIGH-RISK INTERNET PERFORMANCE ZONE CLASSIFICATION",
        "=" * 80,
        f"Train zones: {len(X_train):,}",
        f"Test zones: {len(X_test):,}",
        f"Feature count: {X_train.shape[1]}",
        f"Target type: {best_payload['target_type']}",
        f"Selected risk quantile: {best_payload['risk_quantile']}",
        f"Selected risk cutoff: {float(best_payload['risk_cutoff_ms']):.4f} ms (zone P90 latency)",
        f"Train positive rate: {float(best_payload['positive_rate_train']):.4f}",
        f"Test positive rate: {float(best_payload['positive_rate_test']):.4f}",
        "",
        "Model comparison across risk thresholds:",
    ]

    for risk_quantile, risk_frame in all_results.groupby("risk_quantile", sort=False):
        cutoff = float(risk_frame.iloc[0]["risk_cutoff_ms"])
        test_positive_rate = float(risk_frame.iloc[0]["positive_rate_test"])
        report_lines.append(f"- {risk_quantile} risk threshold ({cutoff:.4f} ms), test positive rate={test_positive_rate:.4f}")
        for _, row in risk_frame.iterrows():
            report_lines.append(
                f"  {row['model']}: accuracy={row['accuracy']:.4f}, balanced_accuracy={row['balanced_accuracy']:.4f}, macro_f1={row['macro_f1']:.4f}, high_risk_f1={row['high_risk_f1']:.4f}, precision={row['high_risk_precision']:.4f}, recall={row['high_risk_recall']:.4f}"
            )

    report_lines.extend(
        [
            "",
            "Best model:",
            f"- {best_payload['name']}",
            f"- Risk threshold: {best_payload['risk_quantile']}",
            f"- Accuracy: {best_result['accuracy']:.4f}",
            f"- Balanced accuracy: {best_result['balanced_accuracy']:.4f}",
            f"- Macro F1: {best_result['macro_f1']:.4f}",
            f"- High-risk F1: {best_result['high_risk_f1']:.4f}",
            f"- High-risk precision: {best_result['high_risk_precision']:.4f}",
            f"- High-risk recall: {best_result['high_risk_recall']:.4f}",
            "",
            "Best-model classification report:",
            class_report,
            "Confusion matrix:",
            confusion_df.to_string(),
        ]
    )

    (REPORT_DIR / f"phase8_india_zone_risk_modeling{suffix}.txt").write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    X, y_source = load_dataset(args.dataset_path)
    X_train, X_test, y_train_source, y_test_source = split_data(X, y_source)

    all_results_frames: list[pd.DataFrame] = []
    payloads: list[dict[str, object]] = []
    predictions_list: list[dict[str, np.ndarray]] = []
    targets_list: list[tuple[pd.Series, pd.Series]] = []

    for quantile_level in RISK_QUANTILES:
        results_df, payload, predictions, y_train, y_test = evaluate_quantile(
            X_train,
            X_test,
            y_train_source,
            y_test_source,
            quantile_level,
        )
        all_results_frames.append(results_df)
        payloads.append(payload)
        predictions_list.append(predictions)
        targets_list.append((y_train, y_test))

    all_results = pd.concat(all_results_frames, ignore_index=True)
    best_overall = all_results.sort_values(
        ["high_risk_f1", "balanced_accuracy", "accuracy"],
        ascending=False,
    ).iloc[0]
    best_index = next(
        index
        for index, payload in enumerate(payloads)
        if payload["risk_quantile"] == best_overall["risk_quantile"] and payload["name"] == best_overall["model"]
    )
    best_payload = payloads[best_index]
    best_predictions = predictions_list[best_index][best_payload["name"]]
    y_train, y_test = targets_list[best_index]

    write_outputs(all_results, best_payload, best_predictions, y_test_source, y_test, X_train, y_train, X_test, args.output_suffix)

    print("India zone-risk modeling complete.")
    print(f"Dataset path: {args.dataset_path}")
    print(all_results.to_string(index=False))
    suffix = args.output_suffix if not args.output_suffix or args.output_suffix.startswith("_") else f"_{args.output_suffix}"
    print(f"Saved best zone-risk model: {OUTPUT_DIR / f'india_best_zone_risk_model{suffix}.pkl'}")


if __name__ == "__main__":
    main()