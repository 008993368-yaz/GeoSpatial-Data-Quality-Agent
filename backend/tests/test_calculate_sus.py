"""Tests for scripts/calculate_sus.py SUS scoring."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from calculate_sus import load_sus_csv, sus_score_from_responses  # noqa: E402


def test_sus_score_brooke_example():
    # P01 pilot row: 4,2,4,2,3,2,4,2,4,2 -> 72.5
    assert sus_score_from_responses([4, 2, 4, 2, 3, 2, 4, 2, 4, 2]) == 72.5


def test_sus_score_all_neutral():
    assert sus_score_from_responses([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]) == 50.0


def test_sus_score_max_usability():
    # Strongly agree on positive items (1,3,5,7,9), disagree on negative (2,4,6,8,10)
    assert sus_score_from_responses([5, 1, 5, 1, 5, 1, 5, 1, 5, 1]) == 100.0


def test_sus_score_invalid_length():
    with pytest.raises(ValueError, match="expected 10"):
        sus_score_from_responses([3, 3, 3])


def test_sus_score_out_of_range():
    with pytest.raises(ValueError, match="must be 1–5"):
        sus_score_from_responses([0, 2, 4, 2, 3, 2, 4, 2, 4, 2])


def test_load_pilot_csv():
    path = ROOT / "docs/user-testing/data/pilot-sus-raw.csv"
    rows = load_sus_csv(path)
    assert len(rows) == 3
    p01 = next(r for pid, r in rows if pid == "P01")
    assert sus_score_from_responses(p01) == 72.5
