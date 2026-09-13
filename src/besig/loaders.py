"""입력 자료(에너지·기상·휴일) 읽기.

원본은 연도 2015~2021과 Windows 경로 ``.\\data input\\``이 코드에 박혀 있었다.
여기서는 자료에 들어 있는 연도를 보고 필요한 파일만 찾아 읽고, 경로는
:class:`pathlib.Path`로 다룬다. CSV 인코딩(UTF-8 / CP949)도 자동 판별한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

__all__ = [
    "Frequency",
    "EnergyData",
    "read_energy",
    "read_weather",
    "read_daynames",
    "build_dataset",
]

_ENCODINGS = ("utf-8-sig", "cp949", "utf-8")


class Frequency(str, Enum):
    """에너지 자료의 시간 해상도. ``USE_DATE`` 문자열 길이로 판별한다."""

    MONTHLY = "monthly"  # yyyyMM  (6자리)
    DAILY = "daily"      # yyyyMMdd (8자리)

    @classmethod
    def from_date_string(cls, value: str) -> "Frequency":
        length = len(str(value).strip())
        if length == 6:
            return cls.MONTHLY
        if length == 8:
            return cls.DAILY
        raise ValueError(
            f"USE_DATE '{value}'의 자릿수({length})를 해석할 수 없다. "
            "월별은 yyyyMM(6자리), 일별은 yyyyMMdd(8자리)여야 한다."
        )

    @property
    def date_format(self) -> str:
        return "%Y%m" if self is Frequency.MONTHLY else "%Y%m%d"

    @property
    def weather_prefix(self) -> str:
        return f"T_weather_all_{self.value}_"


def _read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """인코딩을 차례로 시도하며 CSV를 읽는다.

    원본 자료에는 UTF-8과 CP949 파일이 섞여 있다.
    """
    if not path.exists():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없다: {path}")
    last: Exception | None = None
    for enc in _ENCODINGS:
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except UnicodeDecodeError as exc:
            last = exc
    raise UnicodeDecodeError(  # pragma: no cover - 세 인코딩 모두 실패하는 경우
        "besig", b"", 0, 1, f"{path} 인코딩을 판별하지 못했다: {last}"
    )


@dataclass
class EnergyData:
    """에너지 사용량 자료와 그로부터 파생된 메타데이터."""

    frame: pd.DataFrame  # USE_DATE(str), ES, EUSE, date(datetime), year(int)
    frequency: Frequency

    @property
    def years(self) -> list[int]:
        return sorted(self.frame["year"].unique().tolist())

    @property
    def year_start(self) -> int:
        return int(min(self.years))

    @property
    def year_end(self) -> int:
        return int(max(self.years))


def read_energy(path: str | Path) -> EnergyData:
    """에너지 사용량 CSV(``USE_DATE``, ``ES``, ``EUSE``)를 읽는다."""
    path = Path(path)
    frame = _read_csv(path, dtype={"USE_DATE": str})

    missing = {"USE_DATE", "EUSE"} - set(frame.columns)
    if missing:
        raise ValueError(f"{path}에 필요한 열이 없다: {', '.join(sorted(missing))}")

    frame["USE_DATE"] = frame["USE_DATE"].astype(str).str.strip()
    frequency = Frequency.from_date_string(frame["USE_DATE"].iloc[0])

    frame["date"] = pd.to_datetime(frame["USE_DATE"], format=frequency.date_format)
    frame["year"] = frame["date"].dt.year
    frame["EUSE"] = pd.to_numeric(frame["EUSE"], errors="coerce")
    return EnergyData(frame=frame, frequency=frequency)


def read_weather(
    weather_dir: str | Path,
    years: Iterable[int],
    frequency: Frequency,
    station: int,
) -> pd.DataFrame:
    """연도별 기상 CSV를 이어 붙여 관측소 ``station``의 평균기온만 돌려준다.

    Returns
    -------
    ``USE_DATE``(str), ``t_avg``(float) 두 열의 DataFrame.
    """
    weather_dir = Path(weather_dir)
    years = sorted(set(int(y) for y in years))

    frames = []
    for year in years:
        path = weather_dir / f"{frequency.weather_prefix}{year}.csv"
        raw = _read_csv(path, dtype={"USE_YM": str}, usecols=["loc", "t_avg", "USE_YM"])
        frames.append(raw)

    weather = pd.concat(frames, ignore_index=True)
    weather = weather.rename(columns={"USE_YM": "USE_DATE"})
    weather["t_avg"] = pd.to_numeric(weather["t_avg"], errors="coerce")

    selected = weather.loc[weather["loc"] == station, ["USE_DATE", "t_avg"]]
    if selected.empty:
        available = sorted(weather["loc"].unique().tolist())
        raise ValueError(
            f"관측소 번호 {station}의 기상 자료가 없다. 사용 가능: {available[:20]}"
            + (" ..." if len(available) > 20 else "")
        )
    selected["USE_DATE"] = selected["USE_DATE"].astype(str).str.strip()
    return selected.reset_index(drop=True)


def read_daynames(weather_dir: str | Path, years: Iterable[int]) -> pd.Series | None:
    """휴일/요일 표(``T_oj_day_holi_YYYY.csv``)에서 요일명을 읽는다.

    일별 산점도를 요일별로 색칠하는 데 쓴다. 해당 연도 파일이 하나도 없으면
    ``None``을 돌려주며, 호출부는 연도별 색칠로 되돌아간다.
    """
    weather_dir = Path(weather_dir)
    columns = [
        "t", "DayNumber", "DayName", "locdate", "dateName", "isHoliday", "Day_index",
    ]

    frames = []
    for year in sorted(set(int(y) for y in years)):
        path = weather_dir / f"T_oj_day_holi_{year}.csv"
        if not path.exists():
            continue
        frames.append(_read_csv(path, header=0, names=columns, dtype=str))

    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)["DayName"]


def build_dataset(
    energy: EnergyData,
    weather: pd.DataFrame,
    *,
    fill_missing: bool = True,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """에너지와 기상을 ``USE_DATE`` 기준으로 조인해 ``(T, y, 조인결과)``를 만든다.

    Parameters
    ----------
    fill_missing:
        일별 자료의 결측은 스플라인 보간 후 남은 NaN을 0으로, 월별 자료의
        결측은 바로 0으로 채운다 (원본 동작).
    """
    merged = energy.frame.merge(weather, on="USE_DATE", how="inner")
    if merged.empty:
        raise ValueError(
            "에너지와 기상 자료의 USE_DATE가 하나도 겹치지 않는다. "
            "관측소 번호와 자료 기간을 확인하라."
        )
    merged = merged.sort_values("date").reset_index(drop=True)

    t_out = merged["t_avg"].to_numpy(dtype=float)
    y = merged["EUSE"].to_numpy(dtype=float)

    if fill_missing:
        if energy.frequency is Frequency.DAILY:
            y = (
                pd.Series(y)
                .interpolate(method="spline", order=3, limit_direction="both")
                .to_numpy()
            )
        y = np.nan_to_num(y, nan=0.0)

    return t_out, y, merged
