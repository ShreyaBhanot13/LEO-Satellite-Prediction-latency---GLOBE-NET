"""Tune CatBoost only for the India zone-risk classification task."""

from __future__ import annotations

import itertools
from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs" / "india_zone_risk_dataset.csv"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

RANDOM_STATE = 42
TEST_SIZE = 0.2
RISK_QUANTILE = 0.75
EXCLUDE_COLUMNS = {
    "zone_mean_latency_ms",
    "zone_median_latency_ms",
    "zone_p90_latency_ms",
    "zone_latency_std_ms",
    "zone_high_latency_share",
}


def load_dataset() -> tuple[pd.DataFrame, pd.Series]:
    dataset = pd.read_csv(DATASET_PATH)
    feature_columns = [column for column in dataset.columns if column not in EXCLUDE_COLUMNS]
    X = dataset[feature_columns].copy().astype(float)
    y_source = dataset["zone_p90_latency_ms"].copy()
    return X, y_source


def evaluate_params(X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for depth, iterations, learning_rate, l2_leaf_reg in itertools.product(
        [6, 8],
        [300, 400, 500],
        [0.04, 0.06],
        [3, 5],
    ):
        model = CatBoostClassifier(
            depth=depth,
            iterations=iterations,
            learning_rate=learning_rate,
            l2_leaf_reg=l2_leaf_reg,
            random_state=RANDOM_STATE,
            loss_function="Logloss",
            verbose=0,
            auto_class_weights="Balanced",
        )
        model.fit(X_train, y_train)
        y_pred = pd.Series(model.predict(X_test).reshape(-1), index=y_test.index).astype(int)
        rows.append(
            {
                "depth": depth,
                "iterations": iterations,
                "learning_rate": learning_rate,
                "l2_leaf_reg": l2_leaf_reg,
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
                "macro_f1": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
                "high_risk_f1": float(f1_score(y_test, y_pred, pos_label=1, zero_division=0)),
                "precision": float(precision_score(y_test, y_pred, pos_label=1, zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, pos_label=1, zero_division=0)),
            }
        )
    return pd.DataFrame(rows).sort_values(["high_risk_f1", "balanced_accuracy", "accuracy"], ascending=False).reset_index(drop=True)


def main() -> None:
    X, y_source = load_dataset()
    X_train, X_test, y_train_source, y_test_source = train_test_split(X, y_source, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    cutoff = float(y_train_source.quantile(RISK_QUANTILE))
    y_train = (y_train_source >= cutoff).astype(int)
    y_test = (y_test_source >= cutoff).astype(int)

    results = evaluate_params(X_train, X_test, y_train, y_test)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_DIR / "india_zone_risk_catboost_tuning.csv", index=False)

    top = results.head(10)
    report_lines = [
        "PHASE 8A REPORT: CATBOOST TUNING ON CLEANED ZONE-RISK DATASET",
        "=" * 80,
        f"Dataset rows: {len(X):,}",
        f"Train rows: {len(X_train):,}",
        f"Test rows: {len(X_test):,}",
        f"Feature count: {X_train.shape[1]}",
        f"Risk threshold: P75 ({cutoff:.4f} ms)",
        "",
        "Top 10 parameter sets:",
    ]
    for _, row in top.iterrows():
        report_lines.append(
            f"- depth={int(row['depth'])}, iterations={int(row['iterations'])}, learning_rate={row['learning_rate']:.2f}, l2_leaf_reg={int(row['l2_leaf_reg'])}: accuracy={row['accuracy']:.4f}, balanced_accuracy={row['balanced_accuracy']:.4f}, macro_f1={row['macro_f1']:.4f}, high_risk_f1={row['high_risk_f1']:.4f}, precision={row['precision']:.4f}, recall={row['recall']:.4f}"
        )

    (REPORT_DIR / "phase8a_catboost_tuning.txt").write_text("\n".join(report_lines), encoding="utf-8")
    print(top.to_string(index=False))


if __name__ == "__main__":
    main()
