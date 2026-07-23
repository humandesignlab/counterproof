import type { ChallengeReport } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface DocumentInput {
  document_id: string;
  text: string;
}

// Fire-and-forget health ping to wake the scale-to-zero API while the visitor
// reads the intro, so the first real request is not stuck behind a cold start.
export async function warmup(): Promise<void> {
  try {
    await fetch(`${API_URL}/health`, { method: "GET" });
  } catch {
    // Best effort only; ignore failures.
  }
}

export async function verify(documents: DocumentInput[]): Promise<ChallengeReport> {
  const response = await fetch(`${API_URL}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ documents }),
  });
  if (!response.ok) {
    throw new Error(`Verification failed (HTTP ${response.status})`);
  }
  return (await response.json()) as ChallengeReport;
}
