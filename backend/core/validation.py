"""Core geometry validation logic using Shapely."""
from typing import Any, List, Optional

import geopandas as gpd
from shapely import is_valid
from shapely.geometry.base import BaseGeometry

try:
    from shapely import is_valid_reason
except ImportError:
    from shapely.validation import explain_validity as _explain

    def is_valid_reason(geom):
        return str(_explain(geom)) if geom is not None else "Null geometry"


# Issue type and severity constants
class IssueType:
    """Geometry issue types."""

    EMPTY_GEOMETRY = "empty_geometry"
    INVALID_GEOMETRY = "invalid_geometry"
    SELF_INTERSECTION = "self_intersection"


class Severity:
    """Issue severity levels."""

    CRITICAL = "critical"
    WARNING = "warning"


def _get_location(geom: BaseGeometry) -> Optional[List[float]]:
    """Return [x, y] for map display, or None if not available."""
    if geom is None or geom.is_empty:
        return None
    try:
        pt = geom.centroid if hasattr(geom, "centroid") else geom.representative_point()
        if pt and not pt.is_empty:
            return [float(pt.x), float(pt.y)]
    except Exception:
        pass
    try:
        b = geom.bounds
        if b is not None and len(b) >= 4:
            return [float(b[0] + b[2]) / 2, float(b[1] + b[3]) / 2]
    except Exception:
        pass
    return None


def _check_geometry(geom: Any, feature_id: Any) -> List[dict]:
    """
    Check a single geometry and return a list of issue dicts.
    Each dict has: feature_id, type, severity, location, description.
    """
    issues: List[dict] = []
    if geom is None:
        issues.append({
            "feature_id": feature_id,
            "type": IssueType.EMPTY_GEOMETRY,
            "severity": Severity.CRITICAL,
            "location": None,
            "description": "Null geometry",
        })
        return issues

    if geom.is_empty:
        issues.append({
            "feature_id": feature_id,
            "type": IssueType.EMPTY_GEOMETRY,
            "severity": Severity.CRITICAL,
            "location": None,
            "description": "Empty geometry",
        })
        return issues

    if not is_valid(geom):
        try:
            reason = str(is_valid_reason(geom))
        except Exception:
            reason = "Invalid geometry"
        issue_type = IssueType.SELF_INTERSECTION if "self-intersection" in reason.lower() or "self intersection" in reason.lower() else IssueType.INVALID_GEOMETRY
        issues.append({
            "feature_id": feature_id,
            "type": issue_type,
            "severity": Severity.CRITICAL,
            "location": _get_location(geom),
            "description": reason or "Invalid geometry",
        })

    return issues


def validate_geometries(gdf: gpd.GeoDataFrame) -> List[dict]:
    """
    Run geometry validation on a GeoDataFrame.
    Returns a list of issue dicts with feature_id, type, severity, location, description.
    Uses the GeoDataFrame index as feature_id unless an 'id' column exists.
    """
    if gdf is None or gdf.empty or gdf.geometry is None:
        return []

    issues: List[dict] = []
    for idx, geom in gdf.geometry.items():
        try:
            feature_id = gdf.loc[idx, "id"] if "id" in gdf.columns else idx
        except Exception:
            feature_id = idx
        feature_id = int(feature_id) if isinstance(feature_id, (int, float)) and not isinstance(feature_id, bool) else str(feature_id)
        issues.extend(_check_geometry(geom, feature_id))
    return issues
