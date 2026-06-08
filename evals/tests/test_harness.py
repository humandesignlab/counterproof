from pathlib import Path

from counterproof_evals import PENDING_SET_NAMES, Thresholds, run_harness


def test_harness_meets_thresholds_with_deterministic_extractor() -> None:
    report = run_harness(seed=1, count=12)
    metrics = report.metrics

    assert metrics.golden_cases == 12
    assert metrics.adversarial_cases == 12

    # The deterministic extractor + YTD check should catch every planted tamper,
    # raise no false positives on clean docs, and ground every value exactly.
    assert metrics.discrepancy_recall == 1.0
    assert metrics.false_positive_rate == 0.0
    assert metrics.grounding_accuracy == 1.0

    assert report.passed
    assert report.violations == []


def test_pending_sets_are_reported_not_scored() -> None:
    report = run_harness(seed=2, count=4)
    assert set(report.pending_sets) == set(PENDING_SET_NAMES)


def test_thresholds_flag_a_regression() -> None:
    # An impossible recall threshold must surface as a violation, proving the gate
    # actually fails when a metric drops below threshold.
    impossible = Thresholds(discrepancy_recall_min=1.01)
    report = run_harness(seed=3, count=6, thresholds=impossible)
    assert not report.passed
    assert any("discrepancy_recall" in violation for violation in report.violations)


def test_work_dir_generates_both_sets(tmp_path: Path) -> None:
    run_harness(seed=4, count=3, work_dir=tmp_path)
    assert (tmp_path / "golden" / "manifest.json").is_file()
    assert (tmp_path / "adversarial" / "manifest.json").is_file()
