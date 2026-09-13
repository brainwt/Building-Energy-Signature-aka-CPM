"""통계 지표 검증."""

import numpy as np
import pytest

from besig import compute_stats, cooks_distance, standardized_residuals
from besig.stats import format_index_list, segment_geometry

T = np.linspace(-5.0, 30.0, 60)


def test_perfect_fit_gives_zero_error_metrics():
    """예측이 실측과 같으면 RMSE·NMBE·CVRMSE는 0, R²는 1이어야 한다."""
    x = [100.0, 5.0, 15.0]
    y = np.where(T <= x[2], x[0] + x[1] * (x[2] - T), x[0])
    s = compute_stats("3p_h", x, T, y)
    assert s.rmse == pytest.approx(0.0, abs=1e-9)
    assert s.nmbe == pytest.approx(0.0, abs=1e-9)
    assert s.cvrmse == pytest.approx(0.0, abs=1e-9)
    assert s.r2 == pytest.approx(1.0, abs=1e-6)


def test_rmse_uses_n_minus_p_degrees_of_freedom():
    """원본과 같이 표본수가 아니라 n-p로 나눈다."""
    y = np.full_like(T, 10.0)
    s = compute_stats("1p", [11.0], T, y)  # 잔차가 모두 1
    expected = np.sqrt(T.size / (T.size - 1))
    assert s.rmse == pytest.approx(expected)


def test_cvrmse_is_rmse_over_mean_in_percent():
    y = np.full_like(T, 10.0)
    s = compute_stats("1p", [11.0], T, y)
    assert s.cvrmse == pytest.approx(s.rmse / 10.0 * 100.0)


def test_nmbe_sign_follows_bias_direction():
    """과대예측이면 NMBE가 음수, 과소예측이면 양수."""
    y = np.full_like(T, 10.0)
    assert compute_stats("1p", [12.0], T, y).nmbe < 0
    assert compute_stats("1p", [8.0], T, y).nmbe > 0


def test_ns_counts_every_sample():
    s = compute_stats("1p", [1.0], T, np.ones_like(T))
    assert s.ns == T.size


def test_coefficients_are_padded_to_five():
    s = compute_stats("3p_h", [100.0, 5.0, 15.0], T, np.ones_like(T))
    assert s.coefficients.shape == (5,)
    assert s.coefficients[3] == 0.0 and s.coefficients[4] == 0.0


def test_change_point_sample_index_is_one_based():
    """P_M1은 변곡점에 가장 가까운 표본의 1-based 위치."""
    t = np.array([0.0, 10.0, 20.0, 30.0])
    s = compute_stats("3p_h", [100.0, 1.0, 19.0], t, np.ones_like(t))
    assert s.p_m1 == 3  # 20.0 이 세 번째
    assert s.p_m2 == 0


def test_models_without_change_point_report_zero():
    for cpm_type, x in (("1p", [1.0]), ("2p_h", [1.0, 0.5]), ("2p_c", [1.0, 0.5])):
        s = compute_stats(cpm_type, x, T, np.ones_like(T))
        assert (s.p_m1, s.p_m2) == (0, 0)


def test_center_pvalue_is_nan_when_segments_cover_everything():
    """3파라메터 이하는 좌우 구간이 전체를 덮어 가운데 구간이 비어 있다."""
    s = compute_stats("3p_h", [100.0, 5.0, 15.0], T, np.ones_like(T))
    assert np.isnan(s.pval_c_center)


def test_5p_has_a_center_segment():
    y = np.where(T <= 10, 100 + 5 * (10 - T), np.where(T > 20, 100 + 4 * (T - 20), 100.0))
    s = compute_stats("5p", [100.0, 5.0, 4.0, 10.0, 20.0], T, y + np.sin(T))
    assert not np.isnan(s.pval_c_center)


def test_zero_slope_gives_pvalue_one():
    """기울기가 0이면 t=0이므로 양측 p-value는 1."""
    s = compute_stats("1p", [10.0], T, np.full_like(T, 10.0) + np.arange(T.size) % 3)
    assert s.pval_b_left == pytest.approx(1.0)
    assert s.pval_b_right == pytest.approx(1.0)


def test_cooks_distance_flags_an_injected_outlier():
    y = np.full_like(T, 10.0)
    y[7] = 400.0
    d, idx = cooks_distance(T, y, np.full_like(T, 10.0), 1)
    assert 7 in idx
    assert d[7] == np.nanmax(d)


def test_standardized_residuals_flag_large_deviations():
    y = np.full_like(T, 10.0)
    y[3] = 10.0 + 50.0
    zre, idx = standardized_residuals(y, np.full_like(T, 10.0), 1)
    assert 3 in idx
    assert zre.shape == T.shape


def test_zre_threshold_is_configurable():
    y = np.full_like(T, 10.0)
    y[3] = 12.0
    _, strict = standardized_residuals(y, np.full_like(T, 10.0), 1, threshold=0.5)
    _, loose = standardized_residuals(y, np.full_like(T, 10.0), 1, threshold=100.0)
    assert strict.size > loose.size == 0


def test_format_index_list_matches_matlab_output():
    """MATLAB mat2str의 쉼표를 /로 바꾼 형식, 인덱스는 1-based."""
    assert format_index_list(np.array([1, 2, 9])) == "[2 3 10]"
    assert format_index_list(np.array([], dtype=int)) == "zeros(1/0)"


def test_segment_geometry_linearises_each_side():
    """구간 절편·기울기가 그 구간의 실제 직선과 일치해야 한다."""
    x = [100.0, 5.0, 15.0]
    geom = segment_geometry("3p_h", x, T)
    t_left = T[geom.idx_left]
    from besig import predict

    assert np.allclose(
        geom.yint_left + geom.yslope_left * t_left, predict("3p_h", x, t_left)
    )
    assert geom.yslope_right == 0.0
    assert geom.yint_right == pytest.approx(100.0)


def test_segment_geometry_covers_all_samples_for_two_parameter_models():
    """2파라메터 이하는 변곡점이 없어 좌우가 모두 전 구간을 가리킨다."""
    geom = segment_geometry("2p_h", [10.0, 1.0], T)
    assert geom.idx_left.size == T.size
    assert geom.idx_right.size == T.size
