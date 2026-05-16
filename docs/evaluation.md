# Evaluation Methodology

This document summarizes how the GeoSpatial Data Quality Agent is evaluated across **formative user testing** (Phase 3) and **formal evaluation** (Phase 4). Metrics align with the [README Evaluation Metrics](../README.md#evaluation-metrics) section.

## Phase 3: Formative user testing (issue #13)

Goal: validate usability of the validation dashboard and correction workflow before formal benchmarks.

| Metric | How it is collected | Target (hypothesis) |
|--------|---------------------|---------------------|
| Task completion | Moderator marks Y/N per task | ≥ 80% of tasks completed unaided for GIS-familiar users |
| Time on task | Stopwatch per task (seconds) | See per-task targets in [tasks.md](user-testing/tasks.md) |
| System Usability Scale (SUS) | Post-session questionnaire (1–5) | Mean SUS ≥ 68 (above average) |
| Qualitative feedback | Think-aloud + debrief notes | Themes → prioritized GitHub issues |

**Artifacts:** [User testing kit](user-testing/README.md) (protocol, scripts, CSV templates, SUS calculator).

**Pilot example:** [pilot-findings.md](user-testing/pilot-findings.md) uses synthetic data to demonstrate reporting format. Replace with real session data before thesis conclusions.

## Phase 4: Formal evaluation (planned)

Goal: measure validation accuracy, suggestion quality, and performance on labeled test datasets.

| Category | Metrics |
|----------|---------|
| Validation accuracy | Precision, recall, F1 vs. expert labels |
| Suggestion quality | Acceptance rate, correction accuracy, Cohen's Kappa |
| Performance | Processing time per 1k features, API cost, memory |
| User experience | Time savings vs. manual baseline (may extend Phase 3 study) |

Formal scripts and labeled datasets will live under `datasets/test/` and `scripts/run_evaluation.py` when Phase 4 begins.

## SUS scoring

Raw Likert responses (1–5) for 10 standard SUS items are aggregated with:

```text
odd items:  contribution = score - 1
even items: contribution = 5 - score
SUS = (sum of contributions) × 2.5   # range 0–100
```

Use `scripts/calculate_sus.py` on `docs/user-testing/data/sus-raw-*.csv` files.

## Related links

- [User testing README](user-testing/README.md)
- [Findings report template](user-testing/findings-report-template.md)
- [Pilot findings (synthetic)](user-testing/pilot-findings.md)
