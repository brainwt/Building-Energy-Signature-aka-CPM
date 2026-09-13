"""CPM 산점도와 적합선 그리기.

MATLAB ``fn_CPM_plot_bestfit.m``을 옮겼다. 모델마다 통째로 복사되어 있던
그리기 코드를 변곡점 목록 하나로 일반화해, 모델이 늘어도 분기를 더할 필요가 없다.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Sequence, TYPE_CHECKING

import matplotlib

matplotlib.use("Agg")  # 화면 없는 환경에서도 저장되도록
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

from .models import predict

if TYPE_CHECKING:  # 순환 임포트 방지
    from .pipeline import CPMResult

__all__ = ["plot_model", "plot_model_grid", "use_korean_font"]

#: 좌측(난방)·기저·우측(냉방) 구간 색. 원본의 빨강/초록/파랑을 따른다.
_SEGMENT_COLORS = {"heating": "#d62728", "base": "#2ca02c", "cooling": "#1f77b4"}

_KOREAN_FONT_CANDIDATES = (
    "Malgun Gothic", "AppleGothic", "NanumGothic",
    "Noto Sans CJK KR", "Noto Sans KR", "UnDotum",
)


def use_korean_font() -> str | None:
    """설치된 한글 글꼴을 찾아 matplotlib 기본값으로 지정한다.

    Returns
    -------
    적용한 글꼴 이름. 한글 글꼴이 없으면 ``None`` (라벨이 네모로 보일 수 있다).
    """
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in _KOREAN_FONT_CANDIDATES:
        if name in installed:
            plt.rcParams["font.family"] = name
            plt.rcParams["axes.unicode_minus"] = False
            return name
    return None


def _change_points(cpm_type: str, x: Sequence[float]) -> list[float]:
    """모델의 변곡점 외기온 목록 (없으면 빈 목록)."""
    if cpm_type in ("3p_h", "3p_c"):
        return [float(x[2])]
    if cpm_type in ("4p_h", "4p_c"):
        return [float(x[3])]
    if cpm_type == "5p":
        return [float(x[3]), float(x[4])]
    return []


def _segment_color(cpm_type: str, index: int, n_segments: int) -> str:
    """구간 번호에 맞는 색. 좌측은 난방, 우측은 냉방, 사이는 기저."""
    if n_segments == 1:
        if cpm_type.endswith("_h"):
            return _SEGMENT_COLORS["heating"]
        if cpm_type.endswith("_c"):
            return _SEGMENT_COLORS["cooling"]
        return _SEGMENT_COLORS["base"]
    if index == 0:
        return _SEGMENT_COLORS["heating"] if cpm_type != "3p_c" else _SEGMENT_COLORS["base"]
    if index == n_segments - 1:
        return _SEGMENT_COLORS["cooling"] if cpm_type != "3p_h" else _SEGMENT_COLORS["base"]
    return _SEGMENT_COLORS["base"]


def plot_model(
    result: "CPMResult",
    t_out: np.ndarray,
    y_mea: np.ndarray,
    group_labels: np.ndarray | None = None,
    ax: plt.Axes | None = None,
    building_id: str = "",
) -> plt.Axes:
    """실측 산점도 위에 적합된 CPM 곡선을 그린다.

    ``group_labels``가 주어지면 그 값(연도 또는 요일)별로 점 색을 나눈다.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(5, 4))

    t = np.asarray(t_out, dtype=float)
    y = np.asarray(y_mea, dtype=float)

    if group_labels is not None:
        labels = np.asarray(group_labels)
        unique = list(dict.fromkeys(labels.tolist()))
        for label in unique:
            mask = labels == label
            ax.scatter(t[mask], y[mask], s=12, alpha=0.65, label=str(label))
        # 요일 7개가 세로로 늘어지지 않도록 줄당 최대 4개씩 배치한다.
        ax.legend(fontsize=6, loc="best", framealpha=0.6, ncol=min(4, len(unique)))
    else:
        ax.scatter(t, y, s=12, alpha=0.65, color="0.4")

    # 변곡점을 경계로 구간을 나눠 색을 달리한 적합선. 변곡점 자체도 표본에
    # 넣어야 꺾이는 지점이 정확히 찍힌다.
    x = result.stats.coefficients
    cps = _change_points(result.cpm_type, x)
    t_line = np.sort(np.concatenate([t, np.asarray(cps, dtype=float)]))
    y_line = predict(result.cpm_type, x, t_line)

    edges = [t_line.min(), *sorted(cps), t_line.max()]
    n_seg = len(edges) - 1
    for i in range(n_seg):
        lo, hi = edges[i], edges[i + 1]
        mask = (t_line >= lo) & (t_line <= hi)
        if mask.sum() < 2:
            continue
        ax.plot(
            t_line[mask], y_line[mask],
            color=_segment_color(result.cpm_type, i, n_seg), lw=1.8, zorder=3,
        )

    b0 = float(x[0])
    ax.axhline(b0, color="k", ls=":", lw=0.8, zorder=2)
    ax.annotate("b0", (t_line.min(), b0), fontsize=7, va="bottom", ha="left")
    for i, cp in enumerate(cps, start=2):
        ax.axvline(cp, color="k", ls=":", lw=0.8, zorder=2)
        ax.annotate(f"b{i if len(cps) == 1 else i + 1}", (cp, b0), fontsize=7, va="bottom", ha="left")

    ax.set_xlabel("Temperature [°C]")
    ax.set_ylabel("Energy Use")
    prefix = f"PK:{building_id} /" if building_id else ""
    ax.set_title(
        f"{prefix}TYPE:{result.cpm_type}\nCVRMSE: {result.stats.cvrmse:.1f}", fontsize=9
    )
    ax.grid(True, alpha=0.3)
    return ax


def plot_model_grid(
    results: Sequence["CPMResult"],
    t_out: np.ndarray,
    y_mea: np.ndarray,
    group_labels: np.ndarray | None,
    building_id: str,
    save_path: str | Path | None = None,
    ncols: int = 3,
) -> plt.Figure:
    """여러 모델의 적합 결과를 한 장의 격자 그림으로 그린다."""
    font = use_korean_font()
    if font is None:
        # 한글 글꼴이 없으면 요일 범례가 네모로 찍힌다. 글자 하나마다 경고가
        # 쏟아지는 대신 한 번만 알린다.
        warnings.warn(
            "한글 글꼴을 찾지 못해 그림의 한글 라벨이 깨질 수 있다. "
            "나눔고딕 등을 설치하면 정상 출력된다.",
            UserWarning,
            stacklevel=2,
        )

    n = len(results)
    ncols = max(1, min(ncols, n))
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.6 * ncols, 3.8 * nrows), squeeze=False)

    for i, result in enumerate(results):
        plot_model(result, t_out, y_mea, group_labels, axes[i // ncols][i % ncols], building_id)
    for j in range(n, nrows * ncols):  # 남는 칸 숨기기
        axes[j // ncols][j % ncols].axis("off")

    with warnings.catch_warnings():
        # 글꼴 문제는 위에서 한 번 알렸으므로 글자별 "missing glyph" 경고는 덮는다.
        warnings.filterwarnings("ignore", message=".*missing from font.*")
        fig.tight_layout()
        if save_path is not None:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=130)
            plt.close(fig)
    return fig
