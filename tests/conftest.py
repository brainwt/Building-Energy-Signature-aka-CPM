"""테스트 공용 픽스처."""

from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
WEATHER_DIR = DATA_DIR / "weather"
FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def daily_dataset():
    """동봉된 일별 검증 자료 (2018년, 365일)의 ``(외기온, 사용량)``."""
    from besig import build_dataset, read_energy, read_weather

    energy = read_energy(DATA_DIR / "Y_daily.csv")
    weather = read_weather(WEATHER_DIR, energy.years, energy.frequency, 108)
    t_out, y_mea, _ = build_dataset(energy, weather)
    return t_out, y_mea


@pytest.fixture(scope="session")
def monthly_dataset():
    """동봉된 월별 검증 자료 (2018~2020년, 36개월)의 ``(외기온, 사용량)``."""
    from besig import build_dataset, read_energy, read_weather

    energy = read_energy(DATA_DIR / "Y_monthly.csv")
    weather = read_weather(WEATHER_DIR, energy.years, energy.frequency, 108)
    t_out, y_mea, _ = build_dataset(energy, weather)
    return t_out, y_mea


#: `global-optimization` 브랜치가 멀티스타트의 효과를 보이려고 추가한 예제 자료.
#: 둘 다 2018~2019년 월별 24점이다.
MULTISTART_EXAMPLES = (
    "Y_monthly_41220-52882.csv",
    "Y_monthly_41670-100177112.csv",
)


def load_monthly(name: str, station: int = 108):
    """``data/``의 월별 에너지 자료를 읽어 ``(외기온, 사용량)``을 만든다."""
    from besig import build_dataset, read_energy, read_weather

    energy = read_energy(DATA_DIR / name)
    weather = read_weather(WEATHER_DIR, energy.years, energy.frequency, station)
    t_out, y_mea, _ = build_dataset(energy, weather)
    return t_out, y_mea


@pytest.fixture(scope="session", params=MULTISTART_EXAMPLES)
def multistart_example(request):
    """멀티스타트 예제 자료 ``(이름, 외기온, 사용량)``."""
    return request.param, *load_monthly(request.param)


@pytest.fixture
def synthetic_3p_h():
    """계수를 아는 난방 3파라메터 자료 — 적합 정확도 확인용.

    b0=100, b1=5, b2=15 이고 관측잡음은 없다.
    """
    t = np.linspace(-10.0, 30.0, 200)
    b0, b1, b2 = 100.0, 5.0, 15.0
    y = np.where(t <= b2, b0 + b1 * (b2 - t), b0)
    return t, y, np.array([b0, b1, b2])
