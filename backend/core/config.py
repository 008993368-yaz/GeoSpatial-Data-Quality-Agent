"""Configuration management for the backend."""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # File upload
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"
    OUTPUT_DIR: str = "./outputs"

    # Geometry validation (POST/GET /validate): all checks enabled by default
    # Checks: null/empty geometry, invalid geometry, self-intersection (see core.validation)
    GEOMETRY_VALIDATION_ENABLED: bool = True

    # Allowed geospatial file extensions (lowercase)
    ALLOWED_EXTENSIONS: List[str] = [
        ".shp",
        ".zip",  # Shapefile as zip (.shp + .shx, .dbf, .prj)
        ".geojson",
        ".json",  # GeoJSON often has .json
        ".kml",
        ".kmz",
    ]

    @property
    def max_upload_size_bytes(self) -> int:
        """Max upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        """Resolved upload directory path."""
        p = Path(self.UPLOAD_DIR).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def output_path(self) -> Path:
        """Resolved output directory path."""
        p = Path(self.OUTPUT_DIR).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins as a list."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
