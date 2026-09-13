"""에너지 분해 검증."""

import numpy as np
import pytest

from besig import disaggregate, predict

T = np.linspace(-10.0, 35.0, 100)


@pytest.mark.parametrize(
    "cpm_type,x",
    [
        ("1p", [100.0]),
        ("2p_h", [200.0, 3.0]),
        ("2p_c", [100.0, 3.0]),
        ("3p_h", [100.0, 5.0, 15.0]),
        ("3p_c", [100.0, 5.0, 18.0]),
        ("4p_h", [100.0, 5.0, 2.0, 15.0]),
        ("4p_c", [100.0, 2.0, 5.0, 15.0]),
        ("5p", [100.0, 5.0, 4.0, 10.0, 20.0]),
    ],
)
def test_components_sum_to_the_prediction(cpm_type, x):
    """기저 + 난방 + 냉방이 예측값과 같아야 한다 (에너지 보존)."""
    d = disaggregate(cpm_type, x, T)
    total = d.base_series + d.heating_series + d.cooling_series
    assert np.allclose(total, predict(cpm_type, x, T))


@pytest.mark.parametrize("cpm_type,x", [("3p_h", [100.0, 5.0, 15.0]), ("5p", [100.0, 5.0, 4.0, 10.0, 20.0])])
def test_components_are_non_negative_for_valid_coefficients(cpm_type, x):
    d = disaggregate(cpm_type, x, T)
    assert np.all(d.heating_series >= -1e-9)
    assert np.all(d.cooling_series >= -1e-9)


def test_1p_is_entirely_base_load():
    d = disaggregate("1p", [100.0], T)
    assert d.heating_total == 0.0 and d.cooling_total == 0.0
    assert d.base_total == pytest.approx(100.0 * T.size)


def test_heating_only_models_produce_no_cooling():
    assert disaggregate("3p_h", [100.0, 5.0, 15.0], T).cooling_total == 0.0
    assert disaggregate("2p_h", [200.0, 3.0], T).cooling_total == 0.0


def test_cooling_only_models_produce_no_heating():
    assert disaggregate("3p_c", [100.0, 5.0, 18.0], T).heating_total == 0.0
    assert disaggregate("2p_c", [100.0, 3.0], T).heating_total == 0.0


def test_5p_splits_both_ways():
    d = disaggregate("5p", [100.0, 5.0, 4.0, 10.0, 20.0], T)
    assert d.heating_total > 0 and d.cooling_total > 0
    assert d.base_total == pytest.approx(100.0 * T.size)


def test_4p_models_are_disaggregated():
    """원본은 4파라메터 분해를 빼먹어 호출 시 오류가 났다. 여기서는 채워 넣었다."""
    d = disaggregate("4p_h", [100.0, 5.0, 2.0, 15.0], T)
    assert d.heating_series.shape == T.shape
    assert d.heating_total > 0


def test_as_dict_exposes_totals():
    d = disaggregate("3p_h", [100.0, 5.0, 15.0], T)
    row = d.as_dict()
    assert row["CPM_TY"] == "3p_h"
    assert row["Eb"] == pytest.approx(d.base_total)
