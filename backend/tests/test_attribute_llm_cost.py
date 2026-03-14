"""Tests for services.attribute_llm_cost (issue #70)."""
import pytest

from services.attribute_llm_cost import (
    estimate_attribute_prompt_tokens,
    estimate_naive_tokens,
)


def test_estimate_attribute_prompt_tokens_small():
    """Optimized prompt estimate is bounded by limits."""
    records = [{"feature_id": i, "name": f"r{i}", "val": i} for i in range(100)]
    per_field = {"name": ["a", "b"] * 50, "val": list(range(100))}
    tokens = estimate_attribute_prompt_tokens(
        records,
        per_field,
        max_records_in_prompt=10,
        max_values_per_field=15,
    )
    assert tokens > 0
    assert tokens < 5000


def test_estimate_naive_tokens():
    """Naive estimate scales with rows and fields."""
    small = estimate_naive_tokens(100, 5)
    large = estimate_naive_tokens(10000, 10)
    assert large > small
    assert small > 0