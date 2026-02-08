"""Tests for API upload route, validate route, and error handling."""
from pathlib import Path

import pytest
from api.models import ErrorCode


def test_health(client):
    """Health endpoint returns ok."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_upload_no_file(client):
    """Upload with empty filename returns 400 with NO_FILE code."""
    # Send file with whitespace-only filename so FastAPI accepts it; our handler treats as no file
    r = client.post("/api/v1/upload", files={"file": ("   ", b"content")})
    assert r.status_code == 400
    data = r.json()
    # FastAPI may nest our detail in response["detail"]
    detail = data.get("detail")
    code = detail.get("code") if isinstance(detail, dict) else data.get("code")
    assert code == ErrorCode.NO_FILE
    assert detail is not None or "detail" in data


def test_upload_invalid_file_type(client):
    """Upload with disallowed extension returns 400 with INVALID_FILE_TYPE."""
    path = Path(__file__).parent.parent / "resources" / "sample.geojson"
    if not path.exists():
        pytest.skip("sample.geojson not found")
    # Send with wrong extension by using a different filename
    r = client.post(
        "/api/v1/upload",
        files={"file": ("bad.pdf", path.read_bytes(), "application/pdf")},
    )
    assert r.status_code == 400
    data = r.json()
    detail = data.get("detail")
    code = detail.get("code") if isinstance(detail, dict) else data.get("code")
    msg = detail.get("detail", detail) if isinstance(detail, dict) else str(detail or "")
    assert code == ErrorCode.INVALID_FILE_TYPE
    assert "Allowed extensions" in msg


def test_upload_success_geojson(client):
    """Upload valid GeoJSON returns 200 and unified UploadResponse."""
    path = Path(__file__).parent.parent / "resources" / "sample.geojson"
    if not path.exists():
        pytest.skip("sample.geojson not found")
    r = client.post(
        "/api/v1/upload",
        files={"file": ("sample.geojson", path.read_bytes(), "application/geo+json")},
    )
    assert r.status_code == 200
    data = r.json()
    assert "dataset_id" in data
    assert data["filename"] == "sample.geojson"
    assert data["feature_count"] >= 0
    assert "geometry_type" in data
    assert "crs" in data or data["crs"] is None
    assert "bounds" in data or data["bounds"] is None


def test_validate_dataset_not_found(client):
    """POST /validate with unknown dataset_id returns 404 with DATASET_NOT_FOUND."""
    r = client.post("/api/v1/validate", json={"dataset_id": "00000000-0000-0000-0000-000000000000"})
    assert r.status_code == 404
    detail = r.json().get("detail")
    code = detail.get("code") if isinstance(detail, dict) else r.json().get("code")
    assert code == ErrorCode.DATASET_NOT_FOUND


def test_get_validation_not_found(client):
    """GET /validate/{dataset_id} with unknown dataset_id returns 404."""
    r = client.get("/api/v1/validate/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    detail = r.json().get("detail")
    code = detail.get("code") if isinstance(detail, dict) else r.json().get("code")
    assert code == ErrorCode.DATASET_NOT_FOUND


def test_post_validate_success(client):
    """POST /validate with valid dataset_id returns ValidationResult with issues list."""
    path = Path(__file__).parent.parent / "resources" / "sample.geojson"
    if not path.exists():
        pytest.skip("sample.geojson not found")
    upload = client.post(
        "/api/v1/upload",
        files={"file": ("sample.geojson", path.read_bytes(), "application/geo+json")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["dataset_id"]
    r = client.post("/api/v1/validate", json={"dataset_id": dataset_id})
    assert r.status_code == 200
    data = r.json()
    assert data["dataset_id"] == dataset_id
    assert "issues" in data
    assert isinstance(data["issues"], list)
    for issue in data["issues"]:
        assert "feature_id" in issue and "type" in issue and "severity" in issue


def test_get_validate_success(client):
    """GET /validate/{dataset_id} returns same ValidationResult shape."""
    path = Path(__file__).parent.parent / "resources" / "sample.geojson"
    if not path.exists():
        pytest.skip("sample.geojson not found")
    upload = client.post(
        "/api/v1/upload",
        files={"file": ("sample.geojson", path.read_bytes(), "application/geo+json")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["dataset_id"]
    r = client.get(f"/api/v1/validate/{dataset_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["dataset_id"] == dataset_id
    assert "issues" in data
    assert isinstance(data["issues"], list)
