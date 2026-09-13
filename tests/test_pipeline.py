"""분석 파이프라인·CLI 검증."""

import numpy as np
import pandas as pd
import pytest

from besig import AnalysisConfig, run_analysis, run_cpm
from besig.cli import main
from besig.pipeline import RESULT_COLUMNS

from conftest import DATA_DIR, WEATHER_DIR


@pytest.fixture(scope="module")
def analysis(tmp_path_factory):
    config = AnalysisConfig(
        energy_path=DATA_DIR / "Y_daily.csv",
        weather_dir=WEATHER_DIR,
        output_dir=tmp_path_factory.mktemp("out"),
        building_id="test",
        station=108,
    )
    return run_analysis(config)


def test_writes_result_table_and_plot(analysis):
    assert analysis.result_path.exists()
    assert analysis.plot_path.exists()
    assert analysis.plot_path.stat().st_size > 0


def test_written_table_round_trips(analysis):
    frame = pd.read_csv(analysis.result_path, sep="\t")
    assert list(frame.columns) == RESULT_COLUMNS
    assert len(frame) == len(analysis.results)


def test_ranks_are_a_permutation_of_one_to_n(analysis):
    ranks = sorted(r.rank for r in analysis.results)
    assert ranks == list(range(1, len(analysis.results) + 1))


def test_best_model_has_lowest_rmse(analysis):
    best = analysis.best
    assert best.rank == 1
    assert best.stats.rmse == min(r.stats.rmse for r in analysis.results)


def test_every_result_carries_a_disaggregation(analysis):
    assert all(r.disaggregation is not None for r in analysis.results)


def test_daily_analysis_groups_by_weekday(analysis):
    assert set(analysis.group_labels) <= {"월", "화", "수", "목", "금", "토", "일"}


def test_monthly_analysis_groups_by_year(tmp_path):
    config = AnalysisConfig(
        energy_path=DATA_DIR / "Y_monthly.csv",
        weather_dir=WEATHER_DIR,
        output_dir=tmp_path,
        make_plots=False,
    )
    out = run_analysis(config)
    assert set(out.group_labels) == {2018, 2019, 2020}


def test_plots_can_be_skipped(tmp_path):
    config = AnalysisConfig(
        energy_path=DATA_DIR / "Y_daily.csv",
        weather_dir=WEATHER_DIR,
        output_dir=tmp_path,
        make_plots=False,
    )
    out = run_analysis(config)
    assert out.plot_path is None
    assert not (tmp_path / "pics_CPM").exists()


def test_model_selection_is_honoured(daily_dataset, tmp_path):
    t, y = daily_dataset
    config = AnalysisConfig(
        energy_path=DATA_DIR / "Y_daily.csv",
        weather_dir=WEATHER_DIR,
        output_dir=tmp_path,
        model_types=("1p", "3p_h"),
    )
    results = run_cpm(t, y, config)
    assert [r.cpm_type for r in results] == ["1p", "3p_h"]


def test_cli_run_writes_output(tmp_path, capsys):
    code = main([
        "run",
        "--energy", str(DATA_DIR / "Y_daily.csv"),
        "--weather", str(WEATHER_DIR),
        "--output", str(tmp_path),
        "--id", "clitest",
        "--no-plot",
    ])
    assert code == 0
    assert (tmp_path / "csv_CPM" / "CPM_Result_pkclitest20182018.txt").exists()
    assert "최적 모델" in capsys.readouterr().out


def test_cli_reports_a_missing_file_without_traceback(tmp_path, capsys):
    code = main([
        "run", "--energy", str(tmp_path / "없음.csv"),
        "--weather", str(WEATHER_DIR), "--output", str(tmp_path),
    ])
    assert code == 1
    assert "오류:" in capsys.readouterr().err


def test_cli_models_lists_every_model(capsys):
    assert main(["models"]) == 0
    out = capsys.readouterr().out
    assert "5p" in out and "4p_c" in out
