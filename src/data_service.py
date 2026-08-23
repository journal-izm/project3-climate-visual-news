from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "year", "region", "latitude", "longitude", "avg_temp_c", "max_temp_c",
    "precipitation_mm", "source_name", "source_url", "collected_at",
}
NUMERIC_COLUMNS = [
    "year", "latitude", "longitude", "avg_temp_c", "max_temp_c", "precipitation_mm"
]
METRICS = {
    "평균기온": ("avg_temp_c", "°C"),
    "최고기온": ("max_temp_c", "°C"),
    "강수량": ("precipitation_mm", "mm"),
}


def load_csv(source: str | Path | BytesIO) -> pd.DataFrame:
    return validate_and_clean(pd.read_csv(source))


def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"필수 열 누락: {', '.join(sorted(missing))}")
    clean = df.copy()
    for column in NUMERIC_COLUMNS:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")
    if clean[NUMERIC_COLUMNS].isna().any().any():
        raise ValueError("숫자 열에 결측값 또는 잘못된 값이 있습니다.")
    if clean[["region", "source_name", "source_url", "collected_at"]].isna().any().any():
        raise ValueError("지역 또는 출처 메타데이터가 누락되었습니다.")
    clean["year"] = clean["year"].astype(int)
    clean["region"] = clean["region"].astype(str).str.strip()
    clean = clean.drop_duplicates(subset=["year", "region"], keep="last")
    if not clean["year"].between(1900, 2100).all():
        raise ValueError("연도 허용 범위를 벗어났습니다.")
    if not clean["avg_temp_c"].between(-50, 60).all():
        raise ValueError("평균기온 허용 범위를 벗어났습니다.")
    if not clean["max_temp_c"].between(-50, 70).all():
        raise ValueError("최고기온 허용 범위를 벗어났습니다.")
    if (clean["precipitation_mm"] < 0).any():
        raise ValueError("강수량은 음수가 될 수 없습니다.")
    return clean.sort_values(["year", "region"]).reset_index(drop=True)


def filter_data(
    df: pd.DataFrame, start_year: int, end_year: int, regions: list[str]
) -> pd.DataFrame:
    if start_year > end_year:
        raise ValueError("시작 연도는 종료 연도보다 클 수 없습니다.")
    result = df[df["year"].between(start_year, end_year) & df["region"].isin(regions)]
    if result.empty:
        raise ValueError("선택 조건에 해당하는 데이터가 없습니다.")
    return result.copy()


def summarize(df: pd.DataFrame, metric_name: str, focus_region: str) -> dict:
    column, unit = METRICS[metric_name]
    region_df = df[df["region"] == focus_region].sort_values("year")
    if region_df.empty:
        raise ValueError("기준 지역 데이터가 없습니다.")
    first = region_df.iloc[0]
    last = region_df.iloc[-1]
    change = float(last[column] - first[column])
    rate = None if float(first[column]) == 0 else change / abs(float(first[column])) * 100
    max_row = region_df.loc[region_df[column].idxmax()]
    min_row = region_df.loc[region_df[column].idxmin()]
    return {
        "region": focus_region,
        "metric": metric_name,
        "column": column,
        "unit": unit,
        "start_year": int(first["year"]),
        "end_year": int(last["year"]),
        "start_value": float(first[column]),
        "end_value": float(last[column]),
        "change": change,
        "change_rate": rate,
        "mean": float(region_df[column].mean()),
        "max_year": int(max_row["year"]),
        "max_value": float(max_row[column]),
        "min_year": int(min_row["year"]),
        "min_value": float(min_row[column]),
        "source_name": str(last["source_name"]),
        "source_url": str(last["source_url"]),
        "collected_at": str(last["collected_at"]),
    }


def to_powerbi(df: pd.DataFrame) -> pd.DataFrame:
    id_columns = [
        "year", "region", "latitude", "longitude", "source_name", "source_url", "collected_at"
    ]
    long_df = df.melt(
        id_vars=id_columns,
        value_vars=[item[0] for item in METRICS.values()],
        var_name="metric_code",
        value_name="value",
    )
    labels = {value[0]: key for key, value in METRICS.items()}
    units = {value[0]: value[1] for value in METRICS.values()}
    long_df["metric_name"] = long_df["metric_code"].map(labels)
    long_df["unit"] = long_df["metric_code"].map(units)
    return long_df
