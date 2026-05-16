import type {
  CorrectionDecision,
  CorrectionOverride,
  GeometryIssue,
  UploadResponse,
  ValidationConfigResponse,
  ValidationResult,
} from "../types/api";

export type IssueCategory = "geometry" | "attribute" | "topology";

export function categorizeIssueType(type: string): IssueCategory {
  if (type.startsWith("attribute_")) return "attribute";
  if (type.startsWith("topology_")) return "topology";
  return "geometry";
}

export type IssueSummary = {
  totalIssues: number;
  critical: number;
  warning: number;
  byCategory: Record<IssueCategory, number>;
  byType: Record<string, number>;
};

export function computeIssueSummary(issues: GeometryIssue[]): IssueSummary {
  const byCategory: Record<IssueCategory, number> = {
    geometry: 0,
    attribute: 0,
    topology: 0,
  };
  const byType: Record<string, number> = {};

  let critical = 0;
  let warning = 0;

  for (const issue of issues) {
    const sev = (issue.severity || "").toLowerCase();
    if (sev === "critical") critical += 1;
    else if (sev === "warning") warning += 1;

    const cat = categorizeIssueType(issue.type || "");
    byCategory[cat] += 1;

    const t = issue.type || "unknown";
    byType[t] = (byType[t] ?? 0) + 1;
  }

  return {
    totalIssues: issues.length,
    critical,
    warning,
    byCategory,
    byType,
  };
}

export type CorrectionDecisionsSnapshot = Record<
  string,
  { decision: CorrectionDecision; hasOverride?: boolean }
>;

export type QualityReportPayload = {
  generated_at: string;
  dataset: UploadResponse;
  validation: ValidationResult;
  summary: IssueSummary;
  correction_decisions?: CorrectionDecisionsSnapshot;
  validation_config?: ValidationConfigResponse | null;
};

const DEFAULT_VALIDATION_CONFIG: ValidationConfigResponse = {
  pipeline_steps: [
    "geometry_validation",
    "attribute_validation",
    "topology_validation",
    "generate_recommendations",
  ],
  geometry_validation_enabled: true,
  attribute_sample_size: 500,
  attribute_max_records_in_prompt: 10,
  openai_model: "gpt-4o-mini",
  topology_checks: { gaps: true, overlaps: true, connectivity: true },
};

export function buildQualityReportPayload(
  dataset: UploadResponse,
  validation: ValidationResult,
  options?: {
    correctionDecisions?: Record<number, CorrectionDecision>;
    correctionOverrides?: Record<number, CorrectionOverride>;
    validationConfig?: ValidationConfigResponse | null;
    generatedAt?: string;
  },
): QualityReportPayload {
  const correction_decisions: CorrectionDecisionsSnapshot | undefined =
    options?.correctionDecisions && Object.keys(options.correctionDecisions).length > 0
      ? Object.fromEntries(
          Object.entries(options.correctionDecisions).map(([idx, decision]) => [
            idx,
            {
              decision,
              hasOverride: Boolean(options.correctionOverrides?.[Number(idx)]),
            },
          ]),
        )
      : undefined;

  return {
    generated_at: options?.generatedAt ?? new Date().toISOString(),
    dataset,
    validation,
    summary: computeIssueSummary(validation.issues),
    correction_decisions,
    validation_config: options?.validationConfig ?? DEFAULT_VALIDATION_CONFIG,
  };
}

export const APPENDIX_ISSUE_LIMIT = 500;
