import type { QualityReportPayload } from "./reportSummary";
import { APPENDIX_ISSUE_LIMIT } from "./reportSummary";

function safeFilename(base: string): string {
  return base.replace(/[^\w.-]+/g, "_").slice(0, 80) || "quality-report";
}

export function downloadJson(payload: QualityReportPayload, filenameBase: string): void {
  const name = `${safeFilename(filenameBase)}-report.json`;
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

function formatBounds(bounds: number[] | null | undefined): string {
  if (!bounds?.length) return "—";
  return bounds.map((n) => n.toFixed(4)).join(", ");
}

export function renderReportMarkdown(payload: QualityReportPayload): string {
  const { dataset, validation, summary, generated_at, validation_config, correction_decisions } =
    payload;
  const lines: string[] = [];

  lines.push(`# Quality assessment report`);
  lines.push("");
  lines.push(`**Dataset:** ${dataset.filename}`);
  lines.push(`**Dataset ID:** ${dataset.dataset_id}`);
  lines.push(`**Generated:** ${generated_at}`);
  lines.push("");

  lines.push(`## Dataset metadata`);
  lines.push("");
  lines.push(`| Field | Value |`);
  lines.push(`| --- | --- |`);
  lines.push(`| Features | ${dataset.feature_count ?? "—"} |`);
  lines.push(`| Geometry type | ${dataset.geometry_type ?? "—"} |`);
  lines.push(`| CRS | ${dataset.crs ?? "—"} |`);
  lines.push(`| Bounds | ${formatBounds(dataset.bounds)} |`);
  lines.push("");

  if (validation_config) {
    lines.push(`## Validation configuration`);
    lines.push("");
    lines.push(`| Setting | Value |`);
    lines.push(`| --- | --- |`);
    lines.push(`| Pipeline | ${validation_config.pipeline_steps.join(" → ")} |`);
    lines.push(
      `| Geometry validation | ${validation_config.geometry_validation_enabled ? "enabled" : "disabled"} |`,
    );
    lines.push(`| Attribute sample size | ${validation_config.attribute_sample_size} |`);
    lines.push(
      `| Records in LLM prompt | ${validation_config.attribute_max_records_in_prompt} |`,
    );
    lines.push(`| LLM model | ${validation_config.openai_model} |`);
    const tc = validation_config.topology_checks;
    lines.push(
      `| Topology checks | gaps=${tc.gaps}, overlaps=${tc.overlaps}, connectivity=${tc.connectivity} |`,
    );
    lines.push("");
  }

  lines.push(`## Summary`);
  lines.push("");
  lines.push(`| Metric | Count |`);
  lines.push(`| --- | --- |`);
  lines.push(`| Total issues | ${summary.totalIssues} |`);
  lines.push(`| Critical | ${summary.critical} |`);
  lines.push(`| Warnings | ${summary.warning} |`);
  lines.push(`| Geometry | ${summary.byCategory.geometry} |`);
  lines.push(`| Attribute | ${summary.byCategory.attribute} |`);
  lines.push(`| Topology | ${summary.byCategory.topology} |`);
  lines.push("");

  const corrections = validation.corrections ?? [];
  lines.push(`## Corrections`);
  lines.push("");
  lines.push(`Suggested corrections: ${corrections.length}`);
  if (correction_decisions && Object.keys(correction_decisions).length > 0) {
    lines.push("");
    lines.push(`| Issue index | Decision | Custom override |`);
    lines.push(`| --- | --- | --- |`);
    for (const [idx, entry] of Object.entries(correction_decisions)) {
      lines.push(
        `| ${idx} | ${entry.decision} | ${entry.hasOverride ? "yes" : "no"} |`,
      );
    }
  }
  lines.push("");

  const issues = validation.issues;
  const shown = issues.slice(0, APPENDIX_ISSUE_LIMIT);
  lines.push(`## Issues (${shown.length}${issues.length > shown.length ? ` of ${issues.length}` : ""})`);
  lines.push("");
  lines.push(`| # | Type | Severity | Feature | Description |`);
  lines.push(`| --- | --- | --- | --- | --- |`);
  for (let i = 0; i < shown.length; i++) {
    const issue = shown[i];
    const fid =
      issue.feature_id !== undefined && issue.feature_id !== null
        ? String(issue.feature_id)
        : "—";
    const desc = (issue.description ?? "").replace(/\|/g, "\\|").slice(0, 120);
    lines.push(`| ${i} | ${issue.type} | ${issue.severity} | ${fid} | ${desc} |`);
  }
  if (issues.length > shown.length) {
    lines.push("");
    lines.push(`_…and ${issues.length - shown.length} more issues not listed._`);
  }

  return lines.join("\n");
}

export function downloadMarkdown(payload: QualityReportPayload, filenameBase: string): void {
  const name = `${safeFilename(filenameBase)}-report.md`;
  const blob = new Blob([renderReportMarkdown(payload)], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

export function printReport(): void {
  window.print();
}
