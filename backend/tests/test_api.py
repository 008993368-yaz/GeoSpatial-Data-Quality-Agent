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


def test_apply_corrections_empty_returns_400(client):
    """POST /corrections/apply returns 400 when corrections list is empty."""
    response = client.post(
        "/api/v1/corrections/apply",
        json={"dataset_id": "any", "corrections": []},
    )
    assert response.status_code == 400


def test_apply_corrections_success(client, tmp_path, monkeypatch):
    """POST /corrections/apply returns applied/skipped counts when dataset exists."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    dataset_id = "ds-apply"
    (tmp_path / dataset_id).mkdir()
    (tmp_path / dataset_id / "data.geojson").write_text('{"type":"FeatureCollection","features":[]}')

    response = client.post(
        "/api/v1/corrections/apply",
        json={
            "dataset_id": dataset_id,
            "corrections": [
                {"issue_index": 0, "action": "approve"},
                {"issue_index": 1, "action": "reject"},
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["applied"] == 1
    assert data["skipped"] == 1
    assert dataset_id in (data.get("download_url") or "")


def test_apply_corrections_duplicate_issue_index_last_wins(client, tmp_path, monkeypatch):
    """Duplicate issue_index in body: last action wins for counts."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    dataset_id = "ds-dup"
    (tmp_path / dataset_id).mkdir()
    (tmp_path / dataset_id / "data.geojson").write_text('{"type":"FeatureCollection","features":[]}')

    response = client.post(
        "/api/v1/corrections/apply",
        json={
            "dataset_id": dataset_id,
            "corrections": [
                {"issue_index": 0, "action": "approve"},
                {"issue_index": 0, "action": "reject"},
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["applied"] == 0
    assert data["skipped"] == 1


def test_apply_corrections_dataset_not_found(client, tmp_path, monkeypatch):
    """POST /corrections/apply returns 404 when dataset has no vector file."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))

    response = client.post(
        "/api/v1/corrections/apply",
        json={"dataset_id": "missing", "corrections": [{"issue_index": 0, "action": "approve"}]},
    )

    assert response.status_code == 404
