"""API route handlers."""
from io import BytesIO
from pathlib import Path
import uuid

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from api.models import ErrorCode, ErrorResponse, UploadResponse, ValidationJobStatus, ValidateRequest, ValidationResult
from core.config import settings
from services.file_handler import (
    extract_zip_in_upload_dir,
    get_primary_vector_path,
    get_saved_file_path,
    get_upload_path,
    save_upload,
)
from services.geojson_parser import parse_geojson_metadata
from services.shapefile_parser import parse_shapefile_metadata
from agents.orchestrator import empty_state, validation_graph

router = APIRouter()

# In-memory store for async validation jobs (issue #64).
_validation_jobs: dict[str, dict] = {}


def _allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    suffix = Path(filename).suffix.lower()
    return suffix in settings.ALLOWED_EXTENSIONS


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        200: {"description": "Dataset uploaded successfully"},
        400: {"description": "Invalid or missing file", "model": ErrorResponse},
        413: {"description": "File too large", "model": ErrorResponse},
        500: {"description": "Server error saving file", "model": ErrorResponse},
    },
)
async def upload_dataset(file: UploadFile = File(..., description="Shapefile, GeoJSON, KML, or ZIP")):
    """
    Upload a geospatial dataset. Returns a unified UploadResponse with dataset_id,
    filename, and optional metadata (feature_count, geometry_type, crs, bounds).
    """
    if not file.filename or not file.filename.strip():
        raise HTTPException(
            status_code=400,
            detail={"detail": "No file provided. Send a file in the 'file' form field.", "code": ErrorCode.NO_FILE},
        )

    if not _allowed_file(file.filename):
        allowed = ", ".join(settings.ALLOWED_EXTENSIONS)
        raise HTTPException(
            status_code=400,
            detail={
                "detail": f"File type not allowed. Allowed extensions: {allowed}",
                "code": ErrorCode.INVALID_FILE_TYPE,
            },
        )

    contents = await file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail={
                "detail": f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB.",
                "code": ErrorCode.FILE_TOO_LARGE,
            },
        )

    try:
        dataset_id = save_upload(BytesIO(contents), file.filename)
    except OSError as e:
        raise HTTPException(
            status_code=500,
            detail={"detail": f"Failed to save file: {str(e)}", "code": ErrorCode.SAVE_FAILED},
        )

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


@router.post(
    "/validate",
    response_model=ValidationResult,
    responses={
        200: {"description": "Validation completed; issues list may be empty"},
        404: {"description": "Dataset not found", "model": ErrorResponse},
    },
)
async def validate_dataset(body: ValidateRequest):
    """
    Run the LangGraph validation workflow on an uploaded dataset (by dataset_id).
    Runs geometry, attribute, topology agents and generate_recommendations;
    routes by severity (critical -> apply_corrections). Returns issues for frontend.
    """
    path = get_primary_vector_path(body.dataset_id)
    if path is None or not path.exists():
        raise HTTPException(
            status_code=404,
            detail={
                "detail": f"Dataset not found or no vector file: {body.dataset_id}",
                "code": ErrorCode.DATASET_NOT_FOUND,
            },
        )
    initial_state = empty_state(body.dataset_id, str(path))
    final_state = validation_graph.invoke(initial_state)
    issues = final_state.get("issues") or []
    corrections = final_state.get("corrections") or []
    return ValidationResult(dataset_id=body.dataset_id, issues=issues, corrections=corrections if corrections else None)


@router.get(
    "/validate/{dataset_id}",
    response_model=ValidationResult,
    responses={
        200: {"description": "Validation results for the dataset"},
        404: {"description": "Dataset not found", "model": ErrorResponse},
    },
)
async def get_validation_results(dataset_id: str):
    """
    Run the LangGraph validation workflow for a dataset and return results (same as POST /validate).
    Runs geometry, attribute, topology agents; returns issues for frontend.
    """
    path = get_primary_vector_path(dataset_id)
    if path is None or not path.exists():
        raise HTTPException(
            status_code=404,
            detail={
                "detail": f"Dataset not found or no vector file: {dataset_id}",
                "code": ErrorCode.DATASET_NOT_FOUND,
            },
        )
    initial_state = empty_state(dataset_id, str(path))
    final_state = validation_graph.invoke(initial_state)
    issues = final_state.get("issues") or []
    corrections = final_state.get("corrections") or []
    return ValidationResult(dataset_id=dataset_id, issues=issues, corrections=corrections if corrections else None)


@router.post(
    "/validate/async",
    response_model=ValidationJobStatus,
    responses={
        200: {"description": "Enqueue async validation job"},
        404: {"description": "Dataset not found", "model": ErrorResponse},
    },
)
async def validate_dataset_async(body: ValidateRequest, background_tasks: BackgroundTasks):
    """
    Run validation asynchronously using the LangGraph workflow.

    Returns immediately with a job_id; the job can be polled via GET /validate/jobs/{job_id}.
    """
    path = get_primary_vector_path(body.dataset_id)
    if path is None or not path.exists():
        raise HTTPException(
            status_code=404,
            detail={
                "detail": f"Dataset not found or no vector file: {body.dataset_id}",
                "code": ErrorCode.DATASET_NOT_FOUND,
            },
        )

    job_id = str(uuid.uuid4())
    _validation_jobs[job_id] = {
        "job_id": job_id,
        "dataset_id": body.dataset_id,
        "status": "pending",
        "error": None,
        "result": None,
    }

    def _run_job(jid: str, dataset_id: str, dataset_path: str) -> None:
        # Mark as running
        job = _validation_jobs.get(jid)
        if not job:
            return
        job["status"] = "running"
        try:
            state = empty_state(dataset_id, dataset_path)
            final_state = validation_graph.invoke(state)
            issues = final_state.get("issues") or []
            corrections = final_state.get("corrections") or []
            result = ValidationResult(
                dataset_id=dataset_id,
                issues=issues,
                corrections=corrections if corrections else None,
            )
            job["result"] = result
            job["status"] = "completed"
        except Exception as exc:  # noqa: BLE001
            job["status"] = "failed"
            job["error"] = str(exc)

    background_tasks.add_task(_run_job, job_id, body.dataset_id, str(path))

    return ValidationJobStatus(
        job_id=job_id,
        dataset_id=body.dataset_id,
        status="pending",
        error=None,
        result=None,
    )


@router.get(
    "/validate/jobs/{job_id}",
    response_model=ValidationJobStatus,
    responses={
        200: {"description": "Status for an async validation job"},
        404: {"description": "Job not found", "model": ErrorResponse},
    },
)
async def get_validation_job(job_id: str):
    """
    Get status for an asynchronous validation job (issue #64).

    When status is 'completed', the response includes the ValidationResult in 'result'.
    """
    job = _validation_jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "detail": f"Validation job not found: {job_id}",
                "code": "JOB_NOT_FOUND",
            },
        )
    return ValidationJobStatus(**job)


@router.get(
    "/datasets/{dataset_id}/geojson",
    response_class=FileResponse,
    responses={
        200: {"description": "GeoJSON file", "content": {"application/geo+json": {}}},
        400: {"description": "No vector file for dataset", "model": ErrorResponse},
        404: {"description": "Dataset not found", "model": ErrorResponse},
    },
)
async def get_dataset_geojson(dataset_id: str):
    """
    Return the primary vector file (e.g. GeoJSON) for a dataset for map display.
    """
    path = get_primary_vector_path(dataset_id)
    if path is None:
        raise HTTPException(
            status_code=400,
            detail={
                "detail": "No vector file available for this dataset.",
                "code": ErrorCode.DATASET_NOT_FOUND,
            },
        )
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail={
                "detail": f"Dataset not found: {dataset_id}",
                "code": ErrorCode.DATASET_NOT_FOUND,
            },
        )
    return FileResponse(path, media_type="application/geo+json")