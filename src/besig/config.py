"""분석 설정.

원본 ``.mlx`` 스크립트 맨 위의 "환경설정" 절을 대체한다. 경로·관측소 번호·
변곡점 범위 같은 값이 코드 곳곳에 흩어져 있던 것을 한 dataclass로 모았다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from .bounds import ChangePointRange
from .fitting import Strategy
from .models import DEFAULT_MODEL_TYPES

__all__ = ["AnalysisConfig", "DEFAULT_STATION"]

#: 서울(108). 관측소 번호는 ``data/weather/최적기상대목록 210217.xlsx`` 참고.
DEFAULT_STATION = 108


@dataclass
class AnalysisConfig:
    """CPM 분석 한 건의 설정."""

    energy_path: Path
    weather_dir: Path
    output_dir: Path = Path("outputs")
    building_id: str = "test"
    station: int = DEFAULT_STATION
    energy_source: str = "총계"
    model_types: Sequence[str] = DEFAULT_MODEL_TYPES
    cp_range: ChangePointRange = field(default_factory=ChangePointRange)
    strategy: Strategy = "multistart"
    n_starts: int = 8
    seed: int | None = 0
    fill_missing: bool = True
    make_plots: bool = True

    def __post_init__(self) -> None:
        self.energy_path = Path(self.energy_path)
        self.weather_dir = Path(self.weather_dir)
        self.output_dir = Path(self.output_dir)

    @property
    def csv_dir(self) -> Path:
        """결과 표(TSV)가 저장되는 폴더."""
        return self.output_dir / "csv_CPM"

    @property
    def plot_dir(self) -> Path:
        """산점도 PNG가 저장되는 폴더."""
        return self.output_dir / "pics_CPM"

    def ensure_dirs(self) -> None:
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        if self.make_plots:
            self.plot_dir.mkdir(parents=True, exist_ok=True)
