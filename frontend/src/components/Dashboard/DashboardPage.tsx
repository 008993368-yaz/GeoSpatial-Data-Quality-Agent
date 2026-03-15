import { useState } from "react";
import { CalcitePanel, CalciteButton, CalciteLoader } from "@esri/calcite-components-react";

import { MapViewer } from "../Map/MapViewer";
import { SummaryStats } from "./SummaryStats";
import { IssuesPanel } from "./IssuesPanel";
import { DetailView } from "./DetailView";
import { useApp } from "../../context/AppContext";

export function DashboardPage() {
  const {
    currentDataset,
    validationIssues,
    isValidating,
    validationError,
    handleValidate,
  } = useApp();
  const [selectedIssueIndex, setSelectedIssueIndex] = useState<number | null>(null);

  const totalFeatures =
    typeof currentDataset?.feature_count === "number" ? currentDataset.feature_count : null;

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
              disabled={isValidating}
              loading={isValidating}
              label={isValidating ? "Validating…" : "Run validation"}
            >
              {isValidating ? "Validating…" : "Run validation"}
            </CalciteButton>
            {isValidating && (
              <div className="dashboard-validation-status" role="status" aria-live="polite">
                <CalciteLoader scale="s" />
                <span>Validation in progress. Issues and map will update when complete.</span>
              </div>
            )}
            {validationError && (
              <p className="status-message status-message--error" role="alert">
                {validationError}
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

