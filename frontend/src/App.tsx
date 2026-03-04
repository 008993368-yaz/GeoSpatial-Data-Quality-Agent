import { useState } from "react";
import { MapViewer } from "./components/Map/MapViewer";

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
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Upload failed";
      setError(msg);
    } finally {
      setIsUploading(false);
      // reset input so same file can be selected again if needed
      event.target.value = "";
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
      </header>
      <main style={{ flex: 1, minHeight: 0 }}>
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
