import type { ReactNode } from "react";

import { naiveVerdict } from "../lib/baseline";
import type { ChallengeReport, Citation, Finding } from "../lib/types";
import { CLASSIFICATION_LABEL, StatusChip, actionStatus } from "./status";

function fieldKey(field: string): string {
  const dot = field.lastIndexOf(".");
  return dot >= 0 ? field.slice(dot + 1) : field;
}

function valueText(value: unknown): string {
  if (value === null || value === undefined) return "not found";
  return String(value);
}

function isDiscrepancy(finding: Finding): boolean {
  return (
    finding.classification === "material_discrepancy" ||
    finding.classification === "contradiction"
  );
}

function CitedLine({ citation }: { citation: Citation }) {
  return (
    <div className="mt-2 border-l-2 border-line pl-3">
      <div className="font-mono text-xs text-ink-faint">{citation.location}</div>
      <div className="whitespace-pre-wrap break-words font-mono text-[13px] text-ink-muted">
        {citation.snippet}
      </div>
    </div>
  );
}

function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <h2 className="text-[11px] font-medium uppercase tracking-[0.14em] text-ink-faint">
      {children}
    </h2>
  );
}

export function Report({ report }: { report: ChallengeReport }) {
  const naive = naiveVerdict(report);
  const counterproof = report.recommended_action;
  const caught = naive === "pass" && counterproof !== "pass";

  const failedChecks = report.checks.filter((check) => check.status === "fail");
  const hasChecks = report.checks.length > 0;

  const fieldFindings = report.findings.filter((finding) => !isDiscrepancy(finding));
  const grounded = fieldFindings.filter(
    (finding) => finding.classification !== "missing" && finding.citations.length > 0,
  ).length;

  return (
    <section className="flex flex-col gap-10" aria-label="Challenge report">
      {/* Verdict hero: the comparison is the point, so it gets the one contained surface. */}
      <div className="grid grid-cols-1 border border-line bg-surface sm:grid-cols-2">
        <div className="border-b border-line p-6 sm:border-b-0 sm:border-r">
          <SectionLabel>Naive single-pass</SectionLabel>
          <div className="mt-3">
            <StatusChip status={actionStatus(naive)} size="lg" />
          </div>
          <p className="mt-3 text-sm text-ink-muted">Reads each field once. No reconciliation.</p>
        </div>
        <div className="p-6">
          <h2 className="text-[11px] font-medium uppercase tracking-[0.14em] text-ink">
            Counterproof
          </h2>
          <div className="mt-3">
            <StatusChip status={actionStatus(counterproof)} size="lg" />
          </div>
          <p className="mt-3 text-sm text-ink-muted">
            {grounded} of {fieldFindings.length} fields grounded with a citation.
          </p>
        </div>
      </div>

      {caught && (
        <div
          role="status"
          aria-live="polite"
          className="border-l-2 border-review-line bg-review-bg px-5 py-4"
        >
          <p className="text-[15px] font-medium text-review">Discrepancy found.</p>
          <p className="mt-1 text-sm text-ink-muted">
            A naive single-pass read would pass this document. Counterproof{" "}
            {counterproof === "block" ? "blocks" : "flags"} it for review.
          </p>
        </div>
      )}

      {failedChecks.length > 0 && (
        <section aria-label="Evidence" className="flex flex-col gap-5">
          <SectionLabel>Evidence</SectionLabel>
          {failedChecks.map((check) => (
            <div key={check.name}>
              <p className="text-base text-ink">{check.detail}</p>
              <p className="mt-1 font-mono text-xs text-ink-faint">check: {check.name}</p>
              {check.citations.map((citation, index) => (
                <CitedLine key={index} citation={citation} />
              ))}
            </div>
          ))}
        </section>
      )}

      {hasChecks && failedChecks.length === 0 && (
        <p className="text-sm text-ink-muted">All cross-validation checks passed.</p>
      )}

      {fieldFindings.length > 0 && (
        <details className="border-t border-line pt-5">
          <summary className="cursor-pointer text-sm text-ink-muted marker:text-ink-faint">
            Extracted fields ({fieldFindings.length})
          </summary>
          <p className="mt-2 max-w-prose text-xs text-ink-faint">
            Re-derived from the document and cited. No cross-check applies to these individually.
          </p>
          <ul className="mt-3 divide-y divide-line">
            {fieldFindings.map((finding) => {
              const citation = finding.citations[0];
              return (
                <li
                  key={finding.field}
                  className="flex items-baseline justify-between gap-4 py-2.5"
                >
                  <div className="min-w-0">
                    <span className="font-mono text-[13px] text-ink">{fieldKey(finding.field)}</span>
                    <span className="ml-3 break-words font-mono text-[13px] text-ink-muted">
                      {valueText(finding.independent_value)}
                    </span>
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    {citation && (
                      <span className="font-mono text-xs text-ink-faint">{citation.location}</span>
                    )}
                    <span className="text-[11px] uppercase tracking-wide text-ink-faint">
                      {CLASSIFICATION_LABEL[finding.classification]}
                    </span>
                  </div>
                </li>
              );
            })}
          </ul>
        </details>
      )}

      <details className="border-t border-line pt-5">
        <summary className="cursor-pointer text-sm text-ink-muted marker:text-ink-faint">
          Audit trail
        </summary>
        <ol className="mt-3 flex flex-col gap-1.5 font-mono text-xs text-ink-faint">
          {report.audit_trail.map((event) => (
            <li key={event.step}>
              <span className="text-ink-muted">{event.step}</span> {event.detail}{" "}
              <span className="text-ink-faint">({event.output_sha256.slice(0, 12)})</span>
            </li>
          ))}
        </ol>
        <p className="mt-3 font-mono text-xs text-ink-faint">
          engine {report.engine_version} · model {report.model_version} · policy{" "}
          {report.policy_version}
        </p>
      </details>
    </section>
  );
}
