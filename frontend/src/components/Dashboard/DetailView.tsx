import { useMemo } from "react";

import { useApp } from "../../context/AppContext";
import type { CorrectionSuggestion, GeometryIssue } from "../../types/api";

export type DetailViewProps = {
  selectedIssueIndex: number | null;
};

export function DetailView({ selectedIssueIndex }: DetailViewProps) {
  const { validationResult } = useApp();

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

  if (!issue) {
    return <p className="empty-state">Select an issue to see its details and suggested fix.</p>;
  }

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
          </>
        )}
      </div>
    </div>
  );
}

