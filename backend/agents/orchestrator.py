"""
LangGraph orchestration for the validation pipeline.

Coordinates geometry, attribute, and topology agents with shared ValidationState.
StateGraph with nodes and edges (issue #61); conditional routing by severity (issue #62).

Attribute Agent (issue #72, #73): The attribute_validation node is the LLM-backed
implementation (agents.attribute_agent.run). It appends attribute issues to state["issues"]
with the same GeometryIssue shape (type=attribute_*, severity, etc.).

Topology Agent (issue #81, #82): The topology_validation node uses the real implementation
(agents.topology_agent.run), not a stub. It loads the dataset from state["dataset_path"],
runs core.topology.validate_topology, and appends topology issues as GeometryIssue
(type=topology_gap, topology_overlap, topology_dangle, etc.).

All issues—geometry, attribute, and topology—are accumulated in state["issues"] and
considered by _route_by_severity for conditional routing (e.g. any critical topology
issue routes to apply_corrections).

Recommendation Agent (issue #87, #88): The generate_recommendations node uses the real
implementation (agents.recommendation_agent.run), not a stub. It reads state["issues"],
produces one CorrectionSuggestion per issue (method, confidence, explanation, issue_index)
via GPT-4 when an LLM is provided or rule-based fallbacks, and returns
{"corrections": [...]}. state["corrections"] is merged into state; the apply_corrections
node receives it (stub does not apply fixes yet), and the validation API returns
corrections in ValidationResult.

Routing logic (after generate_recommendations):
- If any issue has severity "critical" -> apply_corrections node (stub; apply fixes when implemented).
- Otherwise -> END (review path; no automatic corrections).
"""
from typing import Any, Literal

from api.models import GeometryIssue
from langgraph.graph import END, StateGraph

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


def _apply_corrections_node(state: ValidationState) -> dict[str, Any]:
    """
    Node: apply user-approved corrections to the dataset.
    Stub: no-op until correction application is implemented (Phase 2/3).
    """
    return {}


def _route_by_severity(state: ValidationState) -> Literal["critical", "review"]:
    """
    Conditional routing after generate_recommendations.

    Considers all issues in state["issues"] (geometry, attribute, topology).
    - critical: at least one issue has severity "critical" -> run apply_corrections.
    - review: otherwise -> END (workflow finishes; user can review issues without auto-apply).
    """
    issues = state.get("issues") or []
    for issue in issues:
        if getattr(issue, "severity", "").lower() == "critical":
            return "critical"
    return "review"


def _build_graph() -> Any:
    """Build and compile the validation StateGraph with conditional routing by severity."""
    workflow_builder = StateGraph(ValidationState)

    workflow_builder.add_node("geometry_validation", _geometry_validation_node)
    workflow_builder.add_node("attribute_validation", attribute_validation)
    workflow_builder.add_node("topology_validation", topology_validation)  # real impl: agents.topology_agent.run
    workflow_builder.add_node("generate_recommendations", generate_recommendations)  # real impl: agents.recommendation_agent.run
    workflow_builder.add_node("apply_corrections", _apply_corrections_node)

    workflow_builder.set_entry_point("geometry_validation")
    workflow_builder.add_edge("geometry_validation", "attribute_validation")
    workflow_builder.add_edge("attribute_validation", "topology_validation")
    workflow_builder.add_edge("topology_validation", "generate_recommendations")

    # Conditional routing: critical issues -> apply_corrections; else -> END (review)
    workflow_builder.add_conditional_edges(
        "generate_recommendations",
        _route_by_severity,
        path_map={"critical": "apply_corrections", "review": END},
    )
    workflow_builder.add_edge("apply_corrections", END)

    return workflow_builder.compile()


# Compiled graph for API use (issue #63)
validation_graph = _build_graph()

__all__ = ["ValidationState", "empty_state", "validation_graph"]
