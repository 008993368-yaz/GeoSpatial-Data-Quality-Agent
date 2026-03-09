"""Topology validation agent: gaps, overlaps, connectivity. Stub for #61."""
from agents.state import ValidationState


def run(state: ValidationState) -> dict:
    """
    Run topology validation on the dataset in state.
    Returns partial state update (e.g. {"issues": [...]}).
    Stub: no-op until topology validation is implemented.
    """
    return {}
