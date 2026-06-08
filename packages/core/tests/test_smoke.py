import counterproof_core


def test_version_is_exposed() -> None:
    assert counterproof_core.__version__ == "0.1.0"


def test_pipeline_stage_modules_import() -> None:
    from counterproof_core import (  # noqa: F401
        extract,
        guard,
        ingest,
        report,
        score,
        validate,
    )
