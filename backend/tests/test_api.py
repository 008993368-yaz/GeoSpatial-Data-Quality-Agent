"""Tests for API upload route and error handling."""
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
    # Send file with empty filename to trigger "No file provided"
    r = client.post("/api/v1/upload", files={"file": ("", b"content")})
    assert r.status_code == 400
    data = r.json()
    assert data.get("code") == ErrorCode.NO_FILE
    assert "detail" in data


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
    assert data.get("code") == ErrorCode.INVALID_FILE_TYPE
    assert "Allowed extensions" in data.get("detail", "")


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
