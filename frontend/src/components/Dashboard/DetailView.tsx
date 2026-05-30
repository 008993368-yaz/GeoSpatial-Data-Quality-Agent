import { useEffect, useMemo, useState } from "react";
import { CalciteButton, CalciteDialog, CalciteNotice } from "@esri/calcite-components-react";

import { useApp } from "../../context/AppContext";
import type { CorrectionDecision, CorrectionSuggestion, GeometryIssue } from "../../types/api";
import { getFirstCorrectionIssueIndex } from "../../utils/correctionSuggestions";
import { severityTone } from "../../utils/severity";
import { CustomCorrectionEditor } from "./CustomCorrectionEditor";

export type DetailViewProps = {
  selectedIssueIndex: number | null;
};

function validationCalloutKey(
  datasetId: string | undefined,
  corrections: { issue_index: number }[] | null | undefined,
): string {
  const indices = (corrections ?? [])
    .map((c) => c.issue_index)
    .filter((i) => typeof i === "number")
    .sort((a, b) => a - b)
    .join(",");
  return `${datasetId ?? ""}:${indices}`;
}

export function DetailView({ selectedIssueIndex }: DetailViewProps) {
  const [resetAllConfirmOpen, setResetAllConfirmOpen] = useState(false);
  const [calloutDismissed, setCalloutDismissed] = useState(false);
  const {
    validationResult,
    currentDataset,
    correctionDecisions,
    correctionOverrides,
    setCorrectionDecision,
    setCorrectionOverride,
    clearCorrectionOverride,
    clearCorrectionDecision,
    resetCorrectionDecisions,
    isApplyingCorrections,
  } = useApp();

  const calloutResetKey = validationCalloutKey(
    validationResult?.dataset_id,
    validationResult?.corrections,
  );

  useEffect(() => {
    setCalloutDismissed(false);
  }, [calloutResetKey]);

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

  const firstCorrectionIssueIndex = useMemo(
    () =>
      getFirstCorrectionIssueIndex(
        validationResult?.corrections,
        validationResult?.issues?.length ?? 0,
      ),
    [validationResult?.corrections, validationResult?.issues?.length],
  );

  const hasAnyDecisions = Object.keys(correctionDecisions).length > 0;

  if (!issue || selectedIssueIndex === null) {
    return <p className="empty-state">Select an issue to see its details and suggested fix.</p>;
  }

  const issueIndex = selectedIssueIndex;
  const decision = correctionDecisions[issueIndex];

  const showApproveRejectCallout =
    Boolean(suggestion) &&
    firstCorrectionIssueIndex !== null &&
    issueIndex === firstCorrectionIssueIndex &&
    decision === undefined &&
    !calloutDismissed;

  function handleCorrectionDecision(choice: CorrectionDecision) {
    if (choice === "approve" || choice === "reject") {
      setCalloutDismissed(true);
    }
    setCorrectionDecision(issueIndex, choice);
  }

  return (
    <div className="detail-view">
      <CalciteDialog
        open={resetAllConfirmOpen}
        heading="Reset all correction choices?"
        onCalciteDialogClose={() => setResetAllConfirmOpen(false)}
      >
        <p className="dashboard-confirm-dialog__body">
          This removes Approve, Reject, and Custom selections for every issue. You will need to choose again before
          applying corrections.
        </p>
        <CalciteButton
          slot="footer-start"
          appearance="outline"
          kind="neutral"
          onClick={() => setResetAllConfirmOpen(false)}
        >
          Cancel
        </CalciteButton>
        <CalciteButton
          slot="footer-end"
          kind="brand"
          onClick={() => {
            setResetAllConfirmOpen(false);
            resetCorrectionDecisions();
          }}
        >
          Reset all
        </CalciteButton>
      </CalciteDialog>
      <div className="detail-view__section">
        <h3 className="detail-view__heading">Issue details</h3>
        <p>
          <strong>Type:</strong> {issue.type}
        </p>
        <p>
          <strong>Severity:</strong>{" "}
          <span className="severity-badge" data-severity={severityTone(issue.severity)}>
            {issue.severity}
          </span>
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
              <strong>Method:</strong> <code className="detail-view__method">{suggestion.method}</code>
            </p>
            <div className="detail-view__confidence">
              <strong>Confidence:</strong>
              <span
                className="confidence-bar"
                role="img"
                aria-label={`Confidence ${(suggestion.confidence * 100).toFixed(0)} percent`}
              >
                <span
                  className="confidence-bar__fill"
                  data-level={
                    suggestion.confidence >= 0.75
                      ? "high"
                      : suggestion.confidence >= 0.4
                        ? "medium"
                        : "low"
                  }
                  style={{ width: `${Math.round(suggestion.confidence * 100)}%` }}
                />
              </span>
              <span className="confidence-bar__value">
                {(suggestion.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <p>
              <strong>Explanation:</strong> {suggestion.explanation}
            </p>

            <div
              className={`correction-actions${showApproveRejectCallout ? " correction-actions--onboarding" : ""}`}
              role="group"
              aria-labelledby="correction-actions-label"
            >
              <p id="correction-actions-label" className="correction-actions__label">
                How should we handle this suggestion?
              </p>
              {showApproveRejectCallout && (
                <CalciteNotice
                  open
                  kind="info"
                  icon
                  scale="s"
                  width="full"
                  closable
                  className="correction-callout"
                  onCalciteNoticeClose={() => setCalloutDismissed(true)}
                >
                  <div slot="message">
                    Choose <strong>Approve</strong> or <strong>Reject</strong> to record your decision. You need at
                    least one choice before <strong>Apply corrections</strong> is enabled.
                  </div>
                </CalciteNotice>
              )}
              <div className="correction-actions__buttons">
                <CalciteButton
                  kind={decision === "approve" ? "brand" : "neutral"}
                  appearance={decision === "approve" ? "solid" : "outline"}
                  onClick={() => handleCorrectionDecision("approve")}
                  disabled={isApplyingCorrections}
                  label="Approve suggested fix"
                >
                  Approve
                </CalciteButton>
                <CalciteButton
                  kind={decision === "reject" ? "brand" : "neutral"}
                  appearance={decision === "reject" ? "solid" : "outline"}
                  onClick={() => handleCorrectionDecision("reject")}
                  disabled={isApplyingCorrections}
                  label="Reject suggested fix"
                >
                  Reject
                </CalciteButton>
                <CalciteButton
                  kind={decision === "custom" ? "brand" : "neutral"}
                  appearance={decision === "custom" ? "solid" : "outline"}
                  onClick={() => handleCorrectionDecision("custom")}
                  disabled={isApplyingCorrections}
                  label="Use a custom fix you will edit before apply"
                >
                  Custom
                </CalciteButton>
              </div>
              {decision === "custom" && currentDataset?.dataset_id && (
                <CustomCorrectionEditor
                  datasetId={currentDataset.dataset_id}
                  issue={issue}
                  savedOverride={correctionOverrides[issueIndex]}
                  onSave={(override) => setCorrectionOverride(issueIndex, override)}
                  onClear={() => clearCorrectionOverride(issueIndex)}
                  disabled={isApplyingCorrections}
                />
              )}
              {decision === "custom" && !correctionOverrides[issueIndex] && (
                <p className="correction-actions__hint correction-actions__hint--custom">
                  <strong>Custom:</strong> save your geometry WKT and/or attribute JSON before applying
                  corrections.
                </p>
              )}
              <div className="correction-actions__footer">
                <button
                  type="button"
                  className="correction-actions__link"
                  onClick={() => clearCorrectionDecision(issueIndex)}
                  disabled={decision === undefined || isApplyingCorrections}
                >
                  Clear choice for this issue
                </button>
                {hasAnyDecisions && (
                  <button
                    type="button"
                    className="correction-actions__link"
                    onClick={() => setResetAllConfirmOpen(true)}
                    disabled={isApplyingCorrections}
                  >
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
