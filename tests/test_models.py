"""모델식 검증."""

import numpy as np
import pytest

from besig import ALL_MODEL_TYPES, DEFAULT_MODEL_TYPES, MODELS, n_params, predict

T = np.array([-10.0, -5.0, 0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0])


def test_default_types_are_the_six_matlab_fits():
    """원본 fn_CPM_run.m이 실제 적합하는 6종 (4파라메터 모델 제외)."""
    assert DEFAULT_MODEL_TYPES == ("1p", "2p_h", "2p_c", "3p_h", "3p_c", "5p")
    assert set(DEFAULT_MODEL_TYPES) <= set(ALL_MODEL_TYPES)


def test_1p_is_constant():
    assert np.allclose(predict("1p", [42.0], T), 42.0)


def test_2p_h_slopes_downward_and_2p_c_upward():
    """난방은 기온이 오르면 줄고, 냉방은 늘어야 한다."""
    heating = predict("2p_h", [100.0, 2.0], T)
    cooling = predict("2p_c", [100.0, 2.0], T)
    assert np.all(np.diff(heating) < 0)
    assert np.all(np.diff(cooling) > 0)


@pytest.mark.parametrize(
    "cpm_type,x",
    [
        ("3p_h", [100.0, 5.0, 15.0]),
        ("3p_c", [100.0, 5.0, 15.0]),
        ("4p_h", [100.0, 5.0, 2.0, 15.0]),
        ("4p_c", [100.0, 2.0, 5.0, 15.0]),
        ("5p", [100.0, 5.0, 4.0, 10.0, 20.0]),
    ],
)
def test_piecewise_models_are_continuous_at_change_points(cpm_type, x):
    """변곡점 좌우에서 예측값이 끊기지 않아야 한다."""
    cps = x[2:3] if cpm_type.startswith("3p") else (x[3:4] if cpm_type.startswith("4p") else x[3:5])
    eps = 1e-7
    for cp in cps:
        left = predict(cpm_type, x, np.array([cp - eps]))[0]
        right = predict(cpm_type, x, np.array([cp + eps]))[0]
        assert left == pytest.approx(right, abs=1e-4)


def test_3p_models_are_flat_at_base_load():
    """3파라메터는 변곡점 반대편이 정확히 기저부하 b0로 평평하다."""
    b0 = 100.0
    assert np.allclose(predict("3p_h", [b0, 5.0, 15.0], np.array([16.0, 20.0, 30.0])), b0)
    assert np.allclose(predict("3p_c", [b0, 5.0, 15.0], np.array([-5.0, 0.0, 14.0])), b0)


def test_5p_has_flat_base_between_change_points():
    b0 = 100.0
    mid = predict("5p", [b0, 5.0, 4.0, 10.0, 20.0], np.array([11.0, 15.0, 19.0]))
    assert np.allclose(mid, b0)


def test_predict_accepts_padded_coefficients():
    """길이 5짜리 [b0..b4]를 넘겨도 모델이 쓰는 만큼만 잘라 쓴다."""
    padded = predict("3p_h", [100.0, 5.0, 15.0, 0.0, 0.0], T)
    exact = predict("3p_h", [100.0, 5.0, 15.0], T)
    assert np.allclose(padded, exact)


def test_predict_rejects_too_few_coefficients():
    with pytest.raises(ValueError, match="파라메터"):
        predict("5p", [1.0, 2.0], T)


def test_unknown_model_raises():
    with pytest.raises(ValueError, match="알 수 없는 CPM 모델"):
        predict("9p", [1.0], T)


@pytest.mark.parametrize("cpm_type", ALL_MODEL_TYPES)
def test_declared_param_count_matches_name(cpm_type):
    assert n_params(cpm_type) == int(cpm_type[0])
    assert MODELS[cpm_type].name == cpm_type
