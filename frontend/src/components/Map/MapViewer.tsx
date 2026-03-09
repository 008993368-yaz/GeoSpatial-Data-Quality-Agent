import { useEffect, useRef, useState } from "react";
import esriConfig from "@arcgis/core/config.js";
import Map from "@arcgis/core/Map.js";
import MapView from "@arcgis/core/views/MapView.js";
import GeoJSONLayer from "@arcgis/core/layers/GeoJSONLayer.js";
import GraphicsLayer from "@arcgis/core/layers/GraphicsLayer.js";
import Graphic from "@arcgis/core/Graphic.js";
import Point from "@arcgis/core/geometry/Point.js";
import SimpleMarkerSymbol from "@arcgis/core/symbols/SimpleMarkerSymbol.js";
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
const ISSUES_LAYER_ID = "validation-issues-layer";
const WKID_WGS84 = 4326;

function escapeHtml(s: string): string {
  const el = document.createElement("div");
  el.textContent = s;
  return el.innerHTML;
}

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
  const issuesLayerRef = useRef<GraphicsLayer | null>(null);
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

    view.on("click", async (event) => {
      const hit = await view.hitTest(event);
      const issuesLayer = issuesLayerRef.current;
      if (!issuesLayer) return;
      let graphic: __esri.Graphic | null = null;
      for (const r of hit.results) {
        const g = (r as { graphic?: __esri.Graphic }).graphic;
        if (g && g.layer === issuesLayer) {
          graphic = g;
          break;
        }
      }
      if (!graphic?.attributes) return;
      const { type, severity, description } = graphic.attributes as {
        type?: string;
        severity?: string;
        description?: string;
      };
      const safeType = escapeHtml(String(type ?? ""));
      const safeSeverity = escapeHtml(String(severity ?? ""));
      const safeDesc = escapeHtml(String(description ?? ""));
      view.popup.open({
        location: graphic.geometry as __esri.Point,
        title: "Validation issue",
        content: `<p><strong>Type:</strong> ${safeType}</p><p><strong>Severity:</strong> ${safeSeverity}</p><p><strong>Description:</strong> ${safeDesc || "—"}</p>`,
      });
    });

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
      if (issuesLayerRef.current) {
        issuesLayerRef.current.destroy();
        issuesLayerRef.current = null;
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

  // Graphics layer: show validation issue locations as points (Option B for #53)
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Remove existing issues layer
    if (issuesLayerRef.current) {
      map.remove(issuesLayerRef.current);
      issuesLayerRef.current.destroy();
      issuesLayerRef.current = null;
    }

    const issues = validationIssues ?? [];
    const withLocation = issues.filter(
      (i): i is GeometryIssue & { location: number[] } =>
        Array.isArray(i.location) && i.location.length >= 2
    );
    if (withLocation.length === 0) return;

    const symbol = new SimpleMarkerSymbol({
      color: [220, 53, 69, 0.9],
      outline: { color: [180, 40, 50], width: 1.5 },
      size: 12,
    });

    const graphics = withLocation.map(
      (issue) =>
        new Graphic({
          geometry: new Point({
            longitude: issue.location[0],
            latitude: issue.location[1],
            spatialReference: { wkid: WKID_WGS84 },
          }),
          symbol,
          attributes: {
            feature_id: issue.feature_id,
            type: issue.type,
            severity: issue.severity,
            description: issue.description ?? "",
          },
        })
    );

    const issuesLayer = new GraphicsLayer({
      id: ISSUES_LAYER_ID,
      title: "Validation issues",
      listMode: "show",
    });
    issuesLayer.addMany(graphics);
    map.add(issuesLayer);
    issuesLayerRef.current = issuesLayer;
  }, [validationIssues]);

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
