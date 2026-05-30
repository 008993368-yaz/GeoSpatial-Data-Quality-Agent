"""Pydantic schemas for API request/response."""
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


def _to_native(value: Any) -> Any:
    """Coerce numpy scalars (e.g. int32 from shapefile/GeoJSON id columns) to native
    Python types so Pydantic can JSON-serialize them. Leaves other values untouched."""
    item = getattr(value, "item", None)
    if callable(item) and getattr(value, "ndim", None) == 0:
        # numpy scalar: 0-dim array-like with .item()
        try:
            return value.item()
        except Exception:
            return value
    return value


class GeometryIssue(BaseModel):
    """A single geometry validation issue."""

    feature_id: Any = Field(..., description="Feature identifier (index or id column)")
    type: str = Field(..., description="Issue type: empty_geometry, invalid_geometry, self_intersection")
    severity: str = Field(..., description="critical or warning")
    location: Optional[List[float]] = Field(None, description="[x, y] for map display")
    description: Optional[str] = Field(None, description="Human-readable reason")

    @field_validator("feature_id", mode="before")
    @classmethod
    def _coerce_feature_id(cls, v: Any) -> Any:
        return _to_native(v)


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
    feature_id: Optional[Any] = Field(
        None,
        description="Feature to update when geometry_wkt or attributes overrides are supplied (issue #106)",
    )
    geometry_wkt: Optional[str] = Field(
        None,
        description="Optional Well-Known Text geometry to apply for this feature when action is approve",
    )
    attributes: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional attribute key/value overrides for this feature when action is approve",
    )


class ApplyCorrectionsRequest(BaseModel):
    """Request body for POST /corrections/apply (issue #86)."""

    dataset_id: str = Field(..., description="Dataset identifier")
    corrections: List[CorrectionAction] = Field(
        default_factory=list,
        description="List of approve/reject decisions per issue index",
    )


class ApplyCorrectionsResponse(BaseModel):
    """Response from POST /corrections/apply (README + issue #104, UX #105)."""

    applied: int = Field(..., ge=0, description="Number of corrections approved for application")
    skipped: int = Field(..., ge=0, description="Number of corrections rejected (skipped)")
    download_url: Optional[str] = Field(
        None,
        description="Optional URL to download cleaned export when implemented; may point at dataset GeoJSON meanwhile",
    )
    export_note: Optional[str] = Field(
        None,
        description="Short human-readable note about what the download contains (issue #105)",
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


class TopologyChecksConfig(BaseModel):
    """Topology validation toggles exposed in reports (issue #12)."""

    gaps: bool = True
    overlaps: bool = True
    connectivity: bool = True


class ValidationConfigResponse(BaseModel):
    """Public validation pipeline settings for quality reports (issue #12)."""

    pipeline_steps: List[str] = Field(
        ...,
        description="Ordered LangGraph pipeline steps",
    )
    geometry_validation_enabled: bool = True
    attribute_sample_size: int = 500
    attribute_max_records_in_prompt: int = 10
    openai_model: str = "gpt-4o-mini"
    topology_checks: TopologyChecksConfig = Field(default_factory=TopologyChecksConfig)


class QualityReportRequest(BaseModel):
    """Client-built quality report document for server-side export (issue #12)."""

    generated_at: str
    dataset: UploadResponse
    validation: ValidationResult
    summary: Dict[str, Any] = Field(..., description="Issue summary counts and breakdowns")
    correction_decisions: Optional[Dict[str, Any]] = None
    validation_config: Optional[ValidationConfigResponse] = None


class ErrorResponse(BaseModel):
    """Standard error response for failed requests."""

    detail: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")
