import { CalciteButton, CalcitePanel } from "@esri/calcite-components-react";

import type { QualityReportPayload } from "../../utils/reportSummary";
import { APPENDIX_ISSUE_LIMIT } from "../../utils/reportSummary";
import { downloadJson, downloadMarkdown, printReport } from "../../utils/exportReport";

export type QualityReportProps = {
  payload: QualityReportPayload;
};

function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function formatBounds(bounds: number[] | null | undefined): string {
  if (!bounds?.length) return "—";
  return bounds.map((n) => n.toFixed(4)).join(", ");
}

type BarChartProps = {
  label: string;
  segments: { name: string; value: number; className: string }[];
  total: number;
};

function BarChart({ label, segments, total }: BarChartProps) {
  const max = Math.max(total, 1);
  return (
    <div className="quality-report-chart">
      <p className="quality-report-chart__title">{label}</p>
      <div className="quality-report-chart__bars" role="img" aria-label={label}>
        {segments.map((seg) => (
          <div key={seg.name} className="quality-report-chart__row">
            <span className="quality-report-chart__label">{seg.name}</span>
            <span className="quality-report-chart__track">
              <span
                className={`quality-report-chart__fill ${seg.className}`}
                style={{ width: `${(seg.value / max) * 100}%` }}
              />
            </span>
            <span className="quality-report-chart__value">{seg.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function QualityReport({ payload }: QualityReportProps) {
  const { dataset, validation, summary, generated_at, validation_config, correction_decisions } =
    payload;

  const filenameBase = dataset.filename.replace(/\.[^.]+$/, "") || dataset.dataset_id;
  const issues = validation.issues;
  const appendixIssues = issues.slice(0, APPENDIX_ISSUE_LIMIT);
  const corrections = validation.corrections ?? [];

  const topTypes = Object.entries(summary.byType)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  const decisionCounts = { approve: 0, reject: 0, custom: 0 };
  if (correction_decisions) {
    for (const entry of Object.values(correction_decisions)) {
      if (entry.decision in decisionCounts) {
        decisionCounts[entry.decision as keyof typeof decisionCounts] += 1;
      }
    }
  }

  return (
    <div className="quality-report">
      <div className="quality-report__toolbar no-print">
        <CalciteButton
          appearance="outline"
          onClick={() => downloadJson(payload, filenameBase)}
          label="Download report as JSON"
        >
          Download JSON
        </CalciteButton>
        <CalciteButton
          appearance="outline"
          onClick={() => downloadMarkdown(payload, filenameBase)}
          label="Download report as Markdown"
        >
          Download Markdown
        </CalciteButton>
        <CalciteButton appearance="solid" onClick={() => printReport()} label="Print or save as PDF">
          Print / Save as PDF
        </CalciteButton>
      </div>

      <div id="quality-report-print-root" className="quality-report__body">
        <header className="quality-report__header">
          <h3 className="quality-report__title">Quality assessment report</h3>
          <p className="quality-report__meta">
            <strong>{dataset.filename}</strong> · {dataset.dataset_id}
          </p>
          <p className="quality-report__meta">Generated {formatTimestamp(generated_at)}</p>
        </header>

        <CalcitePanel heading="Dataset metadata" className="quality-report__panel">
          <dl className="quality-report__dl">
            <div>
              <dt>Features</dt>
              <dd>{typeof dataset.feature_count === "number" ? dataset.feature_count : "—"}</dd>
            </div>
            <div>
              <dt>Geometry type</dt>
              <dd>{dataset.geometry_type ?? "—"}</dd>
            </div>
            <div>
              <dt>CRS</dt>
              <dd>{dataset.crs ?? "—"}</dd>
            </div>
            <div>
              <dt>Bounds</dt>
              <dd>{formatBounds(dataset.bounds)}</dd>
            </div>
          </dl>
        </CalcitePanel>

        {validation_config ? (
          <CalcitePanel heading="Validation configuration" className="quality-report__panel">
            <dl className="quality-report__dl">
              <div>
                <dt>Pipeline</dt>
                <dd>{validation_config.pipeline_steps.join(" → ")}</dd>
              </div>
              <div>
                <dt>Geometry validation</dt>
                <dd>{validation_config.geometry_validation_enabled ? "Enabled" : "Disabled"}</dd>
              </div>
              <div>
                <dt>Attribute sample size</dt>
                <dd>{validation_config.attribute_sample_size}</dd>
              </div>
              <div>
                <dt>Records in LLM prompt</dt>
                <dd>{validation_config.attribute_max_records_in_prompt}</dd>
              </div>
              <div>
                <dt>LLM model</dt>
                <dd>{validation_config.openai_model}</dd>
              </div>
              <div>
                <dt>Topology checks</dt>
                <dd>
                  Gaps {validation_config.topology_checks.gaps ? "on" : "off"}, overlaps{" "}
                  {validation_config.topology_checks.overlaps ? "on" : "off"}, connectivity{" "}
                  {validation_config.topology_checks.connectivity ? "on" : "off"}
                </dd>
              </div>
            </dl>
          </CalcitePanel>
        ) : null}

        <CalcitePanel heading="Summary" className="quality-report__panel">
          <div className="summary-stats">
            <div className="summary-stats__item">
              <span className="summary-stats__label">Total issues</span>
              <span className="summary-stats__value">{summary.totalIssues}</span>
            </div>
            <div className="summary-stats__item">
              <span className="summary-stats__label">Critical</span>
              <span className="summary-stats__value">{summary.critical}</span>
            </div>
            <div className="summary-stats__item">
              <span className="summary-stats__label">Warnings</span>
              <span className="summary-stats__value">{summary.warning}</span>
            </div>
          </div>

          <div className="quality-report__charts">
            <BarChart
              label="By severity"
              total={summary.totalIssues}
              segments={[
                {
                  name: "Critical",
                  value: summary.critical,
                  className: "quality-report-chart__fill--critical",
                },
                {
                  name: "Warning",
                  value: summary.warning,
                  className: "quality-report-chart__fill--warning",
                },
              ]}
            />
            <BarChart
              label="By category"
              total={summary.totalIssues}
              segments={[
                {
                  name: "Geometry",
                  value: summary.byCategory.geometry,
                  className: "quality-report-chart__fill--geometry",
                },
                {
                  name: "Attribute",
                  value: summary.byCategory.attribute,
                  className: "quality-report-chart__fill--attribute",
                },
                {
                  name: "Topology",
                  value: summary.byCategory.topology,
                  className: "quality-report-chart__fill--topology",
                },
              ]}
            />
          </div>
        </CalcitePanel>

        <CalcitePanel heading="Issue breakdown" className="quality-report__panel">
          {topTypes.length > 0 ? (
            <table className="quality-report__table">
              <thead>
                <tr>
                  <th scope="col">Issue type</th>
                  <th scope="col">Count</th>
                </tr>
              </thead>
              <tbody>
                {topTypes.map(([type, count]) => (
                  <tr key={type}>
                    <td>{type}</td>
                    <td>{count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="empty-state">No issues recorded.</p>
          )}
        </CalcitePanel>

        <CalcitePanel heading="Corrections" className="quality-report__panel">
          <p>Suggested corrections: {corrections.length}</p>
          {correction_decisions && Object.keys(correction_decisions).length > 0 ? (
            <ul className="quality-report__decisions">
              <li>Approved: {decisionCounts.approve}</li>
              <li>Rejected: {decisionCounts.reject}</li>
              <li>Custom: {decisionCounts.custom}</li>
            </ul>
          ) : (
            <p className="quality-report__hint">No user correction decisions recorded for this run.</p>
          )}
        </CalcitePanel>

        <CalcitePanel heading="Issues" className="quality-report__panel quality-report__panel--issues">
          {appendixIssues.length === 0 ? (
            <p className="empty-state">No issues found.</p>
          ) : (
            <>
              <div className="quality-report__table-wrap">
                <table className="quality-report__table quality-report__table--issues">
                  <thead>
                    <tr>
                      <th scope="col">#</th>
                      <th scope="col">Type</th>
                      <th scope="col">Severity</th>
                      <th scope="col">Feature</th>
                      <th scope="col">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {appendixIssues.map((issue, index) => (
                      <tr key={index}>
                        <td>{index}</td>
                        <td>{issue.type}</td>
                        <td>{issue.severity}</td>
                        <td>
                          {issue.feature_id !== undefined && issue.feature_id !== null
                            ? String(issue.feature_id)
                            : "—"}
                        </td>
                        <td>{issue.description ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {issues.length > appendixIssues.length ? (
                <p className="quality-report__hint">
                  Showing {appendixIssues.length} of {issues.length} issues. Export JSON or Markdown
                  for the full list.
                </p>
              ) : null}
            </>
          )}
        </CalcitePanel>
      </div>
    </div>
  );
}
