"""Tests for agents.recommendation_agent (issue #87)."""
from unittest.mock import MagicMock, patch

import pytest

from api.models import GeometryIssue
from agents.recommendation_agent import run as recommendation_agent_run


def test_run_with_no_issues_returns_empty_corrections():
    """When state has no issues, return empty corrections list."""
    state = {"dataset_id": "test", "issues": [], "corrections": []}
    result = recommendation_agent_run(state)
    assert "corrections" in result
    assert result["corrections"] == []


def test_run_with_none_issues_returns_empty_corrections():
    """When state["issues"] is missing/None, return empty corrections."""
    state = {"dataset_id": "test"}
    result = recommendation_agent_run(state)
    assert result["corrections"] == []


def test_run_returns_rule_based_corrections_for_issues():
    """Without LLM, agent returns one CorrectionSuggestion per issue with rule-based method/confidence/explanation."""
    issues = [
        GeometryIssue(feature_id=0, type="self_intersection", severity="critical", location=None, description="Self-intersecting ring"),
        GeometryIssue(feature_id=1, type="attribute_typo", severity="warning", location=None, description="Field 'name': Use 'Main Street'"),
    ]
    state = {"issues": issues}
    result = recommendation_agent_run(state)

    assert "corrections" in result
    corrections = result["corrections"]
    assert len(corrections) == 2

    assert corrections[0]["issue_index"] == 0
    assert corrections[0]["method"] == "buffer(0)"
    assert 0 <= corrections[0]["confidence"] <= 1
    assert "buffer" in (corrections[0]["explanation"] or "").lower()

    assert corrections[1]["issue_index"] == 1
    assert "suggested" in (corrections[1]["method"] or "").lower() or "apply" in (corrections[1]["method"] or "").lower()
    assert 0 <= corrections[1]["confidence"] <= 1


def test_run_self_intersection_gets_buffer_suggestion():
    """Rule-based: self_intersection issue yields buffer(0) and high confidence."""
    state = {
        "issues": [
            GeometryIssue(feature_id=5, type="self_intersection", severity="critical", location=[0, 0], description="Invalid"),
        ],
    }
    result = recommendation_agent_run(state)
    assert len(result["corrections"]) == 1
    c = result["corrections"][0]
    assert c["method"] == "buffer(0)"
    assert c["confidence"] == 0.9
    assert c["issue_index"] == 0


def test_run_with_llm_uses_llm_suggestions():
    """When LLM is provided and returns suggestions, those are used instead of rules."""
    issues = [
        GeometryIssue(feature_id=0, type="self_intersection", severity="critical", location=None, description="Bad"),
    ]
    state = {"issues": issues}
    mock_llm = MagicMock()

    mock_suggestions = [
        {"method": "custom_fix", "confidence": 0.95, "explanation": "LLM-generated suggestion."},
    ]

    with patch("agents.recommendation_agent.get_recommendation_suggestions_from_llm", return_value=mock_suggestions):
        result = recommendation_agent_run(state, llm=mock_llm)

    assert len(result["corrections"]) == 1
    assert result["corrections"][0]["method"] == "custom_fix"
    assert result["corrections"][0]["confidence"] == 0.95
    assert "LLM-generated" in result["corrections"][0]["explanation"]
    assert result["corrections"][0]["issue_index"] == 0


def test_run_llm_failure_falls_back_to_rules():
    """When LLM is provided but raises, fall back to rule-based suggestions."""
    issues = [
        GeometryIssue(feature_id=0, type="self_intersection", severity="critical", location=None, description="Bad"),
    ]
    state = {"issues": issues}
    mock_llm = MagicMock()

    with patch("agents.recommendation_agent.get_recommendation_suggestions_from_llm", side_effect=RuntimeError("API error")):
        result = recommendation_agent_run(state, llm=mock_llm)

    assert len(result["corrections"]) == 1
    assert result["corrections"][0]["method"] == "buffer(0)"
    assert result["corrections"][0]["issue_index"] == 0


def test_run_correction_schema_compatible_with_apply_corrections():
    """Each correction has method, confidence, explanation, issue_index (CorrectionSuggestion shape)."""
    state = {
        "issues": [
            GeometryIssue(feature_id=0, type="topology_overlap", severity="warning", location=None, description="Overlap"),
        ],
    }
    result = recommendation_agent_run(state)
    c = result["corrections"][0]
    assert "method" in c and isinstance(c["method"], str)
    assert "confidence" in c and isinstance(c["confidence"], (int, float)) and 0 <= c["confidence"] <= 1
    assert "explanation" in c and isinstance(c["explanation"], str)
    assert "issue_index" in c and c["issue_index"] == 0
