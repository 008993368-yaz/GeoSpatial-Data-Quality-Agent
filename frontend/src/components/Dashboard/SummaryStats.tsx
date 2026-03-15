import type { GeometryIssue } from "../../types/api";

export type SummaryStatsProps = {
  totalFeatures?: number | null;
  issues: GeometryIssue[];
};

export function SummaryStats({ totalFeatures, issues }: SummaryStatsProps) {
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

