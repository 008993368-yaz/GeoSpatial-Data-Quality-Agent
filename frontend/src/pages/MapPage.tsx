import { MapViewer } from "../components/Map/MapViewer";
import { useApp } from "../context/AppContext";

export function MapPage() {
  const { currentDataset, validationIssues } = useApp();

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
        <MapViewer
          datasetId={currentDataset.dataset_id}
          bounds={currentDataset.bounds ?? null}
          layerTitle={currentDataset.filename}
          validationIssues={validationIssues}
        />
      )}
    </section>
  );
}
