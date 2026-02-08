"""Tests for services.file_handler."""
import io
from pathlib import Path

import pytest

# Backend on path via conftest
from services.file_handler import (
    _sanitize_filename,
    extract_zip_in_upload_dir,
    get_primary_vector_path,
    get_saved_file_path,
    get_upload_path,
    save_upload,
)


def test_sanitize_filename():
    """Sanitize keeps alphanumeric and ._- space."""
    assert _sanitize_filename("valid.geojson") == "valid.geojson"
    assert _sanitize_filename("  parks.shp  ") == "parks.shp"
    assert _sanitize_filename("file with spaces.json") == "file with spaces.json"
    # Strip path-like or unsafe
    safe = _sanitize_filename("../../etc/passwd")
    assert ".." not in safe and "/" not in safe


def test_save_upload_returns_uuid(tmp_path, monkeypatch):
    """save_upload creates dataset dir and returns a UUID string."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    content = io.BytesIO(b"test content")
    dataset_id = save_upload(content, "test.geojson")
    assert dataset_id
    assert len(dataset_id) == 36  # UUID format
    dest_dir = tmp_path / dataset_id
    assert dest_dir.is_dir()
    assert (dest_dir / "test.geojson").read_bytes() == b"test content"


def test_get_upload_path():
    """get_upload_path returns path under upload_path."""
    path = get_upload_path("some-uuid")
    assert "some-uuid" in str(path)


def test_get_saved_file_path():
    """get_saved_file_path combines dataset dir and sanitized filename."""
    path = get_saved_file_path("abc-123", "my file.geojson")
    assert path.name == "my file.geojson"
    assert "abc-123" in str(path)


def test_extract_zip_in_upload_dir_no_zip(tmp_path, monkeypatch):
    """extract_zip_in_upload_dir returns False when no zip in dir."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    dataset_id = "no-zip-dataset"
    (tmp_path / dataset_id).mkdir()
    assert extract_zip_in_upload_dir(dataset_id) is False


def test_extract_zip_in_upload_dir_with_zip(tmp_path, monkeypatch):
    """extract_zip_in_upload_dir extracts when single zip present."""
    import zipfile
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    dataset_id = "zip-dataset"
    dest_dir = tmp_path / dataset_id
    dest_dir.mkdir()
    zip_path = dest_dir / "data.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("inside.txt", "hello")
    assert extract_zip_in_upload_dir(dataset_id) is True
    assert (dest_dir / "inside.txt").read_text() == "hello"


def test_get_primary_vector_path_missing(tmp_path, monkeypatch):
    """get_primary_vector_path returns None when dataset dir does not exist."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    assert get_primary_vector_path("nonexistent-id") is None


def test_get_primary_vector_path_geojson(tmp_path, monkeypatch):
    """get_primary_vector_path returns path to .geojson when present."""
    monkeypatch.setattr("core.config.settings.UPLOAD_DIR", str(tmp_path))
    dataset_id = "geo-dataset"
    dest_dir = tmp_path / dataset_id
    dest_dir.mkdir()
    (dest_dir / "data.geojson").write_text("{}")
    path = get_primary_vector_path(dataset_id)
    assert path is not None
    assert path.name == "data.geojson"
