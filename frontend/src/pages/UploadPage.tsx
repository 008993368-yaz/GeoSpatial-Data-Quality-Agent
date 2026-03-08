import { useApp } from "../context/AppContext";

export function UploadPage() {
  const { currentDataset, isUploading, error, handleFileChange } = useApp();

  return (
    <section className="page-section" aria-labelledby="upload-heading">
      <h2 id="upload-heading" className="page-heading">
        Upload dataset
      </h2>
      <label className="upload-label">
        <span className="upload-label-text">Choose a GeoJSON or JSON file</span>
        <input
          type="file"
          accept=".geojson,.json"
          onChange={handleFileChange}
          disabled={isUploading}
          aria-describedby={error ? "upload-error" : currentDataset ? "upload-success" : undefined}
          className="upload-input"
        />
      </label>
      {isUploading && (
        <p className="status-message status-message--info" role="status">
          Uploading…
        </p>
      )}
      {currentDataset && (
        <p id="upload-success" className="status-message status-message--success">
          Loaded: <strong>{currentDataset.filename}</strong>
        </p>
      )}
      {error && (
        <p id="upload-error" className="status-message status-message--error" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
