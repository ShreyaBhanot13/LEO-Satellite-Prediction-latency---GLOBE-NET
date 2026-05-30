"""Generate presentation-ready India anomaly charts from the official Phase 5 outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
DEFAULT_HANDOFF_DIR = Path.home() / "Downloads" / "Anomaly results" / "Indian Dataset Anomaly"
FLAGS_PATH = OUTPUT_DIR / "india_test_predictions_with_anomaly_flags.csv"
STATE_SUMMARY_PATH = OUTPUT_DIR / "india_state_anomaly_summary.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_HANDOFF_DIR,
        help="Folder to write the presentation-ready India anomaly charts.",
    )
    return parser.parse_args()


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    anomaly_flags = pd.read_csv(FLAGS_PATH)
    state_summary = pd.read_csv(STATE_SUMMARY_PATH)
    return anomaly_flags, state_summary


def apply_chart_style() -> None:
    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )


def plot_residual_distribution(anomaly_flags: pd.DataFrame, destination: Path) -> None:
    p95 = anomaly_flags.loc[anomaly_flags["residual_underperforming_p95"], "residual_ms"].min()
    p99 = anomaly_flags.loc[anomaly_flags["residual_severe_p99"], "residual_ms"].min()
    p01 = anomaly_flags.loc[anomaly_flags["better_than_expected_p01"], "residual_ms"].max()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(anomaly_flags["residual_ms"], bins=80, color="#4C78A8", edgecolor="white", alpha=0.9)
    ax.axvline(p95, color="#E45756", linestyle="--", linewidth=2, label=f"P95 underperformance ({p95:.2f} ms)")
    ax.axvline(p99, color="#B22222", linestyle=":", linewidth=2, label=f"P99 severe ({p99:.2f} ms)")
    ax.axvline(p01, color="#2E8B57", linestyle="--", linewidth=2, label=f"P01 better-than-expected ({p01:.2f} ms)")
    ax.set_title("India Residual Distribution for Phase 5 Anomaly Detection")
    ax.set_xlabel("Residual (Actual Latency - Predicted Latency) in ms")
    ax.set_ylabel("Number of Test Samples")
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(destination / "india_residual_distribution.png", bbox_inches="tight")
    plt.close(fig)


def plot_actual_vs_predicted(anomaly_flags: pd.DataFrame, destination: Path) -> None:
    sampled_normal = anomaly_flags.loc[~anomaly_flags["dual_signal_anomaly"]].sample(
        n=min(12000, int((~anomaly_flags["dual_signal_anomaly"]).sum())),
        random_state=42,
    )
    dual_signal = anomaly_flags.loc[anomaly_flags["dual_signal_anomaly"]]
    critical = anomaly_flags.loc[anomaly_flags["priority_level"] == "critical"]

    lower_bound = min(anomaly_flags["actual_latency_ms"].min(), anomaly_flags["predicted_latency_ms"].min())
    upper_bound = max(anomaly_flags["actual_latency_ms"].quantile(0.995), anomaly_flags["predicted_latency_ms"].quantile(0.995))

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(
        sampled_normal["actual_latency_ms"],
        sampled_normal["predicted_latency_ms"],
        s=8,
        alpha=0.18,
        color="#9AA5B1",
        label="Other test samples",
    )
    ax.scatter(
        dual_signal["actual_latency_ms"],
        dual_signal["predicted_latency_ms"],
        s=18,
        alpha=0.55,
        color="#F28E2B",
        label="Dual-signal anomalies",
    )
    ax.scatter(
        critical["actual_latency_ms"],
        critical["predicted_latency_ms"],
        s=28,
        alpha=0.8,
        color="#B22222",
        label="Critical anomalies",
    )
    ax.plot([lower_bound, upper_bound], [lower_bound, upper_bound], linestyle="--", color="black", linewidth=1.5, label="Perfect prediction")
    ax.set_xlim(lower_bound, upper_bound)
    ax.set_ylim(lower_bound, upper_bound)
    ax.set_title("India Actual vs Predicted Latency with Dual-Signal Anomalies")
    ax.set_xlabel("Actual Latency (ms)")
    ax.set_ylabel("Predicted Latency (ms)")
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(destination / "india_actual_vs_predicted_latency.png", bbox_inches="tight")
    plt.close(fig)


def plot_top_states(state_summary: pd.DataFrame, destination: Path) -> None:
    top_states = state_summary.nlargest(10, "dual_signal_rate").sort_values("dual_signal_rate", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    bars = ax.barh(top_states["state"], top_states["dual_signal_rate"], color="#F28E2B", edgecolor="#8C4F12")
    ax.set_title("Top Indian States by Dual-Signal Anomaly Rate")
    ax.set_xlabel("Dual-Signal Anomaly Rate")
    ax.set_ylabel("State")
    ax.set_xlim(0, float(top_states["dual_signal_rate"].max()) * 1.15)

    for bar, rate in zip(bars, top_states["dual_signal_rate"]):
        ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2, f"{rate:.3f}", va="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(destination / "india_top_states_dual_signal_rate.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)

    apply_chart_style()
    anomaly_flags, state_summary = load_inputs()
    plot_residual_distribution(anomaly_flags, args.destination)
    plot_actual_vs_predicted(anomaly_flags, args.destination)
    plot_top_states(state_summary, args.destination)

    print(f"Charts written to {args.destination}")


if __name__ == "__main__":
    main()