import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { QualityReport } from "../components/Report/QualityReport";
import { useApp } from "../context/AppContext";
import type { ValidationConfigResponse } from "../types/api";
import { buildQualityReportPayload } from "../utils/reportSummary";

export function ReportPage() {
  const {
    currentDataset,
    validationResult,
    correctionDecisions,
    correctionOverrides,
  } = useApp();
  const [validationConfig, setValidationConfig] = useState<ValidationConfigResponse | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/v1/validation/config");
        if (!res.ok) return;
        const data = (await res.json()) as ValidationConfigResponse;
        if (!cancelled) setValidationConfig(data);
      } catch {
        /* use defaults in buildQualityReportPayload */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const payload = useMemo(() => {
    if (!currentDataset || !validationResult) return null;
    return buildQualityReportPayload(currentDataset, validationResult, {
      correctionDecisions,
      correctionOverrides,
      validationConfig,
    });
  }, [
    currentDataset,
    validationResult,
    correctionDecisions,
    correctionOverrides,
    validationConfig,
  ]);

  return (
    <section className="page-section page-section--report" aria-labelledby="report-heading">
      <h2 id="report-heading" className="page-heading">
        Quality report
      </h2>
      {!currentDataset ? (
        <p className="empty-state">
          Upload a dataset on the <Link to="/upload">Upload</Link> page first.
        </p>
      ) : !validationResult ? (
        <p className="empty-state">
          Run validation on the <Link to="/dashboard">Dashboard</Link> to generate a report.
        </p>
      ) : payload ? (
        <QualityReport payload={payload} />
      ) : null}
    </section>
  );
}
