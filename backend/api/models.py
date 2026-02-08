"""Pydantic schemas for API request/response."""
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response after successful dataset upload."""

    dataset_id: str = Field(..., description="Unique identifier for the uploaded dataset")
    filename: str = Field(..., description="Original filename")
    feature_count: int = Field(0, description="Number of features (0 until parsed)")
    geometry_type: Optional[str] = Field(None, description="Geometry type e.g. Polygon, Point")
    crs: Optional[str] = Field(None, description="Coordinate reference system e.g. EPSG:4326")
    bounds: Optional[List[float]] = Field(None, description="[minX, minY, maxX, maxY]")


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Optional error code")
