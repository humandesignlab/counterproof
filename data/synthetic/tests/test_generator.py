from pathlib import Path

from counterproof_synthetic import (
    PERIODS_PER_YEAR,
    Manifest,
    PaystubFields,
    generate_set,
)


def _read_manifest(out_dir: Path) -> Manifest:
    return Manifest.model_validate_json((out_dir / "manifest.json").read_text(encoding="utf-8"))


def _assert_reconciles(fields: PaystubFields) -> None:
    assert round(fields.net_pay + fields.deductions, 2) == fields.gross_pay
    assert fields.annualized_gross == round(
        fields.gross_pay * PERIODS_PER_YEAR[fields.pay_frequency], 2
    )
    periods = round(fields.ytd_gross / fields.gross_pay)
    assert periods >= 1
    assert fields.ytd_gross == round(fields.gross_pay * periods, 2)
    assert fields.ytd_net == round(fields.net_pay * periods, 2)


def test_clean_set_manifest_round_trips_and_reconciles(tmp_path: Path) -> None:
    generate_set(tmp_path, count=5, variant="clean", seed=7)
    manifest = _read_manifest(tmp_path)

    assert manifest.generator_version
    assert manifest.seed == 7
    assert len(manifest.cases) == 5

    for case in manifest.cases:
        assert (tmp_path / case.path).is_file()
        assert case.variant == "clean"
        assert case.injected_issue is None
        assert case.expected_classification == "match"
        assert case.expected_recommended_action == "pass"
        _assert_reconciles(case.fields)


def test_tampered_set_plants_altered_income(tmp_path: Path) -> None:
    generate_set(tmp_path, count=4, variant="tampered", seed=3)
    manifest = _read_manifest(tmp_path)

    assert len(manifest.cases) == 4
    for case in manifest.cases:
        assert case.variant == "tampered"
        assert case.expected_classification == "material_discrepancy"
        assert case.expected_recommended_action == "review"

        issue = case.injected_issue
        assert issue is not None
        assert issue.type == "altered_income"
        assert issue.field == "gross_pay"
        # Manifest stores the true value; the document shows the inflated one.
        assert issue.true_value == case.fields.gross_pay
        assert issue.shown_value > issue.true_value

        text = (tmp_path / case.path).read_text(encoding="utf-8")
        earnings_line = next(
            line for line in text.splitlines() if "Gross Pay (this period)" in line
        )
        assert f"{issue.shown_value:.2f}" in earnings_line
        assert f"{issue.true_value:.2f}" not in earnings_line


def test_mixed_set_alternates_variants(tmp_path: Path) -> None:
    generate_set(tmp_path, count=6, variant="mixed", seed=1)
    manifest = _read_manifest(tmp_path)
    variants = [case.variant for case in manifest.cases]
    assert variants == ["clean", "tampered", "clean", "tampered", "clean", "tampered"]


def test_same_seed_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "a"
    second = tmp_path / "b"
    m1 = generate_set(first, count=5, variant="mixed", seed=42)
    m2 = generate_set(second, count=5, variant="mixed", seed=42)
    assert m1.model_dump() == m2.model_dump()
    assert (first / "manifest.json").read_text() == (second / "manifest.json").read_text()
