"""
Attribute validation agent: LLM-backed consistency, typos, outliers (issue #73).

Uses services.attribute_extractor for sampled attribute data and services.llm_service
for inconsistency detection. Appends attribute issues into state["issues"] using
GeometryIssue-compatible structure (type=attribute_*, description=field + suggestion).
"""
from typing import Any, Dict, List, Optional

import geopandas as gpd

from api.models import GeometryIssue
from agents.state import ValidationState
from core.config import settings
from services.attribute_extractor import get_attribute_columns, get_attribute_records
from services.llm_service import (
    AttributeIssue as LLMAttributeIssue,
    SupportsInvoke,
    validate_attributes_with_llm,
)


# Fixed random_state for deterministic sampling (issue #73: deterministic node).
_ATTRIBUTE_SAMPLE_RANDOM_STATE = 0


def _attribute_issue_to_geometry_issue(attr: Dict[str, Any]) -> GeometryIssue:
    """Map an LLM attribute-issue dict to GeometryIssue for state["issues"]."""
    field = attr.get("field") or ""
    suggestion = attr.get("suggestion") or ""
    issue_type = attr.get("issue_type") or "other"
    severity = attr.get("severity") or "warning"
    description = f"Field '{field}': {suggestion}".strip()
    return GeometryIssue(
        feature_id=attr.get("feature_id"),
        type=f"attribute_{issue_type}",
        severity=severity,
        location=None,
        description=description or None,
    )


def run(
    state: ValidationState,
    *,
    sample_size: Optional[int] = None,
    llm: Optional[SupportsInvoke] = None,
) -> dict:
    """
    Run attribute validation on the dataset in state (issue #73).

    - Loads the dataset from state["dataset_path"] and extracts attribute samples
      (no geometry) via services.attribute_extractor.
    - Calls the LLM service for inconsistency detection.
    - Converts results to GeometryIssue-like entries and appends them to state["issues"].

    Deterministic: uses fixed random_state when sampling. Side-effect free apart from
    the returned state update (no global state mutation).

    Args:
        state: Current validation state (dataset_path, issues, ...).
        sample_size: Max rows to sample; default from settings.ATTRIBUTE_SAMPLE_SIZE.
        llm: Optional LLM instance for testing; if None, default client is used.

    Returns:
        Partial state update: {"issues": existing_issues + new_attribute_issues}.
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

    n = sample_size if sample_size is not None else settings.ATTRIBUTE_SAMPLE_SIZE
    max_fields = getattr(settings, "ATTRIBUTE_MAX_FIELDS", None)
    records = get_attribute_records(
        gdf, sample_size=n, random_state=_ATTRIBUTE_SAMPLE_RANDOM_STATE, max_fields=max_fields
    )
    per_field = get_attribute_columns(
        gdf, sample_size=n, random_state=_ATTRIBUTE_SAMPLE_RANDOM_STATE, max_fields=max_fields
    )

    if not records and not per_field:
        return {"issues": existing}

    raw_issues: List[LLMAttributeIssue] = validate_attributes_with_llm(
        records,
        per_field_values=per_field,
        llm=llm,
    )
    new_issues = [_attribute_issue_to_geometry_issue(attr) for attr in raw_issues]
    return {"issues": existing + new_issues}
