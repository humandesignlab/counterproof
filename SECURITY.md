# Security

Counterproof verifies the integrity of an underwriting decision, so its own integrity and the trust boundaries around it matter more than for a typical tool. This document is the reference. The non-negotiable rules are enforced on every change.

## Threat model

### Who we defend against
- **The document submitter.** The primary adversary. A borrower or broker has a direct incentive to get a doctored, inflated, or poisoned document past the verifier. Catching this is the product.
- **A compromised or buggy primary system.** The output we challenge can be wrong, malformed, or manipulated. We never treat it as ground truth.
- **Embedded attackers in document content.** Prompt injection, fake "system" text, and instructions hidden in documents that try to steer the model.
- **Insiders and the supply chain.** People with access, and dependencies that parse untrusted input.

### What we protect
- The integrity of the verification verdict and its citations.
- The integrity and access control of the audit trail (the effective-challenge record).
- PII contained in documents.
- Secrets and credentials.

### Trust boundaries
- Documents: untrusted, always.
- Primary-system output: untrusted.
- The model provider: a third party that receives document content in any real deployment.

## Controls

**Document handling (file).** Constrained parsing: size, page, and time limits; external entity resolution disabled (XXE); no fetching of URLs or resources from document content (SSRF); archives and decompression bombs rejected; unexpected file types rejected.

**Document handling (content).** Document text is data, never instructions, and never enters a system or instruction role. Model outputs are constrained to strict schemas and validated before use. The injection eval set tests this and a regression fails the build.

**Data governance.** v1 uses synthetic data only and persists nothing. For real deployments the model provider and its retention and training settings are configurable, default to no training on input, and the chosen posture is documented. Sensitive data is never sent to an external service silently.

**Secrets.** Loaded from the environment, never hardcoded, never logged, never committed.

**Dependencies.** Versions pinned. Libraries that parse untrusted input are kept minimal, maintained, and reviewed.

**Audit-trail integrity.** Inputs and outputs are hashed and recorded. In a real deployment the audit log is tamper-evident and access-controlled.

**Logging and PII.** No raw PII in logs or traces. Redaction by default.

## Scope for v1

v1 is a synthetic-data, stateless reference. Several controls (encryption at rest, access control, audit-log hardening) are documented here but deferred until there is real data and persistence. Deferral is stated explicitly, never skipped silently.

## Not a certification

Counterproof produces evidence and documentation to support effective challenge. It is not a security or regulatory certification and does not provide one.

## Reporting a vulnerability

<!-- Add a contact (a security@ address or a private GitHub security advisory) before the repo goes public. -->
