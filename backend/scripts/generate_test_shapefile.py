"""
Generate a minimal shapefile in backend/resources/ for testing.

Run from backend directory:
    python scripts/generate_test_shapefile.py

Creates: resources/parks.shp, parks.shx, parks.dbf, parks.prj
"""
from pathlib import Path

try:
    import geopandas as gpd
    from shapely.geometry import Polygon
except ImportError as e:
    print("Requires geopandas and shapely. Install with: pip install geopandas")
    raise SystemExit(1) from e

RESOURCES = Path(__file__).resolve().parent.parent / "resources"
RESOURCES.mkdir(parents=True, exist_ok=True)
OUT_PATH = RESOURCES / "parks.shp"


def main():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["Park A", "Park B", "Park C"],
            "area_ha": [1.2, 0.8, 2.1],
        },
        geometry=[
            Polygon([(-122.43, 37.77), (-122.41, 37.77), (-122.41, 37.79), (-122.43, 37.79), (-122.43, 37.77)]),
            Polygon([(-122.42, 37.774), (-122.41, 37.774), (-122.41, 37.776), (-122.42, 37.776), (-122.42, 37.774)]),
            Polygon([(-122.44, 37.76), (-122.42, 37.76), (-122.42, 37.78), (-122.44, 37.78), (-122.44, 37.76)]),
        ],
        crs="EPSG:4326",
    )
    gdf.to_file(OUT_PATH)
    print(f"Wrote {OUT_PATH} and sidecars to {RESOURCES}")


if __name__ == "__main__":
    main()
