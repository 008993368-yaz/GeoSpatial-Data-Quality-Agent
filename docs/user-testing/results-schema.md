# Results Data Schema

CSV files live in [data/](data/). Use UTF-8, comma-separated, header row included.

## participants-*.csv

| Column | Type | Description |
|--------|------|-------------|
| `participant_id` | string | Anonymous ID, e.g. `P01` |
| `role` | string | e.g. `student`, `analyst`, `practitioner` |
| `gis_experience` | string | e.g. `1yr coursework`, `5yr professional` |
| `session_date` | string | ISO date `YYYY-MM-DD` |

## task-results-*.csv

| Column | Type | Description |
|--------|------|-------------|
| `participant_id` | string | Matches participants file |
| `task_id` | string | `T1` … `T6` |
| `completed` | string | `Y` or `N` |
| `time_seconds` | integer | Elapsed seconds for task |
| `assistance` | string | `none`, `verbal`, or `demo` |
| `notes` | string | Free text; quote optional |

## sus-raw-*.csv

| Column | Type | Description |
|--------|------|-------------|
| `participant_id` | string | Anonymous ID |
| `q1` … `q10` | integer | Likert 1–5 per SUS item |

## Derived metrics (analysis)

| Metric | Formula |
|--------|---------|
| Task completion rate | % rows with `completed=Y` per task_id |
| Workflow completion | participant completed T1–T6 all `Y` |
| Mean time on task | mean(`time_seconds`) per task_id |
| SUS per participant | `scripts/calculate_sus.py` |
| Mean SUS | mean of participant SUS scores |

## Templates and pilot data

| File | Purpose |
|------|---------|
| `task-results-template.csv` | Empty template |
| `sus-raw-template.csv` | Empty template |
| `participants-template.csv` | Empty template |
| `pilot-task-results.csv` | Synthetic example (n=3) |
| `pilot-sus-raw.csv` | Synthetic example |
| `pilot-participants.csv` | Synthetic example |
