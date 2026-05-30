"""Summarize state-wise and Karnataka-specific findings for the final India zone-risk classifier."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, f1_score, precision_score, recall_score


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

DATASET_PATH = OUTPUT_DIR / "india_zone_risk_dataset.csv"
MODEL_PATH = OUTPUT_DIR / "india_best_zone_risk_model.pkl"
TEST_DATA_PATH = OUTPUT_DIR / "india_zone_risk_test_data.pkl"

KARNATAKA = "Karnataka"


def load_artifacts() -> tuple[pd.DataFrame, dict[str, object], pd.DataFrame, pd.Series]:
    full_dataset = pd.read_csv(DATASET_PATH)
    payload = joblib.load(MODEL_PATH)
    X_test, y_test = joblib.load(TEST_DATA_PATH)

    required = {"name", "model", "features", "risk_quantile", "risk_cutoff_ms", "class_labels"}
    missing = required - set(payload)
    if missing:
        raise KeyError(f"Zone-risk model payload is missing keys: {sorted(missing)}")

    X_test = X_test.loc[:, payload["features"]].copy()
    return full_dataset, payload, X_test, y_test


def decode_state_from_features(X: pd.DataFrame) -> pd.Series:
    state_columns = [
        column
        for column in X.columns
        if column.startswith("state_") and not column.startswith("state_zone_avg_")
    ]
    if not state_columns:
        return pd.Series("Unknown", index=X.index)

    state_frame = X[state_columns].astype(float)
    max_columns = state_frame.idxmax(axis=1)
    has_state = state_frame.max(axis=1) > 0
    decoded = max_columns.str.replace("state_", "", regex=False)
    return decoded.where(has_state, "Unknown")


def build_prediction_frame(
    full_dataset: pd.DataFrame,
    payload: dict[str, object],
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> pd.DataFrame:
    model = payload["model"]
    prediction_probability = np.asarray(model.predict_proba(X_test))[:, 1]
    predicted_label = (prediction_probability >= 0.5).astype(int)

    detail = full_dataset.loc[X_test.index].copy()
    detail = detail.reset_index().rename(columns={"index": "source_row_index"})
    detail["decoded_state"] = decode_state_from_features(X_test).values
    detail["actual_high_risk"] = y_test.values.astype(int)
    detail["predicted_high_risk"] = predicted_label.astype(int)
    detail["high_risk_probability"] = prediction_probability
    detail["prediction_correct"] = detail["actual_high_risk"] == detail["predicted_high_risk"]
    detail["false_positive"] = (detail["actual_high_risk"] == 0) & (detail["predicted_high_risk"] == 1)
    detail["false_negative"] = (detail["actual_high_risk"] == 1) & (detail["predicted_high_risk"] == 0)
    detail["true_positive"] = (detail["actual_high_risk"] == 1) & (detail["predicted_high_risk"] == 1)
    detail["risk_gap_ms"] = detail["zone_p90_latency_ms"] - float(payload["risk_cutoff_ms"])
    return detail


def build_state_summary(prediction_frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []

    for state_name, group in prediction_frame.groupby("decoded_state", dropna=False):
        y_true = group["actual_high_risk"]
        y_pred = group["predicted_high_risk"]
        rows.append(
            {
                "state": state_name,
                "zones": int(len(group)),
                "actual_high_risk_zones": int(y_true.sum()),
                "predicted_high_risk_zones": int(y_pred.sum()),
                "true_positive_zones": int(group["true_positive"].sum()),
                "false_positive_zones": int(group["false_positive"].sum()),
                "false_negative_zones": int(group["false_negative"].sum()),
                "actual_high_risk_rate": float(y_true.mean()),
                "predicted_high_risk_rate": float(y_pred.mean()),
                "mean_zone_p90_latency_ms": float(group["zone_p90_latency_ms"].mean()),
                "mean_high_risk_probability": float(group["high_risk_probability"].mean()),
                "precision": float(precision_score(y_true, y_pred, zero_division=0)),
                "recall": float(recall_score(y_true, y_pred, zero_division=0)),
                "high_risk_f1": float(f1_score(y_true, y_pred, zero_division=0)),
                "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)) if len(np.unique(y_true)) > 1 else np.nan,
            }
        )

    state_summary = pd.DataFrame(rows).sort_values(
        ["predicted_high_risk_rate", "actual_high_risk_rate", "mean_high_risk_probability"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    state_summary["predicted_high_risk_rank"] = state_summary["predicted_high_risk_rate"].rank(method="min", ascending=False).astype(int)
    state_summary["actual_high_risk_rank"] = state_summary["actual_high_risk_rate"].rank(method="min", ascending=False).astype(int)
    return state_summary


def build_karnataka_outputs(prediction_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float | int]]:
    karnataka = prediction_frame[prediction_frame["decoded_state"] == KARNATAKA].copy()
    if karnataka.empty:
        raise ValueError("No Karnataka zones found in the zone-risk test split.")

    high_risk_karnataka = karnataka[karnataka["predicted_high_risk"] == 1].copy()
    high_risk_karnataka = high_risk_karnataka.sort_values(
        ["high_risk_probability", "zone_p90_latency_ms", "zone_sample_count"],
        ascending=[False, False, False],
    )

    top_columns = [
        "source_row_index",
        "decoded_state",
        "tile_x_bin",
        "tile_y_bin",
        "zone_sample_count",
        "zone_mean_latency_ms",
        "zone_p90_latency_ms",
        "risk_gap_ms",
        "zone_mean_download_kbps",
        "zone_mean_upload_kbps",
        "zone_mean_tests",
        "zone_mean_devices",
        "high_risk_probability",
        "actual_high_risk",
        "predicted_high_risk",
        "prediction_correct",
    ]
    top_karnataka = high_risk_karnataka.head(25)[top_columns].copy()

    summary = {
        "zones": int(len(karnataka)),
        "predicted_high_risk_zones": int(karnataka["predicted_high_risk"].sum()),
        "actual_high_risk_zones": int(karnataka["actual_high_risk"].sum()),
        "true_positive_zones": int(karnataka["true_positive"].sum()),
        "false_positive_zones": int(karnataka["false_positive"].sum()),
        "false_negative_zones": int(karnataka["false_negative"].sum()),
        "predicted_high_risk_rate": float(karnataka["predicted_high_risk"].mean()),
        "actual_high_risk_rate": float(karnataka["actual_high_risk"].mean()),
        "mean_zone_p90_latency_ms": float(karnataka["zone_p90_latency_ms"].mean()),
        "mean_high_risk_probability": float(karnataka["high_risk_probability"].mean()),
        "precision": float(precision_score(karnataka["actual_high_risk"], karnataka["predicted_high_risk"], zero_division=0)),
        "recall": float(recall_score(karnataka["actual_high_risk"], karnataka["predicted_high_risk"], zero_division=0)),
        "high_risk_f1": float(f1_score(karnataka["actual_high_risk"], karnataka["predicted_high_risk"], zero_division=0)),
    }
    return karnataka, top_karnataka, summary


def write_outputs(
    payload: dict[str, object],
    prediction_frame: pd.DataFrame,
    state_summary: pd.DataFrame,
    karnataka_all: pd.DataFrame,
    karnataka_top: pd.DataFrame,
    karnataka_summary: dict[str, float | int],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    prediction_frame.to_csv(OUTPUT_DIR / "india_zone_risk_predictions_detailed.csv", index=False)
    state_summary.to_csv(OUTPUT_DIR / "india_zone_risk_state_summary.csv", index=False)
    karnataka_all.to_csv(OUTPUT_DIR / "karnataka_zone_risk_all_test_zones.csv", index=False)
    karnataka_top.to_csv(OUTPUT_DIR / "karnataka_top_high_risk_zones.csv", index=False)

    top_states = state_summary.head(10)
    report_lines = [
        "PHASE 10 REPORT: STATE-WISE AND KARNATAKA ZONE-RISK SUMMARY",
        "=" * 80,
        f"Final model: {payload['name']}",
        f"Risk threshold: {payload['risk_quantile']} ({float(payload['risk_cutoff_ms']):.4f} ms zone P90 latency)",
        f"Class labels: {', '.join(payload['class_labels'])}",
        "",
        "Top states by predicted high-risk zone rate:",
    ]
    for _, row in top_states.iterrows():
        report_lines.append(
            f"- {row['state']}: predicted_rate={row['predicted_high_risk_rate']:.4f}, actual_rate={row['actual_high_risk_rate']:.4f}, probability_mean={row['mean_high_risk_probability']:.4f}, zones={int(row['zones'])}"
        )

    report_lines.extend(
        [
            "",
            "Karnataka summary:",
            f"- Zones evaluated: {karnataka_summary['zones']}",
            f"- Predicted high-risk zones: {karnataka_summary['predicted_high_risk_zones']}",
            f"- Actual high-risk zones: {karnataka_summary['actual_high_risk_zones']}",
            f"- True positives: {karnataka_summary['true_positive_zones']}",
            f"- False positives: {karnataka_summary['false_positive_zones']}",
            f"- False negatives: {karnataka_summary['false_negative_zones']}",
            f"- Predicted high-risk rate: {karnataka_summary['predicted_high_risk_rate']:.4f}",
            f"- Actual high-risk rate: {karnataka_summary['actual_high_risk_rate']:.4f}",
            f"- Mean zone P90 latency: {karnataka_summary['mean_zone_p90_latency_ms']:.4f} ms",
            f"- Mean high-risk probability: {karnataka_summary['mean_high_risk_probability']:.4f}",
            f"- Karnataka precision: {karnataka_summary['precision']:.4f}",
            f"- Karnataka recall: {karnataka_summary['recall']:.4f}",
            f"- Karnataka high-risk F1: {karnataka_summary['high_risk_f1']:.4f}",
            "",
            "Output files:",
            "- 03_outputs/india_zone_risk_state_summary.csv",
            "- 03_outputs/india_zone_risk_predictions_detailed.csv",
            "- 03_outputs/karnataka_zone_risk_all_test_zones.csv",
            "- 03_outputs/karnataka_top_high_risk_zones.csv",
        ]
    )
    (REPORT_DIR / "phase10_zone_risk_state_and_karnataka_summary.txt").write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    full_dataset, payload, X_test, y_test = load_artifacts()
    prediction_frame = build_prediction_frame(full_dataset, payload, X_test, y_test)
    state_summary = build_state_summary(prediction_frame)
    karnataka_all, karnataka_top, karnataka_summary = build_karnataka_outputs(prediction_frame)
    write_outputs(payload, prediction_frame, state_summary, karnataka_all, karnataka_top, karnataka_summary)

    print("India Phase 10 zone-risk summaries complete.")
    print(state_summary.head(10).to_string(index=False))
    print(pd.DataFrame([karnataka_summary]).to_string(index=False))


if __name__ == "__main__":
    main()