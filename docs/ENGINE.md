# Engine Specification

The engine is the product. This is the part to build carefully. It is a transparent, reproducible pipeline that produces an auditable challenge report from a document set.

## Inputs

- `documents`: a set of source documents (synthetic). v1 supports paystubs and bank statements.
- `primary_output` (optional): the figures or decision the primary system produced, which we will challenge. When absent, the engine runs as a standalone independent extraction-and-validation pass.
- `policy` (optional): thresholds and which checks are required.

## Pipeline stages

### 1. Ingest and normalize
Convert each document to text and, where possible, lightweight structure (tables, line items), with positional metadata so later stages can cite a location. Tag every document as untrusted. Do not let document text enter a system or instruction role.

### 2. Independent extraction
Re-derive a focused set of underwriting-relevant fields, each as a typed value with a per-field confidence and one or more source spans. Minimum field set for v1:
- gross income per period, net income per period, pay frequency, pay period dates, employer name, employee name (paystub)
- account holder, statement period, total deposits, recurring deposits, average daily balance (bank statement)
- derived: annualized income, year-to-date consistency

Use tool use with a strict schema. The model returns structured fields, never prose conclusions.

### 3. Grounding and citation
Every extracted value must carry at least one citation: document id plus location (page, line, or span). A value that cannot be grounded is marked ungrounded and treated as low confidence. No grounding, no trust.

### 4. Cross-validation
Check internal and cross-document consistency. v1 checks:
- paystub net income vs corresponding bank deposits (within tolerance)
- year-to-date figure vs per-period figure times periods elapsed
- stated vs computed debt-to-income, if liabilities are present
- identity and date consistency across documents (same name, overlapping periods)
Each check yields pass, variance-within-tolerance, or fail, with the evidence.

### 5. Disagreement detection
When `primary_output` is present, compare it field by field to the independent extraction and classify each:
- match
- minor variance (within tolerance)
- material discrepancy (outside tolerance)
- missing (primary has it, we do not, or the reverse)
- contradiction (cross-validation says the primary's value cannot be right)

### 6. Confidence scoring and escalation
Combine per-field confidence, grounding quality, and check results into an overall confidence and a per-finding severity. Apply an explicit, documented escalation policy:
- high confidence and no material findings: auto-pass (still logged)
- any material discrepancy, contradiction, or low grounding: flag for human review
- detected tampering or injection: block and escalate
Thresholds live in `policy` and are versioned. The policy is data, not hardcoded.

### 7. Guardrails
The guard layer assumes the document submitter is an adversary. See SECURITY.md for the full threat model. The essentials:
- Hostile text: treat all document content as data, never instructions, and never place it in a system or instruction role. Defend against embedded injection (fake system text, "ignore previous instructions"). The injection eval set tests this directly.
- Hostile file: parse documents in a constrained way. Enforce size, page, and time limits, disable external entity resolution (XXE), never fetch URLs or resources referenced by document content (SSRF), and reject archives and decompression bombs. The malicious-file eval set tests this.
- Data governance: real documents would be sent to a third-party model provider. Make the provider and its retention and training settings configurable, default to no training on input, and never send sensitive data to an external service silently.
- PII: never log raw PII, and redact it in all traces. v1 is synthetic-only, so this is a discipline to establish now, not later.
- Output validation: validate every model output against its strict schema before use, so a manipulated document cannot smuggle unexpected structure into the report.

### 8. Challenge report assembly
Produce the structured report (schema below) plus a human-readable rendering. The report is the SR 11-7 effective-challenge artifact: it records what was checked, what was found, the evidence, the confidence, and the recommended action.

## Output schema (sketch)

```python
class Citation(BaseModel):
    document_id: str
    location: str            # page/line/span
    snippet: str             # short, for display

class Finding(BaseModel):
    field: str
    independent_value: Any
    primary_value: Any | None
    citations: list[Citation]
    confidence: float        # 0..1
    classification: Literal["match","minor_variance","material_discrepancy",
                            "missing","contradiction","unverified"]
    severity: Literal["info","review","block"]
    rationale: str           # short, evidence-based, no hallucinated detail

class ChallengeReport(BaseModel):
    document_ids: list[str]
    findings: list[Finding]
    checks: list[CheckResult]
    overall_confidence: float
    recommended_action: Literal["pass","review","block"]
    audit_trail: list[AuditEvent]   # ordered record of every step + inputs/outputs hashes
    engine_version: str
    model_version: str
    policy_version: str
```

## Determinism and reproducibility

- Pin the model version. Use low temperature for extraction and validation.
- Version prompts and store the version in the report.
- Hash inputs and record them in the audit trail so a run can be reproduced and defended.

## The verify loop

Within extraction and validation, prefer plan then act then self-check over a single pass: extract, then have the engine re-examine its own findings against the citations and the cross-checks before finalizing. This self-check step is a meaningful quality lever.

## Failure modes to handle explicitly

- Unreadable or partial documents (return ungrounded, not a guess).
- Conflicting documents (surface the conflict, do not silently pick one).
- Missing fields (report as missing, never fabricate).
- Injection attempts (caught by the guard layer and recorded).
