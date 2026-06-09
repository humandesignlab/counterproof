import { naiveVerdict } from "../lib/baseline";
import type { ChallengeReport, RecommendedAction } from "../lib/types";

const ACTION_STYLES: Record<RecommendedAction, string> = {
  pass: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
  review: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
  block: "bg-red-500/15 text-red-300 ring-red-500/30",
};

function ActionBadge({ action }: { action: RecommendedAction }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold uppercase tracking-wide ring-1 ${ACTION_STYLES[action]}`}
    >
      {action}
    </span>
  );
}

function valueText(value: unknown): string {
  if (value === null || value === undefined) return "—";
  return String(value);
}

export function Report({ report }: { report: ChallengeReport }) {
  const naive = naiveVerdict(report);
  const counterproof = report.recommended_action;
  const caughtWhatNaiveMissed = naive === "pass" && counterproof !== "pass";

  return (
    <section className="flex flex-col gap-6" aria-label="Challenge report">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-400">Naive single-pass</p>
          <div className="mt-2">
            <ActionBadge action={naive} />
          </div>
          <p className="mt-2 text-sm text-slate-400">Reads each field once. No reconciliation.</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-400">Counterproof</p>
          <div className="mt-2">
            <ActionBadge action={counterproof} />
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Overall confidence {(report.overall_confidence * 100).toFixed(0)}% · policy{" "}
            {report.policy_version}
          </p>
        </div>
      </div>

      {caughtWhatNaiveMissed && (
        <p
          className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200"
          role="status"
        >
          A naive single-pass read would have passed this document. Counterproof caught a
          discrepancy the source read missed.
        </p>
      )}

      {report.checks.length > 0 && (
        <div>
          <h3 className="mb-2 text-sm font-semibold text-slate-200">Cross-validation checks</h3>
          <ul className="flex flex-col gap-2">
            {report.checks.map((check) => (
              <li
                key={check.name}
                className="rounded-lg border border-slate-800 bg-slate-900/50 p-3 text-sm"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-slate-300">{check.name}</span>
                  <span
                    className={check.status === "fail" ? "text-red-300" : "text-emerald-300"}
                  >
                    {check.status}
                  </span>
                </div>
                <p className="mt-1 text-slate-400">{check.detail}</p>
                {check.citations.map((citation, index) => (
                  <p key={index} className="mt-1 text-xs text-slate-500">
                    {citation.location}: <span className="font-mono">{citation.snippet}</span>
                  </p>
                ))}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-200">Findings</h3>
        <ul className="flex flex-col gap-2">
          {report.findings.map((finding) => (
            <li
              key={finding.field}
              className="rounded-lg border border-slate-800 bg-slate-900/50 p-3 text-sm"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-slate-300">{finding.field}</span>
                <span className="text-xs uppercase tracking-wide text-slate-500">
                  {finding.classification}
                </span>
              </div>
              <p className="mt-1 text-slate-200">{valueText(finding.independent_value)}</p>
              {finding.citations.map((citation, index) => (
                <p key={index} className="mt-1 text-xs text-slate-500">
                  {citation.location}: <span className="font-mono">{citation.snippet}</span>
                </p>
              ))}
            </li>
          ))}
        </ul>
      </div>

      <details className="rounded-lg border border-slate-800 bg-slate-900/50 p-3 text-sm">
        <summary className="cursor-pointer text-slate-300">Audit trail</summary>
        <ol className="mt-2 flex flex-col gap-1 text-xs text-slate-400">
          {report.audit_trail.map((event) => (
            <li key={event.step}>
              <span className="font-mono text-slate-300">{event.step}</span>: {event.detail}{" "}
              <span className="text-slate-600">({event.output_sha256.slice(0, 12)}…)</span>
            </li>
          ))}
        </ol>
        <p className="mt-2 text-xs text-slate-600">
          engine {report.engine_version} · model {report.model_version}
        </p>
      </details>
    </section>
  );
}
