"""File I/O operations for uploads and outputs."""
import shutil
import uuid
from pathlib import Path
from typing import BinaryIO

from core.config import settings


def save_upload(file: BinaryIO, filename: str) -> str:
    """
    Save an uploaded file to UPLOAD_DIR under a new dataset_id.
    Returns the dataset_id (UUID string).
    """
    dataset_id = str(uuid.uuid4())
    dest_dir = settings.upload_path / dataset_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / _sanitize_filename(filename)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file, f)
    return dataset_id


def get_upload_path(dataset_id: str) -> Path:
    """Return the directory path for a given dataset_id."""
    return settings.upload_path / dataset_id


def _sanitize_filename(name: str) -> str:
    """Keep only safe filename characters."""
    safe = "".join(c for c in name if c.isalnum() or c in "._- ")
    return safe.strip() or "upload"
