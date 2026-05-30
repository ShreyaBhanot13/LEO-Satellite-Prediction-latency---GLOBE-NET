"""Build a zone-level India dataset for high-risk internet performance classification."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OOKLA_PATH = ROOT / "outputs_v5" / "ookla_data_with_states.csv"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"
TRAI_MASTER_PATH = OUTPUT_DIR / "trai_2025_state_service_provider_master.csv"

ZONE_ROUNDING = 1
MIN_ZONE_SAMPLES = 10


def load_data() -> pd.DataFrame:
    return pd.read_csv(OOKLA_PATH)


def load_trai_master() -> pd.DataFrame:
    return pd.read_csv(TRAI_MASTER_PATH)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-trai-context",
        action="store_true",
        help="Merge aggregated TRAI state/operator context into the zone dataset.",
    )
    return parser.parse_args()


def to_feature_key(value: str) -> str:
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("&", "and")
    )


def summarize_operator_metric(metric_df: pd.DataFrame, value_column: str, prefix: str) -> pd.DataFrame:
    summary = (
        metric_df.groupby("state_merge_key", dropna=False)
        .agg(
            metric_mean=(value_column, "mean"),
            metric_median=(value_column, "median"),
            metric_std=(value_column, "std"),
            metric_max=(value_column, "max"),
            metric_min=(value_column, "min"),
        )
        .reset_index()
        .rename(columns={"state_merge_key": "state"})
    )
    summary = summary.rename(
        columns={
            "metric_mean": f"{prefix}_mean",
            "metric_median": f"{prefix}_median",
            "metric_std": f"{prefix}_std",
            "metric_max": f"{prefix}_max",
            "metric_min": f"{prefix}_min",
        }
    )
    summary[f"{prefix}_gap"] = summary[f"{prefix}_max"] - summary[f"{prefix}_min"]
    summary[f"{prefix}_cv"] = summary[f"{prefix}_std"] / summary[f"{prefix}_mean"].replace(0, np.nan)
    return summary


def build_operator_share_statistics(operator_base: pd.DataFrame) -> pd.DataFrame:
    share_stats = []
    for state_key, group in operator_base.groupby("state_merge_key", dropna=False):
        shares = group["operator_row_share"].dropna().sort_values(ascending=False).to_numpy()
        if len(shares) == 0:
            continue

        dominant_share = float(shares[0])
        runner_up_share = float(shares[1]) if len(shares) > 1 else 0.0
        entropy = float(-(shares * np.log(np.clip(shares, 1e-12, None))).sum())
        normalized_entropy = entropy / np.log(len(shares)) if len(shares) > 1 else 0.0
        share_stats.append(
            {
                "state": state_key,
                "trai_operator_dominant_share": dominant_share,
                "trai_operator_runner_up_share": runner_up_share,
                "trai_operator_share_gap": dominant_share - runner_up_share,
                "trai_operator_share_hhi": float(np.square(shares).sum()),
                "trai_operator_share_entropy": entropy,
                "trai_operator_share_entropy_norm": float(normalized_entropy),
            }
        )

    return pd.DataFrame(share_stats)


def add_record_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["tile_x_bin"] = df["tile_x"].round(ZONE_ROUNDING)
    df["tile_y_bin"] = df["tile_y"].round(ZONE_ROUNDING)

    df["tests_per_device"] = df["tests"] / df["devices"].replace(0, np.nan)
    df["tests_per_device"] = df["tests_per_device"].replace([np.inf, -np.inf], np.nan).fillna(0)

    df["devices_per_test"] = df["devices"] / df["tests"].replace(0, np.nan)
    df["devices_per_test"] = df["devices_per_test"].replace([np.inf, -np.inf], np.nan).fillna(0)

    df["download_upload_ratio"] = df["avg_d_kbps"] / df["avg_u_kbps"].replace(0, np.nan)
    df["download_upload_ratio"] = df["download_upload_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0)
    return df


def aggregate_zones(df: pd.DataFrame) -> pd.DataFrame:
    zone_df = (
        df.groupby(["state", "tile_x_bin", "tile_y_bin"], dropna=False)
        .agg(
            zone_sample_count=("avg_lat_ms", "size"),
            zone_mean_download_kbps=("avg_d_kbps", "mean"),
            zone_median_download_kbps=("avg_d_kbps", "median"),
            zone_std_download_kbps=("avg_d_kbps", "std"),
            zone_mean_upload_kbps=("avg_u_kbps", "mean"),
            zone_median_upload_kbps=("avg_u_kbps", "median"),
            zone_std_upload_kbps=("avg_u_kbps", "std"),
            zone_mean_tests=("tests", "mean"),
            zone_median_tests=("tests", "median"),
            zone_std_tests=("tests", "std"),
            zone_mean_devices=("devices", "mean"),
            zone_median_devices=("devices", "median"),
            zone_std_devices=("devices", "std"),
            zone_mean_tests_per_device=("tests_per_device", "mean"),
            zone_mean_devices_per_test=("devices_per_test", "mean"),
            zone_mean_download_upload_ratio=("download_upload_ratio", "mean"),
            zone_mean_latency_ms=("avg_lat_ms", "mean"),
            zone_median_latency_ms=("avg_lat_ms", "median"),
            zone_p90_latency_ms=("avg_lat_ms", lambda s: s.quantile(0.9)),
            zone_latency_std_ms=("avg_lat_ms", "std"),
            zone_high_latency_share=("avg_lat_ms", lambda s: (s >= s.quantile(0.9)).mean()),
        )
        .reset_index()
    )
    return zone_df


def build_trai_state_context(trai_df: pd.DataFrame) -> pd.DataFrame:
    eligible = trai_df[trai_df["state_merge_key"].notna()].copy()
    eligible["operator_feature_key"] = eligible["operator"].map(to_feature_key)

    state_base = (
        eligible.groupby("state_merge_key", dropna=False)
        .agg(
            trai_operator_count=("operator", "nunique"),
            trai_lsa_count=("lsa", "nunique"),
            trai_total_rows=("speed_kbps", "size"),
            trai_mean_signal_strength=("signal_strength", "mean"),
        )
        .reset_index()
        .rename(columns={"state_merge_key": "state"})
    )

    download_df = eligible[eligible["is_download_measurement"]].copy()
    upload_df = eligible[eligible["is_upload_measurement"]].copy()

    state_download = (
        download_df.groupby("state_merge_key", dropna=False)
        .agg(
            trai_state_mean_download_kbps=("speed_kbps", "mean"),
            trai_state_median_download_kbps=("speed_kbps", "median"),
        )
        .reset_index()
        .rename(columns={"state_merge_key": "state"})
    )
    state_upload = (
        upload_df.groupby("state_merge_key", dropna=False)
        .agg(
            trai_state_mean_upload_kbps=("speed_kbps", "mean"),
            trai_state_median_upload_kbps=("speed_kbps", "median"),
        )
        .reset_index()
        .rename(columns={"state_merge_key": "state"})
    )

    operator_download = (
        download_df.groupby(["state_merge_key", "operator_feature_key"], dropna=False)
        .agg(operator_mean_download_kbps=("speed_kbps", "mean"))
        .reset_index()
    )
    operator_upload = (
        upload_df.groupby(["state_merge_key", "operator_feature_key"], dropna=False)
        .agg(operator_mean_upload_kbps=("speed_kbps", "mean"))
        .reset_index()
    )
    operator_speed_gap = (
        operator_download.groupby("state_merge_key", dropna=False)
        .agg(
            trai_best_operator_download_kbps=("operator_mean_download_kbps", "max"),
            trai_worst_operator_download_kbps=("operator_mean_download_kbps", "min"),
        )
        .reset_index()
        .rename(columns={"state_merge_key": "state"})
    )
    operator_speed_gap["trai_operator_download_gap_kbps"] = (
        operator_speed_gap["trai_best_operator_download_kbps"] - operator_speed_gap["trai_worst_operator_download_kbps"]
    )

    operator_download_stats = summarize_operator_metric(
        operator_download,
        "operator_mean_download_kbps",
        "trai_operator_download_distribution",
    )
    operator_upload_stats = summarize_operator_metric(
        operator_upload,
        "operator_mean_upload_kbps",
        "trai_operator_upload_distribution",
    )

    operator_base = (
        eligible.groupby(["state_merge_key", "operator_feature_key"], dropna=False)
        .agg(
            operator_rows=("speed_kbps", "size"),
            operator_mean_signal_strength=("signal_strength", "mean"),
        )
        .reset_index()
    )
    state_rows = (
        eligible.groupby("state_merge_key", dropna=False)
        .agg(state_rows_total=("speed_kbps", "size"))
        .reset_index()
    )
    operator_base = operator_base.merge(state_rows, on="state_merge_key", how="left")
    operator_base["operator_row_share"] = operator_base["operator_rows"] / operator_base["state_rows_total"].replace(0, np.nan)
    operator_signal_stats = summarize_operator_metric(
        operator_base,
        "operator_mean_signal_strength",
        "trai_operator_signal_distribution",
    )
    operator_share_stats = build_operator_share_statistics(operator_base)

    operator_download_wide = (
        operator_download.pivot(index="state_merge_key", columns="operator_feature_key", values="operator_mean_download_kbps")
        .add_prefix("trai_operator_download_kbps_")
        .reset_index()
        .rename(columns={"state_merge_key": "state"})
    )
    operator_upload_wide = (
        operator_upload.pivot(index="state_merge_key", columns="operator_feature_key", values="operator_mean_upload_kbps")
        .add_prefix("trai_operator_upload_kbps_")
        .reset_index()
        .rename(columns={"state_merge_key": "state"})
    )
    operator_signal_wide = (
        operator_base.pivot(index="state_merge_key", columns="operator_feature_key", values="operator_mean_signal_strength")
        .add_prefix("trai_operator_signal_strength_")
        .reset_index()
        .rename(columns={"state_merge_key": "state"})
    )
    operator_share_wide = (
        operator_base.pivot(index="state_merge_key", columns="operator_feature_key", values="operator_row_share")
        .add_prefix("trai_operator_row_share_")
        .reset_index()
        .rename(columns={"state_merge_key": "state"})
    )

    state_context = state_base.merge(state_download, on="state", how="left")
    state_context = state_context.merge(state_upload, on="state", how="left")
    state_context = state_context.merge(operator_speed_gap, on="state", how="left")
    state_context = state_context.merge(operator_download_stats, on="state", how="left")
    state_context = state_context.merge(operator_upload_stats, on="state", how="left")
    state_context = state_context.merge(operator_signal_stats, on="state", how="left")
    state_context = state_context.merge(operator_share_stats, on="state", how="left")
    state_context = state_context.merge(operator_download_wide, on="state", how="left")
    state_context = state_context.merge(operator_upload_wide, on="state", how="left")
    state_context = state_context.merge(operator_signal_wide, on="state", how="left")
    state_context = state_context.merge(operator_share_wide, on="state", how="left")

    download_operator_columns = [column for column in state_context.columns if column.startswith("trai_operator_download_kbps_")]
    for column in download_operator_columns:
        ratio_column = column.replace("trai_operator_download_kbps_", "trai_operator_download_vs_state_avg_")
        state_context[ratio_column] = state_context[column] / state_context["trai_state_mean_download_kbps"].replace(0, np.nan)

    upload_operator_columns = [column for column in state_context.columns if column.startswith("trai_operator_upload_kbps_")]
    for column in upload_operator_columns:
        ratio_column = column.replace("trai_operator_upload_kbps_", "trai_operator_upload_vs_state_avg_")
        state_context[ratio_column] = state_context[column] / state_context["trai_state_mean_upload_kbps"].replace(0, np.nan)

    signal_operator_columns = [column for column in state_context.columns if column.startswith("trai_operator_signal_strength_")]
    for column in signal_operator_columns:
        gap_column = column.replace("trai_operator_signal_strength_", "trai_operator_signal_gap_")
        state_context[gap_column] = state_context[column] - state_context["trai_mean_signal_strength"]

    return state_context


def add_zone_features(zone_df: pd.DataFrame, trai_state_context: pd.DataFrame | None = None) -> pd.DataFrame:
    zone_df = zone_df.copy()
    fill_zero_columns = [column for column in zone_df.columns if column.startswith("zone_std_") or column.endswith("_std_ms")]
    zone_df[fill_zero_columns] = zone_df[fill_zero_columns].fillna(0)

    zone_df["zone_tile_x_sq"] = zone_df["tile_x_bin"] ** 2
    zone_df["zone_tile_y_sq"] = zone_df["tile_y_bin"] ** 2
    zone_df["zone_tile_xy_interaction"] = zone_df["tile_x_bin"] * zone_df["tile_y_bin"]

    zone_df["zone_throughput_sum_kbps"] = zone_df["zone_mean_download_kbps"] + zone_df["zone_mean_upload_kbps"]
    zone_df["zone_throughput_gap_kbps"] = zone_df["zone_mean_download_kbps"] - zone_df["zone_mean_upload_kbps"]
    zone_df["zone_density_proxy"] = zone_df["zone_mean_tests"] + zone_df["zone_mean_devices"]
    zone_df["zone_usage_pressure"] = zone_df["zone_mean_tests"] * zone_df["zone_mean_devices"]
    zone_df["zone_download_cv"] = zone_df["zone_std_download_kbps"] / zone_df["zone_mean_download_kbps"].replace(0, np.nan)
    zone_df["zone_upload_cv"] = zone_df["zone_std_upload_kbps"] / zone_df["zone_mean_upload_kbps"].replace(0, np.nan)
    zone_df["zone_tests_cv"] = zone_df["zone_std_tests"] / zone_df["zone_mean_tests"].replace(0, np.nan)
    zone_df["zone_devices_cv"] = zone_df["zone_std_devices"] / zone_df["zone_mean_devices"].replace(0, np.nan)
    zone_df["zone_download_median_gap_kbps"] = zone_df["zone_mean_download_kbps"] - zone_df["zone_median_download_kbps"]
    zone_df["zone_upload_median_gap_kbps"] = zone_df["zone_mean_upload_kbps"] - zone_df["zone_median_upload_kbps"]
    zone_df["zone_tests_median_gap"] = zone_df["zone_mean_tests"] - zone_df["zone_median_tests"]
    zone_df["zone_devices_median_gap"] = zone_df["zone_mean_devices"] - zone_df["zone_median_devices"]

    variability_columns = [
        "zone_download_cv",
        "zone_upload_cv",
        "zone_tests_cv",
        "zone_devices_cv",
    ]
    zone_df[variability_columns] = zone_df[variability_columns].replace([np.inf, -np.inf], np.nan).fillna(0)

    for column in [
        "zone_mean_download_kbps",
        "zone_mean_upload_kbps",
        "zone_mean_tests",
        "zone_mean_devices",
        "zone_density_proxy",
        "zone_usage_pressure",
        "zone_sample_count",
    ]:
        zone_df[f"log_{column}"] = np.log1p(zone_df[column])

    state_context = (
        zone_df.groupby("state", dropna=False)
        .agg(
            state_zone_avg_download_kbps=("zone_mean_download_kbps", "mean"),
            state_zone_avg_upload_kbps=("zone_mean_upload_kbps", "mean"),
            state_zone_avg_tests=("zone_mean_tests", "mean"),
            state_zone_avg_devices=("zone_mean_devices", "mean"),
            state_zone_avg_density=("zone_density_proxy", "mean"),
            state_zone_avg_sample_count=("zone_sample_count", "mean"),
        )
        .reset_index()
    )
    zone_df = zone_df.merge(state_context, on="state", how="left")

    if trai_state_context is not None and not trai_state_context.empty:
        zone_df = zone_df.merge(trai_state_context, on="state", how="left")

        for numerator, denominator, feature_name in [
            ("zone_mean_download_kbps", "trai_state_mean_download_kbps", "zone_download_vs_trai_state_avg"),
            ("zone_mean_upload_kbps", "trai_state_mean_upload_kbps", "zone_upload_vs_trai_state_avg"),
        ]:
            zone_df[feature_name] = zone_df[numerator] / zone_df[denominator].replace(0, np.nan)
            zone_df[feature_name] = zone_df[feature_name].replace([np.inf, -np.inf], np.nan).fillna(1.0)

        zero_fill_columns = [
            column
            for column in zone_df.columns
            if column.startswith("trai_operator_row_share_")
            or column.endswith("_std")
            or column.endswith("_cv")
            or column.endswith("_gap")
            or column.endswith("_entropy")
            or column.endswith("_entropy_norm")
        ]
        for column in zero_fill_columns:
            if column in zone_df.columns:
                zone_df[column] = zone_df[column].fillna(0)

        neutral_fill_columns = [
            column
            for column in zone_df.columns
            if column.startswith("trai_operator_download_vs_state_avg_")
            or column.startswith("trai_operator_upload_vs_state_avg_")
        ]
        for column in neutral_fill_columns:
            zone_df[column] = zone_df[column].fillna(1.0)

        remaining_trai_columns = [column for column in zone_df.columns if column.startswith("trai_") and zone_df[column].isna().any()]
        for column in remaining_trai_columns:
            zone_df[column] = zone_df[column].fillna(zone_df[column].median())

    ratio_pairs = [
        ("zone_mean_download_kbps", "state_zone_avg_download_kbps", "zone_download_vs_state_avg"),
        ("zone_mean_upload_kbps", "state_zone_avg_upload_kbps", "zone_upload_vs_state_avg"),
        ("zone_mean_tests", "state_zone_avg_tests", "zone_tests_vs_state_avg"),
        ("zone_mean_devices", "state_zone_avg_devices", "zone_devices_vs_state_avg"),
        ("zone_density_proxy", "state_zone_avg_density", "zone_density_vs_state_avg"),
        ("zone_sample_count", "state_zone_avg_sample_count", "zone_sample_count_vs_state_avg"),
    ]
    for numerator, denominator, feature_name in ratio_pairs:
        zone_df[feature_name] = zone_df[numerator] / zone_df[denominator].replace(0, np.nan)
        zone_df[feature_name] = zone_df[feature_name].replace([np.inf, -np.inf], np.nan).fillna(0)

    return zone_df


def encode_features(zone_df: pd.DataFrame) -> pd.DataFrame:
    metadata_columns = [
        "state",
        "tile_x_bin",
        "tile_y_bin",
        "zone_mean_latency_ms",
        "zone_median_latency_ms",
        "zone_p90_latency_ms",
        "zone_latency_std_ms",
        "zone_high_latency_share",
    ]
    numeric_feature_columns = [column for column in zone_df.columns if column not in metadata_columns and column != "state"]
    model_df = zone_df[metadata_columns + numeric_feature_columns].copy()
    model_df = pd.get_dummies(model_df, columns=["state"], drop_first=False)
    return model_df


def build_support_summary(zone_df: pd.DataFrame) -> list[str]:
    quantiles = zone_df["zone_sample_count"].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).to_dict()
    return [
        f"- Min zone samples: {int(zone_df['zone_sample_count'].min())}",
        f"- P10 zone samples: {quantiles[0.1]:.1f}",
        f"- P25 zone samples: {quantiles[0.25]:.1f}",
        f"- Median zone samples: {quantiles[0.5]:.1f}",
        f"- P75 zone samples: {quantiles[0.75]:.1f}",
        f"- P90 zone samples: {quantiles[0.9]:.1f}",
        f"- Max zone samples: {int(zone_df['zone_sample_count'].max())}",
        f"- Share of zones with <= 12 samples: {(zone_df['zone_sample_count'] <= 12).mean():.4f}",
        f"- Share of zones with <= 20 samples: {(zone_df['zone_sample_count'] <= 20).mean():.4f}",
    ]


def write_outputs(
    raw_zone_df: pd.DataFrame,
    filtered_zone_df: pd.DataFrame,
    model_df: pd.DataFrame,
    with_trai_context: bool,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    suffix = "_with_trai_context" if with_trai_context else ""
    dataset_path = OUTPUT_DIR / f"india_zone_risk_dataset{suffix}.csv"
    feature_path = OUTPUT_DIR / f"india_zone_risk_feature_columns{suffix}.txt"
    report_path = REPORT_DIR / f"phase7_india_zone_risk_dataset{suffix}.txt"

    model_df.to_csv(dataset_path, index=False)
    feature_columns = [
        column
        for column in model_df.columns
        if column not in {"zone_mean_latency_ms", "zone_median_latency_ms", "zone_p90_latency_ms", "zone_latency_std_ms", "zone_high_latency_share"}
    ]
    feature_columns = [column for column in feature_columns if not column.startswith("state") or column.startswith("state_")]
    feature_path.write_text("\n".join(feature_columns), encoding="utf-8")

    dropped_zones = len(raw_zone_df) - len(filtered_zone_df)
    dropped_share = dropped_zones / max(len(raw_zone_df), 1)

    report_lines = [
        "PHASE 7 REPORT: INDIA ZONE-RISK DATASET BUILD",
        "=" * 80,
        f"Raw zone rows before support filtering: {len(raw_zone_df):,}",
        f"Zone rows: {len(model_df):,}",
        f"Columns: {model_df.shape[1]}",
        f"Minimum samples per zone: {MIN_ZONE_SAMPLES}",
        f"Dropped low-support zones: {dropped_zones:,} ({dropped_share:.4%})",
        f"Unique states encoded: {filtered_zone_df['state'].nunique()}",
        f"Mean zone P90 latency: {filtered_zone_df['zone_p90_latency_ms'].mean():.4f} ms",
        f"Median zone P90 latency: {filtered_zone_df['zone_p90_latency_ms'].median():.4f} ms",
        "",
        "Support profile after filtering:",
        *build_support_summary(filtered_zone_df),
        "",
        "Design note:",
        "- This dataset is zone-level, not raw-sample level.",
        "- The classification target is derived later from zone P90 latency using train-only thresholds.",
        "- Direct latency fields remain in the file as label sources and metadata, but they are excluded from model features.",
        "- Low-support zones are filtered more aggressively to reduce noisy labels before modeling.",
        f"- TRAI state context enabled: {with_trai_context}",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    raw_df = load_data()
    featured_df = add_record_features(raw_df)
    raw_zone_df = aggregate_zones(featured_df)
    filtered_zone_df = raw_zone_df[raw_zone_df["zone_sample_count"] >= MIN_ZONE_SAMPLES].copy()
    trai_state_context = None
    if args.with_trai_context:
        trai_df = load_trai_master()
        trai_state_context = build_trai_state_context(trai_df)
    filtered_zone_df = add_zone_features(filtered_zone_df, trai_state_context)
    model_df = encode_features(filtered_zone_df)
    write_outputs(raw_zone_df, filtered_zone_df, model_df, args.with_trai_context)

    print("India zone-risk dataset build complete.")
    print(f"Zone rows: {len(model_df):,}")
    print(f"Columns: {model_df.shape[1]}")
    print(f"TRAI context enabled: {args.with_trai_context}")


if __name__ == "__main__":
    main()