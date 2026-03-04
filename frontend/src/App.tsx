import { useState } from "react";
import { MapViewer } from "./components/Map/MapViewer";
import type { ValidationResult } from "./types/api";

type UploadResponse = {
  dataset_id: string;
  filename: string;
  bounds?: number[] | null;
};

function App() {
  const [currentDataset, setCurrentDataset] = useState<UploadResponse | null>(
    null
  );
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setError(null);
    setIsUploading(true);

    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch("/api/v1/upload", {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const detail =
          (typeof data.detail === "string"
            ? data.detail
            : data.detail?.detail) ?? res.statusText;
        throw new Error(detail);
      }

      const data = (await res.json()) as UploadResponse;
      setCurrentDataset(data);
      setValidationResult(null);
      setValidationError(null);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Upload failed";
      setError(msg);
    } finally {
      setIsUploading(false);
      // reset input so same file can be selected again if needed
      event.target.value = "";
    }
  }

  async function handleValidate() {
    if (!currentDataset?.dataset_id) return;
    setValidationError(null);
    setValidationResult(null);
    setIsValidating(true);
    try {
      const res = await fetch(`/api/v1/validate/${currentDataset.dataset_id}`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const detail =
          (typeof data.detail === "string"
            ? data.detail
            : data.detail?.detail) ?? res.statusText;
        throw new Error(detail);
      }
      const data = (await res.json()) as ValidationResult;
      setValidationResult(data);
    } catch (e) {
      setValidationError(
        e instanceof Error ? e.message : "Validation failed"
      );
    } finally {
      setIsValidating(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <header
        style={{
          padding: "0.75rem 1rem",
          borderBottom: "1px solid #e0e0e0",
          background: "#f5f5f5",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
        }}
      >
        <h1 style={{ margin: 0, fontSize: "1.25rem" }}>
          GeoSpatial Data Quality Agent
        </h1>
        <label style={{ fontSize: "0.9rem" }}>
          <span style={{ marginRight: "0.5rem" }}>Upload dataset (.geojson)</span>
          <input
            type="file"
            accept=".geojson,.json"
            onChange={handleFileChange}
            disabled={isUploading}
          />
        </label>
        <button
          type="button"
          onClick={handleValidate}
          disabled={!currentDataset || isUploading || isValidating}
          style={{
            padding: "0.35rem 0.75rem",
            fontSize: "0.85rem",
            borderRadius: "4px",
            border: "1px solid #1976d2",
            background: !currentDataset || isUploading
              ? "#e0e0e0"
              : "#1976d2",
            color: !currentDataset || isUploading ? "#777" : "#fff",
            cursor:
              !currentDataset || isUploading || isValidating
                ? "not-allowed"
                : "pointer",
          }}
        >
          {isValidating ? "Validating…" : "Validate geometry"}
        </button>
        {isUploading && (
          <span style={{ fontSize: "0.85rem", color: "#555" }}>Uploading…</span>
        )}
        {currentDataset && (
          <span style={{ fontSize: "0.85rem", color: "#333" }}>
            Showing: <strong>{currentDataset.filename}</strong>
          </span>
        )}
        {error && (
          <span style={{ fontSize: "0.85rem", color: "#b00020" }}>
            {error}
          </span>
        )}
        {validationError && (
          <span style={{ fontSize: "0.85rem", color: "#b00020" }}>
            Validation error: {validationError}
          </span>
        )}
      </header>
      <main style={{ flex: 1, minHeight: 0 }}>
        {validationResult && (
          <section
            aria-label="Validation summary"
            style={{
              padding: "0.5rem 1rem",
              borderBottom: "1px solid #eee",
              background: "#fafafa",
              fontSize: "0.9rem",
            }}
          >
            {validationResult.issues.length === 0 ? (
              <span style={{ color: "#2e7d32" }}>
                No geometry issues found for this dataset.
              </span>
            ) : (
              <span style={{ color: "#b00020" }}>
                Found {validationResult.issues.length} geometry issue
                {validationResult.issues.length > 1 ? "s" : ""}. See details in
                the API response or future UI.
              </span>
            )}
          </section>
        )}
        <MapViewer
          datasetId={currentDataset?.dataset_id}
          bounds={currentDataset?.bounds ?? null}
          layerTitle={currentDataset?.filename}
        />
      </main>
    </div>
  );
}

export default App;
