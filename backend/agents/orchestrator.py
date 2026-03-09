"""
LangGraph orchestration for the validation pipeline.

Coordinates geometry, attribute, and topology agents with shared ValidationState.
Full graph construction (nodes + edges + conditional routing) is in issue #61.
"""
from agents.state import ValidationState, empty_state

__all__ = ["ValidationState", "empty_state"]
