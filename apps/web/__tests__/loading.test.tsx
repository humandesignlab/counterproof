import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import type { ChallengeReport } from "../lib/types";

vi.mock("../lib/api", () => ({
  warmup: vi.fn(() => Promise.resolve()),
  verify: vi.fn(),
}));

import Home from "../app/page";
import { verify } from "../lib/api";

const REPORT: ChallengeReport = {
  document_ids: ["d"],
  findings: [],
  checks: [],
  overall_confidence: 1,
  recommended_action: "review",
  audit_trail: [],
  engine_version: "0.1.0",
  model_version: "deterministic-extractor-v1",
  prompt_version: "n/a",
  policy_version: "escalation-v1",
};

beforeEach(() => {
  // jsdom does not implement scrollIntoView; the completion effect calls it.
  window.HTMLElement.prototype.scrollIntoView = vi.fn();
});

afterEach(() => {
  vi.useRealTimers();
  vi.clearAllMocks();
});

test("Run shows a pending state immediately and a cold-start hint after the threshold", async () => {
  vi.useFakeTimers();
  let resolveVerify: (report: ChallengeReport) => void = () => {};
  vi.mocked(verify).mockImplementation(
    () => new Promise<ChallengeReport>((resolve) => (resolveVerify = resolve)),
  );

  render(<Home />);
  fireEvent.click(screen.getByRole("button", { name: /run counterproof/i }));

  // Immediately pending: label changes, disabled, aria-busy. Not an inert button.
  const pending = screen.getByRole("button", { name: /verifying/i });
  expect((pending as HTMLButtonElement).disabled).toBe(true);
  expect(pending.getAttribute("aria-busy")).toBe("true");
  expect(screen.queryByText(/Waking the verifier/)).toBeNull();

  // After the cold-start threshold, the waking hint appears.
  act(() => {
    vi.advanceTimersByTime(1300);
  });
  expect(screen.getByText(/Waking the verifier/)).toBeDefined();

  // On completion, it returns to idle, the hint clears, and the report renders.
  await act(async () => {
    resolveVerify(REPORT);
  });
  expect(screen.getByRole("button", { name: /run counterproof/i })).toBeDefined();
  expect(screen.queryByText(/Waking the verifier/)).toBeNull();
  expect(screen.getByLabelText("Challenge report")).toBeDefined();
  expect(window.HTMLElement.prototype.scrollIntoView).toHaveBeenCalled();
});
