import type { Classification, RecommendedAction } from "../lib/types";

// Three visual states. Color reinforces; the shape + word carry meaning in
// grayscale and for colorblind readers, so status is never conveyed by color alone.
export type Status = "pass" | "review" | "fail";

export function actionStatus(action: RecommendedAction): Status {
  if (action === "pass") return "pass";
  if (action === "review") return "review";
  return "fail";
}

export function checkStatus(status: string): Status {
  if (status === "fail") return "fail";
  if (status === "pass") return "pass";
  return "review";
}

const STATUS_LABEL: Record<Status, string> = {
  pass: "PASS",
  review: "REVIEW",
  fail: "FAIL",
};

const STATUS_CLASS: Record<Status, string> = {
  pass: "text-pass bg-pass-bg border-pass-line",
  review: "text-review bg-review-bg border-review-line",
  fail: "text-fail bg-fail-bg border-fail-line",
};

// Distinct shape per status so the difference survives grayscale.
function StatusMark({ status }: { status: Status }) {
  const common = { width: 12, height: 12, "aria-hidden": true, focusable: false } as const;
  if (status === "pass") {
    return (
      <svg {...common} viewBox="0 0 12 12">
        <circle cx="6" cy="6" r="5" fill="currentColor" />
      </svg>
    );
  }
  if (status === "review") {
    return (
      <svg {...common} viewBox="0 0 12 12">
        <path d="M6 1 L11 11 L1 11 Z" fill="currentColor" />
      </svg>
    );
  }
  return (
    <svg {...common} viewBox="0 0 12 12">
      <rect x="1" y="1" width="10" height="10" fill="currentColor" />
    </svg>
  );
}

export function StatusChip({ status, size = "sm" }: { status: Status; size?: "sm" | "lg" }) {
  const scale =
    size === "lg" ? "gap-2.5 px-3 py-1.5 text-lg tracking-wide" : "gap-2 px-2 py-0.5 text-xs";
  return (
    <span
      className={`inline-flex items-center rounded-sm border font-semibold ${scale} ${STATUS_CLASS[status]}`}
    >
      <StatusMark status={status} />
      {STATUS_LABEL[status]}
    </span>
  );
}

// Presentation-only relabeling of the schema's classification enum. The engine
// value is unchanged; "unverified" reads as a failure to a lay viewer, so we show
// "Extracted" (it was re-derived and cited; no cross-check applies to it alone).
export const CLASSIFICATION_LABEL: Record<Classification, string> = {
  match: "Match",
  minor_variance: "Minor variance",
  material_discrepancy: "Discrepancy",
  missing: "Missing",
  contradiction: "Contradiction",
  unverified: "Extracted",
};
