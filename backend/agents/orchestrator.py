"""
LangGraph orchestration for the validation pipeline.

Coordinates geometry, attribute, and topology agents with shared ValidationState.
StateGraph with nodes and edges (issue #61); conditional routing in #62.
"""
from typing import Any

from api.models import GeometryIssue
from langgraph.graph import StateGraph

from agents.attribute_agent import run as attribute_validation
from agents.geometry_agent import validate as run_geometry_validation
from agents.recommendation_agent import run as generate_recommendations
from agents.state import ValidationState, empty_state
from agents.topology_agent import run as topology_validation


def _dict_to_geometry_issue(d: dict) -> GeometryIssue:
    """Convert geometry agent output dict to GeometryIssue model."""
    return GeometryIssue(
        feature_id=d.get("feature_id"),
        type=d.get("type", ""),
        severity=d.get("severity", ""),
        location=d.get("location"),
        description=d.get("description"),
    )


def _geometry_validation_node(state: ValidationState) -> dict[str, Any]:
    """Node: run geometry validation and append issues to state."""
    path = state.get("dataset_path")
    existing = list(state.get("issues") or [])
    if not path:
        return {"issues": existing}
    raw = run_geometry_validation(path)
    new_issues = [_dict_to_geometry_issue(d) for d in raw]
    return {"issues": existing + new_issues}


def _build_graph() -> Any:
    """Build and compile the validation StateGraph."""
    workflow_builder = StateGraph(ValidationState)

    workflow_builder.add_node("geometry_validation", _geometry_validation_node)
    workflow_builder.add_node("attribute_validation", attribute_validation)
    workflow_builder.add_node("topology_validation", topology_validation)
    workflow_builder.add_node("generate_recommendations", generate_recommendations)

    workflow_builder.set_entry_point("geometry_validation")
    workflow_builder.add_edge("geometry_validation", "attribute_validation")
    workflow_builder.add_edge("attribute_validation", "topology_validation")
    workflow_builder.add_edge("topology_validation", "generate_recommendations")

    return workflow_builder.compile()


# Compiled graph for API use (issue #63)
validation_graph = _build_graph()

__all__ = ["ValidationState", "empty_state", "validation_graph"]
