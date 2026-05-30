"""Phase 1 for the India-first workflow: profile original Ookla + real TRAI datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OOKLA_PATH = ROOT / "outputs_v5" / "ookla_data_with_states.csv"
TRAI_PATH = ROOT / "outputs_v5" / "ade6e644-91b8-4d27-97ba-e8c42c48f278_4bc4eb37ff16e2b91e3412bf093ee6e5 (1).csv"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

KARNATAKA = "Karnataka"

OOKLA_REQUIRED = [
    "avg_d_kbps",
    "avg_u_kbps",
    "avg_lat_ms",
    "tests",
    "devices",
    "tile_x",
    "tile_y",
    "state",
]

TRAI_REQUIRED = [
    "operator",
    "technology",
    "download",
    "speed_kbps",
    "signal_strength",
    "lsa",
    "month",
    "year",
]


def ensure_directories() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset(path: Path, required_columns: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {missing}")
    return df


def summarize_series(series: pd.Series) -> dict[str, float]:
    return {
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "p95": float(series.quantile(0.95)),
    }


def build_state_summary(ookla_df: pd.DataFrame) -> pd.DataFrame:
    state_summary = (
        ookla_df.groupby("state", dropna=False)
        .agg(
            tile_count=("avg_lat_ms", "size"),
            mean_latency_ms=("avg_lat_ms", "mean"),
            median_latency_ms=("avg_lat_ms", "median"),
            std_latency_ms=("avg_lat_ms", "std"),
            mean_download_kbps=("avg_d_kbps", "mean"),
            mean_upload_kbps=("avg_u_kbps", "mean"),
        )
        .reset_index()
        .sort_values("mean_latency_ms", ascending=False)
    )
    return state_summary


def build_karnataka_trai_summary(trai_df: pd.DataFrame) -> pd.DataFrame:
    karnataka_df = trai_df[trai_df["lsa"] == KARNATAKA].copy()
    karnataka_df["signal_strength_numeric"] = pd.to_numeric(karnataka_df["signal_strength"], errors="coerce")

    operator_summary = (
        karnataka_df.groupby("operator", dropna=False)
        .agg(
            sample_count=("speed_kbps", "size"),
            mean_speed_kbps=("speed_kbps", "mean"),
            median_speed_kbps=("speed_kbps", "median"),
            mean_signal_strength=("signal_strength_numeric", "mean"),
            median_signal_strength=("signal_strength_numeric", "median"),
        )
        .reset_index()
        .sort_values(["median_speed_kbps", "mean_speed_kbps"], ascending=[False, False])
    )
    operator_summary["rank"] = range(1, len(operator_summary) + 1)
    return operator_summary


def representative_states(state_summary: pd.DataFrame) -> pd.DataFrame:
    state_summary = state_summary.reset_index(drop=True)
    best = state_summary.nsmallest(3, "mean_latency_ms")
    middle = state_summary.iloc[[len(state_summary) // 2]]
    worst = state_summary.nlargest(4, "mean_latency_ms")
    selected = pd.concat([best, middle, worst], ignore_index=True).drop_duplicates(subset=["state"])
    return selected


def write_report(
    ookla_df: pd.DataFrame,
    state_summary: pd.DataFrame,
    trai_summary: pd.DataFrame,
) -> None:
    india_stats = summarize_series(ookla_df["avg_lat_ms"])
    karnataka_stats = summarize_series(ookla_df.loc[ookla_df["state"] == KARNATAKA, "avg_lat_ms"])

    best_two = trai_summary.head(2)[["operator", "median_speed_kbps", "mean_speed_kbps"]]
    worst_two = trai_summary.tail(2)[["operator", "median_speed_kbps", "mean_speed_kbps"]]
    chosen_states = representative_states(state_summary)

    report_lines = [
        "PHASE 1 REPORT: INDIA DATA UNDERSTANDING",
        "=" * 80,
        "",
        "1. DATASET OVERVIEW",
        f"- Original Ookla rows: {len(ookla_df):,}",
        f"- States covered: {ookla_df['state'].nunique()}",
        f"- Karnataka rows in Ookla: {(ookla_df['state'] == KARNATAKA).sum():,}",
        f"- Karnataka rows in TRAI: {int(trai_summary['sample_count'].sum()):,}",
        "",
        "2. INDIA LATENCY SUMMARY",
        f"- Mean latency: {india_stats['mean']:.2f} ms",
        f"- Median latency: {india_stats['median']:.2f} ms",
        f"- Std latency: {india_stats['std']:.2f} ms",
        f"- 95th percentile latency: {india_stats['p95']:.2f} ms",
        "",
        "3. KARNATAKA LATENCY SUMMARY",
        f"- Mean latency: {karnataka_stats['mean']:.2f} ms",
        f"- Median latency: {karnataka_stats['median']:.2f} ms",
        f"- Std latency: {karnataka_stats['std']:.2f} ms",
        f"- 95th percentile latency: {karnataka_stats['p95']:.2f} ms",
        "",
        "4. KARNATAKA TRAI OPERATOR COMPARISON",
    ]

    if len(trai_summary) >= 4:
        report_lines.append("Best two operators by median speed:")
        for _, row in best_two.iterrows():
            report_lines.append(
                f"- {row['operator']}: median {row['median_speed_kbps']:.2f} kbps, mean {row['mean_speed_kbps']:.2f} kbps"
            )

        report_lines.append("Worst two operators by median speed:")
        for _, row in worst_two.iterrows():
            report_lines.append(
                f"- {row['operator']}: median {row['median_speed_kbps']:.2f} kbps, mean {row['mean_speed_kbps']:.2f} kbps"
            )
    else:
        report_lines.append("Available operators in the current TRAI file:")
        for _, row in trai_summary.iterrows():
            report_lines.append(
                f"- {row['operator']}: median {row['median_speed_kbps']:.2f} kbps, mean {row['mean_speed_kbps']:.2f} kbps"
            )
        report_lines.append("- Note: the attached TRAI file currently contains too few operators for a real best-vs-worst ranking.")

    report_lines.extend(
        [
            "",
            "5. REPRESENTATIVE STATES FOR COMPARATIVE ANALYSIS",
            "Suggested state set balances strong, mid, and weak latency conditions:",
        ]
    )

    for _, row in chosen_states.iterrows():
        report_lines.append(f"- {row['state']}: mean latency {row['mean_latency_ms']:.2f} ms")

    report_lines.extend(
        [
            "",
            "6. PHASE 1 TAKEAWAYS",
            "- Karnataka has enough rows to support a focused case-study workflow.",
            "- Original Ookla with states is the correct base for India-native latency modeling.",
            "- Real TRAI data supports operator comparison through speed and signal, not direct latency labels.",
            "- The next phase should build an India-native model dataset from the original Ookla state file only.",
        ]
    )

    report_path = REPORT_DIR / "phase1_india_data_understanding.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    ensure_directories()

    ookla_df = load_dataset(OOKLA_PATH, OOKLA_REQUIRED)
    trai_df = load_dataset(TRAI_PATH, TRAI_REQUIRED)

    state_summary = build_state_summary(ookla_df)
    trai_summary = build_karnataka_trai_summary(trai_df)

    state_summary.to_csv(OUTPUT_DIR / "state_latency_summary_india.csv", index=False)
    trai_summary.to_csv(OUTPUT_DIR / "karnataka_trai_operator_summary.csv", index=False)
    write_report(ookla_df, state_summary, trai_summary)

    print("India Phase 1 profiling complete.")
    print(f"Outputs: {OUTPUT_DIR}")
    print(f"Report: {REPORT_DIR / 'phase1_india_data_understanding.txt'}")


if __name__ == "__main__":
    main()