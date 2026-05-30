"""Merge and clean TRAI state service provider CSV files into a 2025 master dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "State_service_provider"
OUTPUT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "03_outputs"
REPORT_DIR = ROOT / "09_INDIA_FIRST_ANALYSIS" / "04_reports"

MASTER_OUTPUT_PATH = OUTPUT_DIR / "trai_2025_state_service_provider_master.csv"
SUMMARY_OUTPUT_PATH = OUTPUT_DIR / "trai_2025_state_service_provider_summary.csv"
REPORT_OUTPUT_PATH = REPORT_DIR / "phase0_trai_state_service_provider_merge.txt"

REQUIRED_COLUMNS = [
    "operator",
    "technology",
    "download",
    "speed_kbps",
    "signal_strength",
    "lsa",
    "month",
    "year",
]

OPERATOR_MAP = {
    "AIRTEL": "AIRTEL",
    "JIO": "JIO",
    "VI INDIA": "Vi India",
    "CELLONE": "CELLONE",
    "BSNL": "BSNL",
}

LSA_NORMALIZATION_MAP = {
    "Jammu & Kashmir": "Jammu and Kashmir",
    "Orissa": "Odisha",
}

LSA_STATE_MAP = {
    "Andhra Pradesh": ("Andhra Pradesh", "state"),
    "Assam": ("Assam", "state"),
    "Bihar": ("Bihar", "state"),
    "Chennai": ("Tamil Nadu", "metro_circle"),
    "Delhi": ("Delhi", "state"),
    "Gujarat": ("Gujarat", "state"),
    "Haryana": ("Haryana", "state"),
    "Himachal Pradesh": ("Himachal Pradesh", "state"),
    "Jammu and Kashmir": ("Jammu and Kashmir", "state"),
    "Karnataka": ("Karnataka", "state"),
    "Kerala": ("Kerala", "state"),
    "Kolkata": ("West Bengal", "metro_circle"),
    "Madhya Pradesh": ("Madhya Pradesh", "state"),
    "Maharashtra": ("Maharashtra", "state"),
    "Mumbai": ("Maharashtra", "metro_circle"),
    "North East": (pd.NA, "multi_state_circle"),
    "NA": (pd.NA, "unknown"),
    "Odisha": ("Odisha", "state"),
    "Punjab": ("Punjab", "state"),
    "Rajasthan": ("Rajasthan", "state"),
    "Tamil Nadu": ("Tamil Nadu", "state"),
    "UP East": ("Uttar Pradesh", "split_circle"),
    "UP West": ("Uttar Pradesh", "split_circle"),
    "West Bengal": ("West Bengal", "state"),
}


def list_input_files() -> list[Path]:
    return sorted(INPUT_DIR.glob("*.csv"))


def normalize_operator(value: object) -> str:
    cleaned = str(value).strip()
    return OPERATOR_MAP.get(cleaned.upper(), cleaned)


def normalize_lsa(value: object) -> str:
    cleaned = str(value).strip()
    return LSA_NORMALIZATION_MAP.get(cleaned, cleaned)


def load_file(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {missing}")

    frame = frame.loc[:, REQUIRED_COLUMNS].copy()
    frame["source_file"] = path.name
    frame["operator"] = frame["operator"].map(normalize_operator)
    frame["technology"] = frame["technology"].astype(str).str.strip().str.upper()
    frame["download"] = frame["download"].astype(str).str.strip().str.lower()
    frame["lsa"] = frame["lsa"].map(normalize_lsa)
    frame["speed_kbps"] = pd.to_numeric(frame["speed_kbps"], errors="coerce")
    frame["signal_strength"] = pd.to_numeric(frame["signal_strength"], errors="coerce")
    frame["month"] = pd.to_numeric(frame["month"], errors="coerce").astype("Int64")
    frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    return frame


def add_merge_keys(frame: pd.DataFrame) -> pd.DataFrame:
    state_merge_key: list[object] = []
    lsa_merge_type: list[str] = []

    for lsa in frame["lsa"]:
        mapped_state, mapped_type = LSA_STATE_MAP.get(lsa, (pd.NA, "unmapped"))
        state_merge_key.append(mapped_state)
        lsa_merge_type.append(mapped_type)

    enriched = frame.copy()
    enriched["state_merge_key"] = state_merge_key
    enriched["lsa_merge_type"] = lsa_merge_type
    enriched["is_download_measurement"] = enriched["download"].eq("download")
    enriched["is_upload_measurement"] = enriched["download"].eq("upload")
    return enriched


def build_summary(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby(["operator", "lsa", "state_merge_key", "lsa_merge_type", "month", "year"], dropna=False)
        .agg(
            row_count=("speed_kbps", "size"),
            mean_speed_kbps=("speed_kbps", "mean"),
            median_speed_kbps=("speed_kbps", "median"),
            mean_signal_strength=("signal_strength", "mean"),
            technologies=("technology", lambda values: "|".join(sorted(pd.Series(values).dropna().astype(str).unique()))),
            measurement_types=("download", lambda values: "|".join(sorted(pd.Series(values).dropna().astype(str).unique()))),
        )
        .reset_index()
        .sort_values(["operator", "lsa", "month", "year"], ascending=[True, True, True, True])
        .reset_index(drop=True)
    )


def build_report(frame: pd.DataFrame, summary: pd.DataFrame, file_count: int) -> str:
    lines = [
        "PHASE 0 REPORT: TRAI STATE SERVICE PROVIDER MERGE",
        "=" * 80,
        f"Input directory: {INPUT_DIR}",
        f"CSV files merged: {file_count}",
        f"Master rows: {len(frame):,}",
        f"Summary rows: {len(summary):,}",
        f"Years present: {sorted(frame['year'].dropna().astype(int).unique().tolist())}",
        f"Months present: {sorted(frame['month'].dropna().astype(int).unique().tolist())}",
        f"Operators present: {sorted(frame['operator'].dropna().astype(str).unique().tolist())}",
        f"LSAs present: {frame['lsa'].nunique()}",
        f"Mapped state keys: {frame['state_merge_key'].dropna().nunique()}",
        f"Unmapped rows: {int(frame['state_merge_key'].isna().sum()):,}",
        "",
        "Rows by operator:",
    ]

    operator_counts = frame.groupby("operator", dropna=False).size().sort_values(ascending=False)
    for operator, row_count in operator_counts.items():
        lines.append(f"- {operator}: {int(row_count):,}")

    lines.extend(["", "Rows by LSA merge type:"])
    merge_type_counts = frame.groupby("lsa_merge_type", dropna=False).size().sort_values(ascending=False)
    for merge_type, row_count in merge_type_counts.items():
        lines.append(f"- {merge_type}: {int(row_count):,}")

    lines.extend(["", "Top 15 LSAs by row count:"])
    top_lsa_counts = frame.groupby("lsa", dropna=False).size().sort_values(ascending=False).head(15)
    for lsa, row_count in top_lsa_counts.items():
        lines.append(f"- {lsa}: {int(row_count):,}")

    return "\n".join(lines)


def main() -> None:
    files = list_input_files()
    if not files:
        raise FileNotFoundError(f"No CSV files found in {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    frames = [load_file(path) for path in files]
    master = pd.concat(frames, ignore_index=True)
    master = master[master["year"] == 2025].copy()
    master = add_merge_keys(master)
    summary = build_summary(master)

    master.to_csv(MASTER_OUTPUT_PATH, index=False)
    summary.to_csv(SUMMARY_OUTPUT_PATH, index=False)
    REPORT_OUTPUT_PATH.write_text(build_report(master, summary, len(files)), encoding="utf-8")

    print(f"Merged files: {len(files)}")
    print(f"Master rows: {len(master):,}")
    print(f"Master CSV: {MASTER_OUTPUT_PATH}")
    print(f"Summary CSV: {SUMMARY_OUTPUT_PATH}")
    print(f"Report: {REPORT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()