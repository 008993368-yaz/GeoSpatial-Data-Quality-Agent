/**
 * Map configuration and utilities for ArcGIS MapView.
 * Center and zoom are read from env (VITE_MAP_CENTER_LAT, VITE_MAP_CENTER_LNG, VITE_MAP_ZOOM_LEVEL).
 */

const lat = Number(import.meta.env.VITE_MAP_CENTER_LAT);
const lng = Number(import.meta.env.VITE_MAP_CENTER_LNG);
const zoom = Number(import.meta.env.VITE_MAP_ZOOM_LEVEL);

export const defaultCenter = {
  latitude: Number.isFinite(lat) ? lat : 37.7749,
  longitude: Number.isFinite(lng) ? lng : -122.4194,
};

export const defaultZoom = Number.isFinite(zoom) && zoom >= 0 ? zoom : 10;
