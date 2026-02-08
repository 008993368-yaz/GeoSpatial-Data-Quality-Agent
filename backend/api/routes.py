"""API route handlers."""
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from api.models import UploadResponse
from core.config import settings
from services.file_handler import (
    extract_zip_in_upload_dir,
    get_saved_file_path,
    get_upload_path,
    save_upload,
)
from services.geojson_parser import parse_geojson_metadata
from services.shapefile_parser import parse_shapefile_metadata

router = APIRouter()


def _allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    suffix = Path(filename).suffix.lower()
    return suffix in settings.ALLOWED_EXTENSIONS


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        200: {"description": "Dataset uploaded successfully"},
        400: {"description": "Invalid or missing file"},
        413: {"description": "File too large"},
    },
)
async def upload_dataset(file: UploadFile = File(..., description="Shapefile, GeoJSON, or KML file")):
    """
    Upload a geospatial dataset (Shapefile, GeoJSON, KML/KMZ).
    File is saved to UPLOAD_DIR under a new dataset_id.
    """
    if not file.filename or not file.filename.strip():
        raise HTTPException(status_code=400, detail="No file provided")

    if not _allowed_file(file.filename):
        allowed = ", ".join(settings.ALLOWED_EXTENSIONS)
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed extensions: {allowed}",
        )

    # Read into memory to check size (for async UploadFile we read once then pass)
    contents = await file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    try:
        dataset_id = save_upload(BytesIO(contents), file.filename)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Extract metadata for shapefiles (.shp + sidecar .shx, .dbf in same dir)
    feature_count = 0
    geometry_type = None
    crs = None
    bounds = None
    suffix = Path(file.filename).suffix.lower()
    if suffix == ".zip":
        extract_zip_in_upload_dir(dataset_id)
    if suffix in (".shp", ".zip"):
        upload_dir = get_upload_path(dataset_id)
        meta = parse_shapefile_metadata(upload_dir)
        if meta:
            feature_count = meta["feature_count"]
            geometry_type = meta["geometry_type"]
            crs = meta["crs"]
            bounds = meta["bounds"]
    elif suffix in (".geojson", ".json"):
        saved_path = get_saved_file_path(dataset_id, file.filename)
        meta = parse_geojson_metadata(saved_path)
        if meta:
            feature_count = meta["feature_count"]
            geometry_type = meta["geometry_type"]
            crs = meta["crs"]
            bounds = meta["bounds"]

    return UploadResponse(
        dataset_id=dataset_id,
        filename=file.filename,
        feature_count=feature_count,
        geometry_type=geometry_type,
        crs=crs,
        bounds=bounds,
    )