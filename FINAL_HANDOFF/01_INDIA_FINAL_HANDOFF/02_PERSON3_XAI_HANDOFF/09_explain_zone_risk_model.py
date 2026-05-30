"""Explain the final India high-risk zone classifier with SHAP."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, precision_score, recall_score


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"
MODEL_PATH = OUTPUT_DIR / "india_best_zone_risk_model.pkl"
TEST_DATA_PATH = OUTPUT_DIR / "india_zone_risk_test_data.pkl"

MAX_SHAP_SAMPLES = 1000


def load_artifacts() -> tuple[dict[str, object], pd.DataFrame, pd.Series]:
    payload = joblib.load(MODEL_PATH)
    X_test, y_test = joblib.load(TEST_DATA_PATH)

    required = {
        "name",
        "model",
        "features",
        "risk_quantile",
        "risk_cutoff_ms",
        "class_labels",
        "target_type",
    }
    missing = required - set(payload)
    if missing:
        raise KeyError(f"Zone-risk payload is missing keys: {sorted(missing)}")

    X_test = X_test.loc[:, payload["features"]].copy()
    return payload, X_test, y_test


def evaluate(payload: dict[str, object], X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float | int | str]:
    model = payload["model"]
    y_pred = np.asarray(model.predict(X_test)).reshape(-1).astype(int)
    return {
        "model": str(payload["name"]),
        "risk_quantile": str(payload["risk_quantile"]),
        "risk_cutoff_ms": float(payload["risk_cutoff_ms"]),
        "test_rows": int(len(X_test)),
        "feature_count": int(X_test.shape[1]),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "high_risk_f1": float(f1_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "high_risk_precision": float(precision_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "high_risk_recall": float(recall_score(y_test, y_pred, pos_label=1, zero_division=0)),
    }


def get_feature_family(feature_name: str) -> str:
    if feature_name.startswith("state_zone_avg_") or feature_name.endswith("_vs_state_avg"):
        return "context"
    if feature_name.startswith("state_"):
        return "state"
    if feature_name.startswith("tile_") or feature_name.startswith("zone_tile_"):
        return "geography"
    if feature_name.startswith("log_"):
        return "log_transforms"
    if feature_name in {
        "zone_mean_tests",
        "zone_median_tests",
        "zone_std_tests",
        "zone_mean_devices",
        "zone_median_devices",
        "zone_std_devices",
        "zone_density_proxy",
        "zone_usage_pressure",
        "zone_mean_tests_per_device",
        "zone_mean_devices_per_test",
        "zone_tests_vs_state_avg",
        "zone_devices_vs_state_avg",
        "zone_density_vs_state_avg",
        "zone_sample_count",
        "state_zone_avg_tests",
        "state_zone_avg_devices",
        "state_zone_avg_density",
        "state_zone_avg_sample_count",
        "zone_sample_count_vs_state_avg",
    }:
        return "usage"
    if feature_name in {
        "zone_mean_download_kbps",
        "zone_median_download_kbps",
        "zone_std_download_kbps",
        "zone_mean_upload_kbps",
        "zone_median_upload_kbps",
        "zone_std_upload_kbps",
        "zone_mean_download_upload_ratio",
        "zone_throughput_sum_kbps",
        "zone_throughput_gap_kbps",
        "state_zone_avg_download_kbps",
        "state_zone_avg_upload_kbps",
        "zone_download_vs_state_avg",
        "zone_upload_vs_state_avg",
    }:
        return "throughput"
    return "other"


def decode_state(row: pd.Series) -> str:
    state_columns = [column for column in row.index if column.startswith("state_") and not column.startswith("state_zone_avg_")]
    if not state_columns:
        return "Unknown"
    state_values = row[state_columns]
    if float(state_values.max()) <= 0:
        return "Unknown"
    return str(state_values.idxmax()).replace("state_", "", 1)


def run_shap(payload: dict[str, object], X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    try:
        import shap
    except ImportError as exc:
        raise ImportError("SHAP is required for zone-risk explainability.") from exc

    model = payload["model"]
    sample_size = min(MAX_SHAP_SAMPLES, len(X_test))
    X_sample = X_test.sample(sample_size, random_state=42).copy()
    probability = np.asarray(model.predict_proba(X_sample))[:, 1]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    if isinstance(shap_values, list):
        shap_array = np.asarray(shap_values[-1])
    else:
        shap_array = np.asarray(shap_values)
        if shap_array.ndim == 3:
            shap_array = shap_array[:, :, -1]

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

    representative_position = int(np.argmax(probability))
    representative_index = int(X_sample.index[representative_position])
    representative_row = X_sample.iloc[representative_position]
    local_series = pd.Series(shap_array[representative_position], index=X_sample.columns, name="shap_value")
    local_explanation = (
        pd.DataFrame(
            {
                "feature": local_series.index,
                "feature_value": representative_row.values,
                "shap_value": local_series.values,
                "abs_shap": np.abs(local_series.values),
                "feature_family": [get_feature_family(name) for name in local_series.index],
                "sample_index": representative_index,
            }
        )
        .sort_values("abs_shap", ascending=False, ignore_index=True)
    )

    representative_metadata = {
        "sample_index": representative_index,
        "predicted_high_risk_probability": float(probability[representative_position]),
        "state": decode_state(representative_row),
        "tile_x_bin": float(representative_row.get("tile_x_bin", np.nan)),
        "tile_y_bin": float(representative_row.get("tile_y_bin", np.nan)),
    }
    return global_importance, family_importance, local_explanation, representative_metadata


def write_outputs(
    metrics: dict[str, float | int | str],
    global_importance: pd.DataFrame,
    family_importance: pd.DataFrame,
    local_explanation: pd.DataFrame,
    representative_metadata: dict[str, object],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    global_importance.to_csv(OUTPUT_DIR / "india_zone_risk_shap_global_importance.csv", index=False)
    family_importance.to_csv(OUTPUT_DIR / "india_zone_risk_shap_family_importance.csv", index=False)
    local_explanation.to_csv(OUTPUT_DIR / "india_zone_risk_shap_local_explanation.csv", index=False)

    top_global = global_importance.head(10)
    top_family = family_importance.head(5)
    top_local = local_explanation.head(10)

    report_lines = [
        "PHASE 9 REPORT: INDIA ZONE-RISK MODEL SHAP EXPLAINABILITY",
        "=" * 80,
        f"Model explained: {metrics['model']}",
        f"Risk threshold: {metrics['risk_quantile']} ({metrics['risk_cutoff_ms']:.4f} ms zone P90 latency)",
        f"Test zones available: {metrics['test_rows']:,}",
        f"Feature count: {metrics['feature_count']}",
        f"Validated accuracy: {metrics['accuracy']:.4f}",
        f"Validated balanced accuracy: {metrics['balanced_accuracy']:.4f}",
        f"Validated macro F1: {metrics['macro_f1']:.4f}",
        f"Validated high-risk F1: {metrics['high_risk_f1']:.4f}",
        f"Validated high-risk precision: {metrics['high_risk_precision']:.4f}",
        f"Validated high-risk recall: {metrics['high_risk_recall']:.4f}",
        "",
        "Interpretation note:",
        "- SHAP values below rank the features that most influence high-risk zone classification.",
        "- For the classifier, they should be used primarily for feature ranking and local explanation rather than probability calibration.",
        "",
        "Top global SHAP features:",
    ]

    for _, row in top_global.iterrows():
        report_lines.append(f"- {row['feature']} ({row['feature_family']}): mean|SHAP|={row['mean_abs_shap']:.6f}")

    report_lines.extend(["", "Top feature families:"])
    for _, row in top_family.iterrows():
        report_lines.append(f"- {row['feature_family']}: total mean|SHAP|={row['mean_abs_shap']:.6f}")

    report_lines.extend(
        [
            "",
            "Representative high-risk local explanation:",
            f"- Sample index: {representative_metadata['sample_index']}",
            f"- State: {representative_metadata['state']}",
            f"- Tile bin: ({representative_metadata['tile_x_bin']:.4f}, {representative_metadata['tile_y_bin']:.4f})",
            f"- Predicted high-risk probability: {representative_metadata['predicted_high_risk_probability']:.4f}",
            "Top local contributors:",
        ]
    )
    for _, row in top_local.iterrows():
        report_lines.append(f"- {row['feature']}={row['feature_value']}: SHAP={row['shap_value']:.6f}")

    (REPORT_DIR / "phase9_india_zone_risk_shap_explainability.txt").write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    payload, X_test, y_test = load_artifacts()
    metrics = evaluate(payload, X_test, y_test)
    global_importance, family_importance, local_explanation, representative_metadata = run_shap(payload, X_test)
    write_outputs(metrics, global_importance, family_importance, local_explanation, representative_metadata)

    print("India Phase 9 zone-risk SHAP explainability complete.")
    print(pd.DataFrame([metrics]).to_string(index=False))
    print(global_importance.head(10).to_string(index=False))


if __name__ == "__main__":
    main()