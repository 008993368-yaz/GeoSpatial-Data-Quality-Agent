"""
Topology validation: gaps, overlaps, connectivity (issue #80).

Detects spatial relationship violations using GeoPandas/Shapely. Returns a list
of violation dicts (feature_id, type, severity, location, description) suitable
for conversion to GeometryIssue.

Assumptions:
- Geometries are in a projected or geographic CRS; operations use Shapely (planar).
- Gaps/overlaps: intended for polygon layers; invalid or empty geometries are skipped.
- Connectivity: intended for LineString layers; detects dangles (endpoints not touching another line).

Limitations:
- Large datasets: pair-wise overlap check is O(n^2); consider spatial index and tolerance.
- ArcGIS-specific rules are not implemented; can be added later via optional ArcGIS API.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union


# Topology issue type constants (prefix topology_ for consistency with attribute_*)
class TopologyIssueType:
    GAP = "topology_gap"
    OVERLAP = "topology_overlap"
    DANGLE = "topology_dangle"  # disconnected endpoint


class Severity:
    CRITICAL = "critical"
    WARNING = "warning"


def _location(geom: BaseGeometry) -> Optional[List[float]]:
    """Return [x, y] for map display, or None."""
    if geom is None or getattr(geom, "is_empty", True):
        return None
    try:
        pt = getattr(geom, "centroid", None) or getattr(geom, "representative_point", lambda: None)()
        if pt is not None and not getattr(pt, "is_empty", True):
            return [float(pt.x), float(pt.y)]
    except Exception:
        pass
    try:
        b = getattr(geom, "bounds", None)
        if b is not None and len(b) >= 4:
            return [float(b[0] + b[2]) / 2, float(b[1] + b[3]) / 2]
    except Exception:
        pass
    return None


def _get_feature_id(gdf: gpd.GeoDataFrame, idx: Any) -> Any:
    """Use 'id' column if present, else index (aligned with core.validation)."""
    if "id" in gdf.columns:
        try:
            return gdf.loc[idx, "id"]
        except Exception:
            pass
    return idx


def _valid_polygons(gdf: gpd.GeoDataFrame):
    """Yield (index, geometry) for valid non-empty polygon geometries."""
    for idx, geom in gdf.geometry.items():
        if geom is None or geom.is_empty:
            continue
        if not hasattr(geom, "exterior"):  # Polygon-like
            continue
        try:
            if geom.is_valid and not geom.is_empty:
                yield idx, geom
        except Exception:
            continue


def _detect_gaps(gdf: gpd.GeoDataFrame) -> List[Dict[str, Any]]:
    """
    Detect gaps (holes in polygon coverage) using unary_union.
    Each hole in the union is reported as a gap. feature_id is None (gap between features).
    """
    issues: List[Dict[str, Any]] = []
    geoms = [geom for _, geom in _valid_polygons(gdf)]
    if len(geoms) < 1:
        return issues
    try:
        union = unary_union(geoms)
        if union is None or union.is_empty:
            return issues
        # Collect interiors (holes) from the union
        if hasattr(union, "interiors"):
            for ring in union.interiors:
                try:
                    hole = Polygon(ring)
                    if not hole.is_empty:
                        loc = _location(hole)
                        issues.append({
                            "feature_id": None,
                            "other_feature_id": None,
                            "type": TopologyIssueType.GAP,
                            "severity": Severity.WARNING,
                            "location": loc,
                            "description": "Gap in polygon coverage",
                        })
                except Exception:
                    continue
        elif hasattr(union, "geoms"):
            for poly in union.geoms:
                if hasattr(poly, "interiors"):
                    for ring in poly.interiors:
                        try:
                            hole = Polygon(ring)
                            if not hole.is_empty:
                                loc = _location(hole)
                                issues.append({
                                    "feature_id": None,
                                    "other_feature_id": None,
                                    "type": TopologyIssueType.GAP,
                                    "severity": Severity.WARNING,
                                    "location": loc,
                                    "description": "Gap in polygon coverage",
                                })
                        except Exception:
                            continue
    except Exception:
        pass
    return issues


def _detect_overlaps(
    gdf: gpd.GeoDataFrame,
    tolerance: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Detect overlapping polygon pairs. Reports one issue per pair (feature_id, other_feature_id).
    """
    issues: List[Dict[str, Any]] = []
    indices = list(gdf.index)
    geoms = gdf.geometry
    for i in range(len(indices)):
        idx_i = indices[i]
        geom_i = geoms.loc[idx_i] if hasattr(geoms, "loc") else geoms.iloc[i]
        if geom_i is None or geom_i.is_empty or not hasattr(geom_i, "exterior"):
            continue
        if not getattr(geom_i, "is_valid", True):
            continue
        for j in range(i + 1, len(indices)):
            idx_j = indices[j]
            geom_j = geoms.loc[idx_j] if hasattr(geoms, "loc") else geoms.iloc[j]
            if geom_j is None or geom_j.is_empty or not hasattr(geom_j, "exterior"):
                continue
            if not getattr(geom_j, "is_valid", True):
                continue
            try:
                inter = geom_i.intersection(geom_j)
                if inter.is_empty:
                    continue
                area = getattr(inter, "area", None)
                if area is None:
                    area = 0.0
                if area <= tolerance:
                    continue
                loc = _location(inter)
                fid_i = _get_feature_id(gdf, idx_i)
                fid_j = _get_feature_id(gdf, idx_j)
                issues.append({
                    "feature_id": fid_i,
                    "other_feature_id": fid_j,
                    "type": TopologyIssueType.OVERLAP,
                    "severity": Severity.WARNING,
                    "location": loc,
                    "description": f"Overlap with feature {fid_j}",
                })
            except Exception:
                continue
    return issues


def _line_endpoints(geom: BaseGeometry) -> List[Point]:
    """Return list of (start, end) or flattened points for LineString/MultiLineString."""
    points: List[Point] = []
    if geom is None or geom.is_empty:
        return points
    if isinstance(geom, LineString):
        if len(geom.coords) >= 2:
            points.append(Point(geom.coords[0]))
            points.append(Point(geom.coords[-1]))
        return points
    if hasattr(geom, "geoms"):
        for g in geom.geoms:
            points.extend(_line_endpoints(g))
        return points
    return points


def _point_touches_line(pt: Point, line_geom: BaseGeometry, tolerance: float) -> bool:
    """True if pt is within tolerance of line (boundary or interior)."""
    if line_geom is None or line_geom.is_empty:
        return False
    try:
        dist = line_geom.distance(pt)
        return dist <= tolerance
    except Exception:
        return False


def _detect_dangles(gdf: gpd.GeoDataFrame, tolerance: float = 1e-9) -> List[Dict[str, Any]]:
    """
    Detect dangles: line endpoints that do not touch any other line (disconnected).
    Intended for LineString/MultiLineString layers.
    """
    issues: List[Dict[str, Any]] = []
    indices = list(gdf.index)
    geoms = gdf.geometry
    for i in range(len(indices)):
        idx = indices[i]
        geom = geoms.loc[idx] if hasattr(geoms, "loc") else geoms.iloc[i]
        if geom is None or geom.is_empty:
            continue
        endpoints = _line_endpoints(geom)
        for pt in endpoints:
            if pt is None or pt.is_empty:
                continue
            touches_other = False
            for j in range(len(indices)):
                if j == i:
                    continue
                other = geoms.loc[indices[j]] if hasattr(geoms, "loc") else geoms.iloc[j]
                if _point_touches_line(pt, other, tolerance):
                    touches_other = True
                    break
            if not touches_other:
                loc = _location(pt)
                fid = _get_feature_id(gdf, idx)
                issues.append({
                    "feature_id": fid,
                    "other_feature_id": None,
                    "type": TopologyIssueType.DANGLE,
                    "severity": Severity.WARNING,
                    "location": loc,
                    "description": "Disconnected line endpoint (dangle)",
                })
    return issues


def validate_topology(
    gdf: gpd.GeoDataFrame,
    *,
    check_gaps: bool = True,
    check_overlaps: bool = True,
    check_connectivity: bool = True,
    tolerance: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Run topology validation on a GeoDataFrame (issue #80).

    Args:
        gdf: GeoDataFrame with a geometry column.
        check_gaps: Report gaps (holes in polygon coverage).
        check_overlaps: Report overlapping polygon pairs.
        check_connectivity: Report dangles (disconnected line endpoints).
        tolerance: Minimum area for overlap; distance for endpoint touch (default 0).

    Returns:
        List of violation dicts with keys: feature_id, other_feature_id (optional),
        type (topology_gap, topology_overlap, topology_dangle), severity, location, description.
    """
    if gdf is None or gdf.empty or gdf.geometry is None:
        return []
    issues: List[Dict[str, Any]] = []
    # Polygon-based checks
    if check_gaps or check_overlaps:
        if check_gaps:
            issues.extend(_detect_gaps(gdf))
        if check_overlaps:
            issues.extend(_detect_overlaps(gdf, tolerance=tolerance))
    # Line-based check
    if check_connectivity:
        issues.extend(_detect_dangles(gdf, tolerance=tolerance if tolerance > 0 else 1e-9))
    return issues
