from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.chart_service import save_timeseries_png
from src.content_service import generate_article, generate_script, generate_storyboard, validate_generated_numbers
from src.data_service import METRICS, filter_data, load_csv, summarize, to_powerbi
from src.export_service import ensure_output_dirs, save_csv, save_text


ROOT = Path(__file__).parent
DEMO_PATH = ROOT / "data" / "demo" / "climate_demo.csv"

st.set_page_config(page_title="기후 데이터 시각화 뉴스", page_icon="📊", layout="wide")
st.title("📊 기후 데이터 시각화 뉴스 플랫폼")
st.caption("2015~2024년 · 서울·부산·대구 · 평균기온·최고기온·강수량")

with st.sidebar:
    st.header("데이터와 분석 조건")
    mode = st.radio("실행 모드", ["교육용 데모", "기상청 공식 CSV 업로드"])
    uploaded = st.file_uploader("공식 CSV", type="csv") if mode.endswith("업로드") else None

try:
    df = load_csv(uploaded if uploaded is not None else DEMO_PATH)
except Exception as exc:
    st.error(f"데이터를 불러오지 못했습니다: {exc}")
    st.stop()

with st.sidebar:
    years = sorted(df["year"].unique().tolist())
    start_year, end_year = st.select_slider("분석 기간", years, value=(years[0], years[-1]))
    all_regions = sorted(df["region"].unique().tolist())
    regions = st.multiselect("비교 지역", all_regions, default=all_regions)
    focus_region = st.selectbox("기준 지역", regions or all_regions)
    metric_name = st.selectbox("기후지표", list(METRICS))

if not regions:
    st.warning("비교 지역을 한 곳 이상 선택하세요.")
    st.stop()

filtered = filter_data(df, start_year, end_year, regions)
summary = summarize(filtered, metric_name, focus_region)
column, unit = METRICS[metric_name]

tab1, tab2, tab3, tab4 = st.tabs(["변화 탐색", "지역·지도 비교", "데이터 뉴스", "다운로드·출처"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("기간 평균", f"{summary['mean']:.2f} {unit}")
    c2.metric("마지막 연도", f"{summary['end_value']:.2f} {unit}", f"{summary['change']:+.2f} {unit}")
    c3.metric("최고 연도", f"{summary['max_year']}년", f"{summary['max_value']:.2f} {unit}")
    c4.metric("최저 연도", f"{summary['min_year']}년", f"{summary['min_value']:.2f} {unit}")
    fig = px.line(filtered, x="year", y=column, color="region", markers=True, labels={"year": "연도", column: f"{metric_name} ({unit})", "region": "지역"}, title=f"지역별 {metric_name} 변화")
    fig.add_annotation(text=f"출처: {summary['source_name']}", xref="paper", yref="paper", x=0, y=-0.2, showarrow=False)
    st.plotly_chart(fig, width="stretch")

with tab2:
    latest = filtered[filtered["year"] == filtered["year"].max()].copy()
    bar = px.bar(latest.sort_values(column), x="region", y=column, color=column, labels={"region": "지역", column: f"{metric_name} ({unit})"}, title=f"{int(latest['year'].max())}년 지역 비교")
    st.plotly_chart(bar, width="stretch")
    map_fig = px.scatter_map(latest, lat="latitude", lon="longitude", size=column, color=column, hover_name="region", zoom=5, height=520, title=f"{metric_name} 지역 분포")
    st.plotly_chart(map_fig, width="stretch")

with tab3:
    article = generate_article(summary)
    script = generate_script(summary)
    storyboard = pd.DataFrame(generate_storyboard(summary))
    invalid = validate_generated_numbers(article + script, summary)
    if invalid:
        st.error(f"분석 근거에 없는 숫자가 발견되어 저장을 차단했습니다: {', '.join(invalid)}")
    else:
        st.success("기사와 대본의 숫자가 분석 결과와 일치합니다.")
    st.subheader("데이터 스토리텔링 기사")
    st.markdown(article)
    st.subheader("약 1분 뉴스 대본")
    st.markdown(script)
    st.subheader("AI 영상 장면 구성표")
    st.dataframe(storyboard, width="stretch", hide_index=True)
    if st.button("기사·대본·장면표 저장", disabled=bool(invalid)):
        paths = ensure_output_dirs(ROOT / "outputs")
        stem = f"{focus_region}_{metric_name}_{start_year}_{end_year}"
        save_text(article, paths["articles"] / f"{stem}_기사.md")
        save_text(script, paths["scripts"] / f"{stem}_1분대본.md")
        save_csv(storyboard, paths["storyboards"] / f"{stem}_장면표.csv")
        st.success("outputs 폴더에 저장했습니다.")

with tab4:
    powerbi = to_powerbi(filtered)
    st.download_button("Power BI CSV 다운로드", powerbi.to_csv(index=False).encode("utf-8-sig"), "climate_powerbi.csv", "text/csv")
    st.download_button("기사 Markdown 다운로드", generate_article(summary), "climate_article.md", "text/markdown")
    st.download_button("1분 대본 다운로드", generate_script(summary), "climate_script.md", "text/markdown")
    if st.button("뉴스 차트 PNG 저장"):
        paths = ensure_output_dirs(ROOT / "outputs")
        chart_path = save_timeseries_png(
            filtered,
            metric_name,
            summary["source_name"],
            paths["charts"] / f"{focus_region}_{metric_name}_{start_year}_{end_year}.png",
        )
        st.success(f"차트를 저장했습니다: {chart_path.name}")
    st.subheader("데이터 품질과 출처")
    st.write({"행 수": len(filtered), "기간": f"{start_year}~{end_year}", "지역": regions, "출처": summary["source_name"], "수집 시각": summary["collected_at"], "출처 URL": summary["source_url"]})
    st.info("데모 데이터는 교육용 고정 스냅숏입니다. 실제 보도에는 기상청 공식 CSV를 업로드하고 원본 자료를 다시 확인하세요.")
