"""적합된 CPM으로 에너지 사용량을 기저/난방/냉방으로 분해한다.

MATLAB ``fn_CPM_HC.m``을 옮겼다. 원본은 4파라메터 모델에서 분해량을 0으로만
두고 시계열 배열은 아예 만들지 않아 호출 시 오류가 나는 상태였는데,
여기서는 다른 모델과 같은 방식(변곡점 기준 좌우 초과분)으로 채웠다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .models import predict

__all__ = ["Disaggregation", "disaggregate"]


@dataclass
class Disaggregation:
    """기저(base)·난방(heating)·냉방(cooling) 분해 결과.

    ``*_series``는 표본별 시계열, ``*_total``은 그 합이다.
    단위는 입력 에너지 자료와 같다.
    """

    cpm_type: str
    predicted: np.ndarray
    base_series: np.ndarray
    heating_series: np.ndarray
    cooling_series: np.ndarray

    @property
    def base_total(self) -> float:
        return float(np.sum(self.base_series))

    @property
    def heating_total(self) -> float:
        return float(np.sum(self.heating_series))

    @property
    def cooling_total(self) -> float:
        return float(np.sum(self.cooling_series))

    def as_dict(self) -> dict[str, float]:
        return {
            "CPM_TY": self.cpm_type,
            "Eb": self.base_total,
            "Eh": self.heating_total,
            "Ec": self.cooling_total,
        }


def disaggregate(
    cpm_type: str, x: Sequence[float], t_out: Sequence[float]
) -> Disaggregation:
    """계수 ``x``의 ``cpm_type`` 모델로 외기온 ``t_out``에서의 분해량을 구한다.

    분해 규칙
        * 기저부하는 상수항 ``b0``이며 전 구간에 깔린다.
        * 난방/냉방은 각 구간에서 기저부하를 넘는 초과분이다.
        * ``1p``는 전량 기저, ``2p_h``/``2p_c``는 기저부하 구간이 없어
          전량을 난방/냉방으로 본다 (원본 정의).
    """
    t = np.asarray(t_out, dtype=float)
    xa = np.asarray(x, dtype=float)
    y_pred = predict(cpm_type, xa, t)

    zeros = np.zeros_like(t)
    b0 = float(xa[0])
    base = np.full_like(t, b0)

    if cpm_type == "1p":
        return Disaggregation(cpm_type, y_pred, y_pred.copy(), zeros.copy(), zeros.copy())

    if cpm_type == "2p_h":
        return Disaggregation(cpm_type, y_pred, zeros.copy(), y_pred.copy(), zeros.copy())

    if cpm_type == "2p_c":
        return Disaggregation(cpm_type, y_pred, zeros.copy(), zeros.copy(), y_pred.copy())

    heating = zeros.copy()
    cooling = zeros.copy()

    if cpm_type == "3p_h":
        mask = t <= xa[2]
        heating[mask] = y_pred[mask] - b0
    elif cpm_type == "3p_c":
        mask = t >= xa[2]
        cooling[mask] = y_pred[mask] - b0
    elif cpm_type in ("4p_h", "4p_c"):
        # 변곡점 b3 좌우 모두 기울기가 있다. 좌측 초과분을 난방, 우측을 냉방으로 본다.
        left, right = t <= xa[3], t > xa[3]
        heating[left] = y_pred[left] - b0
        cooling[right] = y_pred[right] - b0
    elif cpm_type == "5p":
        left, right = t <= xa[3], t > xa[4]
        heating[left] = y_pred[left] - b0
        cooling[right] = y_pred[right] - b0
    else:
        raise ValueError(f"분해 규칙이 없는 모델: {cpm_type}")

    return Disaggregation(cpm_type, y_pred, base, heating, cooling)
