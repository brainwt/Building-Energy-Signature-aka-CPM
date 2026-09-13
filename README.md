# ***BE-sig*** : ***B***uilding ***E***nergy ***sig***nature Toolkit

[![tests](https://github.com/brainwt/Building-Energy-Signature-aka-CPM/actions/workflows/tests.yml/badge.svg)](https://github.com/brainwt/Building-Energy-Signature-aka-CPM/actions/workflows/tests.yml)

건물 에너지 사용량과 외기온의 관계를 **변곡점 회귀(CPM, Change-Point Model)** 로
적합하는 도구입니다. ASHRAE Guideline 14 계열의 모델 8종을 지원합니다.

> **v1.0 (Python)** — 기존 MATLAB 구현을 Python 패키지로 전면 리팩토링했습니다.
> MATLAB 코드는 [`legacy/matlab/`](legacy/matlab/)에 그대로 보존되어 있습니다.

---

## 설치

```bash
pip install -e .          # 개발 설치
pip install -e ".[dev]"   # 테스트 도구까지
```

Python 3.10 이상, `numpy` / `scipy` / `pandas` / `matplotlib`이 필요합니다.

## 빠른 시작

### 명령줄

```bash
# 일별 자료 분석 (서울 관측소 108)
besig run --energy data/Y_daily.csv --weather data/weather --id 건물명

# 월별 자료, 변곡점 탐색 범위와 모델 지정
besig run -e data/Y_monthly.csv -w data/weather \
          --station 108 --cp-low 5 --cp-high 22 --models 3p_h 3p_c 5p

besig models        # 사용 가능한 모델 목록
besig run --help    # 전체 옵션
```

결과는 `outputs/csv_CPM/CPM_Result_pk<건물명><시작연도><종료연도>.txt`(탭 구분)와
`outputs/pics_CPM/*.png`에 저장됩니다.

### Python

```python
from besig import AnalysisConfig, run_analysis

out = run_analysis(AnalysisConfig(
    energy_path="data/Y_daily.csv",
    weather_dir="data/weather",
    building_id="건물명",
    station=108,
))

print(out.frame)                       # 전체 결과 표 (pandas DataFrame)
best = out.best                        # RMSE가 가장 낮은 모델
print(best.cpm_type, best.stats.cvrmse, best.stats.r2)

d = best.disaggregation                # 기저/난방/냉방 분해
print(d.base_total, d.heating_total, d.cooling_total)
```

모델 하나만 직접 다루려면:

```python
import numpy as np
from besig import fit_model, compute_stats, predict

fit = fit_model("3p_h", t_out, y_mea)          # 계수 추정
stats = compute_stats("3p_h", fit.x, t_out, y_mea)
y_hat = predict("3p_h", fit.x, np.linspace(-10, 35, 100))
```

## 입력 자료 형식

| 파일 | 위치 | 열 |
|---|---|---|
| 에너지 사용량 | 아무 곳 (`--energy`) | `USE_DATE`, `ES`, `EUSE` |
| 기상 (일별) | `--weather` 폴더 | `T_weather_all_daily_YYYY.csv` — `loc`, `t_avg`, `USE_YM` |
| 기상 (월별) | `--weather` 폴더 | `T_weather_all_monthly_YYYY.csv` — 위와 동일 |
| 휴일/요일 | `--weather` 폴더 | `T_oj_day_holi_YYYY.csv` (선택 — 산점도 색 구분용) |

* `USE_DATE`가 6자리(`yyyyMM`)면 월별, 8자리(`yyyyMMdd`)면 일별로 자동 판별합니다.
* 필요한 기상 연도는 에너지 자료에서 읽어 **자동으로** 찾습니다 (연도 제한 없음).
* CSV 인코딩(UTF-8 / CP949)도 자동 판별합니다.
* 관측소 번호(`--station`)는 `data/weather/최적기상대목록 210217.xlsx` 참고.

## 지원 모델

| 모델 | 파라메터 | 설명 |
|---|---|---|
| `1p` | 1 | 상수 (기상 비의존) |
| `2p_h` / `2p_c` | 2 | 난방 / 냉방 선형 |
| `3p_h` / `3p_c` | 3 | 난방 / 냉방 변곡점 |
| `4p_h` / `4p_c` | 4 | 난방 / 냉방 이중기울기 |
| `5p` | 5 | 난방 + 냉방 변곡점 |

기본 적합 대상은 원본과 같은 6종(`1p 2p_h 2p_c 3p_h 3p_c 5p`)이며,
4파라메터 모델은 `--models`로 명시할 때만 적합합니다.

## 결과 표 열 설명

| 열 | 의미 |
|---|---|
| `ID` / `DATE_S` / `DATE_E` | 건물명 / 시작·종료 연도 |
| `CPM_TY` / `MD_RANK` | 모델 종류 / RMSE 기준 순위 (1 = 최적) |
| `b0` ~ `b4` | 모델 계수 (아래 참고) |
| `ns` | 표본 수 |
| `RMSE` / `NMBE` / `CVRMSE` | 오차 지표 (자유도 `n-p` 보정) |
| `R2` / `R2_adj` | 결정계수 / 조정 결정계수 |
| `pval_b_L` / `pval_b_R` | 좌·우 구간 기울기의 양측 t-검정 p-value |
| `pval_c_C` | 기저부하 구간 상수항의 p-value (구간이 없으면 `NaN`) |
| `Ckd_out_idx` | 쿡의 거리 기준 이상치 표본 번호 (1-based) |
| `ZRE_out_idx` | 표준화 잔차 기준 이상치 표본 번호 (`zeros(1/0)` = 없음) |
| `P_M1` / `P_M2` | 변곡점에 가장 가까운 표본 번호 |
| `Es` | 에너지원 이름 |

계수 의미는 모델에 따라 다릅니다 — `b0`는 항상 기저부하(상수항),
`b1`/`b2`는 기울기, `b2`(3p) 또는 `b3`/`b4`(4p·5p)는 변곡점 외기온입니다.
자세한 정의는 [`docs/테이블정의서_cpm_git_hub_vs1.xlsx`](docs/)를 참고하세요.

## 최적화 방식

`--strategy` 로 고를 수 있습니다.

| 값 | 동작 |
|---|---|
| `multistart` (기본) | 원본 초기값 + 무작위 시작점 여러 개에서 SLSQP, 최적해 선택 |
| `slsqp` | 원본과 동일하게 단일 시작점에서 한 번만 |
| `global` | differential evolution 전역 탐색 후 국소 정련 |

기본값이 `multistart`인 이유: 원본의 단일 시작점(기울기 계수 = 0)은 `5p` 모델에서
국소최적해에 갇히는데, MATLAB `fmincon`의 내부점 알고리즘은 우연히 그 함정을 피해
갑니다. SLSQP 한 번만으로는 MATLAB 결과를 재현하지 못하므로 여러 시작점을 씁니다.
시작점 목록에 원본 초기값이 항상 포함되므로 `multistart`의 해는 `slsqp`보다
나빠질 수 없습니다. 동봉 자료 기준 0.2초면 끝납니다.

MATLAB 쪽에서도 같은 문제를 같은 방법으로 다룬 적이 있습니다 —
`global-optimization` 브랜치의 `fn_CPM_run_MS.m`이 `MultiStart` +
`RandomStartPointSet(20)`로 `fmincon`을 감싼 구현입니다. 그 브랜치가 효과를
보이려고 추가했던 예제 자료 두 개를 `data/`로 가져와 회귀 테스트로 고정해
두었습니다 (`tests/test_multistart_benefit.py`).

| 예제 자료 | 개선되는 모델 | RMSE 개선 |
|---|---|---|
| `Y_monthly_41220-52882.csv` | `3p_c`, `5p` | 약 7.0% |
| `Y_monthly_41670-100177112.csv` | `3p_c`, `5p` | 약 3.6% |

변곡점이 없는 모델(`1p`, `2p_h`, `2p_c`)은 목적함수가 볼록해 시작점과 무관하게
같은 해로 수렴하며, 실제로 차이가 없습니다.

## MATLAB 결과와의 일치성

`tests/fixtures/`의 MATLAB 원본 출력과 대조하는 회귀 테스트가 있습니다.
기본 설정에서 동봉된 검증 자료(일별 2018년 365점, 월별 2018–2020년 36점) 기준:

| 지표 | 최대 상대오차 |
|---|---|
| `RMSE`, `CVRMSE` | < 1e-6 |
| `R2`, `R2_adj` | < 1e-4 |
| 계수 `b0`~`b4` | < 1e-3 (모델이 식별 가능한 경우) |
| `MD_RANK` (순위) | 완전 일치 |

기울기가 0으로 수렴한 축퇴 사례(자료가 기온과 무관할 때의 `3p_c` 등)는 변곡점이
유일하게 정해지지 않아 계수가 달라질 수 있습니다. 이때도 `RMSE`와 예측값은 같습니다.

### 원본의 계산상 특이점

결과 호환을 위해 그대로 유지하고 코드에 주석으로 표시해 둔 부분입니다.

* **조정 R²** 가 `1 - (n-1)/(n-p) * (1 - R²**2)` 로, 통상 정의(`1 - R²`)와 다릅니다.
* **NMBE** 를 표본수가 아닌 자유도 `n-p`로 나눕니다.
* **R²** 계산 시 `SStot`에 `1e-5`를 더해 0으로 나누는 것을 막습니다.

## 테스트

```bash
pytest                                        # 137개
pytest -q tests/test_matlab_regression.py     # MATLAB 결과 대조만
pytest -q tests/test_multistart_benefit.py    # 멀티스타트 효과 검증만
```

GitHub Actions가 `main`으로의 push와 모든 PR에서 Python 3.10~3.13 전부에 대해
테스트와 CLI 동작을 확인합니다 (`.github/workflows/tests.yml`).

## 프로젝트 구조

```
src/besig/
├── models.py           # 모델식 8종 (레지스트리)
├── bounds.py           # 초기값·경계·선형 제약
├── fitting.py          # 계수 추정 (scipy.optimize)
├── stats.py            # RMSE/NMBE/CVRMSE/R²/t-검정/Cook's D/표준화잔차
├── disaggregation.py   # 기저·난방·냉방 분해
├── loaders.py          # 에너지·기상·휴일 CSV 읽기
├── plotting.py         # 산점도 + 적합선
├── pipeline.py         # 전체 흐름, 결과 표
├── config.py           # 분석 설정
└── cli.py              # besig 명령
data/                   # 검증용 에너지·기상 자료
                        #   Y_daily.csv, Y_monthly.csv (기본 예제)
                        #   Y_monthly_4122*.csv, Y_monthly_4167*.csv (멀티스타트 예제)
tests/                  # pytest (fixtures/ = MATLAB 원본 출력)
legacy/matlab/          # 기존 MATLAB 구현 (보존)
docs/                   # 테이블정의서
```

## MATLAB 버전에서 달라진 점

* `.mlx`(바이너리) 메인 스크립트 → 평문 Python — diff·코드리뷰가 가능해졌습니다.
* 연도 2015–2021 하드코딩 제거 → 자료에 있는 연도를 자동으로 찾습니다.
* Windows 전용 경로(`.\data input\`) 제거 → 모든 경로가 인자로 지정됩니다.
* 중복 제거: 모델식 8개 파일 → 1개, 제약 조건 정의 2곳(값이 어긋나 있었음) → 1곳,
  `fn_CPM_run*.m` 3종의 복붙 코드 → 전략 인자 하나.
* CP949 깨짐 주석 정리, 4파라메터 모델 분해 누락 수정(원본은 호출 시 오류).
* 테스트 122개 추가 (MATLAB 결과 회귀 테스트 포함).

## 알고리즘 설명 및 출처

* **(250626)** [`docs/테이블정의서_cpm_git_hub_vs1.xlsx`](docs/) 파일 참고
* 참고 문헌: [Energy signature 기반 변곡점 회귀](https://www.sciencedirect.com/science/article/pii/S0378778814009645)

소스코드 사용 시 출처 표기:

> 국문: 건물부문 탄소중립 가속화를 위한 건물에너지 소비 데이터 통합관리 기반기술 개발
> (과제번호 : RS-2023-00244769)

---
# Funding

Research was conducted under the KICT Research Program (project no. 20220260-001, Data-Centric Checkup Technique of Building Energy Performance) funded by the
Ministry of Science and ICT.

This work is supported by the Korea Agency for Infrastructure Technology Advancement(KAIA) grant funded by the Ministry of Land, Infrastructure and Transport (Grant RS-2023-00244769, Development of a data framework for integrating building energy datasets and applications to accelerate carbon neutrality in the building sector).

---
# Copyright
***BE-sig*** : ***B***uilding ***E***nergy ***sig***nature Toolkit Copyright (c) 2023
Korea Institute of Civil Engineering and Building Technology, KICT (subject to receipt of any required approvals from South Korea Ministry of Land, Infrastructure and Transport, MOLIT). All rights reserved.

If you have questions about your rights to use or distribute this code, please contact KICT at deukwookim@kict.re.kr.

NOTICE. This source code was developed under funding from the MOLIT South Korea Government consequently retains certain rights. As such, the South Korea Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the code to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so.

끝.

