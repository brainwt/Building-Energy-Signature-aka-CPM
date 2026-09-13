"""적합·제약 조건 검증."""

import numpy as np
import pytest

from besig import ChangePointRange, build_bounds, fit_all, fit_model, objective_rmse
from besig.models import DEFAULT_MODEL_TYPES


def test_recovers_known_coefficients(synthetic_3p_h):
    """잡음 없는 합성 자료에서 참 계수를 되찾아야 한다."""
    t, y, truth = synthetic_3p_h
    fit = fit_model("3p_h", t, y)
    assert fit.rmse == pytest.approx(0.0, abs=1e-6)
    assert fit.x == pytest.approx(truth, rel=1e-3)


def test_constant_data_is_fit_by_1p():
    t = np.linspace(0.0, 30.0, 50)
    y = np.full_like(t, 7.0)
    fit = fit_model("1p", t, y)
    assert fit.x[0] == pytest.approx(7.0, rel=1e-6)
    assert fit.rmse == pytest.approx(0.0, abs=1e-9)


def test_objective_matches_manual_rmse():
    t = np.linspace(0.0, 10.0, 11)
    y = np.zeros_like(t)
    value = objective_rmse([2.0], t, y, "1p")
    assert value == pytest.approx(np.sqrt(11 * 4.0 / (11 - 1)))


def test_change_point_stays_inside_requested_range():
    t = np.linspace(-20.0, 40.0, 120)
    y = np.where(t <= 30.0, 100 + 3 * (30.0 - t), 100.0)
    fit = fit_model("3p_h", t, y, cp_range=ChangePointRange(5.0, 12.0))
    assert 5.0 <= fit.x[2] <= 12.0


def test_5p_respects_change_point_ordering():
    """b3 <= b4 선형 제약이 지켜져야 한다."""
    rng = np.random.default_rng(1)
    t = np.linspace(-10.0, 35.0, 150)
    y = np.where(t <= 8, 200 + 6 * (8 - t), np.where(t > 22, 200 + 4 * (t - 22), 200.0))
    fit = fit_model("5p", t, y + rng.normal(0, 2, t.size))
    assert fit.x[3] <= fit.x[4] + 1e-6


def test_4p_slope_ordering_constraint():
    """4p_h는 -b1 + b2 <= 0, 즉 b2 <= b1 이어야 한다."""
    rng = np.random.default_rng(2)
    t = np.linspace(-10.0, 30.0, 120)
    y = 300 - 8 * np.minimum(t, 12) - 1.5 * np.maximum(t - 12, 0)
    fit = fit_model("4p_h", t, y + rng.normal(0, 1, t.size))
    assert fit.x[2] <= fit.x[1] + 1e-6


def test_bounds_keep_slopes_non_negative():
    """기울기 계수의 부호는 모델식이 정하므로 계수 자체는 음수가 될 수 없다."""
    y = np.array([1.0, 5.0, 9.0])
    for cpm_type, slope_idx in (("2p_h", 0), ("2p_c", 1), ("3p_h", 1), ("3p_c", 1)):
        pb = build_bounds(cpm_type, y)
        assert pb.lower[slope_idx] == 0.0


def test_clipped_x0_is_inside_bounds():
    """원본은 b0 초기값을 0으로 두지만 하한은 min(y)라 범위를 벗어날 수 있다."""
    y = np.array([10.0, 20.0, 30.0])
    pb = build_bounds("3p_h", y)
    x0 = pb.clipped_x0()
    assert np.all(x0 >= pb.lower) and np.all(x0 <= pb.upper)
    assert x0[0] == 10.0


def test_invalid_change_point_range_rejected():
    with pytest.raises(ValueError, match="뒤집"):
        ChangePointRange(20.0, 5.0)


def test_mismatched_input_lengths_rejected():
    with pytest.raises(ValueError, match="길이가 다르다"):
        fit_model("1p", np.arange(5.0), np.arange(3.0))


def test_empty_input_rejected():
    with pytest.raises(ValueError, match="비어 있다"):
        fit_model("1p", np.array([]), np.array([]))


def test_unknown_strategy_rejected(synthetic_3p_h):
    t, y, _ = synthetic_3p_h
    with pytest.raises(ValueError, match="strategy"):
        fit_model("1p", t, y, strategy="annealing")  # type: ignore[arg-type]


def test_fit_all_preserves_requested_order(daily_dataset):
    t, y = daily_dataset
    fits = fit_all(t, y, strategy="slsqp")
    assert [f.cpm_type for f in fits] == list(DEFAULT_MODEL_TYPES)


def test_multistart_is_never_worse_than_single_start(daily_dataset):
    """시작점 목록에 원본 초기값이 들어 있으므로 성립해야 한다."""
    t, y = daily_dataset
    for cpm_type in DEFAULT_MODEL_TYPES:
        single = fit_model(cpm_type, t, y, strategy="slsqp")
        multi = fit_model(cpm_type, t, y, strategy="multistart")
        assert multi.rmse <= single.rmse + 1e-9


def test_multistart_is_deterministic_for_a_given_seed(daily_dataset):
    t, y = daily_dataset
    a = fit_model("5p", t, y, strategy="multistart", seed=7)
    b = fit_model("5p", t, y, strategy="multistart", seed=7)
    assert a.x == pytest.approx(b.x)
