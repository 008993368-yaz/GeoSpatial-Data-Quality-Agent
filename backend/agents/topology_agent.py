"""
Topology validation agent: gaps, overlaps, connectivity (issue #81).

Loads the dataset from state, runs core.topology.validate_topology, and appends
topology issues to state["issues"] as GeometryIssue (type=topology_gap, topology_overlap,
topology_dangle). Same pattern as attribute_agent (#73).
"""
from typing import Any, Dict, List, Optional

import geopandas as gpd

from api.models import GeometryIssue
from agents.state import ValidationState
from core.topology import validate_topology


def _violation_to_geometry_issue(v: Dict[str, Any]) -> GeometryIssue:
    """Map a topology violation dict to GeometryIssue for state["issues"]."""
    return GeometryIssue(
        feature_id=v.get("feature_id"),
        type=v.get("type", "topology_other"),
        severity=v.get("severity") or "warning",
        location=v.get("location"),
        description=v.get("description") or None,
    )


def run(
    state: ValidationState,
    *,
    check_gaps: bool = True,
    check_overlaps: bool = True,
    check_connectivity: bool = True,
    tolerance: float = 0.0,
) -> dict:
    """
    Run topology validation on the dataset in state (issue #81).

    - Loads the dataset from state["dataset_path"] with GeoPandas.
    - Calls core.topology.validate_topology to get violations (gaps, overlaps, dangles).
    - Converts violations to GeometryIssue and appends to state["issues"].

    Deterministic and side-effect free apart from the returned state update.

    Args:
        state: Current validation state (dataset_path, issues, ...).
        check_gaps: Enable gap detection (holes in polygon coverage).
        check_overlaps: Enable overlap detection.
        check_connectivity: Enable dangle detection (disconnected line endpoints).
        tolerance: Passed to validate_topology (overlap area / endpoint distance).

    Returns:
        Partial state update: {"issues": existing_issues + new_topology_issues}.
    """
    existing = list(state.get("issues") or [])
    path = state.get("dataset_path")
    if not path:
        return {"issues": existing}

    try:
        gdf = gpd.read_file(path)
    except Exception:
        return {"issues": existing}

    if gdf is None or gdf.empty:
        return {"issues": existing}

    raw: List[Dict[str, Any]] = validate_topology(
        gdf,
        check_gaps=check_gaps,
        check_overlaps=check_overlaps,
        check_connectivity=check_connectivity,
        tolerance=tolerance,
    )
    new_issues = [_violation_to_geometry_issue(v) for v in raw]
    return {"issues": existing + new_issues}
