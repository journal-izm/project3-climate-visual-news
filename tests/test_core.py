from pathlib import Path

import pandas as pd
import pytest

from src.chart_service import save_timeseries_png
from src.content_service import generate_article, generate_script, generate_storyboard, validate_generated_numbers
from src.data_service import filter_data, load_csv, summarize, to_powerbi, validate_and_clean
from src.export_service import ensure_output_dirs, save_csv, save_text


DEMO = Path(__file__).parents[1] / "data" / "demo" / "climate_demo.csv"


def test_demo_loads_expected_scope():
    df = load_csv(DEMO)
    assert len(df) == 30
    assert set(df["region"]) == {"서울", "부산", "대구"}
    assert (df["year"].min(), df["year"].max()) == (2015, 2024)


def test_missing_column_is_rejected():
    with pytest.raises(ValueError, match="필수 열 누락"):
        validate_and_clean(pd.DataFrame({"year": [2024]}))


def test_duplicate_region_year_is_removed():
    df = pd.read_csv(DEMO)
    result = validate_and_clean(pd.concat([df, df.iloc[[0]]], ignore_index=True))
    assert len(result) == 30


def test_invalid_temperature_is_rejected():
    df = pd.read_csv(DEMO)
    df.loc[0, "avg_temp_c"] = 999
    with pytest.raises(ValueError, match="평균기온"):
        validate_and_clean(df)


def test_filter_by_period_and_region():
    result = filter_data(load_csv(DEMO), 2020, 2022, ["서울"])
    assert result["year"].tolist() == [2020, 2021, 2022]


def test_empty_filter_is_rejected():
    with pytest.raises(ValueError, match="해당하는 데이터"):
        filter_data(load_csv(DEMO), 2015, 2024, ["제주"])


def test_summary_change_is_correct():
    summary = summarize(load_csv(DEMO), "평균기온", "서울")
    assert summary["change"] == pytest.approx(0.72)
    assert summary["start_year"] == 2015
    assert summary["end_year"] == 2024


def test_powerbi_export_is_long_format():
    result = to_powerbi(load_csv(DEMO))
    assert len(result) == 90
    assert set(result["metric_name"]) == {"평균기온", "최고기온", "강수량"}
    assert result["unit"].notna().all()


def test_generated_article_and_script_use_evidence():
    summary = summarize(load_csv(DEMO), "평균기온", "서울")
    article = generate_article(summary)
    script = generate_script(summary)
    assert "14.32°C" in article
    assert "0.72°C" in script
    assert validate_generated_numbers(article + script, summary) == []


def test_unknown_generated_number_is_detected():
    summary = summarize(load_csv(DEMO), "평균기온", "서울")
    assert "999" in validate_generated_numbers(generate_article(summary) + " 999", summary)


def test_storyboard_is_about_one_minute():
    rows = generate_storyboard(summarize(load_csv(DEMO), "강수량", "부산"))
    assert len(rows) == 6
    assert sum(row["seconds"] for row in rows) == 60
    assert all(row["visual"] and row["narration"] for row in rows)


def test_files_are_saved_utf8(tmp_path):
    paths = ensure_output_dirs(tmp_path)
    text_path = save_text("한글 기사", paths["articles"] / "기사.md")
    csv_path = save_csv(pd.DataFrame({"지역": ["서울"]}), paths["powerbi"] / "data.csv")
    assert text_path.read_text(encoding="utf-8") == "한글 기사"
    assert csv_path.read_bytes().startswith(b"\xef\xbb\xbf")


def test_chart_png_is_created(tmp_path):
    df = load_csv(DEMO)
    path = save_timeseries_png(df, "평균기온", "기상청", tmp_path / "chart.png")
    assert path.exists()
    assert path.stat().st_size > 1000
