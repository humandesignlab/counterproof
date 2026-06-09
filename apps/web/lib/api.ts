import type { ChallengeReport } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface DocumentInput {
  document_id: string;
  text: string;
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
