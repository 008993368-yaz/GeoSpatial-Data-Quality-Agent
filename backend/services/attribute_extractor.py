"""
Extract and sample attribute data from vector datasets for LLM-based validation (issue #74).

Provides two representations:
- Per-feature records: list of dicts (feature_id + attribute columns), for cross-feature consistency.
- Per-field value lists: dict of column name -> list of values, for outlier/typo analysis per field.

Sampling limits row count to control token usage and cost; geometry is never included in output.

Trade-offs and defaults:
- Default sample size is 500 (DEFAULT_ATTRIBUTE_SAMPLE_SIZE). Callers can pass sample_size or use
  backend.core.config.settings.ATTRIBUTE_SAMPLE_SIZE for a configurable default.
- Larger sample_size improves coverage (more features seen by the LLM) but increases tokens and cost.
- Use random_state for reproducible runs (e.g. in tests or repeat validations).
"""
from typing import Any, Dict, List, Optional, Union

import geopandas as gpd
import pandas as pd


# Default sample size when not specified (balance coverage vs token cost for GPT-4).
DEFAULT_ATTRIBUTE_SAMPLE_SIZE = 500


def _get_feature_id(row: pd.Series, idx: Any) -> Any:
    """Use 'id' column if present, else index (aligned with core.validation)."""
    if "id" in row.index:
        try:
            return row["id"]
        except Exception:
            pass
    return idx


def get_attribute_records(
    gdf: gpd.GeoDataFrame,
    sample_size: Optional[int] = None,
    random_state: Optional[int] = None,
    max_fields: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Extract attribute data as a list of per-feature records (no geometry).

    Each record is a dict with "feature_id" and all attribute column names as keys.
    Use for LLM prompts that need row-level context (e.g. consistency across features).

    Args:
        gdf: GeoDataFrame (geometry column is dropped).
        sample_size: Max number of rows to return. If None, uses DEFAULT_ATTRIBUTE_SAMPLE_SIZE.
        random_state: Seed for reproducible sampling.
        max_fields: If set, only the first N attribute columns are included (issue #70).

    Returns:
        List of dicts; each dict has feature_id and attribute key-value pairs.
    """
    if gdf is None or gdf.empty:
        return []

    n = sample_size if sample_size is not None else DEFAULT_ATTRIBUTE_SAMPLE_SIZE
    # Drop geometry so we don't send WKB/WKT to the LLM
    geom_col = gdf.geometry.name if hasattr(gdf, "geometry") and gdf.geometry is not None else None
    cols = [c for c in gdf.columns if c != geom_col]
    if max_fields is not None and max_fields > 0:
        cols = cols[:max_fields]
    if not cols:
        return []

    df = gdf[cols].copy()
    if len(df) > n:
        df = df.sample(n=n, random_state=random_state)

    records: List[Dict[str, Any]] = []
    for idx, row in df.iterrows():
        feature_id = _get_feature_id(row, idx)
        rec: Dict[str, Any] = {"feature_id": feature_id}
        for c in cols:
            val = row[c]
            rec[c] = val.item() if hasattr(val, "item") and callable(getattr(val, "item")) else val
        records.append(rec)
    return records


def get_attribute_columns(
    gdf: gpd.GeoDataFrame,
    sample_size: Optional[int] = None,
    random_state: Optional[int] = None,
    max_fields: Optional[int] = None,
) -> Dict[str, List[Any]]:
    """
    Extract attribute data as per-field value lists (no geometry).

    Result is {column_name: [val1, val2, ...]}. Use for LLM prompts that analyze
    one field at a time (e.g. outliers, naming variations, missing values).

    Args:
        gdf: GeoDataFrame (geometry column is dropped).
        sample_size: Max number of rows per column. If None, uses DEFAULT_ATTRIBUTE_SAMPLE_SIZE.
        random_state: Seed for reproducible sampling.
        max_fields: If set, only the first N attribute columns (issue #70).

    Returns:
        Dict mapping each attribute column name to a list of values (sampled).
    """
    if gdf is None or gdf.empty:
        return {}

    n = sample_size if sample_size is not None else DEFAULT_ATTRIBUTE_SAMPLE_SIZE
    geom_col = gdf.geometry.name if hasattr(gdf, "geometry") and gdf.geometry is not None else None
    cols = [c for c in gdf.columns if c != geom_col]
    if max_fields is not None and max_fields > 0:
        cols = cols[:max_fields]
    if not cols:
        return {}

    df = gdf[cols].copy()
    if len(df) > n:
        df = df.sample(n=n, random_state=random_state)

    out: Dict[str, List[Any]] = {}
    for c in cols:
        vals = df[c].tolist()
        out[c] = [v.item() if hasattr(v, "item") and callable(getattr(v, "item")) else v for v in vals]
    return out


def load_attributes_from_path(
    path: Union[str, "pd.PathLike"],
    sample_size: Optional[int] = None,
    random_state: Optional[int] = None,
    as_records: bool = True,
) -> Union[List[Dict[str, Any]], Dict[str, List[Any]]]:
    """
    Load a vector dataset from path and return attribute data (no geometry).

    Convenience helper for the attribute agent: read file once, return sampled attributes.

    Args:
        path: Path to GeoJSON, shapefile, etc. (GeoPandas read_file).
        sample_size: Max rows to include (default DEFAULT_ATTRIBUTE_SAMPLE_SIZE).
        random_state: Seed for sampling.
        as_records: If True, return list of per-feature dicts; else per-field value lists.

    Returns:
        get_attribute_records(...) if as_records else get_attribute_columns(...).
        Empty list or dict if file cannot be read.
    """
    try:
        gdf = gpd.read_file(path)
    except Exception:
        return [] if as_records else {}
    if as_records:
        return get_attribute_records(gdf, sample_size=sample_size, random_state=random_state)
    return get_attribute_columns(gdf, sample_size=sample_size, random_state=random_state)
