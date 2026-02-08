"""Shapefile parsing and metadata extraction using GeoPandas."""
from pathlib import Path
from typing import Optional

import geopandas as gpd


def parse_shapefile_metadata(directory: Path) -> Optional[dict]:
    """
    Parse a shapefile in the given directory and return metadata.

    Expects at least one .shp file in the directory, with .shx and .dbf
    sidecar files in the same folder (standard shapefile requirement).

    Returns:
        Dict with keys: feature_count, geometry_type, crs, bounds.
        bounds is [minx, miny, maxx, maxy] or None.
        Returns None if no .shp found or read fails (e.g. missing sidecars).
    """
    directory = Path(directory).resolve()
    if not directory.is_dir():
        return None

    shp_files = list(directory.glob("*.shp"))
    if not shp_files:
        return None

    shp_path = shp_files[0]
    try:
        gdf = gpd.read_file(shp_path)
    except Exception:
        return None

    feature_count = len(gdf)
    if gdf.empty or gdf.geometry is None:
        return {
            "feature_count": 0,
            "geometry_type": None,
            "crs": _crs_to_string(gdf.crs) if gdf.crs is not None else None,
            "bounds": None,
        }

    geom_types = gdf.geometry.geom_type.dropna().unique()
    geometry_type = geom_types[0] if len(geom_types) == 1 else ",".join(sorted(geom_types))
    crs = _crs_to_string(gdf.crs)
    try:
        tb = gdf.total_bounds
        bounds = tb.tolist() if tb is not None and len(tb) == 4 else None
    except Exception:
        bounds = None

    return {
        "feature_count": feature_count,
        "geometry_type": geometry_type,
        "crs": crs,
        "bounds": bounds,
    }


def _crs_to_string(crs) -> Optional[str]:
    """Convert a pyproj/CRS object to a string (e.g. EPSG:4326)."""
    if crs is None:
        return None
    try:
        return crs.to_string() if hasattr(crs, "to_string") else str(crs)
    except Exception:
        return str(crs)
