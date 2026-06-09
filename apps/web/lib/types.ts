export type RecommendedAction = "pass" | "review" | "block";
export type Severity = "info" | "review" | "block";
export type Classification =
  | "match"
  | "minor_variance"
  | "material_discrepancy"
  | "missing"
  | "contradiction"
  | "unverified";
export type CheckStatus = "pass" | "variance_within_tolerance" | "fail";

export interface Citation {
  document_id: string;
  location: string;
  snippet: string;
}

export interface Finding {
  field: string;
  independent_value: unknown;
  primary_value: unknown;
  citations: Citation[];
  confidence: number;
  classification: Classification;
  severity: Severity;
  rationale: string;
}

export interface CheckResult {
  name: string;
  status: CheckStatus;
  detail: string;
  citations: Citation[];
}

export interface AuditEvent {
  step: string;
  input_sha256: string;
  output_sha256: string;
  detail: string;
}

export interface ChallengeReport {
  document_ids: string[];
  findings: Finding[];
  checks: CheckResult[];
  overall_confidence: number;
  recommended_action: RecommendedAction;
  audit_trail: AuditEvent[];
  engine_version: string;
  model_version: string;
  prompt_version: string;
  policy_version: string;
}
