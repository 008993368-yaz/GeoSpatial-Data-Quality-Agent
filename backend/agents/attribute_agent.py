"""Attribute validation agent: consistency, outliers, missing values (LLM-assisted). Stub for #61."""
from agents.state import ValidationState


def run(state: ValidationState) -> dict:
    """
    Run attribute validation on the dataset in state.
    Returns partial state update (e.g. {"issues": [...]}).
    Stub: no-op until attribute validation is implemented.
    """
    return {}
