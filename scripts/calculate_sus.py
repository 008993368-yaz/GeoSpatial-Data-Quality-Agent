#!/usr/bin/env python3
"""Compute System Usability Scale (SUS) scores from a CSV of raw Likert responses."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def sus_score_from_responses(responses: list[int]) -> float:
    """Return SUS score (0–100) from ten Likert items (1–5 each)."""
    if len(responses) != 10:
        raise ValueError(f"expected 10 SUS items, got {len(responses)}")
    total = 0.0
    for i, score in enumerate(responses, start=1):
        if not 1 <= score <= 5:
            raise ValueError(f"item {i} must be 1–5, got {score}")
        if i % 2 == 1:
            total += score - 1
        else:
            total += 5 - score
    return round(total * 2.5, 1)


def load_sus_csv(path: Path) -> list[tuple[str, list[int]]]:
    rows: list[tuple[str, list[int]]] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")
        required = ["participant_id"] + [f"q{i}" for i in range(1, 11)]
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV missing columns: {', '.join(missing)}")
        for row in reader:
            pid = (row.get("participant_id") or "").strip()
            if not pid:
                continue
            responses = [int(row[f"q{i}"]) for i in range(1, 11)]
            rows.append((pid, responses))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Calculate SUS scores from a CSV file.")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="docs/user-testing/data/pilot-sus-raw.csv",
        help="Path to sus-raw CSV (default: pilot file)",
    )
    args = parser.parse_args(argv)
    path = Path(args.csv_path)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    participants = load_sus_csv(path)
    if not participants:
        print("error: no participant rows found", file=sys.stderr)
        return 1

    scores: list[float] = []
    print(f"SUS scores ({path}):")
    print(f"{'participant_id':<16} {'sus':>6}")
    print("-" * 24)
    for pid, responses in participants:
        score = sus_score_from_responses(responses)
        scores.append(score)
        print(f"{pid:<16} {score:>6.1f}")

    mean = round(sum(scores) / len(scores), 1)
    print("-" * 24)
    print(f"{'mean':<16} {mean:>6.1f}  (n={len(scores)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
