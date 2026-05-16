# Pilot Findings Report (Synthetic Data)

> **Disclaimer:** This report uses **fabricated** participant data (`data/pilot-*.csv`) to demonstrate the reporting format for issue #13. Do not cite these numbers in thesis conclusions. Run real sessions and replace with `findings-report-template.md`.

**Study:** GeoSpatial Data Quality Agent — Dashboard & correction workflow  
**Date range:** 2026-05-10 – 2026-05-12 (synthetic)  
**Participants:** n = 3 (`P01`–`P03`)  
**Data source:** [pilot-task-results.csv](data/pilot-task-results.csv), [pilot-sus-raw.csv](data/pilot-sus-raw.csv)

## Executive summary

- **Mean SUS:** 66.7 (synthetic; P03 rated mostly neutral with one lower score on item 4)
- **Task completion rate:** 88.9% (16/18 task attempts completed without `demo`)
- **Full workflow completion:** 1/3 participants completed all six tasks unaided
- **Top themes:** issue-filter discoverability, apply-button enablement rules, navigation between Upload and Dashboard

## Participants (synthetic)

| ID | Role | GIS experience |
|----|------|----------------|
| P01 | student | 2 semesters GIS coursework |
| P02 | analyst | 3yr professional GIS |
| P03 | student | 1yr QGIS self-study |

## Task results

| Task | Completion rate | Median time (s) | Common issues |
|------|-----------------|-----------------|---------------|
| T1 Upload | 100% (3/3) | 95 | P03 initially looked for upload on Dashboard |
| T2 Validate | 100% (3/3) | 78 | Waiting for async validation spinner |
| T3 Explore | 67% (2/3) | 115 | Critical severity filter not noticed (P03) |
| T4 Decide | 100% (3/3) | 210 | Approve/Reject affordance clear after first use |
| T5 Apply | 67% (2/3) | 52 | Apply disabled while custom override unsaved (P02) |
| T6 Report | 100% (3/3) | 120 | JSON vs Markdown choice unclear for some |

**Time-on-task pattern (prose):** Upload and validate were fastest (median under 90s). Correction decisions (T4) took longest (median ~210s), reflecting comparison of suggestions in the detail panel. Report export (T6) was moderate once navigation to Report was found.

## SUS results (synthetic)

| ID | SUS score |
|----|-----------|
| P01 | 72.5 |
| P02 | 75.0 |
| P03 | 52.5 |

**Mean SUS:** 66.7  

Recompute with:

```bash
python scripts/calculate_sus.py docs/user-testing/data/pilot-sus-raw.csv
```

P03's uniform neutral ratings illustrate a cautious or rushed post-test questionnaire—worth monitoring in real sessions.

## Qualitative themes (illustrative)

### Theme 1: Issue filters are easy to miss

- **Evidence:** P03 required a demo to locate critical-severity filter; P01 needed a verbal hint.
- **Severity:** High

### Theme 2: Apply corrections prerequisites are opaque

- **Evidence:** P02 could not apply until understanding custom-override requirement; button stayed disabled without explanatory copy.
- **Severity:** High

### Theme 3: Upload vs Dashboard mental model

- **Evidence:** P03 attempted upload from Dashboard; brief onboarding could clarify "Upload first, then Dashboard."
- **Severity:** Medium

### Theme 4: Report export formats

- **Evidence:** Participants used JSON, Markdown, and print differently; labels are accurate but benefit from one-line guidance.
- **Severity:** Low

## Prioritized follow-ups

| Priority | Suggested GitHub issue title | Description | Label |
|----------|------------------------------|-------------|-------|
| P0 | Dashboard: explain why Apply corrections is disabled | Show inline message listing pending custom saves or zero decisions | `ux` |
| P0 | Issues panel: improve filter discoverability | Add helper text or default critical filter when critical issues exist | `ux` |
| P1 | Empty dashboard: onboarding hint after first visit | Link to Upload page when no dataset loaded | `enhancement` |
| P1 | Detail view: highlight Approve/Reject for first suggestion | Subtle callout on first issue with correction | `ux` |
| P2 | Report page: short export format guide | One sentence under export buttons (JSON vs Markdown vs print) | `documentation` |
| P2 | Map tab: cross-link to Dashboard after validation | Reduce duplicate "where do I review issues?" confusion | `enhancement` |

## Recommendations

1. Run **3–5 real sessions** using [protocol.md](protocol.md); replace pilot CSVs with anonymized results.
2. Fix P0 UX items before the Phase 4 formal study.
3. Track acceptance-rate metrics once apply flow is stable.

## Next steps for issue #13

- [x] Testing kit and templates in repository
- [x] Synthetic pilot report (this document)
- [ ] Recruit live participants ([recruitment.md](recruitment.md))
- [ ] Complete real findings report and close GitHub issue #13
