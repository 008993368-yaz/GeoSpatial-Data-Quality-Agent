import { CalciteBlock, CalciteButton } from "@esri/calcite-components-react";
import { MapViewer } from "../components/Map/MapViewer";
import { useApp } from "../context/AppContext";

export function MapPage() {
  const {
    currentDataset,
    validationIssues,
    validationResult,
    isValidating,
    validationError,
    handleValidate,
  } = useApp();

  return (
    <section className="page-section page-section--map" aria-labelledby="map-heading">
      <h2 id="map-heading" className="visually-hidden">
        Map view
      </h2>
      {!currentDataset ? (
        <p className="empty-state">
          Upload a dataset on the <strong>Upload</strong> tab to view it on the map.
        </p>
      ) : (
        <>
          <CalciteBlock
            heading="Validate dataset"
            className="map-validate-block"
            expanded={false}
            collapsible
          >
            <p className="page-section-description">
              Run geometry validation and see issues on the map. Click a red marker to see details.
            </p>
            <CalciteButton
              kind="brand"
              onClick={handleValidate}
              disabled={isValidating}
              loading={isValidating}
              label={isValidating ? "Validating…" : "Validate dataset"}
            >
              {isValidating ? "Validating…" : "Validate dataset"}
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
                  : `Found ${validationResult.issues.length} issue${validationResult.issues.length !== 1 ? "s" : ""}. Click markers on the map for details.`}
              </p>
            )}
          </CalciteBlock>
          <MapViewer
            datasetId={currentDataset.dataset_id}
            bounds={currentDataset.bounds ?? null}
            layerTitle={currentDataset.filename}
            validationIssues={validationIssues}
          />
        </>
      )}
    </section>
  );
}
