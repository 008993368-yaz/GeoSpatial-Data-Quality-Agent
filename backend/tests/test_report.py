"""Tests for quality report endpoints (issue #12)."""
import json

from services.report_builder import export_report_bytes, get_validation_config, render_report_markdown


def _sample_payload() -> dict:
    return {
        "generated_at": "2026-05-16T12:00:00Z",
        "dataset": {
            "dataset_id": "test-dataset",
            "filename": "sample.geojson",
            "feature_count": 10,
            "geometry_type": "Polygon",
            "crs": "EPSG:4326",
            "bounds": [-1.0, -1.0, 1.0, 1.0],
        },
        "validation": {
            "dataset_id": "test-dataset",
            "issues": [
                {
                    "feature_id": 0,
                    "type": "invalid_geometry",
                    "severity": "critical",
                    "description": "Invalid ring",
                },
                {
                    "feature_id": 1,
                    "type": "attribute_missing",
                    "severity": "warning",
                    "description": "Missing field",
                },
            ],
            "corrections": [
                {
                    "method": "buffer(0)",
                    "confidence": 0.9,
                    "explanation": "Fix geometry",
                    "issue_index": 0,
                }
            ],
        },
        "summary": {
            "totalIssues": 2,
            "critical": 1,
            "warning": 1,
            "byCategory": {"geometry": 1, "attribute": 1, "topology": 0},
            "byType": {"invalid_geometry": 1, "attribute_missing": 1},
        },
        "validation_config": get_validation_config(),
    }


def test_get_validation_config():
    cfg = get_validation_config()
    assert cfg["geometry_validation_enabled"] is True
    assert "geometry_validation" in cfg["pipeline_steps"][0]
    assert cfg["topology_checks"]["gaps"] is True


def test_render_report_markdown():
    md = render_report_markdown(_sample_payload())
    assert "# Quality assessment report" in md
    assert "sample.geojson" in md
    assert "invalid_geometry" in md


def test_export_report_bytes_json():
    content, media_type, filename = export_report_bytes(_sample_payload(), "json")
    assert media_type == "application/json"
    assert filename.endswith(".json")
    data = json.loads(content.decode("utf-8"))
    assert data["dataset"]["dataset_id"] == "test-dataset"


def test_export_report_bytes_markdown():
    content, media_type, filename = export_report_bytes(_sample_payload(), "markdown")
    assert "text/markdown" in media_type
    assert filename.endswith(".md")
    assert b"Quality assessment report" in content


def test_validation_config_endpoint(client):
    res = client.get("/api/v1/validation/config")
    assert res.status_code == 200
    data = res.json()
    assert "pipeline_steps" in data
    assert data["openai_model"]


def test_export_report_endpoint_json(client):
    res = client.post(
        "/api/v1/reports/export?format=json",
        json=_sample_payload(),
    )
    assert res.status_code == 200
    assert "application/json" in res.headers.get("content-type", "")
    assert "attachment" in res.headers.get("content-disposition", "").lower()
    data = res.json()
    assert data["summary"]["totalIssues"] == 2


def test_export_report_endpoint_markdown(client):
    res = client.post(
        "/api/v1/reports/export?format=markdown",
        json=_sample_payload(),
    )
    assert res.status_code == 200
    assert "text/markdown" in res.headers.get("content-type", "")
    assert b"Quality assessment report" in res.content
