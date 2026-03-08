import { CalciteBlock, CalciteButton } from "@esri/calcite-components-react";
import { FileUploader } from "../components/Upload/FileUploader";
import { useApp } from "../context/AppContext";

export function UploadPage() {
  const {
    currentDataset,
    validationResult,
    isValidating,
    validationError,
    handleValidate,
  } = useApp();

  return (
    <section className="page-section" aria-labelledby="upload-heading">
      <CalciteBlock heading="Upload dataset" id="upload-heading" expanded collapsible={false}>
        <p className="page-section-description">
          Upload a shapefile or GeoJSON to validate and view on the map.
        </p>
        <FileUploader />
      </CalciteBlock>
      {currentDataset && (
        <CalciteBlock
          heading="Run validation"
          className="upload-validate-block"
          expanded
          collapsible={false}
        >
          <p className="page-section-description">
            Run geometry validation on the current dataset. Results are stored for the map.
          </p>
          <CalciteButton
            kind="brand"
            onClick={handleValidate}
            disabled={isValidating}
            loading={isValidating}
            label={isValidating ? "Validating…" : "Validate geometry"}
          >
            {isValidating ? "Validating…" : "Validate geometry"}
          </CalciteButton>
          {validationError && (
            <p className="status-message status-message--error" role="alert">
              {validationError}
            </p>
          )}
          {validationResult && (
            <p className="status-message validation-summary-inline" role="status">
              {validationResult.issues.length === 0
                ? "No geometry issues found."
                : `Found ${validationResult.issues.length} issue${validationResult.issues.length !== 1 ? "s" : ""}.`}
            </p>
          )}
        </CalciteBlock>
      )}
    </section>
  );
}
