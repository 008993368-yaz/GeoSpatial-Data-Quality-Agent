# Frontend — GeoSpatial Data Quality Agent

React + TypeScript + Vite app with ArcGIS MapView for map-based preview (Issue #32).

## Setup

```bash
npm install
cp .env.example .env
# Edit .env and set VITE_ARCGIS_API_KEY (get one at https://developers.arcgis.com/)
```

## Configurable map (env)

- `VITE_MAP_CENTER_LAT` — Initial map center latitude (default `37.7749`)
- `VITE_MAP_CENTER_LNG` — Initial map center longitude (default `-122.4194`)
- `VITE_MAP_ZOOM_LEVEL` — Initial zoom level (default `10`)

## Run

```bash
npm run dev
```

Open http://localhost:5173. The map container is in the main layout; backend API is proxied at `/api`.

## Build

```bash
npm run build
```

Output in `dist/`.
