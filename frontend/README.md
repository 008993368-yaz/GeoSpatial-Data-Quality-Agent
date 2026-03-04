# Frontend — GeoSpatial Data Quality Agent

React + TypeScript + Vite app with ArcGIS MapView for map-based preview. The map supports zoom/pan (mouse + Zoom widget) and a layer visibility toggle for the uploaded dataset (Issue #32, #34).

## Setup

```bash
npm install
cp .env.example .env
# Edit .env and set VITE_ARCGIS_API_KEY (required for the map — see below)
```

**ArcGIS API key (required):** The map uses the [ArcGIS Maps SDK for JavaScript](https://developers.arcgis.com/) for basemaps and tiles. You must set `VITE_ARCGIS_API_KEY` in `.env`; get a free key at [https://developers.arcgis.com/](https://developers.arcgis.com/).

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
