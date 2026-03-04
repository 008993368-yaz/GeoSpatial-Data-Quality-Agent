import { useEffect, useRef } from "react";
import esriConfig from "@arcgis/core/config.js";
import Map from "@arcgis/core/Map.js";
import MapView from "@arcgis/core/views/MapView.js";
import { defaultCenter, defaultZoom } from "../../services/mapService";

import "@arcgis/core/assets/esri/themes/light/main.css";

const apiKey = import.meta.env.VITE_ARCGIS_API_KEY;
if (apiKey) {
  esriConfig.apiKey = apiKey;
}

export function MapViewer() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new Map({
      basemap: "streets-vector",
    });

    const view = new MapView({
      container: containerRef.current,
      map,
      center: [defaultCenter.longitude, defaultCenter.latitude],
      zoom: defaultZoom,
    });

    return () => {
      view.destroy();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="map-viewer"
      style={{ width: "100%", height: "100%", minHeight: 400 }}
      aria-label="Map view"
    />
  );
}
