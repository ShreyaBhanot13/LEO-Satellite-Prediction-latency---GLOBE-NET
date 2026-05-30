"""Phase 3 for the India-first workflow: train and compare India-native latency models."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs" / "india_model_dataset.csv"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

TARGET = "avg_lat_ms"
RANDOM_STATE = 42
TEST_SIZE = 0.2


def load_dataset() -> tuple[pd.DataFrame, pd.Series]:
    dataset = pd.read_csv(DATASET_PATH)
    X = dataset.drop(columns=[TARGET]).copy()
    y = dataset[TARGET].copy()
    X = X.astype(float)
    return X, y


def split_data(X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def log_transform_target(y_train: pd.Series, y_test: pd.Series) -> tuple[pd.Series, pd.Series, float]:
    shift_amount = -float(y_train.min()) + 1.0
    y_train_log = np.log(y_train + shift_amount)
    y_test_log = np.log(y_test + shift_amount)
    return y_train_log, y_test_log, shift_amount


def get_models() -> dict[str, object]:
    return {
        "RandomForest": RandomForestRegressor(
            n_estimators=300,
            max_depth=18,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "XGBoost": XGBRegressor(
            n_estimators=400,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbosity=0,
        ),
        "CatBoost": CatBoostRegressor(
            depth=8,
            iterations=350,
            learning_rate=0.08,
            subsample=0.85,
            random_state=RANDOM_STATE,
            verbose=0,
        ),
    }


def evaluate_model(model: object, X_test: pd.DataFrame, y_test: pd.Series, shift_amount: float) -> tuple[np.ndarray, dict[str, float]]:
    y_pred_log = model.predict(X_test)
    y_pred = np.exp(y_pred_log) - shift_amount
    metrics = {
        "r2": float(r2_score(y_test, y_pred)),
        "rmse_ms": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "mae_ms": float(mean_absolute_error(y_test, y_pred)),
    }
    return y_pred, metrics


def train_and_compare(X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> tuple[pd.DataFrame, dict[str, object]]:
    y_train_log, y_test_log, shift_amount = log_transform_target(y_train, y_test)
    _ = y_test_log

    results: list[dict[str, float | str]] = []
    trained_models: dict[str, object] = {}

    for model_name, model in get_models().items():
        model.fit(X_train, y_train_log)
        _, metrics = evaluate_model(model, X_test, y_test, shift_amount)
        results.append(
            {
                "model": model_name,
                "features": X_train.shape[1],
                **metrics,
            }
        )
        trained_models[model_name] = model

    results_df = pd.DataFrame(results).sort_values("r2", ascending=False).reset_index(drop=True)
    best_model_name = results_df.iloc[0]["model"]
    best_payload = {
        "name": best_model_name,
        "model": trained_models[best_model_name],
        "shift_amount": shift_amount,
        "features": list(X_train.columns),
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
    }
    return results_df, best_payload


def write_outputs(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    results_df: pd.DataFrame,
    best_payload: dict[str, object],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump((X_train, y_train), OUTPUT_DIR / "india_train_data.pkl")
    joblib.dump((X_test, y_test), OUTPUT_DIR / "india_test_data.pkl")
    joblib.dump(best_payload, OUTPUT_DIR / "india_best_model.pkl")
    results_df.to_csv(OUTPUT_DIR / "india_model_results.csv", index=False)

    best_row = results_df.iloc[0]
    report_lines = [
        "PHASE 3 REPORT: INDIA MODEL TRAINING",
        "=" * 80,
        f"Train rows: {len(X_train):,}",
        f"Test rows: {len(X_test):,}",
        f"Feature count: {X_train.shape[1]}",
        f"Target: {TARGET}",
        "",
        "Model comparison:",
    ]

    for _, row in results_df.iterrows():
        report_lines.append(
            f"- {row['model']}: R2={row['r2']:.4f}, RMSE={row['rmse_ms']:.4f} ms, MAE={row['mae_ms']:.4f} ms"
        )

    report_lines.extend(
        [
            "",
            "Best model:",
            f"- {best_row['model']}",
            f"- R2: {best_row['r2']:.4f}",
            f"- RMSE: {best_row['rmse_ms']:.4f} ms",
            f"- MAE: {best_row['mae_ms']:.4f} ms",
        ]
    )

    (REPORT_DIR / "phase3_india_model_training.txt").write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    X, y = load_dataset()
    X_train, X_test, y_train, y_test = split_data(X, y)
    results_df, best_payload = train_and_compare(X_train, X_test, y_train, y_test)
    write_outputs(X_train, X_test, y_train, y_test, results_df, best_payload)

    print("India Phase 3 model training complete.")
    print(results_df.to_string(index=False))
    print(f"Saved best model: {OUTPUT_DIR / 'india_best_model.pkl'}")


if __name__ == "__main__":
    main()