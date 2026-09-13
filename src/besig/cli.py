"""``besig`` 명령줄 도구."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .bounds import ChangePointRange
from .config import DEFAULT_STATION, AnalysisConfig
from .models import ALL_MODEL_TYPES, DEFAULT_MODEL_TYPES, MODELS

__all__ = ["main", "build_parser"]

_SUMMARY_COLUMNS = ["CPM_TY", "MD_RANK", "b0", "b1", "b2", "b3", "b4", "RMSE", "CVRMSE", "R2"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="besig",
        description="BE-sig — 건물 에너지 시그니처(변곡점 회귀) 분석",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "예시:\n"
            "  besig run --energy data/Y_daily.csv --weather data/weather --id test\n"
            "  besig run --energy data/Y_monthly.csv --weather data/weather "
            "--station 108 --strategy multistart\n"
            "  besig models\n"
        ),
    )
    parser.add_argument("--version", action="version", version=f"besig {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="CPM 분석 실행")
    run.add_argument("--energy", "-e", required=True, type=Path,
                     help="에너지 사용량 CSV (USE_DATE, ES, EUSE)")
    run.add_argument("--weather", "-w", required=True, type=Path,
                     help="기상·휴일 CSV가 들어 있는 폴더")
    run.add_argument("--output", "-o", type=Path, default=Path("outputs"),
                     help="결과 저장 폴더 (기본: outputs)")
    run.add_argument("--id", dest="building_id", default="test", help="건물명/분석명")
    run.add_argument("--station", type=int, default=DEFAULT_STATION,
                     help=f"기상 관측소 번호 (기본: {DEFAULT_STATION})")
    run.add_argument("--source", dest="energy_source", default="총계", help="에너지원 이름")
    run.add_argument("--models", nargs="+", choices=ALL_MODEL_TYPES, default=list(DEFAULT_MODEL_TYPES),
                     metavar="TYPE", help=f"적합할 모델 (기본: {' '.join(DEFAULT_MODEL_TYPES)})")
    run.add_argument("--cp-low", type=float, default=0.0, help="변곡점 탐색 하한 [°C]")
    run.add_argument("--cp-high", type=float, default=25.0, help="변곡점 탐색 상한 [°C]")
    run.add_argument("--strategy", choices=("slsqp", "multistart", "global"), default="multistart",
                     help="최적화 방식 (기본 multistart. slsqp = 원본과 동일한 단일 시작점)")
    run.add_argument("--n-starts", type=int, default=8, help="multistart 시작점 개수")
    run.add_argument("--seed", type=int, default=0, help="난수 시드")
    run.add_argument("--no-plot", action="store_true", help="그림을 그리지 않는다")
    run.add_argument("--no-fill", action="store_true", help="결측값 보간을 하지 않는다")

    sub.add_parser("models", help="사용 가능한 CPM 모델 목록")
    return parser


def _cmd_run(args: argparse.Namespace) -> int:
    from .pipeline import run_analysis  # 지연 임포트 — `besig models`는 빠르게 뜨도록

    config = AnalysisConfig(
        energy_path=args.energy,
        weather_dir=args.weather,
        output_dir=args.output,
        building_id=args.building_id,
        station=args.station,
        energy_source=args.energy_source,
        model_types=tuple(args.models),
        cp_range=ChangePointRange(args.cp_low, args.cp_high),
        strategy=args.strategy,
        n_starts=args.n_starts,
        seed=args.seed,
        fill_missing=not args.no_fill,
        make_plots=not args.no_plot,
    )

    out = run_analysis(config)

    summary = out.frame[_SUMMARY_COLUMNS].sort_values("MD_RANK")
    print(f"\n자료: {config.energy_path}  ({out.energy.frequency.value}, "
          f"{out.energy.year_start}~{out.energy.year_end}, n={len(out.t_out)})")
    print(f"관측소: {config.station}    최적화: {config.strategy}\n")
    print(summary.to_string(index=False, float_format=lambda v: f"{v:.4g}"))

    best = out.best
    print(f"\n최적 모델: {best.cpm_type}  "
          f"CVRMSE={best.stats.cvrmse:.2f}%  NMBE={best.stats.nmbe:.4f}%  R²={best.stats.r2:.4f}")
    if best.disaggregation is not None:
        d = best.disaggregation
        print(f"에너지 분해 — 기저 {d.base_total:,.1f} / 난방 {d.heating_total:,.1f} "
              f"/ 냉방 {d.cooling_total:,.1f}")

    print(f"\n결과 표: {out.result_path}")
    if out.plot_path is not None:
        print(f"산점도 : {out.plot_path}")
    return 0


def _cmd_models(_: argparse.Namespace) -> int:
    print(f"{'모델':<8} {'파라메터':<10} 설명")
    print("-" * 44)
    for name, spec in MODELS.items():
        default = " (기본 포함)" if name in DEFAULT_MODEL_TYPES else ""
        print(f"{name:<8} {spec.n_params:<10} {spec.description}{default}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler = {"run": _cmd_run, "models": _cmd_models}[args.command]
    try:
        return handler(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
