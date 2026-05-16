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

export type ApplyCorrectionsEligibilityInput = {
  hasDataset: boolean;
  validationResult: ValidationResult | null;
  correctionDecisions: Record<number, CorrectionDecision>;
  correctionOverrides: Record<number, CorrectionOverride>;
};

/** Whether the Apply corrections action can run with current UI state. */
export function canApplyCorrections(input: ApplyCorrectionsEligibilityInput): boolean {
  if (!input.hasDataset || !input.validationResult) return false;
  if (hasPendingCustomCorrections(input.correctionDecisions, input.correctionOverrides)) {
    return false;
  }
  return (
    buildApplyCorrectionsActions(
      input.validationResult,
      input.correctionDecisions,
      input.correctionOverrides,
    ).length > 0
  );
}

/** Human-readable reasons Apply corrections stays disabled (issue #116). */
export function getApplyCorrectionsDisabledReasons(
  input: ApplyCorrectionsEligibilityInput,
): string[] {
  if (!input.hasDataset) {
    return ["Upload a dataset before applying corrections."];
  }

  if (!input.validationResult) {
    return ["Run validation to load issues and correction suggestions."];
  }

  const reasons: string[] = [];
  const suggestions = input.validationResult.corrections ?? [];
  const withSuggestion = new Set(suggestions.map((c) => c.issue_index));
  const actions = buildApplyCorrectionsActions(
    input.validationResult,
    input.correctionDecisions,
    input.correctionOverrides,
  );

  if (hasPendingCustomCorrections(input.correctionDecisions, input.correctionOverrides)) {
    reasons.push("Save custom fixes for all Custom issues before applying corrections.");
  }

  if (actions.length === 0) {
    if (suggestions.length === 0) {
      reasons.push("No correction suggestions are available for the current validation result.");
    } else if (Object.keys(input.correctionDecisions).length === 0) {
      reasons.push("Approve or reject at least one suggested correction in Issue details.");
    } else {
      const hasDecisionOnSuggestion = Object.entries(input.correctionDecisions).some(
        ([idx]) => withSuggestion.has(Number(idx)),
      );
      if (!hasDecisionOnSuggestion) {
        reasons.push(
          "Choose Approve or Reject for an issue that has a correction suggestion.",
        );
      }
    }
  }

  return reasons;
}
