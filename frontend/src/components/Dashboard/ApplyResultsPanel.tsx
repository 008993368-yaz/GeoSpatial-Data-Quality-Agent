import { CalciteButton, CalciteNotice, CalcitePanel } from "@esri/calcite-components-react";

import type { ApplyCorrectionsResponse } from "../../types/api";
import { summarizeApplyResults } from "../../utils/applyResultsSummary";

export type ApplyResultsPanelProps = {
  result: ApplyCorrectionsResponse;
  onDismiss: () => void;
};

export function ApplyResultsPanel({ result, onDismiss }: ApplyResultsPanelProps) {
  const { applied, skipped, download_url: downloadUrl, export_note: exportNote } = result;
  const total = applied + skipped;

  return (
    <CalcitePanel className="apply-results-panel" heading="Correction apply results">
      <CalciteNotice open kind="success" icon scale="s" width="full" className="apply-results__success-notice">
        <div slot="title">Apply completed</div>
        <div slot="message">
          Your approve/reject choices were submitted successfully. Review the counts and download below if needed.
        </div>
      </CalciteNotice>
      <p className="apply-results__intro">
        Counts from the last successful request to apply your choices.
      </p>
      <div className="apply-results__counts" role="group" aria-label="Apply counts">
        <div className="apply-results__stat">
          <span className="apply-results__stat-label">Approved</span>
          <span className="apply-results__stat-value">{applied}</span>
        </div>
        <div className="apply-results__stat">
          <span className="apply-results__stat-label">Skipped</span>
          <span className="apply-results__stat-value">{skipped}</span>
        </div>
        <div className="apply-results__stat">
          <span className="apply-results__stat-label">Total</span>
          <span className="apply-results__stat-value">{total}</span>
        </div>
      </div>

      <p className="apply-results__summary">{summarizeApplyResults(applied, skipped)}</p>

      {exportNote ? <p className="apply-results__note">{exportNote}</p> : null}

      {downloadUrl ? (
        <div className="apply-results__download">
          <CalciteButton
            href={downloadUrl}
            rel="noopener noreferrer"
            target="_blank"
            download
            kind="brand"
            label="Download dataset file (opens in a new tab)"
          >
            Download dataset (GeoJSON)
          </CalciteButton>
          <p className="apply-results__download-hint">
            Opens the current layer file from the server. Use &quot;Save as&quot; in the browser if the file opens
            inline instead of downloading.
          </p>
        </div>
      ) : (
        <CalciteNotice open kind="warning" icon scale="s" width="full">
          <div slot="title">No download link</div>
          <div slot="message">
            The server did not return an export URL. A cleaned-dataset download may be added in a later release.
          </div>
        </CalciteNotice>
      )}

      <div className="apply-results__footer">
        <CalciteButton appearance="outline" kind="neutral" onClick={onDismiss}>
          Dismiss results
        </CalciteButton>
      </div>
    </CalcitePanel>
  );
}
