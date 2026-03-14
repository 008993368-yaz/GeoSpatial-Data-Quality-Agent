"""Tests for services.attribute_extractor (issue #74)."""
import geopandas as gpd
import pytest
from shapely.geometry import Point

from services.attribute_extractor import (
    DEFAULT_ATTRIBUTE_SAMPLE_SIZE,
    get_attribute_columns,
    get_attribute_records,
    load_attributes_from_path,
)


def _gdf_with_attrs(n_rows: int, with_id_col: bool = False):
    gdf = gpd.GeoDataFrame(
        {"name": [f"f{i}" for i in range(n_rows)], "value": list(range(n_rows))},
        geometry=[Point(i, i) for i in range(n_rows)],
    )
    if with_id_col:
        gdf["id"] = [100 + i for i in range(n_rows)]
    return gdf


def test_get_attribute_records_no_geometry():
    """Output has no geometry key and only attribute columns."""
    gdf = _gdf_with_attrs(3)
    records = get_attribute_records(gdf, sample_size=10)
    assert len(records) == 3
    for r in records:
        assert "geometry" not in r
        assert "feature_id" in r
        assert "name" in r
        assert "value" in r


def test_get_attribute_records_respects_sample_size():
    """Sampling caps number of rows returned."""
    gdf = _gdf_with_attrs(200)
    records = get_attribute_records(gdf, sample_size=50, random_state=42)
    assert len(records) == 50


def test_get_attribute_records_uses_index_as_feature_id():
    """feature_id is the DataFrame index when no 'id' column."""
    gdf = _gdf_with_attrs(2)
    gdf.index = [7, 8]
    records = get_attribute_records(gdf, sample_size=10)
    fid_set = {r["feature_id"] for r in records}
    assert fid_set == {7, 8}


def test_get_attribute_records_uses_id_column_when_present():
    """feature_id is from 'id' column when present."""
    gdf = _gdf_with_attrs(2, with_id_col=True)
    records = get_attribute_records(gdf, sample_size=10)
    fid_set = {r["feature_id"] for r in records}
    assert fid_set == {100, 101}


def test_get_attribute_columns_no_geometry():
    """Per-field output has no geometry column."""
    gdf = _gdf_with_attrs(3)
    cols = get_attribute_columns(gdf, sample_size=10)
    assert "geometry" not in cols
    assert "name" in cols
    assert "value" in cols
    assert len(cols["name"]) == 3


def test_get_attribute_columns_respects_sample_size():
    """Sampling caps number of values per column."""
    gdf = _gdf_with_attrs(200)
    cols = get_attribute_columns(gdf, sample_size=50, random_state=42)
    assert len(cols["name"]) == 50
    assert len(cols["value"]) == 50


def test_empty_gdf_returns_empty():
    """Empty GeoDataFrame returns empty list/dict."""
    gdf = gpd.GeoDataFrame(geometry=[])
    assert get_attribute_records(gdf) == []
    assert get_attribute_columns(gdf) == {}


def test_default_sample_size_used():
    """When sample_size is None, default caps rows."""
    gdf = _gdf_with_attrs(DEFAULT_ATTRIBUTE_SAMPLE_SIZE + 100)
    records = get_attribute_records(gdf, random_state=0)
    assert len(records) == DEFAULT_ATTRIBUTE_SAMPLE_SIZE


def test_load_attributes_from_path_as_records(tmp_path):
    """load_attributes_from_path with as_records returns list of dicts."""
    gdf = _gdf_with_attrs(2)
    path = tmp_path / "test.geojson"
    gdf.to_file(path, driver="GeoJSON")
    out = load_attributes_from_path(path, sample_size=10, as_records=True)
    assert isinstance(out, list)
    assert len(out) == 2
    assert all("feature_id" in r and "geometry" not in r for r in out)


def test_load_attributes_from_path_as_columns(tmp_path):
    """load_attributes_from_path with as_records=False returns per-field dict."""
    gdf = _gdf_with_attrs(2)
    path = tmp_path / "test.geojson"
    gdf.to_file(path, driver="GeoJSON")
    out = load_attributes_from_path(path, sample_size=10, as_records=False)
    assert isinstance(out, dict)
    assert "geometry" not in out
    assert "name" in out and len(out["name"]) == 2


def test_get_attribute_records_respects_max_fields():
    """max_fields limits number of attribute columns (issue #70)."""
    gdf = gpd.GeoDataFrame(
        {"a": [1], "b": [2], "c": [3]},
        geometry=[Point(0, 0)],
    )
    records = get_attribute_records(gdf, sample_size=10, max_fields=2)
    assert len(records) == 1
    assert "a" in records[0] and "b" in records[0]
    assert "c" not in records[0]
