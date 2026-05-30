"""Tests for api.models serialization edge cases."""
import numpy as np
import pytest

# Backend on path via conftest
from api.models import GeometryIssue, ValidationResult


@pytest.mark.parametrize(
    "value, expected_type",
    [
        (np.int32(10), int),
        (np.int64(11), int),
        (np.float32(3.5), float),
        (np.float64(2.0), float),
        (7, int),
        ("abc", str),
        (None, type(None)),
    ],
)
def test_feature_id_coerced_to_native(value, expected_type):
    """Numpy scalars (e.g. int32 from shapefile id columns) coerce to native
    Python types so Pydantic can JSON-serialize them (regression for
    PydanticSerializationError: numpy.int32)."""
    issue = GeometryIssue(feature_id=value, type="topology_overlap", severity="warning")
    assert type(issue.feature_id) is expected_type


def test_validation_result_serializes_numpy_feature_id():
    """ValidationResult with a numpy feature_id serializes to JSON without error."""
    issue = GeometryIssue(
        feature_id=np.int32(10),
        type="topology_overlap",
        severity="warning",
        location=[1.5, 1.5],
        description="Overlap with feature 11",
    )
    result = ValidationResult(dataset_id="x", issues=[issue])
    payload = result.model_dump_json()
    assert '"feature_id":10' in payload
