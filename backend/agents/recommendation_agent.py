"""
Recommendation agent: generate correction suggestions from issues (issue #87, #9).

Consumes state["issues"] (geometry, attribute, topology), produces one CorrectionSuggestion
per issue (method, confidence, explanation, issue_index). Uses GPT-4 when an LLM is
provided; otherwise uses rule-based fallbacks. Output is compatible with apply-corrections API.
"""
from typing import Any, Dict, List, Optional

from api.models import CorrectionSuggestion
from agents.state import ValidationState
from services.llm_service import (
    SupportsInvoke,
    get_recommendation_suggestions_from_llm,
)


def _issue_to_dict(issue: Any) -> Dict[str, Any]:
    """Convert an issue (GeometryIssue or dict) to a minimal dict for LLM or rules."""
    if isinstance(issue, dict):
        return {
            "type": issue.get("type", ""),
            "severity": issue.get("severity", ""),
            "description": issue.get("description") or "",
        }
    return {
        "type": getattr(issue, "type", ""),
        "severity": getattr(issue, "severity", ""),
        "description": getattr(issue, "description") or "",
    }


def _rule_based_suggestion(issue: Any) -> Dict[str, Any]:
    """
    Return a default method, confidence, and explanation for known issue types.
    Used when no LLM is provided or as fallback.
    """
    d = _issue_to_dict(issue)
    itype = (d.get("type") or "").lower()
    desc = (d.get("description") or "")[:300]

    if "self_intersection" in itype or "invalid_geometry" in itype:
        return {
            "method": "buffer(0)",
            "confidence": 0.9,
            "explanation": "Apply zero-distance buffer to resolve self-intersection or invalid polygon.",
        }
    if "empty_geometry" in itype or "null" in itype:
        return {
            "method": "delete or replace geometry",
            "confidence": 0.8,
            "explanation": "Remove or replace the empty/null geometry.",
        }
    if "topology_overlap" in itype:
        return {
            "method": "merge or clip overlapping features",
            "confidence": 0.7,
            "explanation": "Adjust boundaries or merge overlapping polygons to remove overlap.",
        }
    if "topology_gap" in itype:
        return {
            "method": "add missing polygon or adjust boundaries",
            "confidence": 0.6,
            "explanation": "Fill the gap with a new polygon or extend adjacent boundaries.",
        }
    if "topology_dangle" in itype:
        return {
            "method": "snap endpoint to nearest line or extend",
            "confidence": 0.65,
            "explanation": "Connect the dangle endpoint to the network or extend the line.",
        }
    if itype.startswith("attribute_"):
        return {
            "method": "apply suggested value",
            "confidence": 0.85,
            "explanation": desc or "Correct the attribute value per validation suggestion.",
        }
    # Generic
    return {
        "method": "manual review",
        "confidence": 0.5,
        "explanation": f"Issue type: {itype or 'unknown'}. Review and fix manually.",
    }


def run(
    state: ValidationState,
    *,
    llm: Optional[SupportsInvoke] = None,
) -> dict:
    """
    Generate correction suggestions for all issues in state (issue #87).

    - Reads state["issues"] (geometry, attribute, topology).
    - For each issue, produces a suggestion (method, confidence, explanation) using
      GPT-4 when llm is provided, otherwise rule-based fallbacks.
    - Returns {"corrections": [...]} where each item is a CorrectionSuggestion
      (method, confidence, explanation, issue_index) compatible with the apply-corrections API.

    Args:
        state: Current validation state (issues, ...).
        llm: Optional LangChain-compatible LLM for context-aware suggestions; if None, uses rules only.

    Returns:
        Partial state update: {"corrections": list of CorrectionSuggestion dicts}.
    """
    issues = list(state.get("issues") or [])
    if not issues:
        return {"corrections": []}

    issue_dicts = [_issue_to_dict(iss) for iss in issues]

    if llm is not None:
        try:
            raw_suggestions = get_recommendation_suggestions_from_llm(issue_dicts, llm=llm)
        except Exception:
            raw_suggestions = []
        if len(raw_suggestions) >= len(issues):
            suggestions = [
                CorrectionSuggestion(
                    method=raw_suggestions[i]["method"],
                    confidence=raw_suggestions[i]["confidence"],
                    explanation=raw_suggestions[i]["explanation"],
                    issue_index=i,
                )
                for i in range(len(issues))
            ]
        else:
            # Fallback to rules if LLM returned too few
            suggestions = []
            for i, iss in enumerate(issues):
                rule = _rule_based_suggestion(iss)
                suggestions.append(
                    CorrectionSuggestion(
                        method=rule["method"],
                        confidence=rule["confidence"],
                        explanation=rule["explanation"],
                        issue_index=i,
                    )
                )
    else:
        suggestions = [
            CorrectionSuggestion(
                issue_index=i,
                **_rule_based_suggestion(iss),
            )
            for i, iss in enumerate(issues)
        ]

    return {"corrections": [s.model_dump() for s in suggestions]}
