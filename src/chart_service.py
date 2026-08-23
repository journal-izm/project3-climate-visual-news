from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

from src.data_service import METRICS


def save_timeseries_png(
    df: pd.DataFrame, metric_name: str, source_name: str, path: str | Path
) -> Path:
    column, unit = METRICS[metric_name]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    installed = {font.name for font in font_manager.fontManager.ttflist}
    korean_font = next(
        (name for name in ["Malgun Gothic", "Noto Sans CJK KR", "AppleGothic"] if name in installed),
        None,
    )
    if korean_font:
        plt.rcParams["font.family"] = korean_font
    english_metric = {"평균기온": "Average temperature", "최고기온": "Maximum temperature", "강수량": "Precipitation"}[metric_name]
    region_labels = {"서울": "Seoul", "부산": "Busan", "대구": "Daegu"}
    fig, ax = plt.subplots(figsize=(12, 6.75), constrained_layout=True)
    for region, rows in df.groupby("region"):
        rows = rows.sort_values("year")
        label = region if korean_font else region_labels.get(region, region)
        ax.plot(rows["year"], rows[column], marker="o", linewidth=2, label=label)
    title = f"지역별 {metric_name} 변화" if korean_font else f"Regional {english_metric} trend"
    ax.set_title(title, fontsize=18, fontweight="bold")
    ax.set_xlabel("연도" if korean_font else "Year")
    ax.set_ylabel(f"{metric_name if korean_font else english_metric} ({unit})")
    ax.grid(alpha=0.25)
    ax.legend()
    source = f"출처: {source_name} | 단위: {unit}" if korean_font else f"Source: Korea Meteorological Administration | Unit: {unit}"
    fig.text(0.01, 0.01, source, fontsize=9)
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path
