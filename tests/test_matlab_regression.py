"""MATLAB 원본 결과와의 회귀 검증.

``tests/fixtures/CPM_Result_pktest*.txt``는 리팩토링 전 MATLAB 구현이 동봉된
검증 자료로 만든 실제 출력이다. Python 구현이 같은 입력에서 같은 답을 내는지
확인한다.
"""

import numpy as np
import pandas as pd
import pytest

from besig import AnalysisConfig, build_dataset, read_energy, read_weather, run_cpm
from besig.pipeline import RESULT_COLUMNS, results_to_frame

from conftest import DATA_DIR, FIXTURE_DIR, WEATHER_DIR

#: 적합 품질 지표별 허용 상대오차.
#:
#: RMSE·CVRMSE는 최적화가 같은 해에 도달했는지를 직접 보여주므로 촘촘하게 본다.
#: R²는 ``1 - SSerr/SStot`` 이라 적합이 나쁜 모델(SSerr > SStot)에서 RMSE의
#: 작은 차이를 몇 배로 증폭하고, 조정 R²는 원본 정의상 R²를 제곱해 다시 증폭한다.
#: 따라서 이 둘은 한 자릿수 느슨한 기준을 쓴다.
_FIT_QUALITY_TOLERANCES = {
    "RMSE": 1e-6,
    "CVRMSE": 1e-6,
    "R2": 1e-4,
    "R2_adj": 1e-4,
}

#: (입력 파일, MATLAB 결과 파일) 쌍.
_CASES = [
    ("Y_daily.csv", "CPM_Result_pktest20182018.txt"),
    ("Y_monthly.csv", "CPM_Result_pktest20182020.txt"),
]


def _run(energy_name: str) -> pd.DataFrame:
    energy = read_energy(DATA_DIR / energy_name)
    weather = read_weather(WEATHER_DIR, energy.years, energy.frequency, 108)
    t_out, y_mea, _ = build_dataset(energy, weather)
    config = AnalysisConfig(
        energy_path=DATA_DIR / energy_name, weather_dir=WEATHER_DIR, building_id="test"
    )
    results = run_cpm(t_out, y_mea, config)
    return results_to_frame(results, "test", energy.year_start, energy.year_end, "총계")


@pytest.fixture(scope="module", params=_CASES, ids=[c[0] for c in _CASES])
def case(request):
    energy_name, fixture_name = request.param
    actual = _run(energy_name).set_index("CPM_TY")
    expected = pd.read_csv(FIXTURE_DIR / fixture_name, sep="\t").set_index("CPM_TY")
    return actual, expected


def test_same_models_are_fitted(case):
    actual, expected = case
    assert set(actual.index) == set(expected.index)


def test_result_columns_match_matlab_output(case):
    actual, expected = case
    assert set(actual.reset_index().columns) == set(RESULT_COLUMNS)
    assert set(expected.reset_index().columns) == set(RESULT_COLUMNS)


def test_result_frame_column_order_matches_the_original_file():
    """새로 만든 결과 표의 열 순서가 기존 출력 파일과 같아야 한다."""
    frame = _run("Y_daily.csv")
    original = pd.read_csv(FIXTURE_DIR / "CPM_Result_pktest20182018.txt", sep="\t")
    assert list(frame.columns) == list(original.columns) == RESULT_COLUMNS


@pytest.mark.parametrize("column,rel", sorted(_FIT_QUALITY_TOLERANCES.items()))
def test_fit_quality_metrics_match(case, column, rel):
    """적합 품질 지표가 MATLAB 결과와 허용 오차 안에서 일치해야 한다."""
    actual, expected = case
    for cpm_type in expected.index:
        exp = float(expected.loc[cpm_type, column])
        act = float(actual.loc[cpm_type, column])
        if abs(exp) < 1e-6:  # 0에 가까운 값은 절대오차로 본다
            assert act == pytest.approx(exp, abs=1e-5), f"{cpm_type}.{column}"
        else:
            assert act == pytest.approx(exp, rel=rel), f"{cpm_type}.{column}"


def test_model_ranking_matches(case):
    """RMSE 오름차순 순위가 원본과 같아야 한다."""
    actual, expected = case
    assert actual["MD_RANK"].to_dict() == expected["MD_RANK"].astype(int).to_dict()


def test_sample_count_matches(case):
    actual, expected = case
    assert actual["ns"].to_dict() == expected["ns"].astype(int).to_dict()


def test_coefficients_match_where_the_model_is_identifiable(case):
    """계수 비교.

    기울기가 0으로 수렴한 모델(예: 자료가 기온과 무관할 때의 ``3p_c``)은
    변곡점 b2가 어떤 값이든 예측이 같아 계수가 정해지지 않는다. 그런 축퇴
    사례는 건너뛰고, 그 외에는 계수까지 일치해야 한다.
    """
    actual, expected = case
    checked = 0
    for cpm_type in expected.index:
        if abs(float(expected.loc[cpm_type, "b1"])) < 1e-6:
            continue  # 축퇴 — 계수가 유일하지 않다
        for col in ("b0", "b1", "b2", "b3", "b4"):
            exp = float(expected.loc[cpm_type, col])
            act = float(actual.loc[cpm_type, col])
            assert act == pytest.approx(exp, rel=1e-3, abs=1e-6), f"{cpm_type}.{col}"
        checked += 1
    assert checked >= 3, "비교할 만한 모델이 너무 적다"


def test_outlier_columns_are_matlab_formatted(case):
    """이상치 인덱스 문자열이 원본 형식(``[2 3 10]`` / ``zeros(1/0)``)이다."""
    actual, _ = case
    for column in ("Ckd_out_idx", "ZRE_out_idx"):
        for value in actual[column]:
            assert value == "zeros(1/0)" or (value.startswith("[") and value.endswith("]"))


def test_nmbe_is_effectively_zero_like_the_original(case):
    """NMBE는 양쪽 모두 수치오차 수준(≈0)이다.

    RMSE를 최소화하면 편향이 사라지므로 원본도 1e-4 미만의 값만 낸다.
    부호는 수렴 오차에 따라 달라질 수 있어 크기만 확인한다.
    """
    actual, expected = case
    assert expected["NMBE"].abs().max() < 1e-2
    assert actual["NMBE"].abs().max() < 1e-2


def test_single_start_reproduces_all_but_the_hardest_model(daily_dataset):
    """원본과 동일한 단일 시작점(slsqp)이면 5p만 국소최적해에 갇힌다.

    기본값을 multistart로 둔 이유를 문서가 아닌 코드로 남긴다.
    """
    from besig import fit_model

    t, y = daily_dataset
    expected = pd.read_csv(
        FIXTURE_DIR / "CPM_Result_pktest20182018.txt", sep="\t"
    ).set_index("CPM_TY")["RMSE"]

    single_start_fails = []
    for cpm_type in expected.index:
        rmse = fit_model(cpm_type, t, y, strategy="slsqp").rmse
        if not np.isclose(rmse, expected[cpm_type], rtol=1e-5):
            single_start_fails.append(cpm_type)
    assert single_start_fails == ["5p"]
