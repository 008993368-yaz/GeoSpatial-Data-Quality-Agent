import { useEffect, useRef, useState } from "react";
import esriConfig from "@arcgis/core/config.js";
import Map from "@arcgis/core/Map.js";
import MapView from "@arcgis/core/views/MapView.js";
import GeoJSONLayer from "@arcgis/core/layers/GeoJSONLayer.js";
import Extent from "@arcgis/core/geometry/Extent.js";
import Zoom from "@arcgis/core/widgets/Zoom.js";

import type { GeometryIssue } from "../../types/api";
import { defaultCenter, defaultZoom } from "../../services/mapService";

/* ArcGIS theme loaded via <link> in index.html to avoid loading CSS as module (MIME type error) */

const apiKey = import.meta.env.VITE_ARCGIS_API_KEY;
if (apiKey) {
  esriConfig.apiKey = apiKey;
}

const DATASET_LAYER_ID = "dataset-layer";

export type MapViewerProps = {
  datasetId?: string;
  bounds?: number[] | null;
  /** Optional title for the dataset layer (e.g. filename) for the layer list. */
  layerTitle?: string;
  /** Validation issues for the current dataset (for highlight/symbolize in #53). */
  validationIssues?: GeometryIssue[];
};

export function MapViewer({ datasetId, bounds, layerTitle, validationIssues }: MapViewerProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const viewRef = useRef<MapView | null>(null);
  const layerRef = useRef<GeoJSONLayer | null>(null);
  const [datasetLayerVisible, setDatasetLayerVisible] = useState(true);

  // Initialize map and view once (zoom/pan enabled by default on MapView)
  useEffect(() => {
    if (!containerRef.current) return;

    const map = new Map({
      basemap: "streets-vector",
    });
    mapRef.current = map;

    const view = new MapView({
      container: containerRef.current,
      map,
      center: [defaultCenter.longitude, defaultCenter.latitude],
      zoom: defaultZoom,
    });
    viewRef.current = view;

    const zoom = new Zoom({ view, layout: "vertical" });
    view.ui.add(zoom, "top-right");

    return () => {
      if (viewRef.current) {
        viewRef.current.destroy();
        viewRef.current = null;
      }
      mapRef.current = null;
      if (layerRef.current) {
        layerRef.current.destroy();
        layerRef.current = null;
      }
    };
  }, []);

  // Load dataset layer and fit view when datasetId/bounds change
  useEffect(() => {
    if (!datasetId || !mapRef.current || !viewRef.current) {
      return;
    }

    const map = mapRef.current;
    const view = viewRef.current;

    // Remove previous layer if any
    if (layerRef.current) {
      map.remove(layerRef.current);
      layerRef.current.destroy();
      layerRef.current = null;
    }

    const url = `/api/v1/datasets/${datasetId}/geojson`;
    const layer = new GeoJSONLayer({
      url,
      id: DATASET_LAYER_ID,
      title: layerTitle || "Dataset",
    });
    layer.visible = true;
    setDatasetLayerVisible(true);
    map.add(layer);
    layerRef.current = layer;

    // Fit view to bounds from upload response when available
    if (bounds && bounds.length === 4) {
      const [minX, minY, maxX, maxY] = bounds;
      const extent = new Extent({
        xmin: minX,
        ymin: minY,
        xmax: maxX,
        ymax: maxY,
        spatialReference: { wkid: 4326 },
      });
      view.goTo(extent).catch(() => {
        // ignore goTo errors (e.g. view destroyed)
      });
    } else {
      // Fallback: zoom to layer's full extent when it loads
      layer.when(() => {
        if (layer.fullExtent) {
          view.goTo(layer.fullExtent).catch(() => undefined);
        }
      });
    }
  }, [datasetId, bounds?.join(","), layerTitle]);

  // Sync visibility toggle to layer when layer exists
  useEffect(() => {
    if (layerRef.current) {
      layerRef.current.visible = datasetLayerVisible;
    }
  }, [datasetLayerVisible]);

  const handleLayerVisibilityChange = () => {
    setDatasetLayerVisible((v) => !v);
  };

  return (
    <div className="map-viewer-wrapper" style={{ position: "relative", width: "100%", height: "100%", minHeight: 400 }}>
      {datasetId && (
        <div
          className="map-layer-list"
          style={{
            position: "absolute",
            top: 8,
            left: 8,
            zIndex: 1,
            background: "rgba(255,255,255,0.95)",
            padding: "8px 12px",
            borderRadius: 6,
            boxShadow: "0 1px 4px rgba(0,0,0,0.2)",
            fontSize: "0.875rem",
          }}
          role="group"
          aria-label="Layers"
        >
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Layers</div>
          <label style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={datasetLayerVisible}
              onChange={handleLayerVisibilityChange}
              aria-label="Toggle dataset layer visibility"
            />
            <span>{layerTitle || "Dataset"}</span>
          </label>
        </div>
      )}
      <div
        ref={containerRef}
        className="map-viewer"
        style={{ width: "100%", height: "100%", minHeight: 400 }}
        aria-label="Map view"
      />
    </div>
  );
}
