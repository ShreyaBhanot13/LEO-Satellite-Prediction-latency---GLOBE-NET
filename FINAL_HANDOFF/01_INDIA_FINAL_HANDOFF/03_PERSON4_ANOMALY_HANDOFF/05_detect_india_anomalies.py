"""Phase 5 for the India-first workflow: detect anomalous Indian latency behavior."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

REGRESSION_MODEL_PATH = OUTPUT_DIR / "india_best_model.pkl"
REGRESSION_TEST_PATH = OUTPUT_DIR / "india_test_data.pkl"
CLASSIFIER_MODEL_PATH = OUTPUT_DIR / "india_best_high_latency_classifier.pkl"


def load_artifacts() -> tuple[dict[str, object], dict[str, object], pd.DataFrame, pd.Series]:
    regression_payload = joblib.load(REGRESSION_MODEL_PATH)
    classifier_payload = joblib.load(CLASSIFIER_MODEL_PATH)
    X_test, y_test = joblib.load(REGRESSION_TEST_PATH)

    regression_required = {"name", "model", "shift_amount", "features"}
    classifier_required = {"name", "model", "features", "threshold_ms", "threshold_name"}
    missing_regression = regression_required - set(regression_payload)
    missing_classifier = classifier_required - set(classifier_payload)

    if missing_regression:
        raise KeyError(f"Regression payload is missing keys: {sorted(missing_regression)}")
    if missing_classifier:
        raise KeyError(f"Classifier payload is missing keys: {sorted(missing_classifier)}")

    X_test = X_test.copy()
    return regression_payload, classifier_payload, X_test, y_test


def inverse_predict(regression_payload: dict[str, object], X: pd.DataFrame) -> np.ndarray:
    prediction_log = regression_payload["model"].predict(X.loc[:, regression_payload["features"]])
    return np.exp(prediction_log) - float(regression_payload["shift_amount"])


def classifier_scores(classifier_payload: dict[str, object], X: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    aligned_X = X.loc[:, classifier_payload["features"]]
    model = classifier_payload["model"]

    if hasattr(model, "predict_proba"):
        probability_matrix = model.predict_proba(aligned_X)
        high_latency_probability = np.asarray(probability_matrix)[:, 1]
    else:
        high_latency_probability = np.asarray(model.predict(aligned_X)).reshape(-1).astype(float)

    predicted_label = (high_latency_probability >= 0.5).astype(int)
    return high_latency_probability, predicted_label


def decode_state(X: pd.DataFrame) -> pd.Series:
    state_columns = [
        column
        for column in X.columns
        if column.startswith("state_") and not column.startswith("state_avg_") and not column.startswith("state_median_")
    ]
    if not state_columns:
        return pd.Series("Unknown", index=X.index)

    state_frame = X[state_columns].astype(float)
    max_columns = state_frame.idxmax(axis=1)
    has_state = state_frame.max(axis=1) > 0
    decoded = max_columns.str.replace("state_", "", regex=False)
    decoded = decoded.where(has_state, "Unknown")
    return decoded


def build_anomaly_frame(
    regression_payload: dict[str, object],
    classifier_payload: dict[str, object],
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple[pd.DataFrame, dict[str, float | int | str]]:
    y_pred = inverse_predict(regression_payload, X_test)
    high_latency_probability, predicted_high_latency = classifier_scores(classifier_payload, X_test)

    anomaly_df = pd.DataFrame(index=X_test.index)
    anomaly_df["state"] = decode_state(X_test)
    anomaly_df["actual_latency_ms"] = y_test.values
    anomaly_df["predicted_latency_ms"] = y_pred
    anomaly_df["residual_ms"] = anomaly_df["actual_latency_ms"] - anomaly_df["predicted_latency_ms"]
    anomaly_df["abs_residual_ms"] = anomaly_df["residual_ms"].abs()
    anomaly_df["high_latency_probability"] = high_latency_probability
    anomaly_df["predicted_high_latency"] = predicted_high_latency.astype(int)
    anomaly_df["actual_high_latency"] = (anomaly_df["actual_latency_ms"] >= float(classifier_payload["threshold_ms"])).astype(int)

    positive_p95 = float(anomaly_df["residual_ms"].quantile(0.95))
    positive_p99 = float(anomaly_df["residual_ms"].quantile(0.99))
    negative_p01 = float(anomaly_df["residual_ms"].quantile(0.01))

    anomaly_df["residual_underperforming_p95"] = anomaly_df["residual_ms"] >= positive_p95
    anomaly_df["residual_severe_p99"] = anomaly_df["residual_ms"] >= positive_p99
    anomaly_df["better_than_expected_p01"] = anomaly_df["residual_ms"] <= negative_p01
    anomaly_df["classifier_high_risk"] = anomaly_df["predicted_high_latency"].astype(bool)
    anomaly_df["dual_signal_anomaly"] = anomaly_df["residual_underperforming_p95"] & anomaly_df["classifier_high_risk"]

    residual_rank = anomaly_df["residual_ms"].rank(method="average", pct=True)
    anomaly_df["priority_score"] = 0.6 * residual_rank + 0.4 * anomaly_df["high_latency_probability"]
    anomaly_df["priority_level"] = np.select(
        [
            anomaly_df["residual_severe_p99"] & anomaly_df["classifier_high_risk"],
            anomaly_df["dual_signal_anomaly"],
            anomaly_df["residual_underperforming_p95"],
            anomaly_df["classifier_high_risk"],
        ],
        ["critical", "high", "medium", "watchlist"],
        default="normal",
    )

    summary = {
        "regression_model": str(regression_payload["name"]),
        "classifier_model": str(classifier_payload["name"]),
        "classifier_threshold_name": str(classifier_payload["threshold_name"]),
        "classifier_threshold_ms": float(classifier_payload["threshold_ms"]),
        "test_rows": int(len(anomaly_df)),
        "residual_p95_ms": positive_p95,
        "residual_p99_ms": positive_p99,
        "residual_p01_ms": negative_p01,
        "residual_underperforming_count": int(anomaly_df["residual_underperforming_p95"].sum()),
        "residual_severe_count": int(anomaly_df["residual_severe_p99"].sum()),
        "classifier_high_risk_count": int(anomaly_df["classifier_high_risk"].sum()),
        "dual_signal_count": int(anomaly_df["dual_signal_anomaly"].sum()),
        "critical_count": int((anomaly_df["priority_level"] == "critical").sum()),
        "mean_residual_ms": float(anomaly_df["residual_ms"].mean()),
        "mean_high_latency_probability": float(anomaly_df["high_latency_probability"].mean()),
    }
    return anomaly_df, summary


def build_state_summary(anomaly_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        anomaly_df.groupby("state", dropna=False)
        .agg(
            samples=("state", "size"),
            actual_latency_mean_ms=("actual_latency_ms", "mean"),
            predicted_latency_mean_ms=("predicted_latency_ms", "mean"),
            residual_mean_ms=("residual_ms", "mean"),
            residual_median_ms=("residual_ms", "median"),
            residual_underperforming_count=("residual_underperforming_p95", "sum"),
            residual_severe_count=("residual_severe_p99", "sum"),
            classifier_high_risk_count=("classifier_high_risk", "sum"),
            dual_signal_count=("dual_signal_anomaly", "sum"),
            high_latency_probability_mean=("high_latency_probability", "mean"),
        )
        .reset_index()
    )

    critical_counts = (
        anomaly_df.assign(is_critical=anomaly_df["priority_level"] == "critical")
        .groupby("state", dropna=False)["is_critical"]
        .sum()
        .reset_index(name="critical_count")
    )
    summary = summary.merge(critical_counts, on="state", how="left")

    summary["residual_underperforming_rate"] = summary["residual_underperforming_count"] / summary["samples"]
    summary["classifier_high_risk_rate"] = summary["classifier_high_risk_count"] / summary["samples"]
    summary["dual_signal_rate"] = summary["dual_signal_count"] / summary["samples"]
    summary["critical_rate"] = summary["critical_count"] / summary["samples"]

    return summary.sort_values(["dual_signal_rate", "residual_mean_ms", "samples"], ascending=[False, False, False]).reset_index(drop=True)


def write_outputs(anomaly_df: pd.DataFrame, state_summary: pd.DataFrame, summary: dict[str, float | int | str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    flagged = anomaly_df[anomaly_df["priority_level"] != "normal"].copy()
    priority = flagged.sort_values(["priority_score", "residual_ms", "high_latency_probability"], ascending=[False, False, False])

    anomaly_df.to_csv(OUTPUT_DIR / "india_test_predictions_with_anomaly_flags.csv", index_label="row_index")
    state_summary.to_csv(OUTPUT_DIR / "india_state_anomaly_summary.csv", index=False)
    priority.to_csv(OUTPUT_DIR / "india_priority_anomalies.csv", index_label="row_index")
    joblib.dump(
        {
            "summary": summary,
            "anomaly_frame": anomaly_df,
            "state_summary": state_summary,
        },
        OUTPUT_DIR / "india_anomaly_detection_results.pkl",
    )

    top_states = state_summary.head(10)
    report_lines = [
        "PHASE 5 REPORT: INDIA ANOMALY DETECTION",
        "=" * 80,
        f"Regression model: {summary['regression_model']}",
        f"Classifier model: {summary['classifier_model']}",
        f"Classifier threshold: {summary['classifier_threshold_name']} ({summary['classifier_threshold_ms']:.4f} ms)",
        f"Test rows evaluated: {summary['test_rows']:,}",
        "",
        "Detection rules:",
        f"- Residual underperformance: residual >= P95 ({summary['residual_p95_ms']:.4f} ms)",
        f"- Severe underperformance: residual >= P99 ({summary['residual_p99_ms']:.4f} ms)",
        f"- Better than expected: residual <= P01 ({summary['residual_p01_ms']:.4f} ms)",
        "- Dual-signal anomaly: residual underperformance + classifier high-risk flag",
        "- Critical anomaly: severe residual underperformance + classifier high-risk flag",
        "",
        "Overall results:",
        f"- Residual underperforming count: {summary['residual_underperforming_count']:,}",
        f"- Severe residual count: {summary['residual_severe_count']:,}",
        f"- Classifier high-risk count: {summary['classifier_high_risk_count']:,}",
        f"- Dual-signal anomaly count: {summary['dual_signal_count']:,}",
        f"- Critical anomaly count: {summary['critical_count']:,}",
        f"- Mean residual: {summary['mean_residual_ms']:.4f} ms",
        f"- Mean high-latency probability: {summary['mean_high_latency_probability']:.4f}",
        "",
        "Top states by dual-signal anomaly rate:",
    ]

    for _, row in top_states.iterrows():
        report_lines.append(
            f"- {row['state']}: dual_rate={row['dual_signal_rate']:.4f}, critical_rate={row['critical_rate']:.4f}, residual_mean={row['residual_mean_ms']:.4f} ms, high_risk_rate={row['classifier_high_risk_rate']:.4f}, samples={int(row['samples'])}"
        )

    (REPORT_DIR / "phase5_india_anomaly_detection.txt").write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    regression_payload, classifier_payload, X_test, y_test = load_artifacts()
    anomaly_df, summary = build_anomaly_frame(regression_payload, classifier_payload, X_test, y_test)
    state_summary = build_state_summary(anomaly_df)
    write_outputs(anomaly_df, state_summary, summary)

    print("India Phase 5 anomaly detection complete.")
    print(pd.DataFrame([summary]).to_string(index=False))
    print(state_summary.head(10).to_string(index=False))


if __name__ == "__main__":
    main()