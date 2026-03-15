"""
LLM service for attribute validation using GPT-4 via LangChain (issue #71).

This module focuses on:
- Designing prompts for attribute validation (inconsistencies, typos, naming variations,
  missing values, outliers).
- Calling a GPT-4-compatible model via LangChain.
- Returning a structured list of issues:
  {feature_id, field, issue_type, severity, suggestion}.

The public entry point `validate_attributes_with_llm` is intentionally simple and accepts
pre-sampled attribute data (e.g. from services.attribute_extractor).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import json

from core.config import settings

try:
    # Optional dependency; tests inject a fake LLM so this import is not required there.
    from langchain_openai import ChatOpenAI  # type: ignore[import]
except ImportError:  # pragma: no cover - handled at runtime
    ChatOpenAI = None  # type: ignore[assignment]


class AttributeIssue(Dict[str, Any]):
    """
    Structured issue format for attribute validation.

    Keys (convention, not enforced at type level):
    - feature_id: identifier of the affected feature (or null for field-level only issues).
    - field: name of the attribute field (e.g. \"name\", \"type\").
    - issue_type: short code such as \"inconsistency\", \"typo\", \"missing_value\", \"outlier\".
    - severity: e.g. \"critical\", \"warning\", \"info\".
    - suggestion: human-readable suggestion or normalized value.
    """


class SupportsInvoke(Protocol):
    """Minimal protocol for LangChain-like LLMs used here."""

    def invoke(self, input: str, **kwargs: Any) -> Any:  # pragma: no cover - protocol
        ...


@dataclass
class AttributeValidationConfig:
    """Configuration for attribute validation prompts and parsing."""

    model: str = settings.OPENAI_MODEL
    max_tokens: int = settings.OPENAI_MAX_TOKENS


def _default_llm(config: Optional[AttributeValidationConfig] = None) -> SupportsInvoke:
    """
    Construct a default ChatOpenAI client.

    Uses OPENAI_API_KEY / OPENAI_MODEL from core.config. Tests should inject a fake llm instead.
    Raises RuntimeError if langchain_openai is not installed.
    """
    if ChatOpenAI is None:
        raise RuntimeError(
            "langchain_openai is not installed. Install backend requirements or "
            "pass an explicit `llm` instance to validate_attributes_with_llm."
        )
    cfg = config or AttributeValidationConfig()
    return ChatOpenAI(model=cfg.model, max_tokens=cfg.max_tokens)  # type: ignore[call-arg]


def build_attribute_validation_prompt(
    attribute_records: List[Dict[str, Any]],
    per_field_values: Optional[Dict[str, List[Any]]] = None,
    *,
    max_records_in_prompt: Optional[int] = None,
    max_values_per_field: Optional[int] = None,
    max_fields: Optional[int] = None,
) -> str:
    """
    Build a prompt for GPT-4 to detect attribute issues (issue #70: token limits).

    Uses settings.ATTRIBUTE_MAX_RECORDS_IN_PROMPT and ATTRIBUTE_MAX_VALUES_PER_FIELD
    when the optional limits are not provided, to keep prompt size and cost manageable.

    Args:
        attribute_records: List of per-feature dicts, usually including \"feature_id\" and
            attribute columns (from services.attribute_extractor.get_attribute_records).
        per_field_values: Optional mapping of field -> list of values across features
            (from get_attribute_columns), useful for outlier / distribution analysis.
        max_records_in_prompt: Cap on records embedded in prompt; default from settings.
        max_values_per_field: Cap on values per field in prompt; default from settings.
        max_fields: If set, only first N fields in per_field_values; default from settings.

    Returns:
        A string prompt instructing the model to return JSON with an \"issues\" list.
    """
    n_rec = max_records_in_prompt if max_records_in_prompt is not None else getattr(
        settings, "ATTRIBUTE_MAX_RECORDS_IN_PROMPT", 10
    )
    n_val = max_values_per_field if max_values_per_field is not None else getattr(
        settings, "ATTRIBUTE_MAX_VALUES_PER_FIELD", 15
    )
    n_fld = max_fields if max_fields is not None else getattr(settings, "ATTRIBUTE_MAX_FIELDS", None)
    pf = per_field_values or {}
    if n_fld is not None and n_fld > 0:
        keys = list(pf.keys())[:n_fld]
        pf = {k: pf[k] for k in keys if k in pf}
    examples = {
        "records": attribute_records[:n_rec],
        "per_field_values": {k: v[:n_val] for k, v in pf.items()},
    }
    instructions = (
        "You are a geospatial data quality assistant. "
        "Analyze attribute data for inconsistencies, typos, naming variations, "
        "missing values, and outliers.\n\n"
        "Return ONLY valid JSON with the following structure:\n"
        "{\n"
        '  "issues": [\n'
        "    {\n"
        '      "feature_id": "<string or number or null>",\n'
        '      "field": "<attribute field name>",\n'
        '      "issue_type": "inconsistency|typo|missing_value|outlier|other",\n'
        '      "severity": "critical|warning|info",\n'
        '      "suggestion": "<short suggestion or normalized value>"\n'
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}\n\n"
        "Do not include explanations outside the JSON.\n"
        "Focus on patterns that indicate data quality problems, not domain semantics.\n"
    )
    return instructions + "\n\nATTRIBUTE_DATA=\n" + json.dumps(examples, default=str)


def parse_llm_attribute_issues(raw: Any) -> List[AttributeIssue]:
    """
    Parse the LLM response into a list of AttributeIssue dicts.

    Accepts either a string (raw content) or an object with `.content` (LangChain message).
    On any parse error, returns an empty list (fail-safe).
    """
    if raw is None:
        return []

    if not isinstance(raw, str):
        # LangChain ChatMessage or similar
        content = getattr(raw, "content", None)
    else:
        content = raw

    if not isinstance(content, str):
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    issues = data.get("issues") if isinstance(data, dict) else None
    if not isinstance(issues, list):
        return []

    # Normalize to dicts with expected keys; accept extra keys.
    out: List[AttributeIssue] = []
    for item in issues:
        if not isinstance(item, dict):
            continue
        feature_id = item.get("feature_id")
        field = item.get("field")
        issue_type = item.get("issue_type")
        severity = item.get("severity")
        suggestion = item.get("suggestion")
        if field is None or issue_type is None:
            # Require at least field + issue_type for usefulness
            continue
        normalized: AttributeIssue = AttributeIssue(
            feature_id=feature_id,
            field=field,
            issue_type=issue_type,
            severity=severity or "warning",
            suggestion=suggestion or "",
        )
        # Preserve any extra metadata the model might emit
        for k, v in item.items():
            if k not in normalized:
                normalized[k] = v
        out.append(normalized)
    return out


def validate_attributes_with_llm(
    attribute_records: List[Dict[str, Any]],
    per_field_values: Optional[Dict[str, List[Any]]] = None,
    *,
    llm: Optional[SupportsInvoke] = None,
    config: Optional[AttributeValidationConfig] = None,
) -> List[AttributeIssue]:
    """
    Validate attributes with GPT-4 via LangChain and return structured issues.

    Args:
        attribute_records: Per-feature records (no geometry) for row-level analysis.
        per_field_values: Optional per-field value lists for distribution/outlier checks.
        llm: Optional LangChain-compatible LLM with `.invoke(str)`; if None, a default
             ChatOpenAI client is created from settings.
        config: Optional AttributeValidationConfig (model, max_tokens).

    Returns:
        List of AttributeIssue dicts. Empty list on error or if no issues found.
    """
    if not attribute_records and not per_field_values:
        return []

    prompt = build_attribute_validation_prompt(attribute_records, per_field_values)
    client = llm or _default_llm(config)
    try:
        response = client.invoke(prompt)
    except Exception:
        return []

    return parse_llm_attribute_issues(response)


# --- Recommendation suggestions (issue #87) ---


def build_recommendation_prompt(issues: List[Dict[str, Any]]) -> str:
    """
    Build a prompt for GPT-4 to suggest a fix (method, confidence, explanation) per issue.

    Args:
        issues: List of dicts with at least "type", "severity", "description" (and optionally
                "feature_id"). Typically from state["issues"] converted to dict.

    Returns:
        Prompt string. Model is asked to return JSON: {"suggestions": [{ "method", "confidence", "explanation" }, ...]}
        in the same order as the input issues.
    """
    if not issues:
        return ""
    # Compact representation for the prompt
    compact = []
    for i, iss in enumerate(issues):
        if isinstance(iss, dict):
            row = iss
        else:
            row = {"type": getattr(iss, "type", ""), "severity": getattr(iss, "severity", ""), "description": getattr(iss, "description") or ""}
        compact.append({"index": i, "type": row.get("type", ""), "severity": row.get("severity", ""), "description": (row.get("description") or "")[:200]})
    instructions = (
        "You are a geospatial data quality assistant. For each validation issue below, "
        "suggest a correction: a short method name (e.g. buffer(0), rename field, snap to grid), "
        "a confidence score from 0 to 1, and a brief natural-language explanation.\n\n"
        "Return ONLY valid JSON with this structure (one suggestion per issue, same order as input):\n"
        "{\n  \"suggestions\": [\n"
        "    { \"method\": \"...\", \"confidence\": 0.9, \"explanation\": \"...\" },\n"
        "    ...\n  ]\n}\n\n"
        "Keep method names short and actionable. Confidence should reflect how likely the fix is to resolve the issue.\n"
    )
    return instructions + "\nISSUES=\n" + json.dumps(compact, default=str)


def parse_recommendation_suggestions(raw: Any) -> List[Dict[str, Any]]:
    """
    Parse LLM response into a list of suggestion dicts (method, confidence, explanation).

    Returns one entry per suggestion; if the response has fewer than expected, missing entries
    are filled with a default. On parse error, returns empty list.
    """
    if raw is None:
        return []
    content = raw if isinstance(raw, str) else getattr(raw, "content", None)
    if not isinstance(content, str):
        return []
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []
    suggestions = data.get("suggestions") if isinstance(data, dict) else None
    if not isinstance(suggestions, list):
        return []
    out: List[Dict[str, Any]] = []
    default = {"method": "manual review", "confidence": 0.5, "explanation": "No suggestion generated."}
    for item in suggestions:
        if not isinstance(item, dict):
            out.append(default.copy())
            continue
        method = item.get("method") or default["method"]
        try:
            conf = float(item.get("confidence", 0.5))
            conf = max(0.0, min(1.0, conf))
        except (TypeError, ValueError):
            conf = 0.5
        explanation = item.get("explanation") or default["explanation"]
        if not isinstance(explanation, str):
            explanation = str(explanation)[:500]
        out.append({"method": str(method)[:200], "confidence": conf, "explanation": explanation})
    return out


def get_recommendation_suggestions_from_llm(
    issues: List[Dict[str, Any]],
    *,
    llm: Optional[SupportsInvoke] = None,
) -> List[Dict[str, Any]]:
    """
    Call GPT-4 to get correction suggestions (method, confidence, explanation) for each issue.

    Args:
        issues: List of issue dicts (type, severity, description, ...).
        llm: Optional LangChain-compatible LLM; if None, uses default ChatOpenAI.

    Returns:
        List of dicts with keys method, confidence, explanation (same order as issues).
        Empty list on error or if no issues.
    """
    if not issues:
        return []
    prompt = build_recommendation_prompt(issues)
    if not prompt:
        return []
    client = llm or _default_llm()
    try:
        response = client.invoke(prompt)
    except Exception:
        return []
    parsed = parse_recommendation_suggestions(response)
    # Pad to match issue count if LLM returned fewer
    while len(parsed) < len(issues):
        parsed.append({"method": "manual review", "confidence": 0.5, "explanation": "No suggestion generated."})
    return parsed[: len(issues)]


__all__ = [
    "AttributeIssue",
    "AttributeValidationConfig",
    "build_attribute_validation_prompt",
    "parse_llm_attribute_issues",
    "validate_attributes_with_llm",
    "build_recommendation_prompt",
    "parse_recommendation_suggestions",
    "get_recommendation_suggestions_from_llm",
]

