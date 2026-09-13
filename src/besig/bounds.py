"""CPM 적합에 쓰이는 초기값·경계·선형 제약.

MATLAB 원본에서는 같은 내용이 ``fn_CPM_run.m``과 ``fn_set_cmp_param.m``에
중복되어 있었고 변곡점 탐색 상한이 각각 25 / 30으로 어긋나 있었다.
여기서는 한 곳으로 합치고, 값은 실제 실행 경로인 ``fn_CPM_run.m``(0~25)을
따르되 :class:`ChangePointRange`로 바꿀 수 있게 열어 두었다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .models import get_model

__all__ = ["ChangePointRange", "ParamBounds", "build_bounds"]


@dataclass(frozen=True)
class ChangePointRange:
    """변곡점(외기온) 탐색 범위 [°C]."""

    low: float = 0.0
    high: float = 25.0

    @property
    def mid(self) -> float:
        return (self.low + self.high) / 2.0

    def __post_init__(self) -> None:
        if self.low >= self.high:
            raise ValueError(f"변곡점 범위가 뒤집혔다: low={self.low} >= high={self.high}")


@dataclass(frozen=True)
class ParamBounds:
    """한 모델의 초기값·상하한·선형 부등식 제약.

    선형 제약은 MATLAB ``fmincon``과 같은 ``A @ x <= b`` 형식이다.
    """

    x0: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    a_ineq: np.ndarray | None = None
    b_ineq: np.ndarray | None = None

    def clipped_x0(self) -> np.ndarray:
        """초기값을 상하한 안으로 밀어 넣는다.

        원본은 b0 초기값을 0으로 두는데 하한이 ``min(y)``라 범위를 벗어나기도 한다.
        ``fmincon``은 이런 초기값을 경계 안으로 옮기므로 같은 동작을 맞춘다.
        """
        return np.clip(self.x0, self.lower, self.upper)


_INF = np.inf


def build_bounds(
    cpm_type: str,
    y_mea: Sequence[float],
    cp_range: ChangePointRange | None = None,
) -> ParamBounds:
    """``cpm_type`` 모델의 적합 제약을 만든다.

    Parameters
    ----------
    cpm_type:
        모델 이름 (``'1p'``, ``'3p_h'`` 등).
    y_mea:
        실측 에너지 사용량. 상수항 경계 ``[min(y), max(y)]``에 쓰인다.
    cp_range:
        변곡점 탐색 범위. 생략하면 0~25 °C.
    """
    spec = get_model(cpm_type)
    cp = cp_range or ChangePointRange()

    y = np.asarray(y_mea, dtype=float)
    y_min = float(np.nanmin(y))
    y_max = float(np.nanmax(y))
    mid = cp.mid

    # 기울기 계수 초기값은 0. 원본 주석대로 초기값에 따라 수렴점이 크게 달라진다.
    if cpm_type == "1p":
        return ParamBounds(np.array([0.0]), np.array([y_min]), np.array([y_max]))

    if cpm_type == "2p_h":
        # b0: 절편, b1: 기울기 크기(>=0). 모델식이 -b1*T 이므로 우하향이 강제된다.
        return ParamBounds(
            np.array([0.0, 0.0]), np.array([0.0, y_min]), np.array([_INF, y_max])
        )

    if cpm_type == "2p_c":
        return ParamBounds(
            np.array([0.0, 0.0]), np.array([y_min, 0.0]), np.array([y_max, _INF])
        )

    if cpm_type in ("3p_h", "3p_c"):
        return ParamBounds(
            np.array([0.0, 0.0, mid]),
            np.array([y_min, 0.0, cp.low]),
            np.array([y_max, _INF, cp.high]),
        )

    if cpm_type == "5p":
        # b3 <= b4 (좌측 변곡점이 우측보다 낮아야 한다)
        return ParamBounds(
            np.array([0.0, 0.0, 0.0, mid, mid]),
            np.array([y_min, 0.0, 0.0, cp.low, cp.low]),
            np.array([y_max, _INF, _INF, cp.high, cp.high]),
            a_ineq=np.array([[0.0, 0.0, 0.0, 1.0, -1.0]]),
            b_ineq=np.array([0.0]),
        )

    if cpm_type in ("4p_h", "4p_c"):
        # 4p_h: -b1 + b2 <= 0 / 4p_c: b1 - b2 <= 0 — 완만한 기울기가 어느 쪽인지 정한다.
        a_row = (
            np.array([[0.0, -1.0, 1.0, 0.0]])
            if cpm_type == "4p_h"
            else np.array([[0.0, 1.0, -1.0, 0.0]])
        )
        return ParamBounds(
            np.array([0.0, 0.0, 0.0, mid]),
            np.array([0.0, 0.0, 0.0, cp.low]),
            np.array([_INF, _INF, _INF, cp.high]),
            a_ineq=a_row,
            b_ineq=np.array([0.0]),
        )

    raise ValueError(f"제약 조건이 정의되지 않은 모델: {spec.name}")
