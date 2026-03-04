import { useEffect, useRef } from "react";
import esriConfig from "@arcgis/core/config.js";
import Map from "@arcgis/core/Map.js";
import MapView from "@arcgis/core/views/MapView.js";
import GeoJSONLayer from "@arcgis/core/layers/GeoJSONLayer.js";
import Extent from "@arcgis/core/geometry/Extent.js";

import { defaultCenter, defaultZoom } from "../../services/mapService";

import "@arcgis/core/assets/esri/themes/light/main.css";

const apiKey = import.meta.env.VITE_ARCGIS_API_KEY;
if (apiKey) {
  esriConfig.apiKey = apiKey;
}

export type MapViewerProps = {
  datasetId?: string;
  bounds?: number[] | null;
};

export function MapViewer({ datasetId, bounds }: MapViewerProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const viewRef = useRef<MapView | null>(null);
  const layerRef = useRef<GeoJSONLayer | null>(null);

  // Initialize map and view once
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
    const layer = new GeoJSONLayer({ url });
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
  }, [datasetId, bounds?.join(",")]);

  return (
    <div
      ref={containerRef}
      className="map-viewer"
      style={{ width: "100%", height: "100%", minHeight: 400 }}
      aria-label="Map view"
    />
  );
}
