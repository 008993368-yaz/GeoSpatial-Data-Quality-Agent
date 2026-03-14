"""
Token and cost estimation for attribute validation LLM calls (issue #70).

Provides rough input-token estimates for attribute prompts so callers can reason about
cost and tune ATTRIBUTE_SAMPLE_SIZE / ATTRIBUTE_MAX_RECORDS_IN_PROMPT / etc.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


# Approximate characters per token for English/JSON (OpenAI ~4, conservative).
CHARS_PER_TOKEN = 4


def estimate_attribute_prompt_tokens(
    attribute_records: List[Dict[str, Any]],
    per_field_values: Optional[Dict[str, List[Any]]] = None,
    *,
    max_records_in_prompt: int = 10,
    max_values_per_field: int = 15,
    max_fields: Optional[int] = None,
) -> int:
    """
    Estimate input token count for the attribute validation prompt.

    Uses the same slicing as build_attribute_validation_prompt (records and
    per_field truncated) plus a fixed instruction size. Useful for comparing
    naive (full dataset) vs optimized (sampled + truncated) usage.

    Args:
        attribute_records: Full or sampled records (only first max_records_in_prompt used).
        per_field_values: Full or sampled per-field lists (sliced by max_*).
        max_records_in_prompt: Same as ATTRIBUTE_MAX_RECORDS_IN_PROMPT.
        max_values_per_field: Same as ATTRIBUTE_MAX_VALUES_PER_FIELD.
        max_fields: Same as ATTRIBUTE_MAX_FIELDS (None = all fields).

    Returns:
        Approximate number of input tokens (instruction + ATTRIBUTE_DATA JSON).
    """
    # Instruction block is ~600 chars in current prompt
    instruction_chars = 600
    pf = per_field_values or {}
    if max_fields is not None and max_fields > 0:
        keys = list(pf.keys())[:max_fields]
        pf = {k: pf[k][:max_values_per_field] for k in keys if k in pf}
    else:
        pf = {k: v[:max_values_per_field] for k, v in pf.items()}
    examples = {
        "records": attribute_records[:max_records_in_prompt],
        "per_field_values": pf,
    }
    data_str = json.dumps(examples, default=str)
    total_chars = instruction_chars + len(data_str)
    return max(0, (total_chars + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN)


def estimate_naive_tokens(num_rows: int, num_fields: int, avg_chars_per_value: int = 15) -> int:
    """
    Rough estimate for a naive prompt that sent all rows and all fields.

    Use to compare against optimized (sampled + truncated) token usage.

    Args:
        num_rows: Total feature count.
        num_fields: Attribute column count.
        avg_chars_per_value: Approximate characters per cell when serialized.

    Returns:
        Approximate input tokens for a naive full-dataset prompt.
    """
    # One record ≈ feature_id + num_fields * avg value
    chars_per_record = 20 + num_fields * avg_chars_per_value
    total_chars = 600 + num_rows * chars_per_record
    return max(0, (total_chars + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN)
