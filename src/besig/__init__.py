"""BE-sig — Building Energy signature Toolkit.

건물 에너지 사용량과 외기온의 관계를 변곡점 회귀(Change-Point Model)로
적합하는 도구. MATLAB 구현을 Python으로 옮긴 것이다.

기본 사용법::

    from besig import AnalysisConfig, run_analysis

    out = run_analysis(AnalysisConfig(
        energy_path="data/Y_daily.csv",
        weather_dir="data/weather",
        building_id="test",
        station=108,
    ))
    print(out.frame)
    print(out.best.cpm_type, out.best.stats.cvrmse)

낮은 수준 API::

    from besig import fit_model, compute_stats

    fit = fit_model("3p_h", t_out, y_mea)
    stats = compute_stats(fit.cpm_type, fit.x, t_out, y_mea)
"""

from .bounds import ChangePointRange, ParamBounds, build_bounds
from .config import AnalysisConfig
from .disaggregation import Disaggregation, disaggregate
from .fitting import FitResult, fit_all, fit_model, objective_rmse
from .loaders import (
    EnergyData,
    Frequency,
    build_dataset,
    read_daynames,
    read_energy,
    read_weather,
)
from .models import ALL_MODEL_TYPES, DEFAULT_MODEL_TYPES, MODELS, ModelSpec, n_params, predict
from .pipeline import (
    RESULT_COLUMNS,
    AnalysisOutput,
    CPMResult,
    results_to_frame,
    run_analysis,
    run_cpm,
)
from .stats import CPMStats, compute_stats, cooks_distance, standardized_residuals

__version__ = "1.0.0"

__all__ = [
    "__version__",
    # 설정 / 파이프라인
    "AnalysisConfig", "AnalysisOutput", "CPMResult", "RESULT_COLUMNS",
    "run_analysis", "run_cpm", "results_to_frame",
    # 모델
    "MODELS", "ModelSpec", "ALL_MODEL_TYPES", "DEFAULT_MODEL_TYPES", "predict", "n_params",
    # 적합
    "FitResult", "fit_model", "fit_all", "objective_rmse",
    "ChangePointRange", "ParamBounds", "build_bounds",
    # 통계
    "CPMStats", "compute_stats", "cooks_distance", "standardized_residuals",
    # 분해
    "Disaggregation", "disaggregate",
    # 입출력
    "EnergyData", "Frequency", "read_energy", "read_weather", "read_daynames", "build_dataset",
]
