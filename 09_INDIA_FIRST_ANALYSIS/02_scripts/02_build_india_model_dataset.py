"""Phase 2 for the India-first workflow: build a model-ready dataset from original Ookla state data."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OOKLA_PATH = ROOT / "outputs_v5" / "ookla_data_with_states.csv"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

TARGET = "avg_lat_ms"


def load_data() -> pd.DataFrame:
    return pd.read_csv(OOKLA_PATH)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["tests_per_device"] = df["tests"] / df["devices"].replace(0, np.nan)
    df["tests_per_device"] = df["tests_per_device"].replace([np.inf, -np.inf], np.nan).fillna(0)

    df["devices_per_test"] = df["devices"] / df["tests"].replace(0, np.nan)
    df["devices_per_test"] = df["devices_per_test"].replace([np.inf, -np.inf], np.nan).fillna(0)

    df["download_upload_ratio"] = df["avg_d_kbps"] / df["avg_u_kbps"].replace(0, np.nan)
    df["download_upload_ratio"] = df["download_upload_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0)

    df["throughput_sum_kbps"] = df["avg_d_kbps"] + df["avg_u_kbps"]
    df["throughput_gap_kbps"] = df["avg_d_kbps"] - df["avg_u_kbps"]
    df["download_per_test"] = df["avg_d_kbps"] / df["tests"].replace(0, np.nan)
    df["download_per_test"] = df["download_per_test"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["upload_per_test"] = df["avg_u_kbps"] / df["tests"].replace(0, np.nan)
    df["upload_per_test"] = df["upload_per_test"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["download_per_device"] = df["avg_d_kbps"] / df["devices"].replace(0, np.nan)
    df["download_per_device"] = df["download_per_device"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["upload_per_device"] = df["avg_u_kbps"] / df["devices"].replace(0, np.nan)
    df["upload_per_device"] = df["upload_per_device"].replace([np.inf, -np.inf], np.nan).fillna(0)

    df["log_download_kbps"] = np.log1p(df["avg_d_kbps"])
    df["log_upload_kbps"] = np.log1p(df["avg_u_kbps"])
    df["log_tests"] = np.log1p(df["tests"])
    df["log_devices"] = np.log1p(df["devices"])

    df["tile_density_proxy"] = df["tests"] + df["devices"]
    df["log_tile_density_proxy"] = np.log1p(df["tile_density_proxy"])
    df["usage_pressure"] = df["tests"] * df["devices"]
    df["log_usage_pressure"] = np.log1p(df["usage_pressure"])

    df["tile_x_sq"] = df["tile_x"] ** 2
    df["tile_y_sq"] = df["tile_y"] ** 2
    df["tile_xy_interaction"] = df["tile_x"] * df["tile_y"]

    df["tile_x_bin"] = df["tile_x"].round(1)
    df["tile_y_bin"] = df["tile_y"].round(1)

    state_stats = (
        df.groupby("state", dropna=False)
        .agg(
            state_avg_download_kbps=("avg_d_kbps", "mean"),
            state_avg_upload_kbps=("avg_u_kbps", "mean"),
            state_avg_tests=("tests", "mean"),
            state_avg_devices=("devices", "mean"),
        )
        .reset_index()
    )
    df = df.merge(state_stats, on="state", how="left")

    cell_stats = (
        df.groupby(["tile_x_bin", "tile_y_bin"], dropna=False)
        .agg(
            cell_sample_count=("tile_x", "size"),
            cell_avg_download_kbps=("avg_d_kbps", "mean"),
            cell_avg_upload_kbps=("avg_u_kbps", "mean"),
            cell_avg_tests=("tests", "mean"),
            cell_avg_devices=("devices", "mean"),
        )
        .reset_index()
    )
    df = df.merge(cell_stats, on=["tile_x_bin", "tile_y_bin"], how="left")

    ratio_pairs = [
        ("avg_d_kbps", "state_avg_download_kbps", "download_vs_state_avg"),
        ("avg_u_kbps", "state_avg_upload_kbps", "upload_vs_state_avg"),
        ("tests", "state_avg_tests", "tests_vs_state_avg"),
        ("devices", "state_avg_devices", "devices_vs_state_avg"),
        ("avg_d_kbps", "cell_avg_download_kbps", "download_vs_cell_avg"),
        ("avg_u_kbps", "cell_avg_upload_kbps", "upload_vs_cell_avg"),
        ("tests", "cell_avg_tests", "tests_vs_cell_avg"),
        ("devices", "cell_avg_devices", "devices_vs_cell_avg"),
    ]
    for numerator, denominator, feature_name in ratio_pairs:
        df[feature_name] = df[numerator] / df[denominator].replace(0, np.nan)
        df[feature_name] = df[feature_name].replace([np.inf, -np.inf], np.nan).fillna(0)

    return df


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    base_numeric = [
        "tile_x",
        "tile_y",
        "tile_x_sq",
        "tile_y_sq",
        "tile_xy_interaction",
        "avg_d_kbps",
        "avg_u_kbps",
        "throughput_sum_kbps",
        "throughput_gap_kbps",
        "tests",
        "devices",
        "tests_per_device",
        "devices_per_test",
        "download_upload_ratio",
        "download_per_test",
        "upload_per_test",
        "download_per_device",
        "upload_per_device",
        "log_download_kbps",
        "log_upload_kbps",
        "log_tests",
        "log_devices",
        "tile_density_proxy",
        "log_tile_density_proxy",
        "usage_pressure",
        "log_usage_pressure",
        "state_avg_download_kbps",
        "state_avg_upload_kbps",
        "state_avg_tests",
        "state_avg_devices",
        "cell_sample_count",
        "cell_avg_download_kbps",
        "cell_avg_upload_kbps",
        "cell_avg_tests",
        "cell_avg_devices",
        "download_vs_state_avg",
        "upload_vs_state_avg",
        "tests_vs_state_avg",
        "devices_vs_state_avg",
        "download_vs_cell_avg",
        "upload_vs_cell_avg",
        "tests_vs_cell_avg",
        "devices_vs_cell_avg",
    ]

    model_df = df[[TARGET] + base_numeric + ["state"]].copy()
    model_df = pd.get_dummies(model_df, columns=["state"], drop_first=False)
    return model_df


def write_outputs(source_df: pd.DataFrame, model_df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    model_path = OUTPUT_DIR / "india_model_dataset.csv"
    features_path = OUTPUT_DIR / "india_feature_columns.txt"
    report_path = REPORT_DIR / "phase2_india_feature_build.txt"

    model_df.to_csv(model_path, index=False)

    feature_columns = [column for column in model_df.columns if column != TARGET]
    features_path.write_text("\n".join(feature_columns), encoding="utf-8")

    report_lines = [
        "PHASE 2 REPORT: INDIA MODEL DATASET BUILD",
        "=" * 80,
        f"Rows: {len(model_df):,}",
        f"Columns: {model_df.shape[1]}",
        f"Target column: {TARGET}",
        f"Feature count: {len(feature_columns)}",
        "",
        "Feature blocks:",
        "- Geographic: tile_x, tile_y, polynomial terms, tile interactions",
        "- Throughput: avg_d_kbps, avg_u_kbps, sums/gaps, per-test and per-device ratios, log transforms",
        "- Usage: tests, devices, cross-ratios, tile_density_proxy, usage_pressure",
        "- Context: state-level and rounded spatial-cell throughput/load aggregates with relative-position ratios",
        "- Latency-adjacent structure: throughput and usage proxies only (no target-derived columns)",
        "- Encoded categories: state_*",
        "",
        "Data quality:",
        f"- Missing values remaining: {int(model_df.isnull().sum().sum())}",
        f"- Unique states encoded: {source_df['state'].nunique()}",
    ]

    report_path.write_text("\n".join(report_lines), encoding="utf-8")


def main() -> None:
    source_df = load_data()
    featured_df = add_features(source_df)
    model_df = encode_features(featured_df)
    write_outputs(source_df, model_df)

    print("India Phase 2 dataset build complete.")
    print(f"Model dataset rows: {len(model_df):,}")
    print(f"Model dataset columns: {model_df.shape[1]}")


if __name__ == "__main__":
    main()