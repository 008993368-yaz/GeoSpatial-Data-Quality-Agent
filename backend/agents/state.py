"""
Shared state schema for the LangGraph validation pipeline.

Used by the orchestrator and all validation agents (geometry, attribute, topology)
so they read and update a single state object.
"""
from typing import Any, List, Optional, TypedDict

from api.models import GeometryIssue


class ValidationState(TypedDict, total=False):
    """
    State passed through the validation workflow.

    All keys are optional (total=False) so graph nodes can return partial updates.
    Aligns with API models: issues use GeometryIssue; dataset_id matches ValidationResult.
    """

    dataset_id: str
    """Dataset identifier (from upload). Matches ValidationResult.dataset_id."""

    dataset_path: Optional[str]
    """Path to the vector file on disk, for agents that need to load the dataset."""

    issues: List[GeometryIssue]
    """All validation issues found (geometry, attribute, topology)."""

    corrections: List[dict]
    """Suggested corrections from Recommendation Agent. Each dict matches api.models.CorrectionSuggestion (method, confidence, explanation, issue_index)."""

    user_approvals: List[bool]
    """User decisions per correction (e.g. approve/reject)."""


def empty_state(dataset_id: str, dataset_path: Optional[str] = None) -> dict[str, Any]:
    """Return an initial ValidationState for a new run."""
    return {
        "dataset_id": dataset_id,
        "dataset_path": dataset_path,
        "issues": [],
        "corrections": [],
        "user_approvals": [],
    }
