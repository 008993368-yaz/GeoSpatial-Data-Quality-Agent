# Session Checklist

## Before session

- [ ] Participant ID assigned (`P0x`)
- [ ] Consent signed or noted
- [ ] Backend + frontend running
- [ ] `datasets/examples/sample.geojson` path sent to participant
- [ ] CSV templates copied: `task-results-P0x.csv`, SUS row ready
- [ ] Screen recording on (if consented)
- [ ] Moderator script and tasks printed or on second monitor

## During session

- [ ] Think-aloud reminder given
- [ ] T1–T6: start/stop timer per task
- [ ] Record `completed`, `time_seconds`, `assistance`, `notes` per task
- [ ] Avoid coaching unless stuck &gt;2 minutes
- [ ] SUS collected (all 10 items 1–5)
- [ ] Debrief notes captured

## After session

- [ ] Save CSVs to `data/` (do not commit PII)
- [ ] Run `python scripts/calculate_sus.py data/<sus-file>.csv`
- [ ] Log top 3 usability issues
- [ ] Update findings draft

## Study-level (after all participants)

- [ ] Aggregate task completion rates
- [ ] Compute mean/median time per task
- [ ] Compute mean SUS and per-participant scores
- [ ] Complete [findings-report-template.md](findings-report-template.md)
- [ ] File GitHub issues for prioritized fixes
- [ ] Update issue #13 with link to findings
