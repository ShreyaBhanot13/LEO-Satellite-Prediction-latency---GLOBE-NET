"""Phase 4 for the India-first workflow: explain the saved India model with SHAP."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"
MODEL_PATH = OUTPUT_DIR / "india_best_model.pkl"
TEST_DATA_PATH = OUTPUT_DIR / "india_test_data.pkl"

MAX_SHAP_SAMPLES = 1000


def load_artifacts() -> tuple[dict[str, object], pd.DataFrame, pd.Series]:
    payload = joblib.load(MODEL_PATH)
    X_test, y_test = joblib.load(TEST_DATA_PATH)

    required = {"name", "model", "shift_amount", "features"}
    missing = required - set(payload)
    if missing:
        raise KeyError(f"India best model payload is missing keys: {sorted(missing)}")

    X_test = X_test.loc[:, payload["features"]].copy()
    return payload, X_test, y_test


def inverse_predict(payload: dict[str, object], X: pd.DataFrame) -> np.ndarray:
    prediction_log = payload["model"].predict(X)
    return np.exp(prediction_log) - float(payload["shift_amount"])


def evaluate(payload: dict[str, object], X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float | int | str]:
    y_pred = inverse_predict(payload, X_test)
    return {
        "model": str(payload["name"]),
        "test_rows": int(len(X_test)),
        "feature_count": int(X_test.shape[1]),
        "r2": float(r2_score(y_test, y_pred)),
        "rmse_ms": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "mae_ms": float(mean_absolute_error(y_test, y_pred)),
    }


def get_feature_family(feature_name: str) -> str:
    if feature_name.startswith("state_avg_") or feature_name.startswith("cell_") or feature_name.endswith("_vs_state_avg") or feature_name.endswith("_vs_cell_avg"):
        return "context"
    if feature_name in {
        "tests",
        "devices",
        "tests_per_device",
        "devices_per_test",
        "tile_density_proxy",
        "log_tile_density_proxy",
        "usage_pressure",
        "log_usage_pressure",
    }:
        return "usage"
    if feature_name.startswith("state_"):
        return "state"
    if feature_name.startswith("tile_"):
        return "geography"
    if feature_name.startswith("log_"):
        return "log_transforms"
    if feature_name in {
        "avg_d_kbps",
        "avg_u_kbps",
        "download_upload_ratio",
        "throughput_sum_kbps",
        "throughput_gap_kbps",
        "download_per_test",
        "upload_per_test",
        "download_per_device",
        "upload_per_device",
    }:
        return "throughput"
    return "other"


def run_shap(payload: dict[str, object], X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        import shap
    except ImportError as exc:
        raise ImportError("SHAP is required for Phase 4 explainability.") from exc

    sample_size = min(MAX_SHAP_SAMPLES, len(X_test))
    X_sample = X_test.sample(sample_size, random_state=42).copy()

    explainer = shap.TreeExplainer(payload["model"])
    shap_values = explainer.shap_values(X_sample)
    if isinstance(shap_values, list):
        shap_array = np.asarray(shap_values[0])
    else:
        shap_array = np.asarray(shap_values)

    global_importance = pd.DataFrame(
        {
            "feature": X_sample.columns,
            "mean_abs_shap": np.abs(shap_array).mean(axis=0),
            "feature_family": [get_feature_family(name) for name in X_sample.columns],
        }
    ).sort_values("mean_abs_shap", ascending=False, ignore_index=True)

    family_importance = (
        global_importance.groupby("feature_family", as_index=False)["mean_abs_shap"]
        .sum()
        .sort_values("mean_abs_shap", ascending=False, ignore_index=True)
    )

    representative_position = int(np.argmax(np.abs(shap_array).sum(axis=1)))
    representative_index = int(X_sample.index[representative_position])
    local_series = pd.Series(shap_array[representative_position], index=X_sample.columns, name="shap_value")
    local_explanation = (
        pd.DataFrame(
            {
                "feature": local_series.index,
                "feature_value": X_sample.iloc[representative_position].values,
                "shap_value": local_series.values,
                "abs_shap": np.abs(local_series.values),
                "feature_family": [get_feature_family(name) for name in local_series.index],
                "sample_index": representative_index,
            }
        )
        .sort_values("abs_shap", ascending=False, ignore_index=True)
    )

    return global_importance, family_importance, local_explanation


def write_outputs(
    metrics: dict[str, float | int | str],
    global_importance: pd.DataFrame,
    family_importance: pd.DataFrame,
    local_explanation: pd.DataFrame,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    global_importance.to_csv(OUTPUT_DIR / "india_shap_global_importance.csv", index=False)
    family_importance.to_csv(OUTPUT_DIR / "india_shap_family_importance.csv", index=False)
    local_explanation.to_csv(OUTPUT_DIR / "india_shap_local_explanation.csv", index=False)

    top_global = global_importance.head(10)
    top_family = family_importance.head(5)
    top_local = local_explanation.head(10)
    sample_index = int(local_explanation.iloc[0]["sample_index"])

    report_lines = [
        "PHASE 4 REPORT: INDIA MODEL SHAP EXPLAINABILITY",
        "=" * 80,
        f"Model explained: {metrics['model']}",
        f"Test rows available: {metrics['test_rows']:,}",
        f"Feature count: {metrics['feature_count']}",
        f"Validated test R2: {metrics['r2']:.4f}",
        f"Validated test RMSE: {metrics['rmse_ms']:.4f} ms",
        f"Validated test MAE: {metrics['mae_ms']:.4f} ms",
        "",
        "Interpretation note:",
        "- SHAP values below explain the model output in the transformed prediction space used during training.",
        "- They are still valid for ranking which features the model relies on most.",
        "",
        "Top global SHAP features:",
    ]

    for _, row in top_global.iterrows():
        report_lines.append(
            f"- {row['feature']} ({row['feature_family']}): mean|SHAP|={row['mean_abs_shap']:.6f}"
        )

    report_lines.extend(["", "Top feature families:"])
    for _, row in top_family.iterrows():
        report_lines.append(f"- {row['feature_family']}: total mean|SHAP|={row['mean_abs_shap']:.6f}")

    report_lines.extend(
        [
            "",
            f"Representative local explanation sample index: {sample_index}",
            "Top local contributors:",
        ]
    )
    for _, row in top_local.iterrows():
        report_lines.append(
            f"- {row['feature']}={row['feature_value']}: SHAP={row['shap_value']:.6f}"
        )

    (REPORT_DIR / "phase4_india_shap_explainability.txt").write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    payload, X_test, y_test = load_artifacts()
    metrics = evaluate(payload, X_test, y_test)
    global_importance, family_importance, local_explanation = run_shap(payload, X_test)
    write_outputs(metrics, global_importance, family_importance, local_explanation)

    print("India Phase 4 SHAP explainability complete.")
    print(pd.DataFrame([metrics]).to_string(index=False))
    print(global_importance.head(10).to_string(index=False))


if __name__ == "__main__":
    main()