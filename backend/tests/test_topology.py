"""Tests for core.topology (issue #80)."""
import geopandas as gpd
import pytest
from shapely.geometry import LineString, Point, Polygon

from core.topology import (
    TopologyIssueType,
    Severity,
    validate_topology,
)


def test_validate_topology_empty_gdf():
    """Empty GeoDataFrame returns no issues."""
    gdf = gpd.GeoDataFrame(geometry=[])
    assert validate_topology(gdf) == []


def test_validate_topology_gap_hole_in_union():
    """A polygon with an interior ring (hole) produces a gap issue."""
    # One polygon with a hole: outer square, inner square as hole
    outer = [(0, 0), (3, 0), (3, 3), (0, 3), (0, 0)]
    hole = [(1, 1), (2, 1), (2, 2), (1, 2), (1, 1)]
    poly_with_hole = Polygon(outer, [hole])
    gdf = gpd.GeoDataFrame(geometry=[poly_with_hole], index=[5])
    issues = validate_topology(gdf, check_overlaps=False, check_connectivity=False)
    gaps = [i for i in issues if i["type"] == TopologyIssueType.GAP]
    assert len(gaps) >= 1
    assert gaps[0]["feature_id"] is None
    assert gaps[0]["location"] is not None
    assert "Gap" in (gaps[0]["description"] or "")


def test_validate_topology_overlap_two_polygons():
    """Two overlapping polygons produce one overlap issue."""
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]),
            Polygon([(1, 1), (3, 1), (3, 3), (1, 3), (1, 1)]),
        ],
        index=[10, 20],
    )
    issues = validate_topology(gdf, check_gaps=False, check_connectivity=False)
    assert len(issues) >= 1
    overlap = next((i for i in issues if i["type"] == TopologyIssueType.OVERLAP), None)
    assert overlap is not None
    assert overlap["feature_id"] == 10
    assert overlap["other_feature_id"] == 20
    assert overlap["severity"] == Severity.WARNING
    assert overlap["location"] is not None
    assert "Overlap" in (overlap["description"] or "")


def test_validate_topology_no_overlap_when_touching():
    """Two polygons that only touch (no area overlap) produce no overlap issue."""
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1), (1, 0)]),
        ],
    )
    issues = validate_topology(gdf, check_gaps=False, check_connectivity=False)
    overlaps = [i for i in issues if i["type"] == TopologyIssueType.OVERLAP]
    assert len(overlaps) == 0


def test_validate_topology_dangle_line():
    """A line whose endpoint does not touch another line produces a dangle issue."""
    gdf = gpd.GeoDataFrame(
        geometry=[
            LineString([(0, 0), (1, 0)]),
            LineString([(2, 0), (3, 0)]),  # disconnected
        ],
        index=[1, 2],
    )
    issues = validate_topology(gdf, check_gaps=False, check_overlaps=False)
    dangles = [i for i in issues if i["type"] == TopologyIssueType.DANGLE]
    assert len(dangles) >= 1
    assert any(d["feature_id"] in (1, 2) for d in dangles)
    assert any(d["location"] is not None for d in dangles)


def test_validate_topology_connected_lines_shared_endpoint_not_dangle():
    """Two lines that meet at (1,0) produce dangles only at the two open ends (0,0) and (1,1)."""
    gdf = gpd.GeoDataFrame(
        geometry=[
            LineString([(0, 0), (1, 0)]),
            LineString([(1, 0), (1, 1)]),
        ],
    )
    issues = validate_topology(gdf, check_gaps=False, check_overlaps=False)
    dangles = [i for i in issues if i["type"] == TopologyIssueType.DANGLE]
    # Open ends at (0,0) and (1,1) are dangles; shared vertex (1,0) is not
    assert len(dangles) == 2


def test_validate_topology_respects_check_flags():
    """Disabling a check skips that detection."""
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]),
            Polygon([(1, 1), (3, 1), (3, 3), (1, 3), (1, 1)]),
        ],
    )
    issues_all = validate_topology(gdf, check_overlaps=True, check_gaps=False, check_connectivity=False)
    issues_no_overlap = validate_topology(gdf, check_overlaps=False, check_gaps=False, check_connectivity=False)
    assert len(issues_all) >= 1
    assert len(issues_no_overlap) == 0


def test_validate_topology_issue_structure():
    """Each violation has feature_id, type, severity, location, description."""
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]),
            Polygon([(1, 1), (3, 1), (3, 3), (1, 3), (1, 1)]),
        ],
    )
    issues = validate_topology(gdf, check_gaps=False, check_connectivity=False)
    for issue in issues:
        assert "feature_id" in issue
        assert "type" in issue
        assert "severity" in issue
        assert "location" in issue
        assert "description" in issue
        assert issue["type"].startswith("topology_")
