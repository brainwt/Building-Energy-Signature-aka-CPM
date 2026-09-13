"""변곡점 회귀(Change-Point Model) 모델식 정의.

ASHRAE Guideline 14 계열의 CPM 8종을 하나의 레지스트리로 통합한다.
MATLAB 원본에서는 모델마다 별도 파일(``fn_CPM_1p.m`` ~ ``fn_CPM_5p.m``)로
흩어져 있던 것을 ``ModelSpec`` 하나로 모았다.

파라메터 의미
    b0  기저 부하(상수항) 또는 절편
    b1  좌측(난방) 기울기
    b2  우측(냉방) 기울기 또는 변곡점(3p)
    b3  변곡점(4p) 또는 좌측 변곡점(5p)
    b4  우측 변곡점(5p)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

__all__ = [
    "ModelSpec",
    "MODELS",
    "DEFAULT_MODEL_TYPES",
    "ALL_MODEL_TYPES",
    "predict",
    "n_params",
    "get_model",
]


def _as_array(t_out: Sequence[float] | np.ndarray) -> np.ndarray:
    return np.asarray(t_out, dtype=float)


# --------------------------------------------------------------------------- #
# 모델식
# --------------------------------------------------------------------------- #
def _m_1p(x: np.ndarray, t: np.ndarray) -> np.ndarray:
    """상수 모델: Y = b0."""
    return np.full_like(t, x[0])


def _m_2p_h(x: np.ndarray, t: np.ndarray) -> np.ndarray:
    """난방 2파라메터: Y = b0 - b1*T (b1 >= 0 이므로 우하향)."""
    return x[0] - x[1] * t


def _m_2p_c(x: np.ndarray, t: np.ndarray) -> np.ndarray:
    """냉방 2파라메터: Y = b0 + b1*T."""
    return x[0] + x[1] * t


def _m_3p_h(x: np.ndarray, t: np.ndarray) -> np.ndarray:
    """난방 3파라메터: T <= b2 구간만 기울기, 그 위는 기저부하 b0."""
    b0, b1, b2 = x[0], x[1], x[2]
    return np.where(t <= b2, b0 + b1 * (b2 - t), b0)


def _m_3p_c(x: np.ndarray, t: np.ndarray) -> np.ndarray:
    """냉방 3파라메터: T >= b2 구간만 기울기, 그 아래는 기저부하 b0."""
    b0, b1, b2 = x[0], x[1], x[2]
    return np.where(t >= b2, b0 + b1 * (t - b2), b0)


def _m_4p_h(x: np.ndarray, t: np.ndarray) -> np.ndarray:
    """난방 4파라메터: 변곡점 b3 좌우로 기울기가 -b1, -b2."""
    b0, b1, b2, b3 = x[0], x[1], x[2], x[3]
    return np.where(t <= b3, b0 - b1 * (t - b3), b0 - b2 * (t - b3))


def _m_4p_c(x: np.ndarray, t: np.ndarray) -> np.ndarray:
    """냉방 4파라메터: 변곡점 b3 좌우로 기울기가 b1, b2."""
    b0, b1, b2, b3 = x[0], x[1], x[2], x[3]
    return np.where(t <= b3, b0 + b1 * (t - b3), b0 + b2 * (t - b3))


def _m_5p(x: np.ndarray, t: np.ndarray) -> np.ndarray:
    """난방+냉방 5파라메터: b3 이하 난방, b4 초과 냉방, 사이는 기저부하."""
    b0, b1, b2, b3, b4 = x[0], x[1], x[2], x[3], x[4]
    y = np.full_like(t, b0)
    left = t <= b3
    right = t > b4
    y[left] = b0 + b1 * (b3 - t[left])
    y[right] = b0 + b2 * (t[right] - b4)
    return y


@dataclass(frozen=True)
class ModelSpec:
    """CPM 모델 한 종의 식·파라메터 수·설명."""

    name: str
    n_params: int
    func: Callable[[np.ndarray, np.ndarray], np.ndarray]
    description: str

    def __call__(self, x: Sequence[float], t_out: Sequence[float]) -> np.ndarray:
        return self.func(np.asarray(x, dtype=float), _as_array(t_out))


MODELS: dict[str, ModelSpec] = {
    spec.name: spec
    for spec in (
        ModelSpec("1p", 1, _m_1p, "상수 (기상 비의존)"),
        ModelSpec("2p_h", 2, _m_2p_h, "난방 선형"),
        ModelSpec("2p_c", 2, _m_2p_c, "냉방 선형"),
        ModelSpec("3p_h", 3, _m_3p_h, "난방 변곡점"),
        ModelSpec("3p_c", 3, _m_3p_c, "냉방 변곡점"),
        ModelSpec("4p_h", 4, _m_4p_h, "난방 이중기울기"),
        ModelSpec("4p_c", 4, _m_4p_c, "냉방 이중기울기"),
        ModelSpec("5p", 5, _m_5p, "난방+냉방 변곡점"),
    )
}

#: MATLAB ``fn_CPM_run.m``이 실제로 적합하는 6종. 4파라메터 모델은 제외된다.
DEFAULT_MODEL_TYPES: tuple[str, ...] = ("1p", "2p_h", "2p_c", "3p_h", "3p_c", "5p")

#: 구현된 전체 모델.
ALL_MODEL_TYPES: tuple[str, ...] = tuple(MODELS)


def get_model(cpm_type: str) -> ModelSpec:
    """모델 이름으로 :class:`ModelSpec`을 찾는다."""
    try:
        return MODELS[cpm_type]
    except KeyError:
        raise ValueError(
            f"알 수 없는 CPM 모델 '{cpm_type}'. 사용 가능: {', '.join(ALL_MODEL_TYPES)}"
        ) from None


def predict(cpm_type: str, x: Sequence[float], t_out: Sequence[float]) -> np.ndarray:
    """``cpm_type`` 모델에 계수 ``x``를 넣어 외기온 ``t_out``에 대한 예측값을 낸다.

    계수는 모델이 쓰는 개수만큼만 앞에서 잘라 쓰므로, 길이 5짜리 ``[b0..b4]``를
    그대로 넘겨도 된다.
    """
    spec = get_model(cpm_type)
    x_arr = np.asarray(x, dtype=float)
    if x_arr.size < spec.n_params:
        raise ValueError(
            f"모델 '{cpm_type}'은 파라메터 {spec.n_params}개가 필요한데 {x_arr.size}개를 받았다"
        )
    return spec(x_arr[: spec.n_params], t_out)


def n_params(cpm_type: str) -> int:
    """모델의 회귀 파라메터 개수."""
    return get_model(cpm_type).n_params
