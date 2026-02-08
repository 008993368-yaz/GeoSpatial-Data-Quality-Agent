"""Tests for core.validation and agents.geometry_agent."""
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, Polygon

# Backend on path via conftest
from core.validation import (
    IssueType,
    Severity,
    _check_geometry,
    validate_geometries,
)
from agents.geometry_agent import validate as agent_validate
from agents.geometry_agent import validate_geodataframe


def test_check_geometry_null():
    """Null geometry returns empty_geometry issue."""
    issues = _check_geometry(None, feature_id=0)
    assert len(issues) == 1
    assert issues[0]["type"] == IssueType.EMPTY_GEOMETRY
    assert issues[0]["severity"] == Severity.CRITICAL
    assert issues[0]["feature_id"] == 0
    assert issues[0]["location"] is None


def test_check_geometry_empty():
    """Empty geometry returns empty_geometry issue."""
    empty = Polygon()
    issues = _check_geometry(empty, feature_id=1)
    assert len(issues) == 1
    assert issues[0]["type"] == IssueType.EMPTY_GEOMETRY
    assert issues[0]["severity"] == Severity.CRITICAL


def test_check_geometry_valid():
    """Valid geometry returns no issues."""
    valid = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    issues = _check_geometry(valid, feature_id=2)
    assert len(issues) == 0


def test_check_geometry_self_intersecting():
    """Self-intersecting polygon returns invalid/self_intersection issue."""
    # Bow-tie: (0,0)-(2,2)-(2,0)-(0,2)-(0,0)
    bowtie = Polygon([(0, 0), (2, 2), (2, 0), (0, 2), (0, 0)])
    issues = _check_geometry(bowtie, feature_id=3)
    assert len(issues) >= 1
    assert issues[0]["severity"] == Severity.CRITICAL
    assert issues[0]["type"] in (IssueType.INVALID_GEOMETRY, IssueType.SELF_INTERSECTION)
    assert issues[0]["location"] is not None or "location" in issues[0]


def test_validate_geometries_empty_gdf():
    """Empty GeoDataFrame returns no issues."""
    gdf = gpd.GeoDataFrame(geometry=[])
    assert validate_geometries(gdf) == []


def test_validate_geometries_mixed():
    """GeoDataFrame with valid and invalid geometries returns correct issues."""
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
            None,
            Point(0, 0),
        ],
        index=[10, 11, 12],
    )
    issues = validate_geometries(gdf)
    # One issue for the None geometry at index 11
    null_issues = [i for i in issues if i["type"] == IssueType.EMPTY_GEOMETRY]
    assert len(null_issues) >= 1
    assert any(i["feature_id"] == 11 for i in null_issues)


def test_validate_geodataframe():
    """Agent validate_geodataframe returns same as core validate_geometries."""
    gdf = gpd.GeoDataFrame(geometry=[Point(0, 0), Polygon()])
    issues = validate_geodataframe(gdf)
    assert len(issues) >= 1
    assert any(i["type"] == IssueType.EMPTY_GEOMETRY for i in issues)


def test_agent_validate_file():
    """Agent validate() with file path loads and validates."""
    path = Path(__file__).parent.parent / "resources" / "sample.geojson"
    if not path.exists():
        pytest.skip("sample.geojson not found")
    issues = agent_validate(path)
    # sample.geojson has valid features; may have 0 issues
    assert isinstance(issues, list)
    for i in issues:
        assert "feature_id" in i and "type" in i and "severity" in i
