import { useState } from "react";
import { CalcitePanel } from "@esri/calcite-components-react";

import { MapViewer } from "../Map/MapViewer";
import { SummaryStats } from "./SummaryStats";
import { useApp } from "../../context/AppContext";
import type { GeometryIssue } from "../../types/api";

type IssuesPanelProps = {
  issues: GeometryIssue[];
  onSelectIssue: (issue: GeometryIssue | null) => void;
};

function IssuesPanel({ issues, onSelectIssue }: IssuesPanelProps) {
  if (!issues.length) {
    return <p className="empty-state">No validation issues yet. Run validation to see results.</p>;
  }

  return (
    <ul className="issues-panel-list" aria-label="Validation issues">
      {issues.map((issue, index) => (
        <li key={index}>
          <button
            type="button"
            className="issues-panel-item"
            onClick={() => onSelectIssue(issue)}
          >
            <span className="issues-panel-item__type">{issue.type}</span>
            <span className="issues-panel-item__severity">{issue.severity}</span>
            <span className="issues-panel-item__feature">
              {issue.feature_id !== undefined && issue.feature_id !== null
                ? `Feature ${issue.feature_id}`
                : "Dataset-level issue"}
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}

type DetailViewProps = {
  issue: GeometryIssue | null;
};

function DetailView({ issue }: DetailViewProps) {
  if (!issue) {
    return <p className="empty-state">Select an issue to see its details.</p>;
  }

  return (
    <div className="detail-view">
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
  );
}

export function DashboardPage() {
  const { currentDataset, validationIssues } = useApp();
  const [selectedIssue, setSelectedIssue] = useState<GeometryIssue | null>(null);

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
            <IssuesPanel issues={validationIssues} onSelectIssue={setSelectedIssue} />
          </CalcitePanel>

          <CalcitePanel heading="Summary" className="dashboard-panel dashboard-panel--summary">
            <SummaryStats totalFeatures={totalFeatures} issues={validationIssues} />
          </CalcitePanel>

          <CalcitePanel heading="Issue details" className="dashboard-panel dashboard-panel--detail">
            <DetailView issue={selectedIssue} />
          </CalcitePanel>
        </div>
      )}
    </section>
  );
}

