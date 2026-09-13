"""CPM 계수 추정 — MATLAB ``fmincon`` 기반 최적화의 Python 대체.

목적함수는 원본 ``fn_CPM_obj.m``과 같이 자유도 보정 RMSE
``sqrt(Σ(y - ŷ)² / (n - p))``이고, 제약 최적화기는 SciPy의 SLSQP다.

기본 전략은 ``"multistart"``다. 원본의 단일 시작점(기울기 계수 = 0)은 5p 모델에서
국소최적해에 갇히는데, ``fmincon``의 내부점 알고리즘은 우연히 그 함정을 피해 가므로
SLSQP 한 번만으로는 MATLAB 결과를 재현하지 못한다. 여러 시작점 중 최적을 고르면
동봉된 검증 자료 기준 전 모델이 MATLAB 결과와 1e-7 이내로 일치한다. 시작점 목록에
원본 초기값이 항상 포함되므로 multistart의 해는 결코 원본보다 나쁠 수 없다.
``"slsqp"``는 원본과 똑같이 단일 시작점만 쓰는 모드로 남겨 두었다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

import numpy as np
from scipy.optimize import LinearConstraint, differential_evolution, minimize

from .bounds import ChangePointRange, ParamBounds, build_bounds
from .models import DEFAULT_MODEL_TYPES, n_params, predict

__all__ = ["FitResult", "objective_rmse", "fit_model", "fit_all"]

Strategy = Literal["slsqp", "multistart", "global"]

#: 기울기 상한이 무한대인 경우 전역 탐색에 쓸 유한 상한을 만들 때의 배수.
_GLOBAL_SLOPE_SCALE = 10.0


@dataclass
class FitResult:
    """한 모델의 적합 결과."""

    cpm_type: str
    x: np.ndarray
    rmse: float
    success: bool
    message: str
    n_params: int

    def predict(self, t_out: Sequence[float]) -> np.ndarray:
        return predict(self.cpm_type, self.x, t_out)


def objective_rmse(
    x: Sequence[float], t_out: np.ndarray, y_mea: np.ndarray, cpm_type: str
) -> float:
    """자유도 보정 RMSE. 최적화 목적함수 (원본 ``fn_CPM_obj.m``)."""
    y_pred = predict(cpm_type, x, t_out)
    p = n_params(cpm_type)
    ns = y_pred.size
    denom = ns - p
    if denom <= 0:
        return float("inf")
    value = np.sqrt(np.nansum((y_mea - y_pred) ** 2) / denom)
    # 변곡점이 자료 범위 밖으로 나가면 예측이 상수가 되어 NaN/Inf가 생길 수 있다.
    return float(value) if np.isfinite(value) else float("inf")


def _constraints(pb: ParamBounds) -> list[LinearConstraint]:
    if pb.a_ineq is None or pb.b_ineq is None:
        return []
    return [LinearConstraint(pb.a_ineq, -np.inf, pb.b_ineq)]


def _finite_bounds(pb: ParamBounds, y_mea: np.ndarray, t_out: np.ndarray) -> list[tuple[float, float]]:
    """전역 탐색용으로 무한 상한을 유한한 값으로 바꾼다.

    무한대 상한은 기울기 계수에만 붙으므로, 자료에서 물리적으로 가능한
    최대 기울기 ``Δy / ΔT``에 여유를 준 값으로 대체한다.
    """
    y_span = float(np.nanmax(y_mea) - np.nanmin(y_mea))
    t_span = float(np.nanmax(t_out) - np.nanmin(t_out))
    slope_cap = (y_span / t_span if t_span > 0 else y_span) * _GLOBAL_SLOPE_SCALE
    slope_cap = max(slope_cap, 1.0)

    out = []
    for lo, hi in zip(pb.lower, pb.upper):
        out.append((float(lo), float(hi) if np.isfinite(hi) else slope_cap))
    return out


def fit_model(
    cpm_type: str,
    t_out: Sequence[float],
    y_mea: Sequence[float],
    *,
    cp_range: ChangePointRange | None = None,
    strategy: Strategy = "multistart",
    n_starts: int = 8,
    seed: int | None = 0,
) -> FitResult:
    """모델 하나를 적합한다.

    Parameters
    ----------
    cpm_type:
        모델 이름.
    t_out, y_mea:
        외기온과 실측 에너지 사용량. 길이가 같아야 한다.
    cp_range:
        변곡점 탐색 범위 (기본 0~25 °C).
    strategy:
        ``"multistart"``(기본)는 원본 초기값 + 무작위 시작점들에서 각각 최적화해
        가장 좋은 해를 고른다. ``"slsqp"``는 원본과 같이 정해진 초기값에서 한 번만,
        ``"global"``은 differential evolution으로 전역 탐색한 뒤 국소 정련한다.
    n_starts:
        ``"multistart"``일 때의 시작점 개수.
    seed:
        난수 시드. ``"multistart"``/``"global"``의 재현성을 위해 쓴다.
    """
    t = np.asarray(t_out, dtype=float)
    y = np.asarray(y_mea, dtype=float)
    if t.shape != y.shape:
        raise ValueError(f"t_out {t.shape}과 y_mea {y.shape}의 길이가 다르다")
    if t.size == 0:
        raise ValueError("입력 자료가 비어 있다")

    pb = build_bounds(cpm_type, y, cp_range)
    bounds = list(zip(pb.lower, pb.upper))
    cons = _constraints(pb)

    def local(x0: np.ndarray) -> tuple[np.ndarray, float, bool, str]:
        res = minimize(
            objective_rmse,
            x0,
            args=(t, y, cpm_type),
            method="SLSQP",
            bounds=bounds,
            constraints=cons,
            options={"maxiter": 500, "ftol": 1e-10},
        )
        return res.x, float(res.fun), bool(res.success), str(res.message)

    if strategy == "slsqp":
        x, fun, ok, msg = local(pb.clipped_x0())

    elif strategy == "multistart":
        rng = np.random.default_rng(seed)
        fin = _finite_bounds(pb, y, t)
        starts = [pb.clipped_x0()]
        for _ in range(max(0, n_starts - 1)):
            starts.append(np.array([rng.uniform(lo, hi) for lo, hi in fin]))
        best = min((local(s) for s in starts), key=lambda r: r[1])
        x, fun, ok, msg = best

    elif strategy == "global":
        fin = _finite_bounds(pb, y, t)
        de = differential_evolution(
            objective_rmse,
            fin,
            args=(t, y, cpm_type),
            constraints=cons if cons else (),
            seed=seed,
            polish=False,
            maxiter=200,
            tol=1e-8,
        )
        x, fun, ok, msg = local(np.clip(de.x, pb.lower, pb.upper))
        if de.fun < fun:  # 정련이 오히려 나빠졌으면 전역해를 쓴다
            x, fun, msg = de.x, float(de.fun), "differential_evolution"

    else:
        raise ValueError(f"알 수 없는 strategy: {strategy!r}")

    return FitResult(
        cpm_type=cpm_type,
        x=np.asarray(x, dtype=float),
        rmse=fun,
        success=ok,
        message=msg,
        n_params=n_params(cpm_type),
    )


def fit_all(
    t_out: Sequence[float],
    y_mea: Sequence[float],
    *,
    model_types: Sequence[str] = DEFAULT_MODEL_TYPES,
    cp_range: ChangePointRange | None = None,
    strategy: Strategy = "multistart",
    n_starts: int = 8,
    seed: int | None = 0,
) -> list[FitResult]:
    """여러 모델을 같은 자료에 적합해 결과 목록을 돌려준다 (순서 보존)."""
    return [
        fit_model(
            m, t_out, y_mea,
            cp_range=cp_range, strategy=strategy, n_starts=n_starts, seed=seed,
        )
        for m in model_types
    ]
