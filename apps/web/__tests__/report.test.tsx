import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { Report } from "../components/Report";
import type { ChallengeReport } from "../lib/types";

const TAMPERED_REPORT: ChallengeReport = {
  document_ids: ["paystub-tampered-sample"],
  findings: [
    {
      field: "paystub-tampered-sample.gross_pay",
      independent_value: 5600.0,
      primary_value: null,
      citations: [
        {
          document_id: "paystub-tampered-sample",
          location: "line 9",
          snippet: "Gross Pay (this period): 5600.00",
        },
      ],
      confidence: 1.0,
      classification: "unverified",
      severity: "info",
      rationale: "Independently extracted, grounded by 1 citation(s).",
    },
  ],
  checks: [
    {
      name: "ytd_vs_per_period",
      status: "fail",
      detail: "YTD gross 8400.00 is not an integer multiple of the per-period gross 5600.00.",
      citations: [
        {
          document_id: "paystub-tampered-sample",
          location: "line 14",
          snippet: "YTD Gross: 8400.00",
        },
      ],
    },
  ],
  overall_confidence: 1.0,
  recommended_action: "review",
  audit_trail: [
    {
      step: "validate",
      input_sha256: "a".repeat(64),
      output_sha256: "b".repeat(64),
      detail: "Ran 1 cross-validation check(s).",
    },
  ],
  engine_version: "0.1.0",
  model_version: "deterministic-extractor-v1",
  prompt_version: "n/a",
  policy_version: "escalation-v1",
};

test("shows the before-and-after verdict contrast for a tampered report", () => {
  render(<Report report={TAMPERED_REPORT} />);
  expect(screen.getByText("Naive single-pass")).toBeDefined();
  expect(screen.getByText("Counterproof")).toBeDefined();
  // Naive passes, Counterproof flags it.
  expect(screen.getByText("PASS")).toBeDefined();
  expect(screen.getByText("REVIEW")).toBeDefined();
});

test("raises a real alert that the naive read would have missed it", () => {
  render(<Report report={TAMPERED_REPORT} />);
  const alert = screen.getByRole("status");
  expect(alert.textContent).toContain("Discrepancy found");
  expect(alert.textContent).toContain("naive single-pass read would pass");
});

test("presents the failing check as evidence with its cited source line", () => {
  render(<Report report={TAMPERED_REPORT} />);
  expect(screen.getByText(/not an integer multiple/)).toBeDefined();
  expect(screen.getByText("check: ytd_vs_per_period")).toBeDefined();
  expect(screen.getByText("YTD Gross: 8400.00")).toBeDefined();
});

test("moves extracted fields behind a disclosure instead of a wall", () => {
  render(<Report report={TAMPERED_REPORT} />);
  expect(screen.getByText(/Extracted fields \(1\)/)).toBeDefined();
});
