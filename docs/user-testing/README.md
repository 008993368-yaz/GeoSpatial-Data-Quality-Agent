# User Testing Kit (Issue #13)

Formative usability study for the validation **Dashboard**, **correction workflow**, and **Quality report**. Use this kit to run consistent moderated sessions with GIS students or practitioners.

## Quick start

1. **Environment:** Start backend and frontend (see [Session setup](#session-setup)).
2. **Dataset:** Use [`datasets/examples/sample.geojson`](../../datasets/examples/sample.geojson) for every participant (same baseline).
3. **Read:** [protocol.md](protocol.md), [tasks.md](tasks.md), [moderator-script.md](moderator-script.md).
4. **Recruit:** [recruitment.md](recruitment.md) — target 3–5 participants.
5. **Run:** [session-checklist.md](session-checklist.md).
6. **Record:** Copy CSV templates from [data/](data/) → fill during/after sessions.
7. **Analyze:** `python scripts/calculate_sus.py docs/user-testing/data/<your-sus-file>.csv`
8. **Report:** [findings-report-template.md](findings-report-template.md) (real study) or review [pilot-findings.md](pilot-findings.md) (synthetic example).

## Session setup

| Component | Typical URL | Notes |
|-----------|-------------|--------|
| Frontend | `http://localhost:5173` | Vite dev server; hash routes (`#/dashboard`, etc.) |
| Backend API | `http://localhost:8000` | Required for upload, validation, and apply corrections |
| Test file | `datasets/examples/sample.geojson` | 3 features; known issues after validation |

**Backend (from repo root):**

```bash
cd backend
# activate venv if used
uvicorn main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Confirm **Upload**, **Dashboard**, and **Report** nav links work before the first participant. Apply corrections requires a running API (not mocked).

## Kit contents

| File | Purpose |
|------|---------|
| [protocol.md](protocol.md) | Session flow, roles, ethics |
| [tasks.md](tasks.md) | Six tasks + success criteria |
| [moderator-script.md](moderator-script.md) | Verbatim prompts |
| [participant-brief.md](participant-brief.md) | Handout for participants |
| [recruitment.md](recruitment.md) | Screening + email template |
| [consent-template.md](consent-template.md) | Consent language |
| [sus-questionnaire.md](sus-questionnaire.md) | Post-session SUS |
| [session-checklist.md](session-checklist.md) | Moderator checklist |
| [results-schema.md](results-schema.md) | CSV column definitions |
| [findings-report-template.md](findings-report-template.md) | Empty findings structure |
| [pilot-findings.md](pilot-findings.md) | Example report (synthetic n=3) |
| [data/](data/) | CSV templates + pilot sample data |

## Ethics and data handling

- Use anonymous IDs only (`P01`, `P02`, …) in committed files.
- Do **not** commit names, emails, or recordings without separate consent and secure storage.
- See [consent-template.md](consent-template.md).

## Parent documentation

- [Evaluation methodology](../evaluation.md)
- [README Phase 3 roadmap](../../README.md#roadmap)
