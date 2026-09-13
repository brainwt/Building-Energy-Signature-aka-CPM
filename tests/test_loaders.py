"""입력 자료 읽기 검증."""

import numpy as np
import pandas as pd
import pytest

from besig import Frequency, build_dataset, read_daynames, read_energy, read_weather

from conftest import DATA_DIR, WEATHER_DIR


def test_detects_daily_frequency():
    energy = read_energy(DATA_DIR / "Y_daily.csv")
    assert energy.frequency is Frequency.DAILY
    assert energy.years == [2018]
    assert len(energy.frame) == 365


def test_detects_monthly_frequency():
    energy = read_energy(DATA_DIR / "Y_monthly.csv")
    assert energy.frequency is Frequency.MONTHLY
    assert energy.years == [2018, 2019, 2020]
    assert (energy.year_start, energy.year_end) == (2018, 2020)


@pytest.mark.parametrize(
    "value,expected",
    [("201801", Frequency.MONTHLY), ("20180101", Frequency.DAILY)],
)
def test_frequency_from_date_string(value, expected):
    assert Frequency.from_date_string(value) is expected


def test_unparseable_date_length_is_reported():
    with pytest.raises(ValueError, match="자릿수"):
        Frequency.from_date_string("2018")


def test_missing_file_is_reported_with_its_path(tmp_path):
    with pytest.raises(FileNotFoundError, match="찾을 수 없다"):
        read_energy(tmp_path / "없는파일.csv")


def test_missing_required_column_is_reported(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("USE_DATE,ES\n20180101,총계\n", encoding="utf-8")
    with pytest.raises(ValueError, match="EUSE"):
        read_energy(path)


def test_cp949_encoded_input_is_read():
    """원본 자료에는 CP949로 저장된 파일이 섞여 있다."""
    energy = read_energy(DATA_DIR / "Y_monthly.csv")
    assert energy.frame["EUSE"].notna().all()


def test_weather_selects_only_the_requested_station():
    weather = read_weather(WEATHER_DIR, [2018], Frequency.DAILY, 108)
    assert len(weather) == 365
    assert list(weather.columns) == ["USE_DATE", "t_avg"]


def test_unknown_station_lists_available_ones():
    with pytest.raises(ValueError, match="관측소 번호 99999"):
        read_weather(WEATHER_DIR, [2018], Frequency.DAILY, 99999)


def test_weather_spans_multiple_years():
    weather = read_weather(WEATHER_DIR, [2018, 2019], Frequency.MONTHLY, 108)
    assert len(weather) == 24


def test_build_dataset_joins_on_use_date():
    energy = read_energy(DATA_DIR / "Y_daily.csv")
    weather = read_weather(WEATHER_DIR, energy.years, energy.frequency, 108)
    t_out, y_mea, merged = build_dataset(energy, weather)
    assert t_out.shape == y_mea.shape == (365,)
    assert merged["date"].is_monotonic_increasing


def test_build_dataset_reports_a_non_overlapping_join():
    energy = read_energy(DATA_DIR / "Y_daily.csv")
    weather = pd.DataFrame({"USE_DATE": ["19000101"], "t_avg": [0.0]})
    with pytest.raises(ValueError, match="겹치지 않는다"):
        build_dataset(energy, weather)


def test_fill_missing_removes_nan_from_daily_data():
    energy = read_energy(DATA_DIR / "Y_daily.csv")
    energy.frame.loc[10:20, "EUSE"] = np.nan
    weather = read_weather(WEATHER_DIR, energy.years, energy.frequency, 108)
    _, filled, _ = build_dataset(energy, weather, fill_missing=True)
    assert not np.isnan(filled).any()


def test_fill_missing_can_be_disabled():
    energy = read_energy(DATA_DIR / "Y_daily.csv")
    energy.frame.loc[10:20, "EUSE"] = np.nan
    weather = read_weather(WEATHER_DIR, energy.years, energy.frequency, 108)
    _, raw, _ = build_dataset(energy, weather, fill_missing=False)
    assert np.isnan(raw).any()


def test_daynames_are_read_for_available_years():
    names = read_daynames(WEATHER_DIR, [2018])
    assert names is not None
    assert len(names) == 365
    assert set(names.unique()) <= {"월", "화", "수", "목", "금", "토", "일"}


def test_daynames_return_none_when_no_year_file_exists():
    """휴일 표는 2021년분이 빠져 있다. 없으면 None을 돌려주고 호출부가 대체한다."""
    assert read_daynames(WEATHER_DIR, [1999]) is None
