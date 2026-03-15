"""Pydantic schemas for API request/response."""
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class GeometryIssue(BaseModel):
    """A single geometry validation issue."""

    feature_id: Any = Field(..., description="Feature identifier (index or id column)")
    type: str = Field(..., description="Issue type: empty_geometry, invalid_geometry, self_intersection")
    severity: str = Field(..., description="critical or warning")
    location: Optional[List[float]] = Field(None, description="[x, y] for map display")
    description: Optional[str] = Field(None, description="Human-readable reason")


# Error codes for consistent API error responses
class ErrorCode:
    """Error codes returned in API error responses."""

    NO_FILE = "NO_FILE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    SAVE_FAILED = "SAVE_FAILED"
    DATASET_NOT_FOUND = "DATASET_NOT_FOUND"


class UploadResponse(BaseModel):
    """Unified response after successful dataset upload. All upload endpoints return this schema."""

    dataset_id: str = Field(..., description="Unique identifier for the uploaded dataset")
    filename: str = Field(..., description="Original filename")
    feature_count: int = Field(0, description="Number of features (0 if not parsed)")
    geometry_type: Optional[str] = Field(None, description="Geometry type e.g. Polygon, Point")
    crs: Optional[str] = Field(None, description="Coordinate reference system e.g. EPSG:4326")
    bounds: Optional[List[float]] = Field(None, description="[minX, minY, maxX, maxY]")


class CorrectionSuggestion(BaseModel):
    """
    A suggested fix for a validation issue (issue #86, #9).

    Used by the Recommendation Agent and apply-corrections API. issue_index links
    this suggestion to state["issues"][issue_index] (or the validation result issues list).
    """

    method: str = Field(..., description="Suggested fix e.g. buffer(0), rename field, snap to grid")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0–1")
    explanation: str = Field(..., description="Natural-language explanation for the suggestion")
    issue_index: int = Field(..., ge=0, description="Index into the issues list this suggestion applies to")


class CorrectionAction(BaseModel):
    """User decision for one correction (apply-corrections API request body)."""

    issue_index: int = Field(..., ge=0, description="Index into the issues list")
    action: Literal["approve", "reject"] = Field(..., description="Whether to apply or skip this correction")


class ApplyCorrectionsRequest(BaseModel):
    """Request body for POST /corrections/apply (issue #86)."""

    dataset_id: str = Field(..., description="Dataset identifier")
    corrections: List[CorrectionAction] = Field(
        default_factory=list,
        description="List of approve/reject decisions per issue index",
    )


class ValidationResult(BaseModel):
    """Result of geometry validation for a dataset."""

    dataset_id: str = Field(..., description="Dataset identifier that was validated")
    issues: List[GeometryIssue] = Field(default_factory=list, description="List of geometry issues found")
    corrections: Optional[List[CorrectionSuggestion]] = Field(
        None,
        description="Suggested fixes from Recommendation Agent (one per issue or subset); indices match issues list",
    )


class ValidationJobStatus(BaseModel):
    """Status of an asynchronous validation job."""

    job_id: str = Field(..., description="Unique identifier for the validation job")
    dataset_id: str = Field(..., description="Dataset identifier that is being validated")
    status: str = Field(..., description="Job status: pending, running, completed, or failed")
    error: Optional[str] = Field(None, description="Error message when status is failed")
    result: Optional[ValidationResult] = Field(
        None, description="ValidationResult when status is completed (may be omitted for large payloads)"
    )


class ValidateRequest(BaseModel):
    """Request body for POST /validate."""

    dataset_id: str = Field(..., description="Dataset identifier (from upload) to validate")


class ErrorResponse(BaseModel):
    """Standard error response for failed requests."""

    detail: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")
