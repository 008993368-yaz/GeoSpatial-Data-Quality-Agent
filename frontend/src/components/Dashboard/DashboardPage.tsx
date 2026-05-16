import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  CalcitePanel,
  CalciteButton,
  CalciteLoader,
  CalciteAlert,
  CalciteDialog,
} from "@esri/calcite-components-react";

import { MapViewer } from "../Map/MapViewer";
import { SummaryStats } from "./SummaryStats";
import { IssuesPanel } from "./IssuesPanel";
import { DetailView } from "./DetailView";
import { ApplyResultsPanel } from "./ApplyResultsPanel";
import { useApp } from "../../context/AppContext";
import {
  canApplyCorrections,
  getApplyCorrectionsDisabledReasons,
} from "../../utils/buildApplyCorrectionsRequest";

export function DashboardPage() {
  const {
    currentDataset,
    validationIssues,
    validationResult,
    correctionDecisions,
    correctionOverrides,
    isValidating,
    validationError,
    handleValidate,
    isApplyingCorrections,
    applyCorrectionsError,
    lastApplyCorrectionsResult,
    handleApplyCorrections,
    dismissLastApplyResult,
    clearValidationError,
    clearApplyCorrectionsError,
  } = useApp();
  const navigate = useNavigate();
  const [selectedIssueIndex, setSelectedIssueIndex] = useState<number | null>(null);
  const [validateConfirmOpen, setValidateConfirmOpen] = useState(false);

  const totalFeatures =
    typeof currentDataset?.feature_count === "number" ? currentDataset.feature_count : null;

  const applyEligibility = useMemo(
    () => ({
      hasDataset: Boolean(currentDataset?.dataset_id),
      validationResult,
      correctionDecisions,
      correctionOverrides,
    }),
    [currentDataset?.dataset_id, validationResult, correctionDecisions, correctionOverrides],
  );

  const applyEnabled = useMemo(() => canApplyCorrections(applyEligibility), [applyEligibility]);

  const applyDisabledReasons = useMemo(
    () => getApplyCorrectionsDisabledReasons(applyEligibility),
    [applyEligibility],
  );

  const showApplyDisabledHints =
    !applyEnabled && !isValidating && !isApplyingCorrections && applyDisabledReasons.length > 0;

  const validateWillClearFeedback =
    Object.keys(correctionDecisions).length > 0 || lastApplyCorrectionsResult !== null;

  function requestRunValidation() {
    if (validateWillClearFeedback) {
      setValidateConfirmOpen(true);
      return;
    }
    void handleValidate();
  }

  function confirmRunValidation() {
    setValidateConfirmOpen(false);
    void handleValidate();
  }

  return (
    <section className="page-section page-section--dashboard" aria-labelledby="dashboard-heading">
      <h2 id="dashboard-heading" className="page-heading">
        Validation dashboard
      </h2>
      {!currentDataset ? (
        <p className="empty-state">
          Upload and validate a dataset first. The dashboard will show issues, stats, and map view
          once validation has run.
        </p>
      ) : (
        <>
          <CalciteDialog
            open={validateConfirmOpen}
            heading="Re-run validation?"
            onCalciteDialogClose={() => setValidateConfirmOpen(false)}
          >
            <p className="dashboard-confirm-dialog__body">
              Starting validation again will clear your correction choices for this result and remove the apply
              results summary until you apply again. Continue?
            </p>
            <CalciteButton
              slot="footer-start"
              appearance="outline"
              kind="neutral"
              onClick={() => setValidateConfirmOpen(false)}
            >
              Cancel
            </CalciteButton>
            <CalciteButton slot="footer-end" kind="brand" onClick={confirmRunValidation}>
              Continue
            </CalciteButton>
          </CalciteDialog>
          <div className="dashboard-actions">
            <CalciteButton
              kind="brand"
              onClick={requestRunValidation}
              disabled={isValidating || isApplyingCorrections}
              loading={isValidating}
              label={isValidating ? "Validating…" : "Run validation"}
            >
              {isValidating ? "Validating…" : "Run validation"}
            </CalciteButton>
            {validationResult ? (
              <CalciteButton
                kind="neutral"
                appearance="outline"
                onClick={() => navigate("/report")}
                label="Open quality report"
              >
                View report
              </CalciteButton>
            ) : null}
            <CalciteButton
              kind="neutral"
              onClick={handleApplyCorrections}
              disabled={!applyEnabled || isValidating || isApplyingCorrections}
              loading={isApplyingCorrections}
              aria-describedby={showApplyDisabledHints ? "apply-corrections-hint" : undefined}
              label={
                isApplyingCorrections
                  ? "Applying corrections…"
                  : "Apply correction choices to the server"
              }
            >
              {isApplyingCorrections ? "Applying…" : "Apply corrections"}
            </CalciteButton>
            {showApplyDisabledHints && (
              <div
                id="apply-corrections-hint"
                className="dashboard-apply-hints-block"
                role="status"
                aria-live="polite"
              >
                {applyDisabledReasons.length === 1 ? (
                  <p className="dashboard-validation-status">{applyDisabledReasons[0]}</p>
                ) : (
                  <>
                    <p className="dashboard-validation-status">Apply corrections is disabled because:</p>
                    <ul className="dashboard-apply-hints">
                      {applyDisabledReasons.map((reason) => (
                        <li key={reason}>{reason}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}
            {isValidating && (
              <div className="dashboard-validation-status" role="status" aria-live="polite">
                <CalciteLoader scale="s" />
                <span>Validation in progress. Issues and map will update when complete.</span>
              </div>
            )}
            {isApplyingCorrections && (
              <div className="dashboard-validation-status" role="status" aria-live="polite">
                <CalciteLoader scale="s" />
                <span>Sending your correction choices to the API…</span>
              </div>
            )}
            {validationError && (
              <CalciteAlert
                kind="danger"
                open
                closable
                label="Validation error"
                onCalciteAlertClose={() => clearValidationError()}
                className="dashboard-feedback-alert"
              >
                <div slot="title">Validation error</div>
                <div slot="message">{validationError}</div>
              </CalciteAlert>
            )}
            {applyCorrectionsError && (
              <CalciteAlert
                kind="danger"
                open
                closable
                label="Apply corrections error"
                onCalciteAlertClose={() => clearApplyCorrectionsError()}
                className="dashboard-feedback-alert"
              >
                <div slot="title">Could not apply corrections</div>
                <div slot="message">{applyCorrectionsError}</div>
              </CalciteAlert>
            )}
          </div>
          {lastApplyCorrectionsResult ? (
            <ApplyResultsPanel result={lastApplyCorrectionsResult} onDismiss={dismissLastApplyResult} />
          ) : null}
          <div className="dashboard-grid">
            <CalcitePanel heading={currentDataset.filename} className="dashboard-panel dashboard-panel--map">
              <MapViewer
                datasetId={currentDataset.dataset_id}
                bounds={currentDataset.bounds ?? null}
                layerTitle={currentDataset.filename}
                validationIssues={validationIssues}
              />
            </CalcitePanel>

            <CalcitePanel heading="Issues" className="dashboard-panel dashboard-panel--issues">
              <IssuesPanel issues={validationIssues} onSelectIssueIndex={setSelectedIssueIndex} />
            </CalcitePanel>

            <CalcitePanel heading="Summary" className="dashboard-panel dashboard-panel--summary">
              <SummaryStats totalFeatures={totalFeatures} issues={validationIssues} />
            </CalcitePanel>

            <CalcitePanel heading="Issue details" className="dashboard-panel dashboard-panel--detail">
              <DetailView selectedIssueIndex={selectedIssueIndex} />
            </CalcitePanel>
          </div>
        </>
      )}
    </section>
  );
}

