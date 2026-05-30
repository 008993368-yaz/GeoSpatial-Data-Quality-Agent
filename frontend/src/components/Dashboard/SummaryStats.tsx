import type { GeometryIssue } from "../../types/api";
import { computeIssueSummary } from "../../utils/reportSummary";

export type SummaryStatsProps = {
  totalFeatures?: number | null;
  issues: GeometryIssue[];
};

export function SummaryStats({ totalFeatures, issues }: SummaryStatsProps) {
  const { totalIssues, critical, warning } = computeIssueSummary(issues);

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
        <span
          className="summary-stats__value"
          data-tone={critical > 0 ? "critical" : undefined}
        >
          {critical}
        </span>
      </div>
      <div className="summary-stats__item">
        <span className="summary-stats__label">Warnings</span>
        <span className="summary-stats__value" data-tone={warning > 0 ? "warning" : undefined}>
          {warning}
        </span>
      </div>
    </div>
  );
}

