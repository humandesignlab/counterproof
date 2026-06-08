"""Challenge report assembly.

Turns extraction output into a structured ChallengeReport with a deterministic
audit trail. Hashes are computed over canonical JSON and there are no timestamps,
so a run is reproducible and the report is byte-stable for testing. Versions are
recorded so a reported result can be reproduced and defended.
"""

from __future__ import annotations

import hashlib
from typing import Any

from .. import __version__
from ..extract.schema import ExtractedField, PaystubExtraction
from ..ingest.document import Document
from ..score.policy import (
    Policy,
    classify_field,
    field_severity,
    overall_confidence,
    recommended_action,
)
from ..validate.checks import run_checks
from .schema import AuditEvent, ChallengeReport, CheckResult, Finding


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _hash_documents(documents: list[Document]) -> str:
    return _sha256("\n".join(document.model_dump_json() for document in documents))


def _hash_extractions(extractions: list[PaystubExtraction]) -> str:
    return _sha256("\n".join(extraction.model_dump_json() for extraction in extractions))


def _hash_findings(findings: list[Finding]) -> str:
    return _sha256("\n".join(finding.model_dump_json() for finding in findings))


def _hash_checks(checks: list[CheckResult]) -> str:
    return _sha256("\n".join(check.model_dump_json() for check in checks))


def _extracted_fields(extraction: PaystubExtraction) -> list[tuple[str, ExtractedField[Any]]]:
    return [
        ("employee_name", extraction.employee_name),
        ("employer_name", extraction.employer_name),
        ("pay_frequency", extraction.pay_frequency),
        ("pay_period_start", extraction.pay_period_start),
        ("pay_period_end", extraction.pay_period_end),
        ("pay_date", extraction.pay_date),
        ("gross_pay", extraction.gross_pay),
        ("net_pay", extraction.net_pay),
    ]


def _rationale(field: ExtractedField[Any]) -> str:
    if field.value is None:
        return "Value could not be grounded in the document."
    return f"Independently extracted, grounded by {len(field.citations)} citation(s)."


def _findings_for(document_id: str, extraction: PaystubExtraction, policy: Policy) -> list[Finding]:
    findings: list[Finding] = []
    for name, field in _extracted_fields(extraction):
        findings.append(
            Finding(
                field=f"{document_id}.{name}",
                independent_value=field.value,
                primary_value=None,
                citations=field.citations,
                confidence=field.confidence,
                classification=classify_field(field),
                severity=field_severity(field, policy),
                rationale=_rationale(field),
            )
        )
    return findings


def _finding_from_failed_check(document_id: str, result: CheckResult) -> Finding:
    return Finding(
        field=f"{document_id}.{result.name}",
        independent_value=None,
        primary_value=None,
        citations=result.citations,
        confidence=1.0,
        classification="material_discrepancy",
        severity="review",
        rationale=result.detail,
    )


def build_report(
    pairs: list[tuple[Document, PaystubExtraction]],
    *,
    model_version: str,
    prompt_version: str,
    policy: Policy | None = None,
) -> ChallengeReport:
    """Assemble a ChallengeReport from one or more (document, extraction) pairs."""
    active_policy = policy or Policy()
    documents = [document for document, _ in pairs]
    extractions = [extraction for _, extraction in pairs]

    field_findings: list[Finding] = []
    check_findings: list[Finding] = []
    checks: list[CheckResult] = []
    for document, extraction in pairs:
        field_findings.extend(_findings_for(document.document_id, extraction, active_policy))
        for result in run_checks(extraction):
            checks.append(result)
            if result.status == "fail":
                check_findings.append(_finding_from_failed_check(document.document_id, result))

    findings = field_findings + check_findings

    raw_input_hash = _sha256("\n".join(document.text for document in documents))
    documents_hash = _hash_documents(documents)
    extractions_hash = _hash_extractions(extractions)
    checks_hash = _hash_checks(checks)
    findings_hash = _hash_findings(findings)

    audit_trail = [
        AuditEvent(
            step="ingest",
            input_sha256=raw_input_hash,
            output_sha256=documents_hash,
            detail=f"Ingested {len(documents)} document(s) as untrusted input.",
        ),
        AuditEvent(
            step="extract",
            input_sha256=documents_hash,
            output_sha256=extractions_hash,
            detail=f"Independently extracted fields via {model_version}.",
        ),
        AuditEvent(
            step="validate",
            input_sha256=extractions_hash,
            output_sha256=checks_hash,
            detail=f"Ran {len(checks)} cross-validation check(s).",
        ),
        AuditEvent(
            step="assemble",
            input_sha256=checks_hash,
            output_sha256=findings_hash,
            detail=f"Assembled {len(findings)} finding(s) under policy {active_policy.version}.",
        ),
    ]

    return ChallengeReport(
        document_ids=[document.document_id for document in documents],
        findings=findings,
        checks=checks,
        overall_confidence=overall_confidence(findings),
        recommended_action=recommended_action(findings),
        audit_trail=audit_trail,
        engine_version=__version__,
        model_version=model_version,
        prompt_version=prompt_version,
        policy_version=active_policy.version,
    )
