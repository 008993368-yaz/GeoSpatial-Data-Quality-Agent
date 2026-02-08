"""GeoJSON parsing and metadata extraction using GeoPandas."""
from pathlib import Path
from typing import Optional

import geopandas as gpd


def parse_geojson_metadata(path: Path) -> Optional[dict]:
    """
    Parse a GeoJSON file and return metadata.

    Returns:
        Dict with keys: feature_count, geometry_type, crs, bounds.
        bounds is [minx, miny, maxx, maxy] or None.
        Returns None if path is not a file, read fails, or content is not valid GeoJSON.
    """
    path = Path(path).resolve()
    if not path.is_file():
        return None

    try:
        gdf = gpd.read_file(path)
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
