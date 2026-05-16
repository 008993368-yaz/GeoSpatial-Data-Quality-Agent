"""Tests for correction_applier service (issue #106)."""
import json

import geopandas as gpd
from shapely.geometry import Point

from services.correction_applier import apply_correction_overrides


def _write_points_geojson(path, coords):
    gdf = gpd.GeoDataFrame(
        {"id": list(range(len(coords))), "name": [f"P{i}" for i in range(len(coords))]},
        geometry=[Point(x, y) for x, y in coords],
        crs="EPSG:4326",
    )
    gdf.to_file(path, driver="GeoJSON")


def test_apply_geometry_wkt_updates_feature(tmp_path):
    geojson_path = tmp_path / "data.geojson"
    _write_points_geojson(geojson_path, [(-122.4, 37.77)])

    mutated = apply_correction_overrides(
        geojson_path,
        [
            {
                "action": "approve",
                "feature_id": 0,
                "geometry_wkt": "POINT (-122.5 37.8)",
            }
        ],
    )
    assert mutated == 1

    gdf = gpd.read_file(geojson_path)
    pt = gdf.geometry.iloc[0]
    assert abs(pt.x + 122.5) < 1e-6
    assert abs(pt.y - 37.8) < 1e-6


def test_apply_attributes_updates_properties(tmp_path):
    geojson_path = tmp_path / "data.geojson"
    _write_points_geojson(geojson_path, [(-122.4, 37.77)])

    mutated = apply_correction_overrides(
        geojson_path,
        [
            {
                "action": "approve",
                "feature_id": 0,
                "attributes": {"name": "Updated", "score": 99},
            }
        ],
    )
    assert mutated == 1

    raw = json.loads(geojson_path.read_text(encoding="utf-8"))
    props = raw["features"][0]["properties"]
    assert props["name"] == "Updated"
    assert props["score"] == 99


def test_invalid_wkt_raises(tmp_path):
    geojson_path = tmp_path / "data.geojson"
    _write_points_geojson(geojson_path, [(-122.4, 37.77)])

    try:
        apply_correction_overrides(
            geojson_path,
            [{"action": "approve", "feature_id": 0, "geometry_wkt": "NOT VALID WKT"}],
        )
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "Invalid WKT" in str(exc)
