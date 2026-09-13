"""분석 전체 흐름 — 자료 읽기 → 적합 → 통계 → 결과 표.

원본 ``Run_CPM_onebyone_f.mlx`` + ``fn_CPM_run.m``의 역할을 합친 모듈이다.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import AnalysisConfig
from .disaggregation import Disaggregation, disaggregate
from .fitting import FitResult, fit_all
from .loaders import (
    EnergyData,
    Frequency,
    build_dataset,
    read_daynames,
    read_energy,
    read_weather,
)
from .stats import CPMStats, compute_stats, format_index_list

__all__ = ["CPMResult", "RESULT_COLUMNS", "run_cpm", "run_analysis", "results_to_frame"]

#: 결과 표의 열 순서. 기존 ``CPM_Result_pk*.txt``와 동일하게 맞춘다.
RESULT_COLUMNS = [
    "ID", "DATE_S", "DATE_E", "CPM_TY", "MD_RANK",
    "b0", "b1", "b2", "b3", "b4",
    "ns", "RMSE", "NMBE", "CVRMSE", "R2_adj",
    "pval_b_L", "pval_b_R", "pval_c_C",
    "Ckd_out_idx", "ZRE_out_idx",
    "P_M1", "P_M2", "R2", "Es",
]


@dataclass
class CPMResult:
    """한 모델의 적합 + 통계 + (선택적) 분해 결과."""

    fit: FitResult
    stats: CPMStats
    rank: int = 0
    disaggregation: Disaggregation | None = None

    @property
    def cpm_type(self) -> str:
        return self.fit.cpm_type

    def to_row(self, building_id: str, year_start: int, year_end: int, energy_source: str) -> dict:
        b0, b1, b2, b3, b4 = self.stats.b
        s = self.stats
        return {
            "ID": building_id,
            "DATE_S": year_start,
            "DATE_E": year_end,
            "CPM_TY": self.cpm_type,
            "MD_RANK": self.rank,
            "b0": b0, "b1": b1, "b2": b2, "b3": b3, "b4": b4,
            "ns": s.ns,
            "RMSE": s.rmse,
            "NMBE": s.nmbe,
            "CVRMSE": s.cvrmse,
            "R2_adj": s.r2_adj,
            "pval_b_L": s.pval_b_left,
            "pval_b_R": s.pval_b_right,
            "pval_c_C": s.pval_c_center,
            "Ckd_out_idx": format_index_list(s.cook_outlier_idx),
            "ZRE_out_idx": format_index_list(s.zre_outlier_idx),
            "P_M1": s.p_m1,
            "P_M2": s.p_m2,
            "R2": s.r2,
            "Es": energy_source,
        }


def run_cpm(
    t_out: np.ndarray,
    y_mea: np.ndarray,
    config: AnalysisConfig,
    *,
    with_disaggregation: bool = True,
) -> list[CPMResult]:
    """설정된 모델들을 적합하고 RMSE 오름차순으로 순위를 매긴다.

    결과 목록의 순서는 ``config.model_types`` 순서를 그대로 유지하며,
    순위는 ``CPMResult.rank`` (1 = RMSE 최소) 에 담긴다.
    """
    fits = fit_all(
        t_out, y_mea,
        model_types=config.model_types,
        cp_range=config.cp_range,
        strategy=config.strategy,
        n_starts=config.n_starts,
        seed=config.seed,
    )

    results = []
    for fit in fits:
        stats = compute_stats(fit.cpm_type, fit.x, t_out, y_mea)
        disagg = disaggregate(fit.cpm_type, stats.coefficients, t_out) if with_disaggregation else None
        results.append(CPMResult(fit=fit, stats=stats, disaggregation=disagg))

    # RMSE 오름차순 순위 (1 = 최적). NaN은 뒤로 보낸다.
    rmses = np.array([r.stats.rmse for r in results], dtype=float)
    order = np.argsort(np.where(np.isnan(rmses), np.inf, rmses), kind="stable")
    for rank, idx in enumerate(order, start=1):
        results[idx].rank = rank

    return results


def results_to_frame(
    results: list[CPMResult],
    building_id: str,
    year_start: int,
    year_end: int,
    energy_source: str,
) -> pd.DataFrame:
    """결과 목록을 기존 출력 파일과 같은 열 구성의 DataFrame으로 만든다."""
    rows = [r.to_row(building_id, year_start, year_end, energy_source) for r in results]
    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


@dataclass
class AnalysisOutput:
    """:func:`run_analysis`의 결과 묶음."""

    results: list[CPMResult]
    frame: pd.DataFrame
    t_out: np.ndarray
    y_mea: np.ndarray
    energy: EnergyData
    dataset: pd.DataFrame
    group_labels: np.ndarray
    result_path: Path | None = None
    plot_path: Path | None = None

    @property
    def best(self) -> CPMResult:
        """RMSE가 가장 낮은 모델."""
        return min(self.results, key=lambda r: r.rank)


def _group_labels(energy: EnergyData, dataset: pd.DataFrame, weather_dir: Path) -> np.ndarray:
    """산점도 색 구분용 라벨.

    월별 자료는 연도로, 일별 자료는 요일명으로 나눈다 (원본 ``fn_CPM_date_index.m``).
    요일 표가 없으면 연도로 되돌아간다.
    """
    if energy.frequency is Frequency.MONTHLY:
        return dataset["year"].to_numpy()

    day_names = read_daynames(weather_dir, energy.years)
    if day_names is not None and len(day_names) >= len(dataset):
        return day_names.iloc[: len(dataset)].to_numpy()
    # 휴일 표가 없는 연도 — 요일을 날짜에서 직접 만든다.
    korean = ["월", "화", "수", "목", "금", "토", "일"]
    return np.array([korean[d] for d in dataset["date"].dt.weekday])


def run_analysis(config: AnalysisConfig) -> AnalysisOutput:
    """설정 하나로 자료 읽기부터 결과 저장까지 수행한다."""
    from . import plotting  # 지연 임포트 — matplotlib은 플롯을 그릴 때만 필요하다

    energy = read_energy(config.energy_path)
    weather = read_weather(config.weather_dir, energy.years, energy.frequency, config.station)
    t_out, y_mea, dataset = build_dataset(energy, weather, fill_missing=config.fill_missing)
    labels = _group_labels(energy, dataset, config.weather_dir)

    results = run_cpm(t_out, y_mea, config)
    frame = results_to_frame(
        results, config.building_id, energy.year_start, energy.year_end, config.energy_source
    )

    config.ensure_dirs()
    stem = f"CPM_Result_pk{config.building_id}{energy.year_start}{energy.year_end}"
    result_path = config.csv_dir / f"{stem}.txt"
    frame.to_csv(result_path, sep="\t", index=False, encoding="utf-8")

    plot_path = None
    if config.make_plots:
        plot_path = config.plot_dir / (
            f"CPM_bestfit0_Tot_{energy.frequency.value}_pk{config.building_id}"
            f"{energy.year_start}{energy.year_end}.png"
        )
        plotting.plot_model_grid(results, t_out, y_mea, labels, config.building_id, plot_path)

    return AnalysisOutput(
        results=results,
        frame=frame,
        t_out=t_out,
        y_mea=y_mea,
        energy=energy,
        dataset=dataset,
        group_labels=labels,
        result_path=result_path,
        plot_path=plot_path,
    )
