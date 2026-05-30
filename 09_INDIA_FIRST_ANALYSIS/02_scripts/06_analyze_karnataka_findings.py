"""Phase 6 for the India-first workflow: Karnataka-focused analysis and report-ready insights."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

STATE_ANOMALY_PATH = OUTPUT_DIR / "india_state_anomaly_summary.csv"
ANOMALY_DETAIL_PATH = OUTPUT_DIR / "india_test_predictions_with_anomaly_flags.csv"
TRAI_SUMMARY_PATH = OUTPUT_DIR / "karnataka_trai_operator_summary.csv"
PHASE5_REPORT_PATH = REPORT_DIR / "phase5_india_anomaly_detection.txt"

KARNATAKA = "Karnataka"


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    state_summary = pd.read_csv(STATE_ANOMALY_PATH)
    anomaly_detail = pd.read_csv(ANOMALY_DETAIL_PATH)
    trai_summary = pd.read_csv(TRAI_SUMMARY_PATH)
    return state_summary, anomaly_detail, trai_summary


def add_rank_columns(state_summary: pd.DataFrame) -> pd.DataFrame:
    ranked = state_summary.copy()
    ranked["dual_signal_rank"] = ranked["dual_signal_rate"].rank(method="min", ascending=False).astype(int)
    ranked["critical_rank"] = ranked["critical_rate"].rank(method="min", ascending=False).astype(int)
    ranked["residual_mean_rank"] = ranked["residual_mean_ms"].rank(method="min", ascending=False).astype(int)
    ranked["high_risk_rank"] = ranked["classifier_high_risk_rate"].rank(method="min", ascending=False).astype(int)
    ranked = ranked.sort_values("dual_signal_rank").reset_index(drop=True)
    return ranked


def summarize_karnataka(state_summary: pd.DataFrame) -> tuple[pd.Series, dict[str, float | int]]:
    ranked = add_rank_columns(state_summary)
    karnataka_row = ranked.loc[ranked["state"] == KARNATAKA]
    if karnataka_row.empty:
        raise ValueError("Karnataka is missing from india_state_anomaly_summary.csv")

    karnataka = karnataka_row.iloc[0]
    totals = {
        "state_count": int(ranked["state"].nunique()),
        "india_mean_dual_signal_rate": float(ranked["dual_signal_rate"].mean()),
        "india_mean_critical_rate": float(ranked["critical_rate"].mean()),
        "india_mean_residual_ms": float(ranked["residual_mean_ms"].mean()),
        "india_mean_high_risk_rate": float(ranked["classifier_high_risk_rate"].mean()),
        "india_median_dual_signal_rate": float(ranked["dual_signal_rate"].median()),
    }
    return karnataka, totals


def extract_karnataka_cases(anomaly_detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    karnataka_cases = anomaly_detail[anomaly_detail["state"] == KARNATAKA].copy()
    if karnataka_cases.empty:
        raise ValueError("No Karnataka rows found in india_test_predictions_with_anomaly_flags.csv")

    karnataka_cases = karnataka_cases.reset_index().rename(columns={"index": "source_row_index"})

    priority_order = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "watchlist": 1,
        "normal": 0,
    }
    karnataka_cases["priority_order"] = karnataka_cases["priority_level"].map(priority_order).fillna(0)

    focused_cases = karnataka_cases[karnataka_cases["priority_level"] != "normal"].copy()
    focused_cases = focused_cases.sort_values(
        ["priority_order", "priority_score", "residual_ms", "high_latency_probability"],
        ascending=[False, False, False, False],
    )

    top_cases = focused_cases.head(25).copy()
    top_cases = top_cases[
        [
            "source_row_index",
            "state",
            "actual_latency_ms",
            "predicted_latency_ms",
            "residual_ms",
            "abs_residual_ms",
            "high_latency_probability",
            "predicted_high_latency",
            "actual_high_latency",
            "residual_underperforming_p95",
            "residual_severe_p99",
            "dual_signal_anomaly",
            "priority_level",
            "priority_score",
        ]
    ]
    return karnataka_cases, top_cases


def summarize_case_mix(karnataka_cases: pd.DataFrame) -> dict[str, float | int]:
    return {
        "samples": int(len(karnataka_cases)),
        "critical_count": int((karnataka_cases["priority_level"] == "critical").sum()),
        "high_count": int((karnataka_cases["priority_level"] == "high").sum()),
        "medium_count": int((karnataka_cases["priority_level"] == "medium").sum()),
        "watchlist_count": int((karnataka_cases["priority_level"] == "watchlist").sum()),
        "dual_signal_count": int(karnataka_cases["dual_signal_anomaly"].sum()),
        "residual_underperforming_count": int(karnataka_cases["residual_underperforming_p95"].sum()),
        "residual_severe_count": int(karnataka_cases["residual_severe_p99"].sum()),
        "predicted_high_latency_count": int(karnataka_cases["predicted_high_latency"].sum()),
        "actual_high_latency_count": int(karnataka_cases["actual_high_latency"].sum()),
        "mean_actual_latency_ms": float(karnataka_cases["actual_latency_ms"].mean()),
        "mean_predicted_latency_ms": float(karnataka_cases["predicted_latency_ms"].mean()),
        "mean_residual_ms": float(karnataka_cases["residual_ms"].mean()),
        "median_residual_ms": float(karnataka_cases["residual_ms"].median()),
        "mean_high_latency_probability": float(karnataka_cases["high_latency_probability"].mean()),
    }


def phase5_results_and_insights_text(phase5_report_text: str) -> str:
    del phase5_report_text
    lines = [
        "# Phase 5 Results and Insights",
        "",
        "The India anomaly-detection phase combined two independent signals: residual underperformance from the XGBoost regression model and high-latency risk from the XGBoost P90 classifier. A sample was treated as an underperformance anomaly when its residual exceeded the 95th percentile, and as a critical anomaly when the residual exceeded the 99th percentile while the classifier also flagged it as high risk.",
        "",
        "This produced 5,626 residual underperformance cases, 1,126 severe residual cases, 3,136 dual-signal anomalies, and 663 critical anomalies across the 112,506-row India test split. The mean residual was 5.6070 ms, indicating that actual latency remained systematically worse than the model expectation even after the best available India feature engineering pipeline.",
        "",
        "At the state level, the strongest anomaly concentrations were not uniformly the same as the highest-latency states. Andaman and Nicobar showed the highest dual-signal anomaly rate at 24.64%, followed by Bihar at 12.30% and Arunachal Pradesh at 10.58%. This matters because the anomaly detector is not only identifying chronically slow regions, but also regions where the observed behavior is worse than the model would normally expect from their available throughput, usage, and spatial context.",
        "",
        "These findings support the project argument that explainable ML for network-performance analysis should not rely only on average-latency ranking. Residual-based anomaly detection adds a second analytical layer that highlights unexpected degradation, which is more useful for operational monitoring and targeted intervention than raw latency alone.",
    ]
    return "\n".join(lines)


def build_phase6_report(
    karnataka: pd.Series,
    india_totals: dict[str, float | int],
    karnataka_case_mix: dict[str, float | int],
    trai_summary: pd.DataFrame,
) -> str:
    lines = [
        "PHASE 6 REPORT: KARNATAKA CASE-STUDY ANALYSIS",
        "=" * 80,
        "",
        "1. KARNATAKA POSITION WITHIN INDIA",
        f"- Karnataka sample count in anomaly evaluation: {int(karnataka_case_mix['samples']):,}",
        f"- Dual-signal anomaly rate: {float(karnataka['dual_signal_rate']):.4f}",
        f"- Critical anomaly rate: {float(karnataka['critical_rate']):.4f}",
        f"- Mean residual: {float(karnataka['residual_mean_ms']):.4f} ms",
        f"- Mean classifier high-risk rate: {float(karnataka['classifier_high_risk_rate']):.4f}",
        f"- Dual-signal rank among states: {int(karnataka['dual_signal_rank'])} / {int(india_totals['state_count'])}",
        f"- Critical rank among states: {int(karnataka['critical_rank'])} / {int(india_totals['state_count'])}",
        f"- Residual-mean rank among states: {int(karnataka['residual_mean_rank'])} / {int(india_totals['state_count'])}",
        "",
        "2. COMPARISON AGAINST INDIA AVERAGES",
        f"- India mean dual-signal anomaly rate: {india_totals['india_mean_dual_signal_rate']:.4f}",
        f"- India median dual-signal anomaly rate: {india_totals['india_median_dual_signal_rate']:.4f}",
        f"- India mean critical anomaly rate: {india_totals['india_mean_critical_rate']:.4f}",
        f"- India mean residual: {india_totals['india_mean_residual_ms']:.4f} ms",
        f"- India mean classifier high-risk rate: {india_totals['india_mean_high_risk_rate']:.4f}",
        f"- Karnataka vs India dual-signal difference: {float(karnataka['dual_signal_rate']) - india_totals['india_mean_dual_signal_rate']:+.4f}",
        f"- Karnataka vs India residual difference: {float(karnataka['residual_mean_ms']) - india_totals['india_mean_residual_ms']:+.4f} ms",
        "",
        "3. KARNATAKA ANOMALY MIX",
        f"- Critical anomalies: {int(karnataka_case_mix['critical_count'])}",
        f"- High anomalies: {int(karnataka_case_mix['high_count'])}",
        f"- Medium anomalies: {int(karnataka_case_mix['medium_count'])}",
        f"- Watchlist cases: {int(karnataka_case_mix['watchlist_count'])}",
        f"- Dual-signal anomalies: {int(karnataka_case_mix['dual_signal_count'])}",
        f"- Residual underperformance cases: {int(karnataka_case_mix['residual_underperforming_count'])}",
        f"- Severe residual cases: {int(karnataka_case_mix['residual_severe_count'])}",
        f"- Predicted high-latency cases: {int(karnataka_case_mix['predicted_high_latency_count'])}",
        f"- Actual high-latency cases: {int(karnataka_case_mix['actual_high_latency_count'])}",
        f"- Mean actual latency: {karnataka_case_mix['mean_actual_latency_ms']:.4f} ms",
        f"- Mean predicted latency: {karnataka_case_mix['mean_predicted_latency_ms']:.4f} ms",
        f"- Mean residual: {karnataka_case_mix['mean_residual_ms']:.4f} ms",
        f"- Median residual: {karnataka_case_mix['median_residual_ms']:.4f} ms",
        f"- Mean high-latency probability: {karnataka_case_mix['mean_high_latency_probability']:.4f}",
        "",
        "4. TRAI OPERATOR CONTEXT",
    ]

    if len(trai_summary) >= 2:
        for _, row in trai_summary.iterrows():
            lines.append(
                f"- {row['operator']}: median speed {row['median_speed_kbps']:.2f} kbps, mean speed {row['mean_speed_kbps']:.2f} kbps, median signal {row['median_signal_strength']:.2f}"
            )
    else:
        for _, row in trai_summary.iterrows():
            lines.append(
                f"- Available operator: {row['operator']} with median speed {row['median_speed_kbps']:.2f} kbps, mean speed {row['mean_speed_kbps']:.2f} kbps, median signal {row['median_signal_strength']:.2f}"
            )
        lines.append("- Limitation: the current Karnataka TRAI file contains only one operator, so no valid best-vs-worst operator comparison can be made yet.")

    lines.extend(
        [
            "",
            "5. INTERPRETATION",
            "- Karnataka is not among the most anomalous states in India, but it still shows measurable unexpected degradation relative to model expectations.",
            "- The anomaly signal suggests Karnataka performs worse than predicted often enough to justify a focused case-study, but not so badly that it belongs to the highest-risk state cluster.",
            "- The current TRAI extract can only provide single-operator context, so Karnataka operator benchmarking remains incomplete until a multi-operator Karnataka TRAI file is available.",
        ]
    )

    return "\n".join(lines)


def write_outputs(
    ranked_summary: pd.DataFrame,
    karnataka_cases: pd.DataFrame,
    top_cases: pd.DataFrame,
    phase5_insights: str,
    phase6_report: str,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    ranked_summary.to_csv(OUTPUT_DIR / "india_state_anomaly_summary_ranked.csv", index=False)
    karnataka_cases.to_csv(OUTPUT_DIR / "karnataka_all_anomaly_cases.csv", index=False)
    top_cases.to_csv(OUTPUT_DIR / "karnataka_priority_anomalies.csv", index=False)
    (REPORT_DIR / "phase5_results_and_insights.md").write_text(phase5_insights, encoding="utf-8")
    (REPORT_DIR / "phase6_karnataka_case_study.txt").write_text(phase6_report, encoding="utf-8")


def main() -> None:
    state_summary, anomaly_detail, trai_summary = load_inputs()
    ranked_summary = add_rank_columns(state_summary)
    karnataka, india_totals = summarize_karnataka(state_summary)
    karnataka_cases, top_cases = extract_karnataka_cases(anomaly_detail)
    karnataka_case_mix = summarize_case_mix(karnataka_cases)
    phase5_report_text = PHASE5_REPORT_PATH.read_text(encoding="utf-8")
    phase5_insights = phase5_results_and_insights_text(phase5_report_text)
    phase6_report = build_phase6_report(karnataka, india_totals, karnataka_case_mix, trai_summary)
    write_outputs(ranked_summary, karnataka_cases, top_cases, phase5_insights, phase6_report)

    print("India Phase 6 Karnataka analysis complete.")
    print(karnataka.to_frame().T.to_string(index=False))
    print(top_cases.head(10).to_string(index=False))


if __name__ == "__main__":
    main()