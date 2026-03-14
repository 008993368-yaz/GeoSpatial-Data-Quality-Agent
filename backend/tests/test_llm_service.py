"""Tests for services.llm_service (issue #71)."""
import json
from typing import Any, Dict, List

import pytest

from services.llm_service import (
    AttributeValidationConfig,
    build_attribute_validation_prompt,
    parse_llm_attribute_issues,
    validate_attributes_with_llm,
)


class DummyLLM:
    """Minimal fake LLM with an invoke() method for tests."""

    def __init__(self, payload: Dict[str, Any]) -> None:
        self.payload = payload
        self.last_prompt: str | None = None

    def invoke(self, input: str, **_: Any) -> Any:
        self.last_prompt = input
        # Mimic LangChain ChatMessage with .content
        return type("Msg", (), {"content": json.dumps(self.payload)})


def test_build_attribute_validation_prompt_includes_attribute_data():
    """Prompt should include serialized attribute records and per-field values."""
    records = [{"feature_id": 1, "name": "Main St", "type": "road"}]
    per_field = {"name": ["Main St", "Main Street"], "type": ["road", "rd"]}

    prompt = build_attribute_validation_prompt(records, per_field)

    assert "ATTRIBUTE_DATA=" in prompt
    # Basic sanity: field names and a sample value should appear
    assert "Main St" in prompt
    assert '"name"' in prompt
    assert '"type"' in prompt


def test_parse_llm_attribute_issues_valid_json():
    """Valid JSON with issues should be parsed into normalized dicts."""
    raw = json.dumps(
        {
            "issues": [
                {
                    "feature_id": 1,
                    "field": "name",
                    "issue_type": "typo",
                    "severity": "warning",
                    "suggestion": "Main Street",
                }
            ]
        }
    )
    issues = parse_llm_attribute_issues(raw)
    assert len(issues) == 1
    issue = issues[0]
    assert issue["feature_id"] == 1
    assert issue["field"] == "name"
    assert issue["issue_type"] == "typo"
    assert issue["severity"] == "warning"
    assert issue["suggestion"] == "Main Street"


def test_parse_llm_attribute_issues_invalid_json_returns_empty():
    """Invalid JSON should return an empty list (fail-safe)."""
    issues = parse_llm_attribute_issues("not-json")
    assert issues == []


def test_validate_attributes_with_llm_uses_given_llm_and_parses_issues():
    """validate_attributes_with_llm should call the provided LLM and parse its response."""
    payload = {
        "issues": [
            {
                "feature_id": 10,
                "field": "name",
                "issue_type": "inconsistency",
                "severity": "warning",
                "suggestion": "Normalize street suffixes",
            }
        ]
    }
    llm = DummyLLM(payload)
    records: List[Dict[str, Any]] = [
        {"feature_id": 10, "name": "Main St", "type": "road"},
        {"feature_id": 11, "name": "Main Street", "type": "road"},
    ]

    issues = validate_attributes_with_llm(records, llm=llm, config=AttributeValidationConfig())

    # Ensure LLM was called with a non-empty prompt that includes attribute data
    assert llm.last_prompt is not None
    assert "ATTRIBUTE_DATA=" in llm.last_prompt
    assert "Main St" in llm.last_prompt

    # And ensure issues are parsed correctly
    assert len(issues) == 1
    issue = issues[0]
    assert issue["feature_id"] == 10
    assert issue["field"] == "name"
    assert issue["issue_type"] == "inconsistency"
    assert "Normalize street suffixes" in issue["suggestion"]


def test_validate_attributes_with_llm_empty_input_returns_empty_and_skips_llm():
    """If both attribute_records and per_field_values are empty, LLM should not be called."""
    llm = DummyLLM({"issues": []})

    issues = validate_attributes_with_llm([], per_field_values=None, llm=llm)

    assert issues == []
    assert llm.last_prompt is None

