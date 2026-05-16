# User Testing Protocol

## Purpose

Evaluate whether GIS-oriented users can upload a dataset, run validation, review issues on the dashboard, make correction decisions, apply them, and export a quality report without critical usability blockers.

## Session overview

| Item | Guideline |
|------|-----------|
| Duration | 45–60 minutes |
| Format | Remote or in-person, moderated |
| Method | Task-based testing + think-aloud |
| Participants | 3–5 (GIS student or practitioner) |
| Facilitator | 1 moderator (+ optional note-taker) |

## Roles

- **Moderator:** Gives tasks, tracks time, records completion/assistance, avoids leading unless participant is stuck >2 minutes.
- **Participant:** Completes tasks using their own words; encouraged to verbalize thoughts.
- **Note-taker (optional):** Captures quotes and usability issues; moderator may dual-role.

## Session structure

1. **Welcome & consent** (5 min) — [consent-template.md](consent-template.md)
2. **Briefing** (3 min) — [participant-brief.md](participant-brief.md); no demo of full workflow
3. **Tasks T1–T6** (30–40 min) — [tasks.md](tasks.md), [moderator-script.md](moderator-script.md)
4. **SUS questionnaire** (5 min) — [sus-questionnaire.md](sus-questionnaire.md)
5. **Debrief** (5–10 min) — open questions in moderator script

## Think-aloud instructions

Tell participants:

> Please say what you are looking for, what you expect to happen, and what confuses you. There are no wrong answers—we are testing the software, not you.

If they fall silent for ~30 seconds, prompt: *"What are you thinking now?"*

## Assistance levels

Record per task in CSV (`assistance` column):

| Level | Definition |
|-------|------------|
| `none` | Participant completes without help |
| `verbal` | Hint only (e.g., "check the Dashboard tab") |
| `demo` | Moderator demonstrates a control |

If `demo` is required, mark task **not completed** unless you explicitly allow assisted completion in your analysis.

## Environment checklist

Before each session:

- [ ] Backend running; health endpoint responds
- [ ] Frontend loads; browser zoom 100%
- [ ] `datasets/examples/sample.geojson` available locally for upload
- [ ] Screen share / recording configured (if consented)
- [ ] Timer ready for per-task timing
- [ ] CSV row prepared for participant ID
- [ ] Incognito or fresh browser profile (optional, to avoid cached state)

## Stopping criteria

End a task when:

- Success criteria met, or
- Participant cannot proceed after verbal help + 2 minutes, or
- 2× the target time in [tasks.md](tasks.md) elapses

Move to next task; note failure reason in `notes`.

## After the session

1. Save task timings and SUS to [data/](data/) CSVs.
2. Run `python scripts/calculate_sus.py` on SUS file.
3. Draft findings using [findings-report-template.md](findings-report-template.md).
4. Open GitHub issues for high-priority follow-ups.
