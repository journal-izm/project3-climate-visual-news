# 데이터 시각화를 활용한 뉴스 콘텐츠 제작 및 AI 영상 보도

기상청 기후 공공데이터를 지역·연도·지표별로 탐색하고, 차트·데이터 기사·약 1분 뉴스 대본·장면 구성표·Power BI CSV를 생성하는 교육용 Streamlit 프로젝트입니다.

## 확정 범위

- 수행시간: 72시간 / 팀 4~6명
- 환경: Windows 11, VS Code, Python 3.13.15
- 기본 기간: 2015~2024년
- 기본 지역: 서울·부산·대구
- 필수 지표: 평균기온, 최고기온, 강수량
- DB, RAG, 대규모 팩트체크, 영상 API 자동 호출은 사용하지 않습니다.

## Windows 실행

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

PowerShell 실행 정책 오류가 나면 현재 터미널에서만 아래 명령을 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

또는 `run_app.bat`을 실행할 수 있습니다.

## 테스트

```powershell
pytest -q
```

## 데이터 모드

- 데모 모드: `data/demo/climate_demo.csv`를 사용하므로 API 키가 필요 없습니다.
- 실제 데이터: 앱의 파일 업로드에서 같은 열 구조의 기상청 공식 CSV를 올립니다.

필수 열은 `year, region, latitude, longitude, avg_temp_c, max_temp_c, precipitation_mm, source_name, source_url, collected_at`입니다.

## 결과물

앱에서 생성한 파일은 `outputs/` 아래에 저장됩니다.

- `charts/`: PNG 뉴스 차트
- `articles/`: Markdown 데이터 기사
- `scripts/`: 약 1분 뉴스 대본
- `storyboards/`: 장면 구성표 CSV
- `powerbi/`: Power BI 연계 CSV

최종 MP4는 생성된 대본·장면표·차트를 이용해 ElevenLabs, HeyGen, Runway 또는 Premiere Pro에서 제작합니다. 프로그램은 외부 영상 API 없이도 실행됩니다.

## 출처 원칙

모든 화면과 출력물에 출처·단위·기준 기간을 표시합니다. 기사와 대본의 수치는 검증된 분석 결과에서만 가져오며, 생성 후 허용되지 않은 숫자가 발견되면 저장하지 않습니다.
