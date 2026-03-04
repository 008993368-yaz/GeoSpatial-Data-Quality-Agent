"""Tests for API routes."""
import pytest


def test_get_dataset_geojson_success(client, tmp_path, monkeypatch):
    """GET /api/v1/datasets/{id}/geojson returns 200 and GeoJSON when dataset exists."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    dataset_id = "test-dataset-id"
    (tmp_path / dataset_id).mkdir()
    geojson_content = '{"type":"FeatureCollection","features":[]}'
    (tmp_path / dataset_id / "data.geojson").write_text(geojson_content)

    response = client.get(f"/api/v1/datasets/{dataset_id}/geojson")

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/geo+json")
    assert response.text == geojson_content


def test_get_dataset_geojson_not_found(client, tmp_path, monkeypatch):
    """GET /api/v1/datasets/{id}/geojson returns 400 when dataset dir does not exist."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))

    response = client.get("/api/v1/datasets/nonexistent-id/geojson")

    assert response.status_code == 400
    data = response.json()
    assert data.get("detail", {}).get("code") == "DATASET_NOT_FOUND"
