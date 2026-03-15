import { useMemo, useState } from "react";
import {
  CalciteLabel,
  CalciteSegmentedControl,
  CalciteSegmentedControlItem,
  CalciteInput,
} from "@esri/calcite-components-react";

import type { GeometryIssue } from "../../types/api";

export type IssuesPanelProps = {
  issues: GeometryIssue[];
  onSelectIssue: (issue: GeometryIssue | null) => void;
};

type TypeFilter = "all" | "geometry" | "attribute" | "topology";
type SeverityFilter = "all" | "critical" | "warning";

function categorizeType(type: string): TypeFilter {
  if (type.startsWith("attribute_")) return "attribute";
  if (type.startsWith("topology_")) return "topology";
  return "geometry";
}

export function IssuesPanel({ issues, onSelectIssue }: IssuesPanelProps) {
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("all");
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>("all");
  const [featureFilter, setFeatureFilter] = useState<string>("");

  const filteredIssues = useMemo(() => {
    return issues.filter((issue) => {
      const t = categorizeType(issue.type || "");
      if (typeFilter !== "all" && t !== typeFilter) return false;

      const sev = (issue.severity || "").toLowerCase();
      if (severityFilter === "critical" && sev !== "critical") return false;
      if (severityFilter === "warning" && sev !== "warning") return false;

      if (featureFilter.trim()) {
        const idStr =
          issue.feature_id !== undefined && issue.feature_id !== null
            ? String(issue.feature_id)
            : "";
        if (!idStr.includes(featureFilter.trim())) return false;
      }

      return true;
    });
  }, [issues, typeFilter, severityFilter, featureFilter]);

  const handleClearFilters = () => {
    setTypeFilter("all");
    setSeverityFilter("all");
    setFeatureFilter("");
  };

  const handleRowClick = (issue: GeometryIssue) => {
    onSelectIssue(issue);
  };

  return (
    <div className="issues-panel">
      <div className="issues-panel__filters">
        <CalciteLabel>
          Type
          <CalciteSegmentedControl
            value={typeFilter}
            onCalciteSegmentedControlChange={(event) => {
              const value = (event.target as HTMLCalciteSegmentedControlElement).value as TypeFilter;
              setTypeFilter(value);
            }}
          >
            <CalciteSegmentedControlItem value="all">All</CalciteSegmentedControlItem>
            <CalciteSegmentedControlItem value="geometry">Geometry</CalciteSegmentedControlItem>
            <CalciteSegmentedControlItem value="attribute">Attribute</CalciteSegmentedControlItem>
            <CalciteSegmentedControlItem value="topology">Topology</CalciteSegmentedControlItem>
          </CalciteSegmentedControl>
        </CalciteLabel>

        <CalciteLabel>
          Severity
          <CalciteSegmentedControl
            value={severityFilter}
            onCalciteSegmentedControlChange={(event) => {
              const value = (event.target as HTMLCalciteSegmentedControlElement)
                .value as SeverityFilter;
              setSeverityFilter(value);
            }}
          >
            <CalciteSegmentedControlItem value="all">All</CalciteSegmentedControlItem>
            <CalciteSegmentedControlItem value="critical">Critical</CalciteSegmentedControlItem>
            <CalciteSegmentedControlItem value="warning">Warning</CalciteSegmentedControlItem>
          </CalciteSegmentedControl>
        </CalciteLabel>

        <CalciteLabel>
          Feature ID
          <CalciteInput
            value={featureFilter}
            placeholder="Filter by feature id"
            onCalciteInputInput={(event) => {
              const value = (event.target as HTMLCalciteInputElement).value ?? "";
              setFeatureFilter(value);
            }}
          />
        </CalciteLabel>

        <button type="button" className="issues-panel__clear" onClick={handleClearFilters}>
          Clear filters
        </button>
      </div>

      {!filteredIssues.length ? (
        <p className="empty-state">No issues match the current filters.</p>
      ) : (
        <ul className="issues-panel-list" aria-label="Validation issues">
          {filteredIssues.map((issue, index) => (
            <li key={index}>
              <button
                type="button"
                className="issues-panel-item"
                onClick={() => handleRowClick(issue)}
              >
                <span className="issues-panel-item__type">{issue.type}</span>
                <span className="issues-panel-item__severity">{issue.severity}</span>
                <span className="issues-panel-item__feature">
                  {issue.feature_id !== undefined && issue.feature_id !== null
                    ? `Feature ${String(issue.feature_id)}`
                    : "Dataset-level issue"}
                </span>
                {issue.description && (
                  <span className="issues-panel-item__description">
                    {issue.description.length > 80
                      ? `${issue.description.slice(0, 77)}…`
                      : issue.description}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

