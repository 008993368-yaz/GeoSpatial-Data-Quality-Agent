import { useMemo, useState } from "react";
import { CalcitePanel, CalciteButton, CalciteLoader } from "@esri/calcite-components-react";

import { MapViewer } from "../Map/MapViewer";
import { SummaryStats } from "./SummaryStats";
import { IssuesPanel } from "./IssuesPanel";
import { DetailView } from "./DetailView";
import { useApp } from "../../context/AppContext";
import { buildApplyCorrectionsActions } from "../../utils/buildApplyCorrectionsRequest";

export function DashboardPage() {
  const {
    currentDataset,
    validationIssues,
    validationResult,
    correctionDecisions,
    isValidating,
    validationError,
    handleValidate,
    isApplyingCorrections,
    applyCorrectionsError,
    lastApplyCorrectionsResult,
    handleApplyCorrections,
  } = useApp();
  const [selectedIssueIndex, setSelectedIssueIndex] = useState<number | null>(null);

  const totalFeatures =
    typeof currentDataset?.feature_count === "number" ? currentDataset.feature_count : null;

  const applyActionsCount = useMemo(() => {
    if (!validationResult) return 0;
    return buildApplyCorrectionsActions(validationResult, correctionDecisions).length;
  }, [validationResult, correctionDecisions]);

  const canApplyCorrections =
    Boolean(currentDataset?.dataset_id && validationResult && applyActionsCount > 0);

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
          <div className="dashboard-actions">
            <CalciteButton
              kind="brand"
              onClick={handleValidate}
              disabled={isValidating || isApplyingCorrections}
              loading={isValidating}
              label={isValidating ? "Validating…" : "Run validation"}
            >
              {isValidating ? "Validating…" : "Run validation"}
            </CalciteButton>
            <CalciteButton
              kind="neutral"
              onClick={handleApplyCorrections}
              disabled={!canApplyCorrections || isValidating || isApplyingCorrections}
              loading={isApplyingCorrections}
              label={
                isApplyingCorrections
                  ? "Applying corrections…"
                  : "Apply correction choices to the server"
              }
            >
              {isApplyingCorrections ? "Applying…" : "Apply corrections"}
            </CalciteButton>
            {isValidating && (
              <div className="dashboard-validation-status" role="status" aria-live="polite">
                <CalciteLoader scale="s" />
                <span>Validation in progress. Issues and map will update when complete.</span>
              </div>
            )}
            {isApplyingCorrections && (
              <div className="dashboard-validation-status" role="status" aria-live="polite">
                <CalciteLoader scale="s" />
                <span>Sending your approve/reject choices to the API…</span>
              </div>
            )}
            {validationError && (
              <p className="status-message status-message--error" role="alert">
                {validationError}
              </p>
            )}
            {applyCorrectionsError && (
              <p className="status-message status-message--error" role="alert">
                {applyCorrectionsError}
              </p>
            )}
            {lastApplyCorrectionsResult && (
              <p className="status-message status-message--success" role="status">
                Applied {lastApplyCorrectionsResult.applied}, skipped {lastApplyCorrectionsResult.skipped}.
                {lastApplyCorrectionsResult.download_url ? (
                  <>
                    {" "}
                    <a href={lastApplyCorrectionsResult.download_url}>Dataset download</a>
                  </>
                ) : null}
              </p>
            )}
          </div>
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

