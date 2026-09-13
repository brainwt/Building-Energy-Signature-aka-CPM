"""멀티스타트가 실제로 더 나은 해를 찾는지 확인한다.

`global-optimization` 브랜치가 MATLAB `MultiStart`로 같은 문제를 다루면서
효과를 보이려고 예제 자료 두 개를 추가했다. 그 자료를 그대로 가져와,
Python 구현에서도 같은 개선이 나오는지 회귀 테스트로 고정한다.

원본 단일 시작점(기울기 계수 = 0)은 **변곡점이 있는 모델**에서 국소최적해에
갇힌다. 변곡점이 없는 모델은 목적함수가 볼록해 시작점과 무관하게 같은 해로 간다.
"""

import pytest

from besig import fit_model
from besig.models import DEFAULT_MODEL_TYPES

#: 이 자료들에서 멀티스타트가 더 나은 해를 찾는 모델과, 최소 RMSE 개선율 [%].
#: 값은 두 예제 모두에서 관측된 개선폭(약 7% / 3.6%)보다 여유 있게 낮춰 잡았다.
_EXPECTED_GAINS = {"3p_c": 3.0, "5p": 3.0}

#: 목적함수가 볼록해 시작점과 무관하게 같은 해가 나오는 모델.
_CONVEX_MODELS = tuple(m for m in DEFAULT_MODEL_TYPES if m not in _EXPECTED_GAINS)


def _rmse(cpm_type, t, y, strategy):
    return fit_model(cpm_type, t, y, strategy=strategy).rmse


@pytest.mark.parametrize("cpm_type,min_gain_pct", sorted(_EXPECTED_GAINS.items()))
def test_multistart_improves_change_point_models(multistart_example, cpm_type, min_gain_pct):
    """변곡점 모델에서 단일 시작점보다 눈에 띄게 나은 해를 찾아야 한다."""
    name, t, y = multistart_example
    single = _rmse(cpm_type, t, y, "slsqp")
    multi = _rmse(cpm_type, t, y, "multistart")

    gain_pct = (single - multi) / single * 100.0
    assert gain_pct >= min_gain_pct, (
        f"{name} / {cpm_type}: 개선 {gain_pct:.2f}% < 기대 {min_gain_pct}% "
        f"(단일 {single:.6f} → 멀티 {multi:.6f})"
    )


@pytest.mark.parametrize("cpm_type", _CONVEX_MODELS)
def test_convex_models_are_unaffected_by_the_start_point(multistart_example, cpm_type):
    """변곡점이 없는 모델은 시작점이 달라도 같은 해에 도달한다."""
    _, t, y = multistart_example
    single = _rmse(cpm_type, t, y, "slsqp")
    multi = _rmse(cpm_type, t, y, "multistart")
    assert multi == pytest.approx(single, rel=1e-6)


def test_global_strategy_is_at_least_as_good_as_multistart(multistart_example):
    """전역 탐색이 멀티스타트보다 나쁜 해를 내면 안 된다."""
    _, t, y = multistart_example
    multi = _rmse("5p", t, y, "multistart")
    glob = _rmse("5p", t, y, "global")
    assert glob <= multi * (1 + 1e-6)


def test_zero_usage_months_do_not_break_the_fit():
    """`41670-100177112`는 사용량 0인 달이 6개 있다. 그래도 적합이 되어야 한다."""
    from conftest import load_monthly

    t, y = load_monthly("Y_monthly_41670-100177112.csv")
    assert (y == 0).sum() == 6
    for cpm_type in DEFAULT_MODEL_TYPES:
        fit = fit_model(cpm_type, t, y)
        assert fit.rmse > 0 and fit.rmse < float("inf")
