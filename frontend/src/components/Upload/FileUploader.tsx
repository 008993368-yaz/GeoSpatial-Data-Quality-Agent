import { useRef, useState, useCallback } from "react";
import { CalciteButton, CalciteAlert, CalciteIcon } from "@esri/calcite-components-react";
import { useApp } from "../../context/AppContext";

const ACCEPT = ".shp,.geojson,.json,.zip";
const ACCEPT_LIST = [".shp", ".geojson", ".json", ".zip"];

function hasAllowedExtension(name: string): boolean {
  const ext = name.slice(name.lastIndexOf(".")).toLowerCase();
  return ACCEPT_LIST.includes(ext);
}

export function FileUploader() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const { isUploading, error, currentDataset, handleUploadFile } = useApp();

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (!file) return;
      if (!hasAllowedExtension(file.name)) {
        return;
      }
      handleUploadFile(file);
    },
    [handleUploadFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const openFileDialog = () => {
    inputRef.current?.click();
  };

  return (
    <div className="file-uploader">
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleUploadFile(file);
          e.target.value = "";
        }}
        disabled={isUploading}
        className="visually-hidden"
        aria-label="Choose a file to upload"
      />
      <div
        className={`file-uploader-dropzone ${isDragOver ? "file-uploader-dropzone--active" : ""}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <CalciteIcon icon="upload" scale="l" />
        <p className="file-uploader-dropzone-text">
          Drag and drop a file here, or choose a file to upload.
        </p>
        <p className="file-uploader-dropzone-hint">Accepted: .shp, .geojson, .json, .zip</p>
        <CalciteButton
          kind="brand"
          onClick={openFileDialog}
          disabled={isUploading}
          label="Choose file"
        >
          Choose file
        </CalciteButton>
      </div>
      {isUploading && (
        <p className="status-message status-message--info" role="status">
          Uploading…
        </p>
      )}
      {currentDataset && (
        <CalciteAlert kind="success" open label="Upload successful">
          <div slot="title">Upload successful</div>
          <div slot="message">
            Loaded: <strong>{currentDataset.filename}</strong>
          </div>
        </CalciteAlert>
      )}
      {error && (
        <CalciteAlert kind="danger" open label="Upload error">
          <div slot="title">Upload error</div>
          <div slot="message">{error}</div>
        </CalciteAlert>
      )}
    </div>
  );
}
