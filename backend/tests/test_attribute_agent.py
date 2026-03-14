"""Tests for agents.attribute_agent (issue #73)."""
from pathlib import Path
from unittest.mock import patch

import geopandas as gpd
import pytest
from shapely.geometry import Point

from agents.attribute_agent import run as attribute_agent_run


def _minimal_geojson_path(tmp_path: Path) -> Path:
    """Create a minimal GeoJSON with two point features and attribute columns."""
    gdf = gpd.GeoDataFrame(
        {"name": ["Main St", "Oak Ave"], "value": [1, 2]},
        geometry=[Point(0, 0), Point(1, 1)],
    )
    path = tmp_path / "sample.geojson"
    gdf.to_file(path, driver="GeoJSON")
    return path


def test_run_appends_attribute_issues_to_state(tmp_path):
    """Attribute agent calls LLM service and appends GeometryIssue-like issues to state."""
    path = _minimal_geojson_path(tmp_path)
    state = {"dataset_id": "test", "dataset_path": str(path), "issues": []}

    mock_issues = [
        {
            "feature_id": 0,
            "field": "name",
            "issue_type": "typo",
            "severity": "warning",
            "suggestion": "Use 'Main Street'",
        }
    ]

    with patch("agents.attribute_agent.validate_attributes_with_llm", return_value=mock_issues):
        result = attribute_agent_run(state)

    assert "issues" in result
    issues = result["issues"]
    assert len(issues) == 1
    issue = issues[0]
    assert issue.feature_id == 0
    assert issue.type == "attribute_typo"
    assert issue.severity == "warning"
    assert "name" in (issue.description or "")
    assert "Main Street" in (issue.description or "")
    assert issue.location is None


def test_run_with_no_dataset_path_returns_existing_issues():
    """When dataset_path is missing, return state with no new issues."""
    state = {"dataset_id": "test", "dataset_path": None, "issues": []}
    result = attribute_agent_run(state)
    assert result["issues"] == []


def test_run_with_invalid_path_returns_existing_issues():
    """When path is invalid or unreadable, return existing issues only."""
    state = {"dataset_id": "test", "dataset_path": "/nonexistent/file.geojson", "issues": []}
    result = attribute_agent_run(state)
    assert result["issues"] == []


def test_run_preserves_existing_issues(tmp_path):
    """New attribute issues are appended to existing geometry (or other) issues."""
    path = _minimal_geojson_path(tmp_path)
    from api.models import GeometryIssue

    existing = [
        GeometryIssue(feature_id=99, type="empty_geometry", severity="critical", location=None, description="Empty"),
    ]
    state = {"dataset_path": str(path), "issues": existing}

    mock_issues = [
        {"feature_id": 1, "field": "name", "issue_type": "inconsistency", "severity": "info", "suggestion": "Normalize"},
    ]

    with patch("agents.attribute_agent.validate_attributes_with_llm", return_value=mock_issues):
        result = attribute_agent_run(state)

    assert len(result["issues"]) == 2
    assert result["issues"][0].feature_id == 99
    assert result["issues"][0].type == "empty_geometry"
    assert result["issues"][1].feature_id == 1
    assert result["issues"][1].type == "attribute_inconsistency"


def test_run_with_injected_llm_uses_it(tmp_path):
    """Passing llm= uses that instance instead of default client."""
    path = _minimal_geojson_path(tmp_path)
    state = {"dataset_path": str(path), "issues": []}

    class CapturingLLM:
        def __init__(self):
            self.invoked = False

        def invoke(self, prompt: str, **kwargs):
            self.invoked = True
            return type("Msg", (), {"content": '{"issues": []}'})()

    llm = CapturingLLM()
    result = attribute_agent_run(state, llm=llm)
    assert llm.invoked
    assert result["issues"] == []
