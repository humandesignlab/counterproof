# Compliance and regulatory considerations

Read this before pointing Counterproof at anything real.

## The short version (the nuance that matters)

Counterproof v1 processes synthetic data only and stores nothing. In that form it processes no personal data, so privacy and financial-data regulations like GDPR, CCPA, and GLBA are not triggered by the reference implementation itself. That is a deliberate design choice, not an accident.

The moment you deploy Counterproof against real borrower documents, this changes completely. You are then handling highly sensitive personal and financial data inside a credit-underwriting workflow, and a stack of obligations attaches to you, the deployer. This document lists them and shows where Counterproof helps and where it does not.

This is not legal advice. I am not a lawyer, and nothing here substitutes for counsel. Treat all of it as considerations to take to your legal and compliance teams.

## If you deploy on real data, you inherit these

- **GLBA Safeguards Rule (US).** Nonpublic personal financial information requires a written security program, access controls, and encryption. This is financial data by definition.
- **FCRA and ECOA / Regulation B (US).** Underwriting touches consumer credit, so you owe adverse-action reasoning when credit is denied and you must not produce disparate impact across protected classes. Explainability is a legal requirement here, not a nicety.
- **EU AI Act.** AI used to evaluate creditworthiness is classified high-risk, which brings obligations around risk management, data governance, record-keeping, transparency, human oversight, and robustness.
- **GDPR (EU and UK).** You need a lawful basis, you must honor data-subject rights, and Article 22 restricts decisions made solely by automated processing with significant effects, which a lending decision is.
- **CCPA and CPRA (California).** Consumer privacy rights, sensitive-personal-information handling, and evolving rules on automated decision-making and profiling.
- **Processor and cross-border transfer.** Counterproof sends document content to a third-party model provider. That is a data-processing relationship needing a data-processing agreement, and moving EU data outside the EU needs a valid transfer mechanism.

## How Counterproof helps

Several of these obligations are easier to meet with Counterproof in place, because an independent, logged, citation-backed challenge is itself a control:

- **Human oversight (EU AI Act, GDPR Article 22).** Counterproof supports, never replaces, the human underwriter. It produces a reviewable challenge for a person to act on, which is exactly the human-in-the-loop these rules expect.
- **Record-keeping (EU AI Act).** The audit trail records what was checked, what disagreed, and why, with versions and input hashes.
- **Explainability and adverse-action reasoning (ECOA).** Every finding is grounded in a citation, so the basis for a flag is traceable rather than a black-box score.
- **Data governance and robustness (EU AI Act).** Independent verification plus the eval harness are evidence of effective challenge and accuracy monitoring.

Counterproof produces evidence and documentation. It does not make you compliant, and it is not a certification.

## What Counterproof does not do (your responsibility)

- Establishing a lawful basis or obtaining consent.
- Honoring data-subject access, deletion, and correction requests.
- Setting and enforcing data-retention and deletion policies.
- Signing data-processing agreements with your model provider and arranging lawful cross-border transfers.
- Fair-lending and disparate-impact testing of your overall decisioning.
- Sending adverse-action notices.
- Production encryption, access control, and storage hardening (see SECURITY.md for the controls deferred in v1).

If a feature you are about to build would process real personal data, stop and treat it as a deployment concern with its own review, not a v1 reference feature.
