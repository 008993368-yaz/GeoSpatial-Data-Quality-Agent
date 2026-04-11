import { useMemo } from "react";
import { CalciteButton } from "@esri/calcite-components-react";

import { useApp } from "../../context/AppContext";
import type { CorrectionSuggestion, GeometryIssue } from "../../types/api";

export type DetailViewProps = {
  selectedIssueIndex: number | null;
};

export function DetailView({ selectedIssueIndex }: DetailViewProps) {
  const {
    validationResult,
    correctionDecisions,
    setCorrectionDecision,
    clearCorrectionDecision,
    resetCorrectionDecisions,
  } = useApp();

  const issue: GeometryIssue | null =
    selectedIssueIndex !== null && validationResult?.issues?.[selectedIssueIndex]
      ? validationResult.issues[selectedIssueIndex]
      : null;

  const suggestion: CorrectionSuggestion | null = useMemo(() => {
    if (selectedIssueIndex === null || !validationResult?.corrections) return null;
    return (
      validationResult.corrections.find(
        (c) => typeof c.issue_index === "number" && c.issue_index === selectedIssueIndex,
      ) ?? null
    );
  }, [selectedIssueIndex, validationResult?.corrections]);

  const hasAnyDecisions = Object.keys(correctionDecisions).length > 0;

  if (!issue || selectedIssueIndex === null) {
    return <p className="empty-state">Select an issue to see its details and suggested fix.</p>;
  }

  const issueIndex = selectedIssueIndex;
  const decision = correctionDecisions[issueIndex];

  return (
    <div className="detail-view">
      <div className="detail-view__section">
        <h3 className="detail-view__heading">Issue details</h3>
        <p>
          <strong>Type:</strong> {issue.type}
        </p>
        <p>
          <strong>Severity:</strong> {issue.severity}
        </p>
        {issue.feature_id !== undefined && issue.feature_id !== null && (
          <p>
            <strong>Feature:</strong> {String(issue.feature_id)}
          </p>
        )}
        {issue.location && (
          <p>
            <strong>Location:</strong> [{issue.location.join(", ")}]
          </p>
        )}
        {issue.description && (
          <p>
            <strong>Description:</strong> {issue.description}
          </p>
        )}
      </div>

      <div className="detail-view__section">
        <h3 className="detail-view__heading">Suggested fix</h3>
        {!suggestion ? (
          <p className="detail-view__no-suggestion">
            No suggested fix is available for this issue. You can review it manually.
          </p>
        ) : (
          <>
            <p>
              <strong>Method:</strong> {suggestion.method}
            </p>
            <p>
              <strong>Confidence:</strong> {(suggestion.confidence * 100).toFixed(0)}%
            </p>
            <p>
              <strong>Explanation:</strong> {suggestion.explanation}
            </p>

            <div className="correction-actions" role="group" aria-labelledby="correction-actions-label">
              <p id="correction-actions-label" className="correction-actions__label">
                How should we handle this suggestion?
              </p>
              <div className="correction-actions__buttons">
                <CalciteButton
                  kind={decision === "approve" ? "brand" : "neutral"}
                  appearance={decision === "approve" ? "solid" : "outline"}
                  onClick={() => setCorrectionDecision(issueIndex, "approve")}
                  label="Approve suggested fix"
                >
                  Approve
                </CalciteButton>
                <CalciteButton
                  kind={decision === "reject" ? "brand" : "neutral"}
                  appearance={decision === "reject" ? "solid" : "outline"}
                  onClick={() => setCorrectionDecision(issueIndex, "reject")}
                  label="Reject suggested fix"
                >
                  Reject
                </CalciteButton>
                <CalciteButton
                  kind={decision === "custom" ? "brand" : "neutral"}
                  appearance={decision === "custom" ? "solid" : "outline"}
                  onClick={() => setCorrectionDecision(issueIndex, "custom")}
                  label="Use a custom fix you will edit before apply"
                >
                  Custom
                </CalciteButton>
              </div>
              <p className="correction-actions__hint correction-actions__hint--custom">
                <strong>Custom:</strong> you will supply or adjust the fix before applying corrections
                (manual editing UI can follow in a later task).
              </p>
              <div className="correction-actions__footer">
                <button
                  type="button"
                  className="correction-actions__link"
                  onClick={() => clearCorrectionDecision(issueIndex)}
                  disabled={decision === undefined}
                >
                  Clear choice for this issue
                </button>
                {hasAnyDecisions && (
                  <button type="button" className="correction-actions__link" onClick={resetCorrectionDecisions}>
                    Reset all correction choices
                  </button>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
