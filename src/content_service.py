from __future__ import annotations

import re


def _number(value: float) -> str:
    return f"{value:.2f}"


def generate_article(summary: dict) -> str:
    rate_text = (
        "계산할 수 없었다"
        if summary["change_rate"] is None
        else f"{abs(summary['change_rate']):.2f}%"
    )
    direction = "상승" if summary["change"] > 0 else "하락" if summary["change"] < 0 else "변화 없음"
    return f"""# {summary['region']} {summary['metric']} 데이터 뉴스

{summary['region']}의 {summary['metric']}은 {summary['start_year']}년 {_number(summary['start_value'])}{summary['unit']}에서 {summary['end_year']}년 {_number(summary['end_value'])}{summary['unit']}로 나타났다. 변화량은 {_number(abs(summary['change']))}{summary['unit']}이며 방향은 {direction}, 변화율은 {rate_text}이다.

분석 기간 평균은 {_number(summary['mean'])}{summary['unit']}이다. 가장 높은 값은 {summary['max_year']}년 {_number(summary['max_value'])}{summary['unit']}, 가장 낮은 값은 {summary['min_year']}년 {_number(summary['min_value'])}{summary['unit']}였다.

이 결과는 선택된 기간과 지역의 관측값을 요약한 것으로, 장기적인 인과관계나 미래 예측을 의미하지 않는다.

출처: {summary['source_name']} ({summary['source_url']})  
수집 시각: {summary['collected_at']}
"""


def generate_script(summary: dict) -> str:
    direction = "올랐습니다" if summary["change"] > 0 else "내렸습니다" if summary["change"] < 0 else "같았습니다"
    return f"""# 약 1분 데이터 뉴스 대본

[앵커] 기후 데이터를 한눈에 살펴보겠습니다.

[리포터] {summary['region']}의 {summary['metric']}을 {summary['start_year']}년부터 {summary['end_year']}년까지 분석했습니다. {summary['start_year']}년 {_number(summary['start_value'])}{summary['unit']}에서 {summary['end_year']}년 {_number(summary['end_value'])}{summary['unit']}로 {_number(abs(summary['change']))}{summary['unit']} {direction}.

분석 기간 평균은 {_number(summary['mean'])}{summary['unit']}입니다. 가장 높은 값은 {summary['max_year']}년 {_number(summary['max_value'])}{summary['unit']}, 가장 낮은 값은 {summary['min_year']}년 {_number(summary['min_value'])}{summary['unit']}로 확인됐습니다.

이 수치는 선택한 관측 자료의 변화이며 원인이나 미래를 단정하지 않습니다. 데이터 시각화 뉴스였습니다.

[출처 자막] {summary['source_name']} | {summary['source_url']}
"""


def generate_storyboard(summary: dict) -> list[dict]:
    return [
        {"scene": 1, "seconds": 6, "visual": "타이틀과 지역 지도", "caption": f"{summary['region']} {summary['metric']}", "narration": "기후 데이터를 한눈에 살펴보겠습니다."},
        {"scene": 2, "seconds": 10, "visual": "분석 기간 카드", "caption": f"{summary['start_year']}~{summary['end_year']}", "narration": "선택한 기간의 관측값을 분석했습니다."},
        {"scene": 3, "seconds": 14, "visual": "시계열 차트", "caption": f"변화 {_number(abs(summary['change']))}{summary['unit']}", "narration": "첫해와 마지막 해의 변화를 확인했습니다."},
        {"scene": 4, "seconds": 12, "visual": "최고·최저 수치 카드", "caption": f"최고 {summary['max_year']} / 최저 {summary['min_year']}", "narration": "기간 중 최고와 최저 연도를 비교했습니다."},
        {"scene": 5, "seconds": 10, "visual": "지역 비교 차트", "caption": "지역별 비교", "narration": "같은 기준으로 지역별 차이를 살펴봅니다."},
        {"scene": 6, "seconds": 8, "visual": "출처와 마무리", "caption": summary["source_name"], "narration": "원인과 미래를 단정하지 않는 데이터 뉴스였습니다."},
    ]


def validate_generated_numbers(text: str, summary: dict) -> list[str]:
    allowed = {
        str(summary["start_year"]), str(summary["end_year"]), str(summary["max_year"]),
        str(summary["min_year"]), "1",
    }
    for key in ["start_value", "end_value", "change", "mean", "max_value", "min_value"]:
        value = abs(float(summary[key]))
        allowed.update({f"{value:.2f}", f"{value:.1f}", str(int(value))})
    if summary["change_rate"] is not None:
        value = abs(float(summary["change_rate"]))
        allowed.update({f"{value:.2f}", f"{value:.1f}", str(int(value))})
    # 수집 시각은 분석 주장에 쓰인 수치가 아니라 필수 출처 메타데이터다.
    metadata_numbers = re.findall(r"\d+(?:\.\d+)?", str(summary["collected_at"]))
    allowed.update(metadata_numbers)
    allowed.update(str(int(value)) for value in metadata_numbers if value.isdigit())
    found = re.findall(r"(?<![가-힣A-Za-z])\d+(?:\.\d+)?", text.replace(",", ""))
    return sorted({value for value in found if value not in allowed})
