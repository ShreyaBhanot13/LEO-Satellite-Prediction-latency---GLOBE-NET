"""Download 2025 TRAI/MySpeed operator data from data.gov.in."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_OUTPUT_DIR = ROOT / "data" / "raw" / "trai_2025_api"
MASTER_OUTPUT_PATH = ROOT / "outputs_v5" / "TRAI_2025_top_operators_api.csv"
SUMMARY_OUTPUT_PATH = ROOT / "outputs_v5" / "TRAI_2025_top_operators_api_summary.txt"

RESOURCE_ID = "ade6e644-91b8-4d27-97ba-e8c42c48f278"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
DEFAULT_OPERATORS = ["AIRTEL", "JIO", "Vi India", "BSNL"]
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
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download 2025 TRAI/MySpeed operator data from the public API.")
    parser.add_argument("--api-key", default=os.getenv("DATA_GOV_IN_API_KEY"), help="data.gov.in API key. Defaults to DATA_GOV_IN_API_KEY.")
    parser.add_argument("--year", type=int, default=2025, help="Year to download. Defaults to 2025.")
    parser.add_argument("--limit", type=int, default=1000, help="Rows to fetch per API page. Defaults to 1000.")
    parser.add_argument("--operators", nargs="*", default=DEFAULT_OPERATORS, help="Operators to download.")
    return parser.parse_args()


def fetch_page(api_key: str, operator: str, year: int, limit: int, offset: int) -> dict[str, Any]:
    query = urlencode(
        {
            "api-key": api_key,
            "format": "json",
            "limit": limit,
            "offset": offset,
            "filters[operator]": operator,
            "filters[year]": year,
        }
    )
    request = Request(f"{BASE_URL}?{query}", headers={"User-Agent": "FY-ML-TRAI-Downloader/1.0"})
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(request) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code not in RETRY_STATUS_CODES or attempt == MAX_RETRIES:
                raise
        except URLError:
            if attempt == MAX_RETRIES:
                raise

        time.sleep(min(2 ** (attempt - 1), 8))

    raise RuntimeError("Unexpected retry loop exit while downloading TRAI API data.")


def fetch_operator_data(api_key: str, operator: str, year: int, limit: int) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    offset = 0

    while True:
        payload = fetch_page(api_key, operator, year, limit, offset)
        batch = payload.get("records", [])
        if not batch:
            break

        records.extend(batch)
        offset += len(batch)

    frame = pd.DataFrame(records)
    if frame.empty:
        return frame

    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"API response for {operator} is missing required columns: {missing}")

    frame = frame.loc[:, REQUIRED_COLUMNS].copy()
    frame["operator"] = frame["operator"].astype(str)
    frame["technology"] = frame["technology"].astype(str)
    frame["download"] = frame["download"].astype(str)
    frame["lsa"] = frame["lsa"].astype(str)
    frame["speed_kbps"] = pd.to_numeric(frame["speed_kbps"], errors="coerce")
    frame["signal_strength"] = pd.to_numeric(frame["signal_strength"], errors="coerce")
    frame["month"] = pd.to_numeric(frame["month"], errors="coerce").astype("Int64")
    frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    return frame


def operator_file_name(operator: str, year: int) -> str:
    safe_operator = operator.lower().replace(" ", "_")
    return f"trai_{year}_{safe_operator}.csv"


def build_summary(frames: dict[str, pd.DataFrame], year: int) -> str:
    lines = [
        "TRAI 2025 API DOWNLOAD SUMMARY",
        "=" * 80,
        f"Year: {year}",
        "",
    ]
    for operator, frame in frames.items():
        if frame.empty:
            lines.extend([f"Operator: {operator}", "- Rows: 0", "- No data returned", ""])
            continue

        lines.extend(
            [
                f"Operator: {operator}",
                f"- Rows: {len(frame):,}",
                f"- LSAs: {frame['lsa'].nunique()}",
                f"- Technologies: {sorted(frame['technology'].dropna().unique().tolist())}",
                f"- Months: {sorted(frame['month'].dropna().astype(int).unique().tolist())}",
                f"- Mean speed_kbps: {frame['speed_kbps'].mean():.2f}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    if not args.api_key:
        raise ValueError("Provide an API key with --api-key or DATA_GOV_IN_API_KEY.")

    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MASTER_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    frames: dict[str, pd.DataFrame] = {}
    for operator in args.operators:
        frame = fetch_operator_data(args.api_key, operator, args.year, args.limit)
        frames[operator] = frame
        if not frame.empty:
            frame.to_csv(RAW_OUTPUT_DIR / operator_file_name(operator, args.year), index=False)

    combined = pd.concat([frame for frame in frames.values() if not frame.empty], ignore_index=True) if any(not frame.empty for frame in frames.values()) else pd.DataFrame(columns=REQUIRED_COLUMNS)
    combined.to_csv(MASTER_OUTPUT_PATH, index=False)

    summary_text = build_summary(frames, args.year)
    SUMMARY_OUTPUT_PATH.write_text(summary_text, encoding="utf-8")

    print(summary_text)
    print(f"Combined CSV: {MASTER_OUTPUT_PATH}")
    print(f"Raw operator files: {RAW_OUTPUT_DIR}")


if __name__ == "__main__":
    main()