"""Apply user-supplied geometry/attribute overrides to dataset GeoJSON (issue #106)."""
from pathlib import Path
from typing import Any, Dict, List, Optional

import geopandas as gpd
from shapely import wkt as shapely_wkt


def _resolve_feature_index(gdf: gpd.GeoDataFrame, feature_id: Any) -> Optional[Any]:
    """Return GeoDataFrame index for feature_id (matches validation feature_id rules)."""
    if "id" in gdf.columns:
        matches = gdf[gdf["id"].astype(str) == str(feature_id)]
        if not matches.empty:
            return matches.index[0]

    for idx in gdf.index:
        if idx == feature_id or str(idx) == str(feature_id):
            return idx
        try:
            if int(idx) == int(feature_id):
                return idx
        except (TypeError, ValueError):
            continue
    return None


def apply_correction_overrides(
    vector_path: Path,
    corrections: List[Dict[str, Any]],
) -> int:
    """
    Apply approved corrections that include geometry_wkt and/or attributes.

    Writes updated GeoJSON back to vector_path. Returns the number of features mutated.
    """
    overrides = [
        c
        for c in corrections
        if c.get("action") == "approve" and (c.get("geometry_wkt") or c.get("attributes"))
    ]
    if not overrides:
        return 0

    gdf = gpd.read_file(vector_path)
    if gdf.empty:
        return 0

    mutated = 0
    for item in overrides:
        feature_id = item.get("feature_id")
        if feature_id is None:
            continue
        row_idx = _resolve_feature_index(gdf, feature_id)
        if row_idx is None:
            continue

        changed = False
        wkt_text = item.get("geometry_wkt")
        if wkt_text and str(wkt_text).strip():
            try:
                geom = shapely_wkt.loads(str(wkt_text).strip())
            except Exception as exc:
                raise ValueError(f"Invalid WKT for feature {feature_id}: {exc}") from exc
            gdf.at[row_idx, gdf.geometry.name] = geom
            changed = True

        attrs = item.get("attributes")
        if attrs:
            for key, value in attrs.items():
                gdf.at[row_idx, key] = value
            changed = True

        if changed:
            mutated += 1

    if mutated:
        gdf.to_file(vector_path, driver="GeoJSON")
    return mutated
