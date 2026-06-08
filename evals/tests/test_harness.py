from pathlib import Path

from counterproof_evals import SET_NAMES, discover_sets, run_harness


def test_discovers_all_expected_sets() -> None:
    summaries = discover_sets()
    discovered = {summary.name for summary in summaries}
    assert discovered == set(SET_NAMES)


def test_empty_harness_runs_green() -> None:
    report = run_harness()
    assert report.total_cases == 0
    assert report.passed
    assert report.violations == []


def test_counts_cases_from_manifest(tmp_path: Path) -> None:
    golden = tmp_path / "golden"
    golden.mkdir()
    (golden / "manifest.json").write_text('{"cases": [{"id": "a"}, {"id": "b"}]}', encoding="utf-8")
    report = run_harness(sets_root=tmp_path)
    by_name = {summary.name: summary for summary in report.sets}
    assert by_name["golden"].case_count == 2
    assert report.total_cases == 2
