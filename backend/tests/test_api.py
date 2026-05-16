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
    assert data.get("export_note")


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


def test_apply_corrections_with_geometry_override(client, tmp_path, monkeypatch):
    """POST /corrections/apply applies geometry_wkt to GeoJSON when provided."""
    import geopandas as gpd
    from shapely.geometry import Point

    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    dataset_id = "ds-override"
    dest = tmp_path / dataset_id
    dest.mkdir()
    geojson_path = dest / "data.geojson"
    gdf = gpd.GeoDataFrame(
        {"id": [1], "name": ["A"]},
        geometry=[Point(-122.4, 37.77)],
        crs="EPSG:4326",
    )
    gdf.to_file(geojson_path, driver="GeoJSON")

    response = client.post(
        "/api/v1/corrections/apply",
        json={
            "dataset_id": dataset_id,
            "corrections": [
                {
                    "issue_index": 0,
                    "action": "approve",
                    "feature_id": 1,
                    "geometry_wkt": "POINT (-122.5 37.8)",
                }
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["applied"] == 1
    assert "manual overrides" in (data.get("export_note") or "").lower()

    updated = gpd.read_file(geojson_path)
    assert abs(updated.geometry.iloc[0].x + 122.5) < 1e-6


def test_apply_corrections_invalid_wkt_returns_400(client, tmp_path, monkeypatch):
    """Invalid geometry_wkt returns 400 with INVALID_OVERRIDE."""
    import geopandas as gpd
    from shapely.geometry import Point

    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    dataset_id = "ds-bad-wkt"
    dest = tmp_path / dataset_id
    dest.mkdir()
    geojson_path = dest / "data.geojson"
    gpd.GeoDataFrame({"id": [0]}, geometry=[Point(0, 0)], crs="EPSG:4326").to_file(
        geojson_path, driver="GeoJSON"
    )

    response = client.post(
        "/api/v1/corrections/apply",
        json={
            "dataset_id": dataset_id,
            "corrections": [
                {
                    "issue_index": 0,
                    "action": "approve",
                    "feature_id": 0,
                    "geometry_wkt": "NOT VALID",
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json().get("detail", {}).get("code") == "INVALID_OVERRIDE"


def test_apply_corrections_dataset_not_found(client, tmp_path, monkeypatch):
    """POST /corrections/apply returns 404 when dataset has no vector file."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))

    response = client.post(
        "/api/v1/corrections/apply",
        json={"dataset_id": "missing", "corrections": [{"issue_index": 0, "action": "approve"}]},
    )

    assert response.status_code == 404
