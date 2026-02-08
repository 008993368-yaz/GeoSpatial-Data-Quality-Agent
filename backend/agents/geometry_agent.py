"""Geometry validation agent: invalid geometries, self-intersections, empty/null."""
from pathlib import Path
from typing import List, Union

import geopandas as gpd

from core.validation import validate_geometries


def validate(path: Union[str, Path]) -> List[dict]:
    """
    Load a vector dataset from path and run geometry validation.
    Returns list of issues with feature_id, type, severity, location, description.
    """
    path = Path(path).resolve()
    if not path.exists():
        return []
    try:
        gdf = gpd.read_file(path)
    except Exception:
        return []
    return validate_geometries(gdf)


def validate_geodataframe(gdf: gpd.GeoDataFrame) -> List[dict]:
    """
    Run geometry validation on an in-memory GeoDataFrame.
    Returns list of issues with feature_id, type, severity, location, description.
    """
    return validate_geometries(gdf)
