from __future__ import annotations

import html
import json
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"
INDIA_GEOJSON_PATH = ASSET_DIR / "india_states.geojson"

STATE_SUMMARY_PATH = OUTPUT_DIR / "india_zone_risk_state_summary.csv"
FULL_ZONE_DATASET_PATH = OUTPUT_DIR / "india_zone_risk_dataset.csv"
DETAILED_PREDICTIONS_PATH = OUTPUT_DIR / "india_zone_risk_predictions_detailed.csv"
KARNATAKA_TOP_PATH = OUTPUT_DIR / "karnataka_top_high_risk_zones.csv"
KARNATAKA_ALL_PATH = OUTPUT_DIR / "karnataka_zone_risk_all_test_zones.csv"
MODEL_PATH = OUTPUT_DIR / "india_best_zone_risk_model.pkl"
SHAP_GLOBAL_PATH = OUTPUT_DIR / "india_zone_risk_shap_global_importance.csv"
SHAP_FAMILY_PATH = OUTPUT_DIR / "india_zone_risk_shap_family_importance.csv"
PHASE9_REPORT_PATH = REPORT_DIR / "phase9_india_zone_risk_shap_explainability.txt"
PHASE10_REPORT_PATH = REPORT_DIR / "phase10_zone_risk_state_and_karnataka_summary.txt"
TRAI_OPERATOR_SUMMARY_PATH = OUTPUT_DIR / "trai_2025_state_service_provider_summary.csv"
PHASE5_RESULTS_PATH = ROOT / "outputs_v5" / "phase5_results.csv"
PHASE5_REPORT_PATH = ROOT / "PHASE5_FINAL_MODEL_REPORT.txt"
FOREIGN_ANOMALY_DIR = ROOT / "Anomaly_detection_updated" / "PERSON4_UPDATED_ANOMALY_FOLDER" / "Foreign dataset Anomaly"
FOREIGN_ANOMALY_SUMMARY_PATH = FOREIGN_ANOMALY_DIR / "foreign_reference_anomaly_summary.txt"
FOREIGN_ANOMALY_RESULTS_PATH = FOREIGN_ANOMALY_DIR / "foreign_reference_anomaly_results.csv"
FOREIGN_ANOMALY_FEATURES_PATH = FOREIGN_ANOMALY_DIR / "foreign_reference_anomaly_feature_importance.csv"

STATE_CONTEXT_COLUMNS = [
    "state_zone_avg_download_kbps",
    "state_zone_avg_upload_kbps",
    "state_zone_avg_tests",
    "state_zone_avg_devices",
    "state_zone_avg_density",
    "state_zone_avg_sample_count",
]

FORM_INPUT_COLUMNS = [
    "tile_x_bin",
    "tile_y_bin",
    "zone_sample_count",
    "zone_mean_download_kbps",
    "zone_median_download_kbps",
    "zone_std_download_kbps",
    "zone_mean_upload_kbps",
    "zone_median_upload_kbps",
    "zone_std_upload_kbps",
    "zone_mean_tests",
    "zone_median_tests",
    "zone_std_tests",
    "zone_mean_devices",
    "zone_median_devices",
    "zone_std_devices",
]


st.set_page_config(
    page_title="GLOBE-NET: Global Internet & LEO Benchmarking",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

pio.templates.default = "plotly_white"


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        /* Custom style for Streamlit download button */
        .stDownloadButton > button {
            background: var(--accent, #0f6d5f) !important;
            color: #fff !important;
            border-radius: 16px !important;
            border: none !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            padding: 0.7rem 2.2rem !important;
            margin: 0.7rem 0 1.2rem 0 !important;
            box-shadow: 0 4px 18px rgba(16, 36, 58, 0.08);
            transition: background 0.2s;
        }
        .stDownloadButton > button:hover {
            background: var(--accent-2, #e36414) !important;
            color: #fff !important;
        }
        :root {
            --ink: #112132;
            --muted: #596779;
            --accent: #0f6d5f;
            --accent-2: #e36414;
            --card: rgba(255, 252, 246, 0.92);
            --line: rgba(17, 33, 50, 0.10);
            --cream: #f7f3ea;
            --shadow: 0 16px 36px rgba(17, 24, 39, 0.08);
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 0%, rgba(15, 109, 95, 0.18), transparent 28%),
                radial-gradient(circle at 85% 8%, rgba(227, 100, 20, 0.18), transparent 25%),
                linear-gradient(180deg, #f7f3ea 0%, #f0ece1 100%);
            color: var(--ink);
        }

        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"] {
            display: none;
        }

        .block-container {
            padding-top: 0.35rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            font-family: Georgia, "Palatino Linotype", serif;
            letter-spacing: -0.02em;
            color: var(--ink);
        }

        p, li, div, label, span {
            font-family: "Aptos", "Segoe UI", "Trebuchet MS", sans-serif;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
            background: rgba(255, 255, 255, 0.28);
            border: 1px solid rgba(17, 33, 50, 0.08);
            border-radius: 18px;
            padding: 0.35rem;
            margin-bottom: 0.75rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 14px;
            padding: 0.6rem 0.95rem;
            color: var(--muted);
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            background: rgba(16, 36, 58, 0.94);
            color: var(--cream);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(255, 250, 242, 0.98) 0%, rgba(244, 238, 227, 0.98) 100%);
            border-right: 1px solid rgba(17, 33, 50, 0.08);
        }

        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: var(--ink) !important;
        }

        div[data-testid="stMetric"] {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 0.85rem 1rem;
            box-shadow: var(--shadow);
        }

        label[data-testid="stMetricLabel"],
        label[data-testid="stMetricLabel"] *,
        label[data-testid="stWidgetLabel"],
        label[data-testid="stWidgetLabel"] *,
        .stSlider label,
        .stSlider p,
        .stSlider span {
            color: var(--ink) !important;
        }

        label[data-testid="stMetricLabel"] {
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.75rem;
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: var(--ink) !important;
        }

        .hero {
            background: linear-gradient(140deg, #10243a 0%, #1c4f7b 58%, #e36414 135%);
            color: #f7f3ea;
            padding: 1.6rem 1.8rem;
            border-radius: 28px;
            box-shadow: 0 20px 50px rgba(16, 36, 58, 0.18);
            margin-bottom: 1rem;
        }

        .hero h1 {
            color: #f7f3ea;
            margin: 0;
            font-size: 2.1rem;
        }

        .hero p {
            color: rgba(247, 243, 234, 0.88);
            line-height: 1.55;
            margin: 0.55rem 0 0 0;
            font-size: 1rem;
        }

        .eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.78rem;
            color: rgba(247, 243, 234, 0.8);
            margin-bottom: 0.45rem;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.9rem;
        }

        .chip {
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: #f7f3ea;
            border-radius: 999px;
            padding: 0.32rem 0.8rem;
            font-size: 0.88rem;
            font-weight: 600;
        }

        .card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 28px rgba(17, 24, 39, 0.05);
            margin-bottom: 0.9rem;
        }

        .card-title {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            color: #33506b;
            margin-bottom: 0.45rem;
            font-weight: 700;
        }

        .card-copy {
            color: var(--muted);
            line-height: 1.55;
            font-size: 0.96rem;
            margin: 0;
        }

        .deck-step {
            border-left: 4px solid var(--accent);
            padding-left: 0.75rem;
            margin-bottom: 0.65rem;
            color: var(--ink);
        }

        .section-intro {
            background: rgba(255, 255, 255, 0.46);
            border: 1px solid rgba(17, 33, 50, 0.08);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 10px 24px rgba(17, 24, 39, 0.04);
        }

        .section-intro p {
            margin: 0;
            color: var(--muted);
            line-height: 1.55;
        }

        .mini-note {
            font-size: 0.92rem;
            color: var(--muted);
            margin-top: 0.25rem;
        }

        .spotlight-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 0.4rem 0 1rem 0;
        }

        .spotlight-card {
            background: linear-gradient(180deg, rgba(255, 252, 246, 0.96) 0%, rgba(249, 244, 235, 0.92) 100%);
            border: 1px solid rgba(17, 33, 50, 0.08);
            border-radius: 22px;
            padding: 1rem 1.05rem;
            box-shadow: 0 14px 30px rgba(17, 24, 39, 0.05);
        }

        .spotlight-kicker {
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.72rem;
            color: #33506b;
            margin-bottom: 0.3rem;
            font-weight: 700;
        }

        .spotlight-title {
            font-family: Georgia, "Palatino Linotype", serif;
            color: var(--ink);
            font-size: 1.15rem;
            margin-bottom: 0.35rem;
        }

        .spotlight-value {
            font-size: 1.9rem;
            line-height: 1;
            color: var(--accent-2);
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .spotlight-copy {
            color: var(--muted);
            line-height: 1.5;
            font-size: 0.94rem;
            margin: 0;
        }

        @media (max-width: 900px) {
            .spotlight-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_geojson(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_resource(show_spinner=False)
def load_model_payload() -> dict[str, object]:
    return joblib.load(MODEL_PATH)


def ensure_files_exist(paths: list[Path]) -> None:
    missing = [path.relative_to(ROOT).as_posix() for path in paths if not path.exists()]
    if missing:
        st.error("Missing required dashboard artifacts.")
        for path in missing:
            st.write(f"- {path}")
        st.stop()


def decode_state(df: pd.DataFrame) -> pd.Series:
    state_columns = [
        column
        for column in df.columns
        if column.startswith("state_") and not column.startswith("state_zone_avg_")
    ]
    state_values = df[state_columns].astype(float)
    decoded = state_values.idxmax(axis=1).str.replace("state_", "", regex=False)
    return decoded


def extract_metric(report_text: str, label: str) -> str:
    match = re.search(rf"{re.escape(label)}:\s*([^\n]+)", report_text)
    return match.group(1).strip() if match else "N/A"


def extract_float(report_text: str, label: str) -> float:
    value = extract_metric(report_text, label)
    match = re.search(r"-?\d+(?:\.\d+)?", value)
    return float(match.group(0)) if match else float("nan")


def extract_int(report_text: str, label: str) -> int:
    value = extract_metric(report_text, label)
    match = re.search(r"\d[\d,]*", value)
    return int(match.group(0).replace(",", "")) if match else 0


def normalize_state_name(name: str) -> str:
    normalized = name.lower().replace("&", "and")
    normalized = normalized.replace("nct of ", "")
    normalized = normalized.replace(" islands", "")
    normalized = normalized.replace(" island", "")
    normalized = normalized.replace("pondicherry", "puducherry")
    normalized = normalized.replace("orissa", "odisha")
    normalized = normalized.replace("uttaranchal", "uttarakhand")
    normalized = re.sub(r"\s+", " ", normalized).strip()

    aliases = {
        "andaman and nicobar": "andaman and nicobar",
        "andaman and nicobar islands": "andaman and nicobar",
        "dadra and nagar haveli and daman and diu": "dadra and nagar haveli and daman and diu",
        "jammu and kashmir": "jammu and kashmir",
        "delhi": "delhi",
    }
    return aliases.get(normalized, normalized)


def parse_phase9_metrics(report_text: str) -> dict[str, object]:
    return {
        "model": extract_metric(report_text, "Model explained"),
        "threshold": extract_metric(report_text, "Risk threshold"),
        "test_zones": extract_metric(report_text, "Test zones available"),
        "test_zone_count": extract_int(report_text, "Test zones available"),
        "feature_count": extract_metric(report_text, "Feature count"),
        "accuracy": extract_float(report_text, "Validated accuracy"),
        "balanced_accuracy": extract_float(report_text, "Validated balanced accuracy"),
        "macro_f1": extract_float(report_text, "Validated macro F1"),
        "high_risk_f1": extract_float(report_text, "Validated high-risk F1"),
        "precision": extract_float(report_text, "Validated high-risk precision"),
        "recall": extract_float(report_text, "Validated high-risk recall"),
        "risk_cutoff_ms": extract_float(report_text, "Risk threshold"),
    }


def parse_phase5_metrics(report_text: str) -> dict[str, object]:
    return {
        "model": extract_metric(report_text, "MODEL"),
        "r2": extract_float(report_text, "R²"),
        "rmse": extract_float(report_text, "RMSE"),
        "mae": extract_float(report_text, "MAE"),
    }


def parse_foreign_anomaly_metrics(report_text: str) -> dict[str, object]:
    return {
        "samples": extract_int(report_text, "Total test samples"),
        "anomalies": extract_int(report_text, "Reference high-risk anomalies"),
        "share_fraction": extract_float(report_text, "High-risk percentage") / 100.0,
    }


def format_percent(value: float) -> str:
    if value == 0:
        return "All stable"
    return f"{value:.1%}"


def format_float(value: float, suffix: str = "") -> str:
    return f"{value:,.1f}{suffix}"


def format_brief_percent(value: float) -> str:
    if value == 0:
        return "All stable"
    return f"{value * 100:.0f}%"


def describe_probability(probability: float) -> str:
    if probability >= 0.75:
        return "Very likely to need attention"
    if probability >= 0.55:
        return "Some risk signs are showing"
    if probability >= 0.35:
        return "Mixed picture"
    return "Looks comparatively stable"


def render_section_intro(title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="section-intro">
            <strong>{title}</strong>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_spotlight_cards(cards: list[dict[str, str]]) -> None:
    card_html = "".join(
        (
            '<div class="spotlight-card">'
            f'<div class="spotlight-kicker">{html.escape(card["kicker"])}</div>'
            f'<div class="spotlight-title">{html.escape(card["title"])}</div>'
            f'<div class="spotlight-value">{html.escape(card["value"])}</div>'
            f'<p class="spotlight-copy">{html.escape(card["copy"])}</p>'
            '</div>'
        )
        for card in cards
    )
    st.markdown(f"<div class='spotlight-grid'>{card_html}</div>", unsafe_allow_html=True)


def apply_figure_style(figure: go.Figure, title_size: int = 22, font_size: int = 13) -> go.Figure:
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#183149", "size": font_size, "family": "Aptos, Segoe UI, Trebuchet MS, sans-serif"},
        title={"font": {"color": "#183149", "size": title_size}},
        legend={
            "font": {"color": "#183149", "size": font_size},
            "title_font": {"color": "#183149", "size": font_size},
        },
        coloraxis_colorbar={
            "title": {"font": {"color": "#183149", "size": font_size}},
            "tickfont": {"color": "#183149", "size": max(font_size - 1, 11)},
        },
    )
    figure.update_xaxes(
        title_font={"color": "#183149", "size": font_size},
        tickfont={"color": "#183149", "size": max(font_size - 1, 11)},
        gridcolor="rgba(29, 79, 122, 0.10)",
        zerolinecolor="rgba(29, 79, 122, 0.16)",
    )
    figure.update_yaxes(
        title_font={"color": "#183149", "size": font_size},
        tickfont={"color": "#183149", "size": max(font_size - 1, 11)},
        gridcolor="rgba(29, 79, 122, 0.10)",
        zerolinecolor="rgba(29, 79, 122, 0.16)",
    )
    figure.update_annotations(font={"color": "#183149", "size": font_size})
    for trace in figure.data:
        try:
            trace.update(textfont={"color": "#183149", "size": max(font_size - 1, 11)})
        except ValueError:
            continue
    return figure


def friendly_foreign_feature_name(feature_name: str) -> str:
    labels = {
        "ping_stddev": "Latency variation",
        "ping_worst": "Worst observed latency",
        "ping_best": "Best observed latency",
        "download": "Download speed",
        "download_std": "Download speed variation",
        "upload": "Upload speed",
        "upload_std": "Upload speed variation",
        "barom": "Air pressure",
        "temp": "Temperature",
        "hour": "Hour of day",
        "day": "Day of month",
        "month": "Month",
        "day_of_week": "Day of week",
        "rain": "Rainfall",
        "ping_packet_loss": "Packet loss",
        "packet_loss_flag": "Packet loss flag",
        "ping_packets_send": "Packets sent",
        "measurement_steps": "Measurement steps",
    }
    return labels.get(feature_name, feature_name.replace("_", " ").title())


def prepare_foreign_region_summary(foreign_results: pd.DataFrame) -> pd.DataFrame:
    results = foreign_results.copy()
    results["final_high_risk"] = results["final_high_risk"].astype(str).str.lower().eq("true")
    results["display_region"] = results["region"].map(
        {
            "Osnabrück": "Germany",
            "Enschede": "Netherlands",
        }
    ).fillna(results["region"])

    summary = (
        results.groupby("display_region", dropna=False)
        .agg(
            samples=("display_region", "size"),
            flagged_cases=("final_high_risk", "sum"),
            flagged_share=("final_high_risk", "mean"),
            avg_residual=("residual_actual_minus_predicted", "mean"),
        )
        .reset_index()
    )
    return summary


def prepare_global_reference_sites(india_zone_count: int, foreign_region_summary: pd.DataFrame) -> pd.DataFrame:
    summary_lookup = foreign_region_summary.set_index("display_region") if not foreign_region_summary.empty else pd.DataFrame()

    def samples_for(region_name: str) -> int:
        if isinstance(summary_lookup, pd.DataFrame) and region_name in summary_lookup.index:
            return int(summary_lookup.loc[region_name, "samples"])
        return 0

    records = [
        {
            "place": "India",
            "country": "India",
            "lat": 22.6,
            "lon": 78.9,
            "role": "Primary coverage view",
            "marker_size": 22,
            "detail": f"{india_zone_count:,} reviewed areas in the India coverage view" if india_zone_count else "India coverage view",
        },
        {
            "place": "Osnabrück",
            "country": "Germany",
            "lat": 52.28,
            "lon": 8.05,
            "role": "Foreign benchmark",
            "marker_size": 16,
            "detail": f"{samples_for('Germany'):,} foreign benchmark tests" if samples_for("Germany") else "Germany benchmark site",
        },
        {
            "place": "Enschede",
            "country": "Netherlands",
            "lat": 52.22,
            "lon": 6.89,
            "role": "Foreign benchmark",
            "marker_size": 16,
            "detail": f"{samples_for('Netherlands'):,} foreign benchmark tests" if samples_for("Netherlands") else "Netherlands benchmark site",
        },
    ]
    return pd.DataFrame(records)


def build_global_reference_cards(
    metrics: dict[str, object],
    phase5_metrics: dict[str, object],
    foreign_metrics: dict[str, object],
    foreign_region_summary: pd.DataFrame,
) -> list[dict[str, str]]:
    summary_lookup = foreign_region_summary.set_index("display_region") if not foreign_region_summary.empty else pd.DataFrame()

    def flagged_share(region_name: str) -> str:
        if isinstance(summary_lookup, pd.DataFrame) and region_name in summary_lookup.index:
            return format_percent(float(summary_lookup.loc[region_name, "flagged_share"]))
        return "N/A"

    return [
        {
            "kicker": "Primary Coverage",
            "title": "India",
            "value": f"{int(metrics.get('test_zone_count', 0)):,}",
            "copy": "Reviewed areas in the India coverage view used across this site.",
        },
        {
            "kicker": "Benchmark",
            "title": "Germany + Netherlands",
            "value": f"{phase5_metrics['r2']:.2f}",
            "copy": "Reference score from the earlier Europe benchmark track, kept here for international context.",
        },
        {
            "kicker": "International Reference",
            "title": "Foreign Weak Cases",
            "value": format_percent(float(foreign_metrics["share_fraction"])),
            "copy": f"Share marked as unusually weak in the earlier foreign reference run. Germany: {flagged_share('Germany')} and Netherlands: {flagged_share('Netherlands')}.",
        },
    ]


def compute_weighted_mean(group: pd.DataFrame, value_column: str, weight_column: str) -> float:
    weights = group[weight_column].fillna(0).astype(float)
    values = group[value_column].astype(float)
    valid = values.notna() & weights.gt(0)
    if not valid.any():
        return float("nan")
    return float(np.average(values[valid], weights=weights[valid]))


def prepare_zone_data(zone_dataset: pd.DataFrame, state_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    enriched = zone_dataset.copy()
    enriched["decoded_state"] = decode_state(enriched)

    centroids = (
        enriched.groupby("decoded_state", dropna=False)
        .agg(
            state_lat=("tile_y_bin", "mean"),
            state_lon=("tile_x_bin", "mean"),
        )
        .reset_index()
        .rename(columns={"decoded_state": "state"})
    )
    state_geo = state_summary.merge(centroids, on="state", how="left")
    return enriched, state_geo


def prepare_state_map_data(state_geo: pd.DataFrame, india_geojson: dict[str, object]) -> pd.DataFrame:
    geojson_name_map: dict[str, str] = {}
    for feature in india_geojson.get("features", []):
        raw_name = str(feature.get("properties", {}).get("ST_NM", "")).strip()
        if raw_name:
            geojson_name_map[normalize_state_name(raw_name)] = raw_name

    mapped = state_geo.copy()
    mapped["map_state_name"] = mapped["state"].map(
        lambda state_name: geojson_name_map.get(normalize_state_name(state_name), state_name)
    )
    return mapped


def prepare_state_context(zone_dataset: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        zone_dataset.groupby("decoded_state", dropna=False)
        .agg(
            zone_median_download_kbps_default=("zone_median_download_kbps", "median"),
            zone_std_download_kbps_default=("zone_std_download_kbps", "median"),
            zone_median_upload_kbps_default=("zone_median_upload_kbps", "median"),
            zone_std_upload_kbps_default=("zone_std_upload_kbps", "median"),
            zone_median_tests_default=("zone_median_tests", "median"),
            zone_std_tests_default=("zone_std_tests", "median"),
            zone_median_devices_default=("zone_median_devices", "median"),
            zone_std_devices_default=("zone_std_devices", "median"),
            state_zone_avg_download_kbps=("state_zone_avg_download_kbps", "mean"),
            state_zone_avg_upload_kbps=("state_zone_avg_upload_kbps", "mean"),
            state_zone_avg_tests=("state_zone_avg_tests", "mean"),
            state_zone_avg_devices=("state_zone_avg_devices", "mean"),
            state_zone_avg_density=("state_zone_avg_density", "mean"),
            state_zone_avg_sample_count=("state_zone_avg_sample_count", "mean"),
        )
        .reset_index()
        .rename(columns={"decoded_state": "state"})
    )
    return grouped


def prepare_operator_context(trai_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    eligible = trai_summary[trai_summary["state_merge_key"].notna()].copy()

    records: list[dict[str, object]] = []
    for (state_name, operator_name), group in eligible.groupby(["state_merge_key", "operator"], dropna=False):
        operator_rows = int(group["row_count"].fillna(0).sum())
        records.append(
            {
                "state": state_name,
                "operator": operator_name,
                "operator_rows": operator_rows,
                "weighted_mean_speed_kbps": compute_weighted_mean(group, "mean_speed_kbps", "row_count"),
                "weighted_mean_signal_strength": compute_weighted_mean(group, "mean_signal_strength", "row_count"),
            }
        )

    operator_state = pd.DataFrame(records)
    if operator_state.empty:
        return operator_state, pd.DataFrame(columns=[
            "state",
            "operator_count",
            "dominant_operator",
            "dominant_operator_share",
            "fastest_operator",
            "fastest_operator_speed_kbps",
            "operator_speed_gap_kbps",
            "operator_signal_gap",
        ])

    state_totals = (
        operator_state.groupby("state", dropna=False)
        .agg(state_operator_rows=("operator_rows", "sum"))
        .reset_index()
    )
    operator_state = operator_state.merge(state_totals, on="state", how="left")
    operator_state["operator_share"] = operator_state["operator_rows"] / operator_state["state_operator_rows"].replace(0, np.nan)

    state_speed_avg = (
        operator_state.groupby("state", dropna=False)
        .agg(state_operator_avg_speed_kbps=("weighted_mean_speed_kbps", "mean"))
        .reset_index()
    )
    operator_state = operator_state.merge(state_speed_avg, on="state", how="left")
    operator_state["speed_vs_state_avg"] = operator_state["weighted_mean_speed_kbps"] / operator_state["state_operator_avg_speed_kbps"].replace(0, np.nan)

    dominant = (
        operator_state.sort_values(["state", "operator_share", "weighted_mean_speed_kbps"], ascending=[True, False, False])
        .groupby("state", dropna=False)
        .first()
        .reset_index()[["state", "operator", "operator_share"]]
        .rename(columns={"operator": "dominant_operator", "operator_share": "dominant_operator_share"})
    )
    fastest = (
        operator_state.sort_values(["state", "weighted_mean_speed_kbps", "operator_share"], ascending=[True, False, False])
        .groupby("state", dropna=False)
        .first()
        .reset_index()[["state", "operator", "weighted_mean_speed_kbps"]]
        .rename(columns={"operator": "fastest_operator", "weighted_mean_speed_kbps": "fastest_operator_speed_kbps"})
    )
    state_snapshot = (
        operator_state.groupby("state", dropna=False)
        .agg(
            operator_count=("operator", "nunique"),
            operator_speed_gap_kbps=("weighted_mean_speed_kbps", lambda s: float(s.max() - s.min())),
            operator_signal_gap=("weighted_mean_signal_strength", lambda s: float(s.max() - s.min())),
        )
        .reset_index()
        .merge(dominant, on="state", how="left")
        .merge(fastest, on="state", how="left")
    )
    return operator_state, state_snapshot


def build_state_rank_chart(state_summary: pd.DataFrame, min_zones: int) -> go.Figure:
    filtered = state_summary[state_summary["zones"] >= min_zones].copy()
    filtered = filtered.sort_values("predicted_high_risk_rate", ascending=False).head(12)
    filtered = filtered.sort_values("predicted_high_risk_rate", ascending=True)
    figure = px.bar(
        filtered,
        x="predicted_high_risk_rate",
        y="state",
        orientation="h",
        color="mean_high_risk_probability",
        text="predicted_high_risk_rate",
        color_continuous_scale=["#d9ece8", "#0f6d5f", "#062f27"],
        labels={
            "predicted_high_risk_rate": "Share of areas needing attention",
            "state": "State",
            "mean_high_risk_probability": "Average attention score",
        },
    )
    figure.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    figure.update_layout(
        height=520,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar_title="Attention score",
    )
    figure.update_traces(texttemplate="%{text:.1%}", textposition="outside", textfont={"color": "#183149", "size": 12})
    figure.update_layout(coloraxis_colorbar={"title": "Attention score", "thickness": 16, "len": 0.72})
    return apply_figure_style(figure)


def build_india_state_map(
    state_geo: pd.DataFrame,
    india_geojson: dict[str, object],
    metric_column: str,
    min_zones: int,
) -> go.Figure:
    filtered = state_geo[state_geo["zones"] >= min_zones].copy()
    figure = px.choropleth(
        filtered,
        geojson=india_geojson,
        featureidkey="properties.ST_NM",
        locations="map_state_name",
        color=metric_column,
        hover_name="state",
        hover_data={
            "predicted_high_risk_rate": ":.3f",
            "actual_high_risk_rate": ":.3f",
            "mean_zone_p90_latency_ms": ":.1f",
            "zones": True,
            "state_lat": False,
            "state_lon": False,
        },
        color_continuous_scale=["#efe4cf", "#f0b46a", "#e36414", "#8f2d12"],
        labels={
            "predicted_high_risk_rate": "Share needing attention",
            "actual_high_risk_rate": "Reported weaker-area share",
            "mean_zone_p90_latency_ms": "Typical slower-end latency (ms)",
            "zones": "Areas reviewed",
        },
    )
    figure.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        bgcolor="rgba(0,0,0,0)",
    )
    figure.update_traces(marker_line_color="#f7f3ea", marker_line_width=0.9)

    label_points = filtered.sort_values(metric_column, ascending=False).head(8)
    figure.add_trace(
        go.Scattergeo(
            lat=label_points["state_lat"],
            lon=label_points["state_lon"],
            text=label_points["state"],
            mode="text",
            textfont={"size": 11, "color": "#183149", "family": "Georgia, serif"},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    figure.update_layout(
        height=540,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar={"title": "Attention level", "thickness": 16, "len": 0.72},
    )
    return apply_figure_style(figure)


def build_state_scatter(state_summary: pd.DataFrame, min_zones: int) -> go.Figure:
    filtered = state_summary[state_summary["zones"] >= min_zones].copy()
    figure = px.scatter(
        filtered,
        x="actual_high_risk_rate",
        y="predicted_high_risk_rate",
        size="zones",
        color="mean_zone_p90_latency_ms",
        hover_name="state",
        hover_data={
            "zones": True,
            "precision": ":.2f",
            "recall": ":.2f",
            "high_risk_f1": ":.2f",
            "mean_zone_p90_latency_ms": ":.1f",
        },
        color_continuous_scale=["#d7e6ef", "#1d4f7a", "#e36414"],
        labels={
            "actual_high_risk_rate": "Observed share of weaker areas",
            "predicted_high_risk_rate": "Estimated share of weaker areas",
            "mean_zone_p90_latency_ms": "Typical slower-end latency (ms)",
        },
    )
    figure.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line={"color": "#607080", "dash": "dash"})
    figure.update_layout(
        height=520,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return apply_figure_style(figure)


def build_zone_geo_map(zone_frame: pd.DataFrame, title: str, color_column: str, size_column: str) -> go.Figure:
    plotted = zone_frame.copy()
    if "predicted_high_risk" in plotted.columns:
        plotted["prediction_label"] = plotted["predicted_high_risk"].map({0: "Stable", 1: "Needs attention"})
    else:
        plotted["prediction_label"] = "Zone"

    figure = px.scatter_geo(
        plotted,
        lat="tile_y_bin",
        lon="tile_x_bin",
        size=size_column,
        color=color_column,
        symbol="prediction_label",
        hover_name="decoded_state" if "decoded_state" in plotted.columns else None,
        hover_data={
            "zone_p90_latency_ms": ":.1f",
            "risk_gap_ms": ":.1f" if "risk_gap_ms" in plotted.columns else False,
            "high_risk_probability": ":.3f" if "high_risk_probability" in plotted.columns else False,
            "zone_mean_download_kbps": ":.0f" if "zone_mean_download_kbps" in plotted.columns else False,
            "zone_mean_upload_kbps": ":.0f" if "zone_mean_upload_kbps" in plotted.columns else False,
            "prediction_correct": True if "prediction_correct" in plotted.columns else False,
        },
        size_max=22,
        color_continuous_scale=["#d9ece8", "#0f6d5f", "#062f27"],
        labels={
            "tile_y_bin": "Latitude bin",
            "tile_x_bin": "Longitude bin",
            color_column: color_column.replace("_", " ").title(),
        },
        title=title,
    )
    lat_padding = 1.0
    lon_padding = 1.0
    figure.update_geos(
        showcountries=True,
        countrycolor="#4b5c6f",
        showland=True,
        landcolor="#f5efe5",
        showocean=True,
        oceancolor="#dfeaf3",
        lataxis_range=[max(5.0, plotted["tile_y_bin"].min() - lat_padding), min(38.0, plotted["tile_y_bin"].max() + lat_padding)],
        lonaxis_range=[max(67.0, plotted["tile_x_bin"].min() - lon_padding), min(98.0, plotted["tile_x_bin"].max() + lon_padding)],
    )
    figure.update_layout(
        height=540,
        margin={"l": 10, "r": 10, "t": 88, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={
            "title": {"text": "Status"},
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0.60,
            "bgcolor": "rgba(247, 243, 234, 0.78)",
            "bordercolor": "rgba(17, 33, 50, 0.10)",
            "borderwidth": 1,
        },
        coloraxis_colorbar={
            "title": "Attention score",
            "thickness": 16,
            "len": 0.82,
            "x": 1.03,
            "y": 0.5,
            "tickfont": {"color": "#183149", "size": 12},
        },
    )
    return apply_figure_style(figure)


def build_shap_feature_chart(shap_global: pd.DataFrame) -> go.Figure:
    top_features = shap_global.head(12).copy().sort_values("mean_abs_shap")
    figure = px.bar(
        top_features,
        x="mean_abs_shap",
        y="feature",
        color="feature_family",
        orientation="h",
        color_discrete_sequence=["#0f6d5f", "#1d4f7a", "#e36414", "#74899a", "#a6b9c7", "#c9a34d"],
        labels={"mean_abs_shap": "Mean |SHAP|", "feature": "Feature", "feature_family": "Family"},
    )
    figure.update_layout(
        height=520,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return apply_figure_style(figure)


def build_shap_family_chart(shap_family: pd.DataFrame) -> go.Figure:
    figure = px.pie(
        shap_family,
        names="feature_family",
        values="mean_abs_shap",
        hole=0.58,
        color_discrete_sequence=["#1d4f7a", "#0f6d5f", "#e36414", "#74899a", "#a6b9c7", "#c9a34d"],
    )
    figure.update_traces(textposition="inside", textinfo="percent+label")
    figure.update_layout(height=420, margin={"l": 10, "r": 10, "t": 20, "b": 10})
    return apply_figure_style(figure)


def build_probability_gauge(probability: float) -> go.Figure:
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=probability * 100,
            number={"suffix": "%", "font": {"size": 38}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0f6d5f"},
                "steps": [
                    {"range": [0, 35], "color": "#d9ece8"},
                    {"range": [35, 65], "color": "#c8dae7"},
                    {"range": [65, 100], "color": "#f2d0be"},
                ],
                "threshold": {"line": {"color": "#e36414", "width": 4}, "value": 50},
            },
            title={"text": "Attention score"},
        )
    )
    figure.update_layout(height=300, margin={"l": 20, "r": 20, "t": 70, "b": 20})
    figure.update_traces(title_font={"color": "#183149", "size": 18}, number_font={"color": "#183149", "size": 38})
    return apply_figure_style(figure)


def build_operator_speed_chart(operator_state: pd.DataFrame) -> go.Figure:
    ordered = operator_state.sort_values("weighted_mean_speed_kbps", ascending=True)
    figure = px.bar(
        ordered,
        x="weighted_mean_speed_kbps",
        y="operator",
        orientation="h",
        color="operator_share",
        text="weighted_mean_speed_kbps",
        color_continuous_scale=["#d7e6ef", "#1d4f7a", "#0f6d5f"],
        labels={
            "weighted_mean_speed_kbps": "Average speed (Kbps)",
            "operator": "Operator",
            "operator_share": "Usage share",
        },
        title="Operator speed snapshot",
    )
    figure.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    figure.update_layout(
        height=340,
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar_title="Share",
    )
    figure.update_layout(coloraxis_colorbar={"title": "Share", "thickness": 16, "len": 0.72})
    return apply_figure_style(figure)


def build_operator_share_chart(operator_state: pd.DataFrame) -> go.Figure:
    figure = px.pie(
        operator_state,
        names="operator",
        values="operator_share",
        hole=0.55,
        color_discrete_sequence=["#0f6d5f", "#1d4f7a", "#e36414", "#74899a", "#c9a34d"],
        title="Operator presence mix",
    )
    figure.update_traces(textposition="inside", textinfo="percent+label")
    figure.update_layout(height=340, margin={"l": 10, "r": 10, "t": 55, "b": 10})
    return apply_figure_style(figure)


def build_global_reference_map(site_frame: pd.DataFrame) -> go.Figure:
    figure = px.scatter_geo(
        site_frame,
        lat="lat",
        lon="lon",
        color="role",
        size="marker_size",
        text="place",
        hover_name="place",
        hover_data={
            "country": True,
            "detail": True,
            "lat": False,
            "lon": False,
            "marker_size": False,
        },
        color_discrete_map={
            "Primary coverage view": "#e36414",
            "Foreign benchmark": "#1d4f7a",
        },
        # No title for the map
    )
    figure.update_traces(
        textposition="top center",
        textfont={"color": "#183149", "size": 14},
        marker={"line": {"width": 1.2, "color": "#f7f3ea"}},
    )
    figure.update_geos(
        showland=True,
        landcolor="#f5efe5",
        showocean=True,
        oceancolor="#dfeaf3",
        showcountries=True,
        countrycolor="#5b6978",
        projection_type="natural earth",
    )
    figure.update_layout(
        height=660,
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Story role",
        font={"color": "#183149", "size": 14},
        title={"font": {"color": "#183149", "size": 24}},
        legend={"font": {"color": "#183149", "size": 13}, "title_font": {"color": "#183149", "size": 13}},
    )
    return apply_figure_style(figure, title_size=24, font_size=14)


def build_phase5_benchmark_chart(phase5_results: pd.DataFrame) -> go.Figure:
    ordered = phase5_results.sort_values("Test_R2", ascending=True)
    figure = px.bar(
        ordered,
        x="Test_R2",
        y="Model",
        orientation="h",
        text="Test_R2",
        color="Test_R2",
        color_continuous_scale=["#d7e6ef", "#1d4f7a", "#0f6d5f"],
        labels={
            "Test_R2": "Benchmark fit score",
            "Model": "Version",
        },
        title="Europe benchmark comparison",
    )
    figure.update_traces(texttemplate="%{text:.3f}", textposition="outside", textfont={"color": "#183149", "size": 13})
    figure.update_layout(
        height=340,
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        font={"color": "#183149", "size": 13},
        title={"font": {"color": "#183149", "size": 22}},
        xaxis={"title_font": {"color": "#183149", "size": 13}, "tickfont": {"color": "#183149", "size": 12}},
        yaxis={"title_font": {"color": "#183149", "size": 13}, "tickfont": {"color": "#183149", "size": 12}},
    )
    return apply_figure_style(figure)


def build_foreign_region_chart(region_summary: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        region_summary,
        x="display_region",
        y="flagged_share",
        color="flagged_share",
        text="flagged_share",
        color_continuous_scale=["#d9ece8", "#f0b46a", "#e36414"],
        hover_data={
            "samples": True,
            "flagged_cases": True,
            "avg_residual": ":.2f",
        },
        labels={
            "display_region": "Reference region",
            "flagged_share": "Share marked as unusually weak",
        },
        title="Legacy anomaly rate by foreign reference region",
    )
    figure.update_traces(texttemplate="%{text:.1%}", textposition="outside", textfont={"color": "#183149", "size": 13})
    figure.update_layout(
        height=340,
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        yaxis_tickformat=".0%",
        font={"color": "#183149", "size": 13},
        title={"font": {"color": "#183149", "size": 22}},
        xaxis={"title_font": {"color": "#183149", "size": 13}, "tickfont": {"color": "#183149", "size": 12}},
        yaxis={"title_font": {"color": "#183149", "size": 13}, "tickfont": {"color": "#183149", "size": 12}},
    )
    return apply_figure_style(figure)


def build_foreign_feature_chart(feature_importance: pd.DataFrame) -> go.Figure:
    top_features = feature_importance.head(8).copy().sort_values("importance")
    top_features["display_feature"] = top_features["feature"].map(friendly_foreign_feature_name)
    figure = px.bar(
        top_features,
        x="importance",
        y="display_feature",
        orientation="h",
        color="importance",
        color_continuous_scale=["#d9ece8", "#1d4f7a", "#e36414"],
        labels={
            "importance": "Relative influence",
            "display_feature": "Network signal",
        },
        title="Main drivers in the foreign anomaly reference",
    )
    figure.update_layout(
        height=340,
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        font={"color": "#183149", "size": 13},
        title={"font": {"color": "#183149", "size": 22}},
        xaxis={"title_font": {"color": "#183149", "size": 13}, "tickfont": {"color": "#183149", "size": 12}},
        yaxis={"title_font": {"color": "#183149", "size": 12}, "tickfont": {"color": "#183149", "size": 12}},
    )
    return apply_figure_style(figure)


def build_template_choices(state_templates: pd.DataFrame) -> dict[str, pd.Series]:
    ranked = state_templates.sort_values("high_risk_probability").reset_index(drop=True)
    if ranked.empty:
        return {}

    choices = {
        "Better-performing example area": ranked.iloc[max(0, int(len(ranked) * 0.15))],
        "Typical example area": ranked.iloc[len(ranked) // 2],
        "Higher-risk example area": ranked.iloc[min(len(ranked) - 1, int(len(ranked) * 0.85))],
    }
    return choices


def apply_easy_adjustments(
    base_values: dict[str, float],
    connection_strength: str,
    traffic_load: str,
    crowding: str,
    stability: str,
) -> dict[str, float]:
    values = base_values.copy()

    strength_factor = {
        "Very weak": 0.68,
        "Weak": 0.84,
        "Typical": 1.00,
        "Good": 1.18,
        "Very good": 1.35,
    }[connection_strength]
    traffic_factor = {
        "Very light": 0.70,
        "Light": 0.86,
        "Typical": 1.00,
        "Busy": 1.20,
        "Very busy": 1.38,
    }[traffic_load]
    crowd_factor = {
        "Very sparse": 0.72,
        "Sparse": 0.88,
        "Typical": 1.00,
        "Crowded": 1.18,
        "Very crowded": 1.35,
    }[crowding]
    stability_factor = {
        "Very unstable": 1.35,
        "Unstable": 1.18,
        "Typical": 1.00,
        "Stable": 0.86,
        "Very stable": 0.74,
    }[stability]

    values["zone_mean_download_kbps"] *= strength_factor
    values["zone_median_download_kbps"] *= strength_factor
    values["zone_mean_upload_kbps"] *= strength_factor * 0.95
    values["zone_median_upload_kbps"] *= strength_factor * 0.95
    values["zone_std_download_kbps"] *= stability_factor
    values["zone_std_upload_kbps"] *= stability_factor

    values["zone_mean_tests"] *= traffic_factor
    values["zone_median_tests"] *= traffic_factor
    values["zone_std_tests"] *= traffic_factor * stability_factor

    values["zone_mean_devices"] *= crowd_factor
    values["zone_median_devices"] *= crowd_factor
    values["zone_std_devices"] *= crowd_factor * stability_factor

    values["zone_sample_count"] *= max(0.75, (traffic_factor + crowd_factor) / 2)
    return values


def apply_scenario(template_row: pd.Series, scenario: str) -> dict[str, float]:
    values = {column: float(template_row[column]) for column in FORM_INPUT_COLUMNS}

    if scenario == "Congestion shock":
        values["zone_sample_count"] *= 1.35
        values["zone_mean_tests"] *= 1.55
        values["zone_median_tests"] *= 1.45
        values["zone_std_tests"] *= 1.30
        values["zone_mean_devices"] *= 1.20
        values["zone_median_devices"] *= 1.15
        values["zone_std_devices"] *= 1.20
        values["zone_mean_download_kbps"] *= 0.68
        values["zone_median_download_kbps"] *= 0.70
        values["zone_std_download_kbps"] *= 1.15
        values["zone_mean_upload_kbps"] *= 0.78
        values["zone_median_upload_kbps"] *= 0.80
        values["zone_std_upload_kbps"] *= 1.10
    elif scenario == "Capacity upgrade":
        values["zone_mean_download_kbps"] *= 1.45
        values["zone_median_download_kbps"] *= 1.45
        values["zone_std_download_kbps"] *= 0.90
        values["zone_mean_upload_kbps"] *= 1.30
        values["zone_median_upload_kbps"] *= 1.30
        values["zone_std_upload_kbps"] *= 0.88
        values["zone_mean_tests"] *= 0.88
        values["zone_median_tests"] *= 0.90
        values["zone_std_tests"] *= 0.92
    elif scenario == "Demand spike":
        values["zone_sample_count"] *= 1.60
        values["zone_mean_tests"] *= 1.65
        values["zone_median_tests"] *= 1.50
        values["zone_std_tests"] *= 1.40
        values["zone_mean_devices"] *= 1.25
        values["zone_median_devices"] *= 1.20
        values["zone_std_devices"] *= 1.25
        values["zone_mean_download_kbps"] *= 0.82
        values["zone_mean_upload_kbps"] *= 0.86
    return values


def build_feature_row(
    payload: dict[str, object],
    selected_state: str,
    form_values: dict[str, float],
    state_context_row: pd.Series,
) -> pd.DataFrame:
    feature_names = list(payload["features"])
    feature_row = {feature: 0.0 for feature in feature_names}

    for column, value in form_values.items():
        if column in feature_row:
            feature_row[column] = float(value)

    feature_row["zone_mean_tests_per_device"] = feature_row["zone_mean_tests"] / max(feature_row["zone_mean_devices"], 1e-6)
    feature_row["zone_mean_devices_per_test"] = feature_row["zone_mean_devices"] / max(feature_row["zone_mean_tests"], 1e-6)
    feature_row["zone_mean_download_upload_ratio"] = feature_row["zone_mean_download_kbps"] / max(feature_row["zone_mean_upload_kbps"], 1e-6)

    feature_row["zone_tile_x_sq"] = feature_row["tile_x_bin"] ** 2
    feature_row["zone_tile_y_sq"] = feature_row["tile_y_bin"] ** 2
    feature_row["zone_tile_xy_interaction"] = feature_row["tile_x_bin"] * feature_row["tile_y_bin"]
    feature_row["zone_throughput_sum_kbps"] = feature_row["zone_mean_download_kbps"] + feature_row["zone_mean_upload_kbps"]
    feature_row["zone_throughput_gap_kbps"] = feature_row["zone_mean_download_kbps"] - feature_row["zone_mean_upload_kbps"]
    feature_row["zone_density_proxy"] = feature_row["zone_mean_tests"] + feature_row["zone_mean_devices"]
    feature_row["zone_usage_pressure"] = feature_row["zone_mean_tests"] * feature_row["zone_mean_devices"]

    for column in [
        "zone_mean_download_kbps",
        "zone_mean_upload_kbps",
        "zone_mean_tests",
        "zone_mean_devices",
        "zone_density_proxy",
        "zone_usage_pressure",
        "zone_sample_count",
    ]:
        feature_row[f"log_{column}"] = float(np.log1p(feature_row[column]))

    for column in STATE_CONTEXT_COLUMNS:
        feature_row[column] = float(state_context_row[column])

    ratio_pairs = [
        ("zone_mean_download_kbps", "state_zone_avg_download_kbps", "zone_download_vs_state_avg"),
        ("zone_mean_upload_kbps", "state_zone_avg_upload_kbps", "zone_upload_vs_state_avg"),
        ("zone_mean_tests", "state_zone_avg_tests", "zone_tests_vs_state_avg"),
        ("zone_mean_devices", "state_zone_avg_devices", "zone_devices_vs_state_avg"),
        ("zone_density_proxy", "state_zone_avg_density", "zone_density_vs_state_avg"),
        ("zone_sample_count", "state_zone_avg_sample_count", "zone_sample_count_vs_state_avg"),
    ]
    for numerator, denominator, target in ratio_pairs:
        feature_row[target] = feature_row[numerator] / max(feature_row[denominator], 1e-6)

    state_columns = [
        feature
        for feature in feature_names
        if feature.startswith("state_") and not feature.startswith("state_zone_avg_")
    ]
    for column in state_columns:
        feature_row[column] = 1.0 if column == f"state_{selected_state}" else 0.0

    frame = pd.DataFrame([[feature_row.get(feature, 0.0) for feature in feature_names]], columns=feature_names)
    return frame.astype(float)


def score_zone(
    payload: dict[str, object],
    selected_state: str,
    form_values: dict[str, float],
    state_context_row: pd.Series,
) -> tuple[float, str, pd.DataFrame]:
    feature_frame = build_feature_row(payload, selected_state, form_values, state_context_row)
    probability = float(payload["model"].predict_proba(feature_frame)[0, 1])
    predicted_label = "high_risk_zone" if probability >= 0.5 else "normal_zone"
    return probability, predicted_label, feature_frame


def render_hero(metrics: dict[str, object]) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">GLOBE-NET</div>
            <h1>Global Internet & LEO Benchmarking</h1>
            <p>Regional Risk Classification & Insights – India Case Study</p>
            <div class="chip-row">
                <div class="chip">India-wide view</div>
                <div class="chip">State comparison</div>
                <div class="chip">Karnataka focus</div>
                <div class="chip">Area check</div>
                <div class="chip">Global snapshot</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_tab(
    metrics: dict[str, object],
    state_summary: pd.DataFrame,
    state_geo: pd.DataFrame,
    india_geojson: dict[str, object],
) -> None:
    st.subheader("Big Picture")
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Overall reliability", f"{metrics['accuracy']:.2f}", help="How well the model identifies areas needing attention (higher is better)")
    kpi_cols[1].metric("Coverage balance", f"{metrics['balanced_accuracy']:.2f}", help="How evenly the model works across all states")
    kpi_cols[2].metric("Attention strength", f"{metrics['high_risk_f1']:.2f}", help="How well the model finds areas that may need attention")

    min_zones = st.slider("Minimum number of sample areas per state", min_value=1, max_value=100, value=20, key="overview_min_zones")
    left, right = st.columns([1.1, 1.2])
    left.plotly_chart(build_state_rank_chart(state_summary, min_zones), width="stretch", key="overview_rank_chart", theme=None)
    right.plotly_chart(
        build_india_state_map(state_geo, india_geojson, "predicted_high_risk_rate", min_zones),
        width="stretch",
        key="overview_india_map",
        theme=None,
    )

    st.dataframe(
        state_summary[[
            "state",
            "zones",
            "predicted_high_risk_rate",
            "actual_high_risk_rate",
            "mean_zone_p90_latency_ms",
        ]].sort_values("predicted_high_risk_rate", ascending=False),
        width="stretch",
        hide_index=True,
        column_config={
            "state": "State",
            "zones": st.column_config.NumberColumn("Areas reviewed", format="%d", help="Number of areas checked in this state"),
            "predicted_high_risk_rate": st.column_config.NumberColumn("Attention rate", format="%.2f", help="Estimated share of areas that may need attention (model-based)"),
            "actual_high_risk_rate": st.column_config.NumberColumn("Reported problem rate", format="%.2f", help="Share of areas with reported problems (from data)"),
            "mean_zone_p90_latency_ms": st.column_config.NumberColumn("Typical slow-end latency", format="%.1f ms", help="Average of the slowest speeds seen in each area (lower is better)"),
        },
    )


def render_state_explorer_tab(
    state_summary: pd.DataFrame,
    state_geo: pd.DataFrame,
    detailed_predictions: pd.DataFrame,
    india_geojson: dict[str, object],
    operator_state: pd.DataFrame,
    operator_snapshot: pd.DataFrame,
) -> None:
    st.subheader("India Story")
    controls = st.columns([1, 1])
    # Removed slider for minimum number of sample areas
    min_zones = 1  # Fixed value, adjust if needed
    selected_state = controls[1].selectbox("State to focus on", options=sorted(state_summary["state"].tolist()), index=sorted(state_summary["state"].tolist()).index("Karnataka"))

    # Removed map emphasis dropdown, default to 'Attention view'
    map_metric = "predicted_high_risk_rate"

    left, right = st.columns([1.1, 1.1])
    left.plotly_chart(
        build_india_state_map(state_geo, india_geojson, map_metric, min_zones),
        width="stretch",
        key="state_map_chart",
        theme=None,
    )

    state_zones = detailed_predictions[detailed_predictions["decoded_state"] == selected_state].copy()
    right.plotly_chart(
        build_zone_geo_map(state_zones, f"{selected_state} test zones", "high_risk_probability", "zone_sample_count"),
        width="stretch",
        key="state_zone_map",
        theme=None,
    )

    selected_row = state_summary[state_summary["state"] == selected_state].iloc[0]
    detail_cols = st.columns(3)
    detail_cols[0].metric("Areas reviewed", int(selected_row["zones"]))
    detail_cols[1].metric("Attention rate", format_percent(float(selected_row["predicted_high_risk_rate"])), help="Estimated share of areas that may need attention (model-based)")
    detail_cols[2].metric("Reported problem rate", format_percent(float(selected_row["actual_high_risk_rate"])), help="Share of areas with reported problems (from data)")

    st.markdown(
        f"<p class='mini-note'>For <strong>{selected_state}</strong>, about <strong>{format_brief_percent(float(selected_row['predicted_high_risk_rate']))}</strong> of reviewed areas may need attention (model estimate), while <strong>{format_brief_percent(float(selected_row['actual_high_risk_rate']))}</strong> had reported problems in the data.</p>",
        unsafe_allow_html=True,
    )

    state_operator_rows = operator_state[operator_state["state"] == selected_state].copy()
    state_operator_snapshot = operator_snapshot[operator_snapshot["state"] == selected_state]
    if not state_operator_rows.empty and not state_operator_snapshot.empty:
        snapshot = state_operator_snapshot.iloc[0]
        st.markdown(
            """
            <div class="card">
                <div class="card-title">Extra Telecom Context</div>
                <p class="card-copy">This section adds a simple operator snapshot for the selected state so visitors can see who is carrying the most traffic and where average speeds differ.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        operator_metrics = st.columns(3)
        operator_metrics[0].metric("Largest presence", str(snapshot["dominant_operator"]))
        operator_metrics[1].metric("Largest share", format_percent(float(snapshot["dominant_operator_share"])), help="Operator with the most users in this state")
        operator_metrics[2].metric("Fastest average", f"{snapshot['fastest_operator']} ({snapshot['fastest_operator_speed_kbps']:.0f} Kbps)", help="Operator with the highest average speed in this state")

        operator_left, operator_right = st.columns([1.15, 1])
        operator_left.plotly_chart(build_operator_speed_chart(state_operator_rows), width="stretch", key="state_operator_speed_chart", theme=None)
        operator_right.plotly_chart(build_operator_share_chart(state_operator_rows), width="stretch", key="state_operator_share_chart", theme=None)

        operator_table = state_operator_rows[["operator", "weighted_mean_speed_kbps", "weighted_mean_signal_strength", "operator_share", "speed_vs_state_avg"]].copy()
        operator_table = operator_table.sort_values("weighted_mean_speed_kbps", ascending=False)
        operator_table["operator_share_percent"] = operator_table["operator_share"] * 100
        operator_table = operator_table.drop(columns=["operator_share"])
        st.dataframe(
            operator_table,
            width="stretch",
            hide_index=True,
            column_config={
                "weighted_mean_speed_kbps": st.column_config.NumberColumn("Average speed", format="%.0f Kbps", help="Average download speed for this operator in the state"),
                "weighted_mean_signal_strength": st.column_config.NumberColumn("Average signal", format="%.1f dBm", help="Average signal strength for this operator in the state"),
                "operator_share_percent": st.column_config.NumberColumn("Share", format="%.1f%%", help="Portion of users on this operator in the state"),
                "speed_vs_state_avg": st.column_config.NumberColumn("Compared with state average", format="%.2f x", help="How this operator's speed compares to the state average (1.0 = same as average)"),
            },
        )
        # Download CSV button for operator table
        csv = operator_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download operator table as CSV",
            data=csv,
            file_name=f"{selected_state}_operator_table.csv",
            mime="text/csv",
        )

    st.dataframe(
        state_summary[["state", "zones", "predicted_high_risk_rate", "actual_high_risk_rate"]]
        [state_summary["zones"] >= min_zones]
        .sort_values("predicted_high_risk_rate", ascending=False),
        width="stretch",
        hide_index=True,
        column_config={
            "state": "State",
            "zones": st.column_config.NumberColumn("Areas reviewed", format="%d", help="Number of areas checked in this state"),
            "predicted_high_risk_rate": st.column_config.NumberColumn("Attention rate", format="%.2f", help="Estimated share of areas that may need attention (model-based)"),
            "actual_high_risk_rate": st.column_config.NumberColumn("Reported problem rate", format="%.2f", help="Share of areas with reported problems (from data)"),
        },
    )


def render_karnataka_tab(karnataka_row: pd.Series, karnataka_all: pd.DataFrame, karnataka_top: pd.DataFrame, phase10_text: str) -> None:
    st.subheader("Karnataka Focus")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Areas reviewed", int(karnataka_row["zones"]))
    metric_cols[1].metric("Areas flagged", int(karnataka_row["predicted_high_risk_zones"]))
    metric_cols[2].metric("Flag rate", format_percent(float(karnataka_row["predicted_high_risk_rate"])))
    metric_cols[3].metric("Observed weaker-area rate", format_percent(float(karnataka_row["actual_high_risk_rate"])))

    left, right = st.columns([1.25, 1])
    left.plotly_chart(
        build_zone_geo_map(karnataka_all, "Karnataka zone map", "high_risk_probability", "zone_sample_count"),
        width="stretch",
        key="karnataka_zone_map",
        theme=None,
    )
    right.markdown("#### Short Karnataka Summary")
    right.write(phase10_text.split("Karnataka summary:")[-1].split("Output files:")[0].strip())

    st.markdown("### Karnataka Areas Most Likely To Need Attention")
    st.dataframe(
        karnataka_top[[
            "tile_y_bin",
            "tile_x_bin",
            "zone_p90_latency_ms",
            "high_risk_probability",
            "zone_mean_download_kbps",
            "zone_mean_upload_kbps",
        ]],
        width="stretch",
        hide_index=True,
        column_config={
            "tile_y_bin": st.column_config.NumberColumn("Lat bin", format="%.2f"),
            "tile_x_bin": st.column_config.NumberColumn("Lon bin", format="%.2f"),
            "zone_p90_latency_ms": st.column_config.NumberColumn(format="%.1f ms"),
            "high_risk_probability": st.column_config.NumberColumn("Attention score", format="%.2f"),
            "zone_mean_download_kbps": st.column_config.NumberColumn("Avg download", format="%.0f"),
            "zone_mean_upload_kbps": st.column_config.NumberColumn("Avg upload", format="%.0f"),
        },
    )


def render_live_scorer_tab(
    payload: dict[str, object],
    state_context: pd.DataFrame,
    detailed_predictions: pd.DataFrame,
) -> None:
    st.subheader("Check Your Area")
    chooser_cols = st.columns([1, 1])
    selected_state = chooser_cols[0].selectbox(
        "Choose a state",
        sorted(detailed_predictions["decoded_state"].unique().tolist()),
        index=sorted(detailed_predictions["decoded_state"].unique().tolist()).index("Karnataka"),
        key="live_state",
    )
    scenario = chooser_cols[1].selectbox(
        "Starting situation",
        ["Keep it similar", "Rush-hour stress", "Network upgrade", "Sudden demand spike"],
        key="live_scenario",
    )

    state_templates = detailed_predictions[detailed_predictions["decoded_state"] == selected_state].copy()
    template_choices = build_template_choices(state_templates)
    template_label = st.selectbox("Example area", list(template_choices.keys()), key="live_template")
    template_row = template_choices[template_label]
    scenario_lookup = {
        "Keep it similar": "Use template as-is",
        "Rush-hour stress": "Congestion shock",
        "Network upgrade": "Capacity upgrade",
        "Sudden demand spike": "Demand spike",
    }
    defaults = apply_scenario(template_row, scenario_lookup[scenario])
    context_row = state_context[state_context["state"] == selected_state].iloc[0]

    form_key = f"live_form_{selected_state}_{int(template_row['source_row_index'])}_{scenario}"
    with st.form(form_key):
        primary_left, primary_right = st.columns(2)
        connection_strength = primary_left.select_slider(
            "Connection strength",
            options=["Very weak", "Weak", "Typical", "Good", "Very good"],
            value="Typical",
        )
        traffic_load = primary_left.select_slider(
            "Traffic load",
            options=["Very light", "Light", "Typical", "Busy", "Very busy"],
            value="Typical",
        )
        crowding = primary_right.select_slider(
            "Crowding",
            options=["Very sparse", "Sparse", "Typical", "Crowded", "Very crowded"],
            value="Typical",
        )
        stability = primary_right.select_slider(
            "Connection stability",
            options=["Very unstable", "Unstable", "Typical", "Stable", "Very stable"],
            value="Typical",
        )

        form_values = apply_easy_adjustments(defaults, connection_strength, traffic_load, crowding, stability)

        submitted = st.form_submit_button("Score this zone", type="primary")

    if submitted:
        probability, predicted_label, feature_frame = score_zone(payload, selected_state, form_values, context_row)
        delta = probability - float(template_row["high_risk_probability"])
        reviewer_label = "Needs attention likely" if predicted_label == "high_risk_zone" else "Looks stable (no major issues)"
        result_cols = st.columns([0.9, 1.1])
        result_cols[0].plotly_chart(build_probability_gauge(probability), width="stretch", key="live_probability_gauge", theme=None)

        result_cols[1].markdown(
            f"""
            <div class="card">
                <div class="card-title">Area Summary</div>
                <p class="card-copy"><strong>Simple outcome:</strong> {reviewer_label}</p>
                <p class="card-copy"><strong>How it reads:</strong> {describe_probability(probability)}</p>
                <p class="card-copy"><strong>Change from the starting example:</strong> {delta:+.2f}</p>
                <p class="card-copy"><strong>State used for comparison:</strong> {selected_state}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        comparison_rows = pd.DataFrame(
            [
                {"feature": "Download strength", "value": float(feature_frame.loc[0, "zone_download_vs_state_avg"]), "baseline": 1.0},
                {"feature": "Upload strength", "value": float(feature_frame.loc[0, "zone_upload_vs_state_avg"]), "baseline": 1.0},
                {"feature": "Demand level", "value": float(feature_frame.loc[0, "zone_tests_vs_state_avg"]), "baseline": 1.0},
                {"feature": "Crowding level", "value": float(feature_frame.loc[0, "zone_devices_vs_state_avg"]), "baseline": 1.0},
                {"feature": "Observed activity", "value": float(feature_frame.loc[0, "zone_sample_count_vs_state_avg"]), "baseline": 1.0},
            ]
        )
        ratio_chart = px.bar(
            comparison_rows,
            x="value",
            y="feature",
            orientation="h",
            color="value",
            color_continuous_scale=["#d9ece8", "#0f6d5f", "#e36414"],
            labels={"value": "Compared with a typical area in this state (1.0 = same as typical)", "feature": "Signal"},
            title="How this area compares with a typical area in the same state",
        )
        ratio_chart.add_vline(x=1.0, line_dash="dash", line_color="#5d6a79")
        ratio_chart.update_layout(height=360, margin={"l": 10, "r": 10, "t": 60, "b": 10}, plot_bgcolor="rgba(0,0,0,0)")
        ratio_chart = apply_figure_style(ratio_chart)
        st.plotly_chart(ratio_chart, width="stretch", key="live_ratio_chart", theme=None)


def render_presentation_tab(
    metrics: dict[str, object],
    state_summary: pd.DataFrame,
    state_geo: pd.DataFrame,
    karnataka_row: pd.Series,
    shap_family: pd.DataFrame,
    india_geojson: dict[str, object],
    operator_state: pd.DataFrame,
    operator_snapshot: pd.DataFrame,
) -> None:
    st.subheader("Quick View")
    top_row = st.columns([1.2, 1])
    top_row[0].plotly_chart(
        build_india_state_map(state_geo, india_geojson, "predicted_high_risk_rate", 20),
        width="stretch",
        key="presentation_india_map",
        theme=None,
    )
    top_row[1].plotly_chart(build_shap_family_chart(shap_family), width="stretch", key="presentation_shap_family", theme=None)

    mid_cols = st.columns(3)
    mid_cols[0].metric("Coverage balance", f"{metrics['balanced_accuracy']:.2f}")
    mid_cols[1].metric("Karnataka attention rate", format_percent(float(karnataka_row["predicted_high_risk_rate"])))
    mid_cols[2].metric("Karnataka reported weaker-area rate", format_percent(float(karnataka_row["actual_high_risk_rate"])))

    karnataka_operator_rows = operator_state[operator_state["state"] == "Karnataka"].copy()
    if not karnataka_operator_rows.empty:
        st.plotly_chart(build_operator_speed_chart(karnataka_operator_rows), width="stretch", key="presentation_karnataka_operator_chart", theme=None)


def render_global_reference_tab(
    metrics: dict[str, object],
    phase5_metrics: dict[str, object],
    phase5_results: pd.DataFrame,
    foreign_metrics: dict[str, object],
    foreign_region_summary: pd.DataFrame,
    foreign_feature_importance: pd.DataFrame,
) -> None:
    st.subheader("Global Snapshot")
    st.caption("This dashboard provides a comprehensive view of India's network quality, with Germany and the Netherlands included as international benchmarks for comparison. The map below highlights the primary coverage in India and reference sites in Europe to help contextualize performance and reliability.")

    site_frame = prepare_global_reference_sites(int(metrics.get("test_zone_count", 0)), foreign_region_summary)
    st.plotly_chart(build_global_reference_map(site_frame), width="stretch", key="global_reference_map", theme=None)

    render_spotlight_cards(build_global_reference_cards(metrics, phase5_metrics, foreign_metrics, foreign_region_summary))

    metric_cols = st.columns(4)
    metric_cols[0].metric("Primary coverage view", "India")
    metric_cols[1].metric("Europe benchmark fit", f"{phase5_metrics['r2']:.2f}")
    metric_cols[2].metric("Foreign flagged cases", f"{foreign_metrics['anomalies']:,}")
    metric_cols[3].metric("Foreign flagged share", format_percent(float(foreign_metrics["share_fraction"])))

    lower_left, lower_right = st.columns([1, 1.1])
    lower_left.plotly_chart(build_foreign_region_chart(foreign_region_summary), width="stretch", key="foreign_region_chart", theme=None)
    lower_right.plotly_chart(build_foreign_feature_chart(foreign_feature_importance), width="stretch", key="foreign_feature_chart", theme=None)

    with st.expander("Open detailed foreign reference numbers"):
        region_table = foreign_region_summary[["display_region", "samples", "flagged_cases", "flagged_share"]].copy()
        st.dataframe(
            region_table,
            width="stretch",
            hide_index=True,
            column_config={
                "display_region": "Reference region",
                "samples": st.column_config.NumberColumn("Measurements reviewed", format="%d"),
                "flagged_cases": st.column_config.NumberColumn("Flagged cases", format="%d"),
                "flagged_share": st.column_config.NumberColumn("Flagged share", format="%.1f%%"),
            },
        )


def render_explainability_tab(shap_global: pd.DataFrame, shap_family: pd.DataFrame, phase9_report: str) -> None:
    st.subheader("Network Drivers")
    left, right = st.columns([1.2, 1])
    left.plotly_chart(build_shap_feature_chart(shap_global), width="stretch", key="explainability_feature_chart", theme=None)
    right.plotly_chart(build_shap_family_chart(shap_family), width="stretch", key="explainability_family_chart", theme=None)
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Interpretation</div>
            <p class="card-copy">This view highlights the signals most closely linked to stressed network areas, including usage pressure, speed patterns, and location context.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Open the detailed technical report only if needed"):
        st.code(phase9_report, language="text")


def main() -> None:
    ensure_files_exist(
        [
            INDIA_GEOJSON_PATH,
            STATE_SUMMARY_PATH,
            FULL_ZONE_DATASET_PATH,
            DETAILED_PREDICTIONS_PATH,
            KARNATAKA_TOP_PATH,
            KARNATAKA_ALL_PATH,
            MODEL_PATH,
            SHAP_GLOBAL_PATH,
            SHAP_FAMILY_PATH,
            PHASE9_REPORT_PATH,
            PHASE10_REPORT_PATH,
            TRAI_OPERATOR_SUMMARY_PATH,
            PHASE5_RESULTS_PATH,
            PHASE5_REPORT_PATH,
            FOREIGN_ANOMALY_SUMMARY_PATH,
            FOREIGN_ANOMALY_RESULTS_PATH,
            FOREIGN_ANOMALY_FEATURES_PATH,
        ]
    )
    inject_styles()

    state_summary = load_csv(STATE_SUMMARY_PATH)
    full_zone_dataset = load_csv(FULL_ZONE_DATASET_PATH)
    detailed_predictions = load_csv(DETAILED_PREDICTIONS_PATH)
    india_geojson = load_geojson(INDIA_GEOJSON_PATH)
    karnataka_top = load_csv(KARNATAKA_TOP_PATH)
    karnataka_all = load_csv(KARNATAKA_ALL_PATH)
    shap_global = load_csv(SHAP_GLOBAL_PATH)
    shap_family = load_csv(SHAP_FAMILY_PATH)
    trai_operator_summary = load_csv(TRAI_OPERATOR_SUMMARY_PATH)
    phase5_results = load_csv(PHASE5_RESULTS_PATH)
    foreign_anomaly_results = load_csv(FOREIGN_ANOMALY_RESULTS_PATH)
    foreign_anomaly_feature_importance = load_csv(FOREIGN_ANOMALY_FEATURES_PATH)
    phase9_report = load_text(PHASE9_REPORT_PATH)
    phase10_report = load_text(PHASE10_REPORT_PATH)
    phase5_report = load_text(PHASE5_REPORT_PATH)
    foreign_anomaly_summary = load_text(FOREIGN_ANOMALY_SUMMARY_PATH)
    payload = load_model_payload()

    full_zone_dataset, state_geo = prepare_zone_data(full_zone_dataset, state_summary)
    state_geo = prepare_state_map_data(state_geo, india_geojson)
    state_context = prepare_state_context(full_zone_dataset)
    operator_state, operator_snapshot = prepare_operator_context(trai_operator_summary)
    metrics = parse_phase9_metrics(phase9_report)
    phase5_metrics = parse_phase5_metrics(phase5_report)
    foreign_metrics = parse_foreign_anomaly_metrics(foreign_anomaly_summary)
    foreign_region_summary = prepare_foreign_region_summary(foreign_anomaly_results)
    karnataka_row = state_summary[state_summary["state"] == "Karnataka"].iloc[0]

    st.sidebar.title("Navigation")
    st.sidebar.markdown(
        """
        <div class="card">
            <div class="card-title">Sections</div>
            <div class="deck-step">1. Big Picture</div>
            <div class="deck-step">2. India Story</div>
            <div class="deck-step">3. Karnataka Focus</div>
            <div class="deck-step">4. Check Your Area</div>
            <div class="deck-step">5. Global Snapshot</div>
            <div class="deck-step">6. Network Drivers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("### Quick Notes")
    st.sidebar.write("Built for quick, simple network-quality reviews.")
    st.sidebar.write(f"Covers {metrics['test_zones']} held-out sample areas.")
    st.sidebar.write("Updated from the latest processed national and reference snapshots.")

    render_hero(metrics)

    tabs = st.tabs([
        "Big Picture",
        "India Story",
        "Karnataka Focus",
        "Check Your Area",
        "Global Snapshot",
        "Quick View",
        "Network Drivers",
    ])

    with tabs[0]:
        render_overview_tab(metrics, state_summary, state_geo, india_geojson)
    with tabs[1]:
        render_state_explorer_tab(state_summary, state_geo, detailed_predictions, india_geojson, operator_state, operator_snapshot)
    with tabs[2]:
        render_karnataka_tab(karnataka_row, karnataka_all, karnataka_top, phase10_report)
    with tabs[3]:
        render_live_scorer_tab(payload, state_context, detailed_predictions)
    with tabs[4]:
        render_global_reference_tab(
            metrics,
            phase5_metrics,
            phase5_results,
            foreign_metrics,
            foreign_region_summary,
            foreign_anomaly_feature_importance,
        )
    with tabs[5]:
        render_presentation_tab(metrics, state_summary, state_geo, karnataka_row, shap_family, india_geojson, operator_state, operator_snapshot)
    with tabs[6]:
        render_explainability_tab(shap_global, shap_family, phase9_report)

    st.caption(
        "Built from processed national network-quality snapshots together with earlier international reference data to help visitors review where service looks stable and where it may need attention."
    )


if __name__ == "__main__":
    main()