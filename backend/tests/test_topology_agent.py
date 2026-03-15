"""Tests for agents.topology_agent (issue #81)."""
from pathlib import Path
from unittest.mock import patch

import geopandas as gpd
import pytest
from shapely.geometry import Polygon

from agents.topology_agent import run as topology_agent_run


def _minimal_geojson_path(tmp_path: Path) -> Path:
    """Create a minimal GeoJSON with two polygons."""
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1), (1, 0)]),
        ],
    )
    path = tmp_path / "sample.geojson"
    gdf.to_file(path, driver="GeoJSON")
    return path


def test_run_appends_topology_issues_to_state(tmp_path):
    """Topology agent calls validate_topology and appends GeometryIssue to state."""
    path = _minimal_geojson_path(tmp_path)
    state = {"dataset_id": "test", "dataset_path": str(path), "issues": []}

    mock_violations = [
        {
            "feature_id": 10,
            "other_feature_id": 20,
            "type": "topology_overlap",
            "severity": "warning",
            "location": [0.5, 0.5],
            "description": "Overlap with feature 20",
        }
    ]

    with patch("agents.topology_agent.validate_topology", return_value=mock_violations):
        result = topology_agent_run(state)

    assert "issues" in result
    issues = result["issues"]
    assert len(issues) == 1
    issue = issues[0]
    assert issue.feature_id == 10
    assert issue.type == "topology_overlap"
    assert issue.severity == "warning"
    assert issue.location == [0.5, 0.5]
    assert "Overlap" in (issue.description or "")


def test_run_with_no_dataset_path_returns_existing_issues():
    """When dataset_path is missing, return state with no new issues."""
    state = {"dataset_id": "test", "dataset_path": None, "issues": []}
    result = topology_agent_run(state)
    assert result["issues"] == []


def test_run_with_invalid_path_returns_existing_issues():
    """When path is invalid or unreadable, return existing issues only."""
    state = {"dataset_id": "test", "dataset_path": "/nonexistent/file.geojson", "issues": []}
    result = topology_agent_run(state)
    assert result["issues"] == []


def test_run_preserves_existing_issues(tmp_path):
    """New topology issues are appended to existing geometry/attribute issues."""
    path = _minimal_geojson_path(tmp_path)
    from api.models import GeometryIssue

    existing = [
        GeometryIssue(
            feature_id=99, type="empty_geometry", severity="critical",
            location=None, description="Empty",
        ),
    ]
    state = {"dataset_path": str(path), "issues": existing}

    mock_violations = [
        {
            "feature_id": 0,
            "other_feature_id": None,
            "type": "topology_gap",
            "severity": "warning",
            "location": [0.5, 0.5],
            "description": "Gap in polygon coverage",
        },
    ]

    with patch("agents.topology_agent.validate_topology", return_value=mock_violations):
        result = topology_agent_run(state)

    assert len(result["issues"]) == 2
    assert result["issues"][0].feature_id == 99
    assert result["issues"][0].type == "empty_geometry"
    assert result["issues"][1].feature_id == 0
    assert result["issues"][1].type == "topology_gap"


def test_run_with_real_overlap(tmp_path):
    """With real overlapping polygons, topology agent returns overlap issues (no mock)."""
    gdf = gpd.GeoDataFrame(
        geometry=[
            Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]),
            Polygon([(1, 1), (3, 1), (3, 3), (1, 3), (1, 1)]),
        ],
    )
    path = tmp_path / "overlap.geojson"
    gdf.to_file(path, driver="GeoJSON")
    state = {"dataset_path": str(path), "issues": []}

    result = topology_agent_run(state)

    assert "issues" in result
    overlaps = [i for i in result["issues"] if i.type == "topology_overlap"]
    assert len(overlaps) >= 1
    assert overlaps[0].location is not None
