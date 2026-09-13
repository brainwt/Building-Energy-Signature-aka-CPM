"""CPM 적합 결과의 통계 지표.

MATLAB ``fn_CPM_stat.m``을 옮긴 것으로, 지표 정의와 자유도 처리는 원본 그대로다.
원본의 계산상 특이점은 그대로 두고 주석으로 표시해 두었다 —
결과 재현이 목적이므로 임의로 고치지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
from scipy import stats as sps

from .models import predict, n_params

__all__ = [
    "SegmentGeometry",
    "CPMStats",
    "segment_geometry",
    "compute_stats",
    "cooks_distance",
    "standardized_residuals",
    "format_index_list",
]

#: 2파라메터 이하 모델에는 실제 변곡점이 없다. 좌/우 구간을 나누는 대신
#: 전 구간을 양쪽 모두로 취급하려고 원본이 쓰던 ±50 °C 더미 경계.
_DUMMY_LEFT_BOUND = 50.0
_DUMMY_RIGHT_BOUND = -50.0


@dataclass(frozen=True)
class SegmentGeometry:
    """t-검정을 위해 좌/우 구간을 나누고 각 구간의 절편·기울기를 뽑은 결과."""

    p: int
    p_left: int
    p_right: int
    idx_left: np.ndarray
    idx_right: np.ndarray
    yint_left: float
    yslope_left: float
    yint_right: float
    yslope_right: float


def segment_geometry(
    cpm_type: str, x: Sequence[float], t_out: Sequence[float]
) -> SegmentGeometry:
    """모델별 좌/우 구간 인덱스와 그 구간의 직선식(절편·기울기)을 구한다.

    기울기 계수는 모델식 안에서 ``(b2 - T)`` 같은 형태로 쓰이므로, 그대로
    t-검정에 넣을 수 없다. 각 구간을 ``y = 절편 + 기울기 * T`` 로 다시 쓴 값이
    필요하며 이 함수가 그 변환을 담당한다.
    """
    t = np.asarray(t_out, dtype=float)
    xa = np.asarray(x, dtype=float)
    b0, b1, b2, b3, b4 = (xa[i] if i < xa.size else 0.0 for i in range(5))
    p = n_params(cpm_type)

    whole_left = np.flatnonzero(t <= _DUMMY_LEFT_BOUND)
    whole_right = np.flatnonzero(t > _DUMMY_RIGHT_BOUND)

    if cpm_type == "1p":
        return SegmentGeometry(p, 1, 1, whole_left, whole_right, b0, 0.0, 0.0, 0.0)

    if cpm_type == "2p_h":
        return SegmentGeometry(p, 2, 2, whole_left, whole_right, b0, -b1, 0.0, 0.0)

    if cpm_type == "2p_c":
        return SegmentGeometry(p, 2, 2, whole_left, whole_right, 0.0, 0.0, b0, b1)

    if cpm_type == "3p_h":
        return SegmentGeometry(
            p, 2, 1,
            np.flatnonzero(t < b2), np.flatnonzero(t >= b2),
            b0 + b1 * b2, -b1, b0, 0.0,
        )

    if cpm_type == "3p_c":
        # (220920 원본 수정분) 기울기가 붙는 쪽은 변곡점 오른쪽이다.
        return SegmentGeometry(
            p, 1, 2,
            np.flatnonzero(t <= b2), np.flatnonzero(t > b2),
            b0, 0.0, b0 - b1 * b2, b1,
        )

    if cpm_type == "4p_h":
        return SegmentGeometry(
            p, 2, 2,
            np.flatnonzero(t <= b3), np.flatnonzero(t > b3),
            b0 + b1 * b3, -b1, b0 + b2 * b3, -b2,
        )

    if cpm_type == "4p_c":
        return SegmentGeometry(
            p, 2, 2,
            np.flatnonzero(t <= b3), np.flatnonzero(t > b3),
            b0 - b1 * b3, b1, b0 - b2 * b3, b2,
        )

    if cpm_type == "5p":
        return SegmentGeometry(
            p, 2, 2,
            np.flatnonzero(t <= b3), np.flatnonzero(t > b4),
            b0 + b1 * b3, -b1, b0 - b2 * b4, b2,
        )

    raise ValueError(f"구간 정의가 없는 모델: {cpm_type}")


def _rmse(y_mea: np.ndarray, y_pred: np.ndarray, p: int) -> float:
    """자유도 ``n - p``로 나눈 RMSE. 원본과 같이 NaN은 건너뛴다."""
    ns = y_mea.size
    if ns <= p:
        return float("nan")
    return float(np.sqrt(np.nansum((y_mea - y_pred) ** 2) / (ns - p)))


def _r_squared(y_mea: np.ndarray, y_pred: np.ndarray, p: int) -> tuple[float, float]:
    """R²과 조정 R².

    원본과 동일하게 ``SStot``에 1e-5를 더해 0으로 나누는 것을 막고,
    조정 R²은 ``1 - (n-1)/(n-p) * (1 - R²**2)``로 계산한다. ``R²**2``은
    통상적인 정의(``1 - R²``)와 다르지만 기존 결과와의 호환을 위해 유지한다.
    """
    ns = y_pred.size
    y_avg = float(np.nanmean(y_mea))
    ss_err = float(np.nansum((y_pred - y_mea) ** 2))
    ss_tot = float(np.nansum((y_mea - y_avg) ** 2))
    r2 = 1.0 - ss_err / (ss_tot + 1e-5)
    if ns == p:
        return r2, float("nan")
    r2_adj = 1.0 - (ns - 1) / (ns - p) * (1.0 - r2**2)
    return r2, r2_adj


def _t_test(
    t_out: np.ndarray,
    y_mea: np.ndarray,
    y_pred: np.ndarray,
    p: int,
    yint: float,
    yslope: float,
) -> tuple[float, float]:
    """구간 절편·기울기의 양측 t-검정 p-value ``(pval_intercept, pval_slope)``.

    표본이 너무 적거나 외기온이 한 점에 몰려 분산이 0이면 NaN을 돌려준다.
    """
    ns = t_out.size
    if ns <= p:
        return float("nan"), float("nan")

    x_bar = float(np.mean(t_out))
    x_var = float(np.sum((t_out - x_bar) ** 2))
    rmse = _rmse(y_mea, y_pred, p)
    if x_var == 0.0 or rmse == 0.0 or not np.isfinite(rmse):
        return float("nan"), float("nan")

    se_b0 = rmse * np.sqrt(1.0 / ns + x_bar**2 / x_var)
    se_b1 = rmse / np.sqrt(x_var)
    df = ns - p

    t_c = yint / se_b0
    t_b = yslope / se_b1
    pval_c = float((1.0 - sps.t.cdf(abs(t_c), df)) * 2.0)
    pval_b = float((1.0 - sps.t.cdf(abs(t_b), df)) * 2.0)
    return pval_c, pval_b


def cooks_distance(
    t_out: np.ndarray, y_mea: np.ndarray, y_pred: np.ndarray, p: int
) -> tuple[np.ndarray, np.ndarray]:
    """쿡의 거리와 이상치 인덱스(0-based).

    지렛대값은 단순회귀 공식 ``h = (T - T̄)² / Σ(T - T̄)² + 1/n``을 쓰고,
    판정 기준은 MATLAB 관례인 ``3 * mean(D)``다.
    """
    ns = t_out.size
    mean_t = float(np.sum(t_out) / ns)
    centered = (t_out - mean_t) ** 2
    denom = float(np.sum(centered))
    h = centered / denom + 1.0 / ns if denom != 0.0 else np.full(ns, 1.0 / ns)

    err = (y_pred - y_mea) ** 2
    mse = np.nansum((y_mea - y_pred) ** 2) / (ns - p) if ns > p else np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        d = err / (mse * p) * (h / (1.0 - h) ** 2)

    ref = 3.0 * float(np.nanmean(d)) if np.isfinite(d).any() else np.nan
    idx = np.flatnonzero(d > ref) if np.isfinite(ref) else np.array([], dtype=int)
    return d, idx


def standardized_residuals(
    y_mea: np.ndarray, y_pred: np.ndarray, p: int, threshold: float = 2.5
) -> tuple[np.ndarray, np.ndarray]:
    """표준화 잔차(ZRE)와 ``|ZRE| > threshold`` 인 이상치 인덱스(0-based)."""
    rmse = _rmse(y_mea, y_pred, p)
    e = y_pred - y_mea
    if not np.isfinite(rmse) or rmse == 0.0:
        zre = np.full_like(e, np.nan)
    else:
        zre = (e - np.nanmean(e)) / rmse
    idx = np.flatnonzero(np.abs(zre) > threshold)
    return zre, idx


def format_index_list(idx: np.ndarray) -> str:
    """이상치 인덱스를 원본 결과 파일과 같은 문자열로 만든다.

    MATLAB이 ``mat2str`` 결과의 쉼표를 ``/``로 바꿔 쓰던 형식을 따른다.
    인덱스는 1-based로 변환하며, 비어 있으면 ``zeros(1/0)``이 된다.
    """
    if idx.size == 0:
        return "zeros(1/0)"
    return "[" + " ".join(str(int(i) + 1) for i in idx) + "]"


@dataclass
class CPMStats:
    """한 모델 적합의 통계 지표 묶음."""

    cpm_type: str
    coefficients: np.ndarray  # 길이 5로 패딩된 [b0, b1, b2, b3, b4]
    ns: int
    rmse: float
    nmbe: float
    cvrmse: float
    r2: float
    r2_adj: float
    pval_b_left: float
    pval_b_right: float
    pval_c_center: float
    cook_d: np.ndarray = field(repr=False)
    cook_outlier_idx: np.ndarray = field(repr=False)
    zre: np.ndarray = field(repr=False)
    zre_outlier_idx: np.ndarray = field(repr=False)
    p_m1: int
    p_m2: int

    @property
    def b(self) -> tuple[float, float, float, float, float]:
        return tuple(float(v) for v in self.coefficients)  # type: ignore[return-value]


def _change_point_sample_index(cpm_type: str, t: np.ndarray, x: np.ndarray) -> tuple[int, int]:
    """변곡점에 가장 가까운 표본의 1-based 인덱스 ``(P_M1, P_M2)``.

    월별 데이터에서는 변곡점이 몇 월에 해당하는지를 보여주는 값이다.
    변곡점이 없는 모델은 (0, 0).
    """
    def nearest(value: float) -> int:
        return int(np.argmin(np.abs(t - value))) + 1

    if cpm_type in ("3p_h", "3p_c"):
        return nearest(x[2]), 0
    if cpm_type in ("4p_h", "4p_c"):
        return nearest(x[3]), 0
    if cpm_type == "5p":
        return nearest(x[3]), nearest(x[4])
    return 0, 0


def compute_stats(
    cpm_type: str,
    x_opt: Sequence[float],
    t_out: Sequence[float],
    y_mea: Sequence[float],
) -> CPMStats:
    """적합된 계수 ``x_opt``에 대한 전체 통계 지표를 계산한다."""
    t = np.asarray(t_out, dtype=float)
    y = np.asarray(y_mea, dtype=float)
    x = np.asarray(x_opt, dtype=float)

    y_pred = predict(cpm_type, x, t)
    geom = segment_geometry(cpm_type, x, t)
    p = geom.p
    ns = t.size

    rmse = _rmse(y, y_pred, p)
    y_avg = float(np.nanmean(y))
    # NMBE도 RMSE와 같은 자유도 n-p로 나눈다 (원본 정의).
    nmbe = float(np.nansum(y - y_pred) / (ns - p) / y_avg * 100.0) if ns > p else float("nan")
    cvrmse = float(rmse / abs(y_avg) * 100.0) if y_avg != 0 else float("nan")
    r2, r2_adj = _r_squared(y, y_pred, p)

    il, ir = geom.idx_left, geom.idx_right
    _, pval_b_left = _t_test(t[il], y[il], y_pred[il], geom.p_left, geom.yint_left, geom.yslope_left)
    _, pval_b_right = _t_test(t[ir], y[ir], y_pred[ir], geom.p_right, geom.yint_right, geom.yslope_right)

    # 좌·우 어디에도 속하지 않는 가운데 구간 (5p 모델의 기저부하 구간).
    center = np.setdiff1d(np.arange(ns), np.union1d(il, ir))
    pval_c_center, _ = _t_test(t[center], y[center], y_pred[center], 1, float(x[0]), 0.0)

    cook_d, cook_idx = cooks_distance(t, y, y_pred, p)
    zre, zre_idx = standardized_residuals(y, y_pred, p)

    padded = np.zeros(5)
    padded[: x.size] = x
    p_m1, p_m2 = _change_point_sample_index(cpm_type, t, padded)

    return CPMStats(
        cpm_type=cpm_type,
        coefficients=padded,
        ns=ns,
        rmse=rmse,
        nmbe=nmbe,
        cvrmse=cvrmse,
        r2=r2,
        r2_adj=r2_adj,
        pval_b_left=pval_b_left,
        pval_b_right=pval_b_right,
        pval_c_center=pval_c_center,
        cook_d=cook_d,
        cook_outlier_idx=cook_idx,
        zre=zre,
        zre_outlier_idx=zre_idx,
        p_m1=p_m1,
        p_m2=p_m2,
    )
