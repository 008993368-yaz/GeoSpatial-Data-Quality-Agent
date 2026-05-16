"""Quality report formatting and validation config snapshot (issue #12)."""
import json
from typing import Any, Dict, List

from core.config import settings


def get_validation_config() -> Dict[str, Any]:
    """Public validation settings for reports (no secrets)."""
    return {
        "pipeline_steps": [
            "geometry_validation",
            "attribute_validation",
            "topology_validation",
            "generate_recommendations",
        ],
        "geometry_validation_enabled": settings.GEOMETRY_VALIDATION_ENABLED,
        "attribute_sample_size": settings.ATTRIBUTE_SAMPLE_SIZE,
        "attribute_max_records_in_prompt": settings.ATTRIBUTE_MAX_RECORDS_IN_PROMPT,
        "openai_model": settings.OPENAI_MODEL,
        "topology_checks": {
            "gaps": True,
            "overlaps": True,
            "connectivity": True,
        },
    }


def _format_bounds(bounds: Any) -> str:
    if not bounds or not isinstance(bounds, list):
        return "—"
    return ", ".join(f"{float(x):.4f}" for x in bounds)


def render_report_markdown(payload: Dict[str, Any]) -> str:
    """Render a quality report payload as Markdown (mirrors frontend export)."""
    dataset = payload.get("dataset") or {}
    validation = payload.get("validation") or {}
    summary = payload.get("summary") or {}
    generated_at = payload.get("generated_at", "")
    validation_config = payload.get("validation_config")
    correction_decisions = payload.get("correction_decisions") or {}

    lines: List[str] = []
    lines.append("# Quality assessment report")
    lines.append("")
    lines.append(f"**Dataset:** {dataset.get('filename', '—')}")
    lines.append(f"**Dataset ID:** {dataset.get('dataset_id', '—')}")
    lines.append(f"**Generated:** {generated_at}")
    lines.append("")

    lines.append("## Dataset metadata")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Features | {dataset.get('feature_count', '—')} |")
    lines.append(f"| Geometry type | {dataset.get('geometry_type') or '—'} |")
    lines.append(f"| CRS | {dataset.get('crs') or '—'} |")
    lines.append(f"| Bounds | {_format_bounds(dataset.get('bounds'))} |")
    lines.append("")

    if validation_config:
        lines.append("## Validation configuration")
        lines.append("")
        lines.append("| Setting | Value |")
        lines.append("| --- | --- |")
        steps = validation_config.get("pipeline_steps") or []
        lines.append(f"| Pipeline | {' → '.join(steps)} |")
        lines.append(
            f"| Geometry validation | {'enabled' if validation_config.get('geometry_validation_enabled') else 'disabled'} |"
        )
        lines.append(f"| Attribute sample size | {validation_config.get('attribute_sample_size', '—')} |")
        lines.append(
            f"| Records in LLM prompt | {validation_config.get('attribute_max_records_in_prompt', '—')} |"
        )
        lines.append(f"| LLM model | {validation_config.get('openai_model', '—')} |")
        tc = validation_config.get("topology_checks") or {}
        lines.append(
            f"| Topology checks | gaps={tc.get('gaps')}, overlaps={tc.get('overlaps')}, connectivity={tc.get('connectivity')} |"
        )
        lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("| --- | --- |")
    lines.append(f"| Total issues | {summary.get('totalIssues', 0)} |")
    lines.append(f"| Critical | {summary.get('critical', 0)} |")
    lines.append(f"| Warnings | {summary.get('warning', 0)} |")
    by_cat = summary.get("byCategory") or {}
    lines.append(f"| Geometry | {by_cat.get('geometry', 0)} |")
    lines.append(f"| Attribute | {by_cat.get('attribute', 0)} |")
    lines.append(f"| Topology | {by_cat.get('topology', 0)} |")
    lines.append("")

    corrections = validation.get("corrections") or []
    lines.append("## Corrections")
    lines.append("")
    lines.append(f"Suggested corrections: {len(corrections)}")
    if correction_decisions:
        lines.append("")
        lines.append("| Issue index | Decision | Custom override |")
        lines.append("| --- | --- | --- |")
        for idx, entry in correction_decisions.items():
            if isinstance(entry, dict):
                decision = entry.get("decision", "—")
                has_override = "yes" if entry.get("hasOverride") else "no"
            else:
                decision = str(entry)
                has_override = "no"
            lines.append(f"| {idx} | {decision} | {has_override} |")
    lines.append("")

    issues = validation.get("issues") or []
    limit = 500
    shown = issues[:limit]
    suffix = f" of {len(issues)}" if len(issues) > len(shown) else ""
    lines.append(f"## Issues ({len(shown)}{suffix})")
    lines.append("")
    lines.append("| # | Type | Severity | Feature | Description |")
    lines.append("| --- | --- | --- | --- | --- |")
    for i, issue in enumerate(shown):
        fid = issue.get("feature_id")
        fid_str = str(fid) if fid is not None else "—"
        desc = (issue.get("description") or "").replace("|", "\\|")[:120]
        lines.append(
            f"| {i} | {issue.get('type', '')} | {issue.get('severity', '')} | {fid_str} | {desc} |"
        )
    if len(issues) > len(shown):
        lines.append("")
        lines.append(f"_…and {len(issues) - len(shown)} more issues not listed._")

    return "\n".join(lines)


def export_report_bytes(payload: Dict[str, Any], fmt: str) -> tuple[bytes, str, str]:
    """
    Return (content_bytes, media_type, filename_suffix) for the given format.
    fmt: 'json' or 'markdown'
    """
    dataset = payload.get("dataset") or {}
    base = (dataset.get("filename") or "quality-report").replace(" ", "_")
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in base)[:80] or "quality-report"

    if fmt == "markdown":
        content = render_report_markdown(payload).encode("utf-8")
        return content, "text/markdown; charset=utf-8", f"{safe}-report.md"
    if fmt == "json":
        content = json.dumps(payload, indent=2).encode("utf-8")
        return content, "application/json", f"{safe}-report.json"
    raise ValueError(f"Unsupported format: {fmt}")
