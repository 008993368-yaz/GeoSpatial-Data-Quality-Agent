# Test / resource files

Sample geospatial files for manual testing and automated tests.

## Files

| File | Description |
|------|-------------|
| `sample.geojson` | Small GeoJSON: 2 points + 1 polygon (San Francisco area). Use for upload and GeoJSON parsing tests. |
| `parks.*` | Shapefile set (after generation): `parks.shp`, `.shx`, `.dbf`, `.prj`. Use for shapefile parser and zip-upload tests. |

## Generating the test shapefile

From the **project root** (or `backend/`), run:

```bash
cd backend
python scripts/generate_test_shapefile.py
```

This writes `resources/parks.shp` (and sidecars). To test zip upload, zip the contents of `resources/` (or just `parks.shp`, `parks.shx`, `parks.dbf`, `parks.prj`) and `POST` to `/api/v1/upload`.

## How to test #26 (Shapefile parser & metadata)

### 1. Start the backend

From project root:

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or with Docker: `docker compose up --build` (from project root).

### 2. Generate the test shapefile

In another terminal:

```bash
cd backend
python scripts/generate_test_shapefile.py
```

You should see `resources/parks.shp` (and .shx, .dbf, .prj).

### 3. Zip the shapefile

Zip **only** the shapefile set (so the .shp is at the root of the zip):

- **Windows (PowerShell):**  
  `Compress-Archive -Path resources\parks.shp, resources\parks.shx, resources\parks.dbf, resources\parks.prj -DestinationPath resources\parks.zip`
- **macOS/Linux:**  
  `cd backend/resources && zip parks.zip parks.shp parks.shx parks.dbf parks.prj`

### 4. Upload and check metadata

**PowerShell:**

```powershell
$zip = Get-Item "backend\resources\parks.zip"
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/upload" -Method Post -Form @{ file = $zip }
```

**curl:**

```bash
curl -X POST http://localhost:8000/api/v1/upload -F "file=@backend/resources/parks.zip"
```

**Expected response:** `200 OK` with JSON like:

```json
{
  "dataset_id": "some-uuid",
  "filename": "parks.zip",
  "feature_count": 3,
  "geometry_type": "Polygon",
  "crs": "EPSG:4326",
  "bounds": [-122.44, 37.76, -122.41, 37.79]
}
```

If `feature_count` is 3, `geometry_type` is `Polygon`, and `bounds` is set, the shapefile parser (#26) is working.

### 5. Optional: single .shp upload

Upload only `parks.shp` (no zip). The file is stored but metadata will be `feature_count: 0`, `geometry_type: null`, etc., because .shx/.dbf are required to read the shapefile. This confirms graceful fallback when sidecars are missing.

## How to test #27 (GeoJSON parser & metadata)

1. Start the backend (same as above).
2. Upload the sample GeoJSON:
   - **PowerShell:** `Invoke-RestMethod -Uri "http://localhost:8000/api/v1/upload" -Method Post -Form @{ file = Get-Item "backend\resources\sample.geojson" }`
   - **curl:** `curl -X POST http://localhost:8000/api/v1/upload -F "file=@backend/resources/sample.geojson"`
3. **Expected response:** `feature_count: 3`, `geometry_type` (e.g. `Point` or mixed), `bounds` set. Standard GeoJSON is WGS84, so `crs` may be `EPSG:4326` or similar.

---

## Usage in tests

Reference paths relative to the backend package, e.g.:

```python
from pathlib import Path
RESOURCES = Path(__file__).resolve().parent.parent / "resources"
sample_geojson = RESOURCES / "sample.geojson"
```
