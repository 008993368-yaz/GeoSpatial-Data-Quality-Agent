import { useState } from "react";
import { CalciteBlock, CalcitePanel } from "@esri/calcite-components-react";

import { MapViewer } from "../Map/MapViewer";
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

type SummaryStatsProps = {
  totalFeatures?: number | null;
  issues: GeometryIssue[];
};

function SummaryStats({ totalFeatures, issues }: SummaryStatsProps) {
  const totalIssues = issues.length;
  const critical = issues.filter((i) => i.severity.toLowerCase() === "critical").length;
  const warning = issues.filter((i) => i.severity.toLowerCase() === "warning").length;

  return (
    <div className="summary-stats">
      <div className="summary-stats__item">
        <span className="summary-stats__label">Total features</span>
        <span className="summary-stats__value">
          {typeof totalFeatures === "number" ? totalFeatures : "—"}
        </span>
      </div>
      <div className="summary-stats__item">
        <span className="summary-stats__label">Issues found</span>
        <span className="summary-stats__value">{totalIssues}</span>
      </div>
      <div className="summary-stats__item">
        <span className="summary-stats__label">Critical</span>
        <span className="summary-stats__value">{critical}</span>
      </div>
      <div className="summary-stats__item">
        <span className="summary-stats__label">Warnings</span>
        <span className="summary-stats__value">{warning}</span>
      </div>
    </div>
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
          <strong>Feature:</strong> {issue.feature_id}
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
  const { currentDataset, validationResult, validationIssues } = useApp();
  const [selectedIssue, setSelectedIssue] = useState<GeometryIssue | null>(null);

  const totalFeatures = validationResult?.summary?.total_features ?? null;

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

          <CalciteBlock
            heading="Issue details"
            className="dashboard-panel dashboard-panel--detail"
            expanded
            collapsible={false}
          >
            <DetailView issue={selectedIssue} />
          </CalciteBlock>
        </div>
      )}
    </section>
  );
}

