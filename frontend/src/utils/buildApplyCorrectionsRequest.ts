import type {
  CorrectionDecision,
  CorrectionOverride,
  ValidationResult,
} from "../types/api";

/** API shape for POST /corrections/apply (backend CorrectionAction). */
export type CorrectionActionPayload = {
  issue_index: number;
  action: "approve" | "reject";
  feature_id?: unknown;
  geometry_wkt?: string;
  attributes?: Record<string, unknown>;
};

/**
 * Build the corrections list from UI state. Only includes indices that have a
 * matching CorrectionSuggestion. Custom decisions require a saved override (issue #106).
 */
export function buildApplyCorrectionsActions(
  validationResult: ValidationResult,
  correctionDecisions: Record<number, CorrectionDecision>,
  correctionOverrides: Record<number, CorrectionOverride> = {},
): CorrectionActionPayload[] {
  const withSuggestion = new Set(
    (validationResult.corrections ?? []).map((c) => c.issue_index),
  );
  const list: CorrectionActionPayload[] = [];
  for (const [idxStr, decision] of Object.entries(correctionDecisions)) {
    const issueIndex = Number(idxStr);
    if (Number.isNaN(issueIndex) || !withSuggestion.has(issueIndex)) continue;
    if (decision === "reject") {
      list.push({ issue_index: issueIndex, action: "reject" });
      continue;
    }
    if (decision === "custom") {
      const override = correctionOverrides[issueIndex];
      if (!override) continue;
      list.push({
        issue_index: issueIndex,
        action: "approve",
        ...(override.feature_id !== undefined ? { feature_id: override.feature_id } : {}),
        ...(override.geometry_wkt ? { geometry_wkt: override.geometry_wkt } : {}),
        ...(override.attributes ? { attributes: override.attributes } : {}),
      });
      continue;
    }
    list.push({ issue_index: issueIndex, action: "approve" });
  }
  list.sort((a, b) => a.issue_index - b.issue_index);
  return list;
}

/** True when any custom decision lacks a saved override (blocks apply). */
export function hasPendingCustomCorrections(
  correctionDecisions: Record<number, CorrectionDecision>,
  correctionOverrides: Record<number, CorrectionOverride>,
): boolean {
  return Object.entries(correctionDecisions).some(
    ([idx, decision]) => decision === "custom" && correctionOverrides[Number(idx)] === undefined,
  );
}
