"""Pydantic schemas for API request/response."""
from typing import Any, List, Optional

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


class ValidationResult(BaseModel):
    """Result of geometry validation for a dataset."""

    dataset_id: str = Field(..., description="Dataset identifier that was validated")
    issues: List[GeometryIssue] = Field(default_factory=list, description="List of geometry issues found")


class ValidateRequest(BaseModel):
    """Request body for POST /validate."""

    dataset_id: str = Field(..., description="Dataset identifier (from upload) to validate")


class ErrorResponse(BaseModel):
    """Standard error response for failed requests."""

    detail: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")
