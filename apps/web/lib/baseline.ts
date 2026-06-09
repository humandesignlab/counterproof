import type { ChallengeReport, RecommendedAction } from "./types";

const CHECK_DRIVEN: ReadonlySet<string> = new Set(["material_discrepancy", "contradiction"]);

/**
 * What a naive single-pass read (fields present, no reconciliation) would conclude.
 * It ignores the cross-validation checks, so it passes a tampered document whose
 * fields are all present, which is the contrast Counterproof exists to show.
 */
export function naiveVerdict(report: ChallengeReport): RecommendedAction {
  const fieldFindings = report.findings.filter((f) => !CHECK_DRIVEN.has(f.classification));
  const allPresent = fieldFindings.every(
    (f) => f.classification !== "missing" && f.citations.length > 0,
  );
  return allPresent ? "pass" : "review";
}
