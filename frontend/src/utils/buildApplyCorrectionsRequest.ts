import type { CorrectionDecision, ValidationResult } from "../types/api";

/** API shape for POST /corrections/apply (backend CorrectionAction). */
export type CorrectionActionPayload = {
  issue_index: number;
  action: "approve" | "reject";
};

/**
 * Build the corrections list from UI state. Only includes indices that have a
 * matching CorrectionSuggestion. Maps "custom" to approve (same suggestion until
 * override payload exists; see issue #106).
 */
export function buildApplyCorrectionsActions(
  validationResult: ValidationResult,
  correctionDecisions: Record<number, CorrectionDecision>,
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
    } else {
      list.push({ issue_index: issueIndex, action: "approve" });
    }
  }
  list.sort((a, b) => a.issue_index - b.issue_index);
  return list;
}
