# User Testing Data

## Privacy

- Use anonymous participant IDs only (`P01`, `P02`, …).
- Do **not** commit real names, email addresses, or unredacted recordings.
- Keep identifiable data in local or institutional storage per your ethics approval.

## Files

| File | Description |
|------|-------------|
| `participants-template.csv` | Empty roster template |
| `task-results-template.csv` | Empty per-task log |
| `sus-raw-template.csv` | Empty SUS responses |
| `pilot-participants.csv` | Synthetic pilot roster (n=3) |
| `pilot-task-results.csv` | Synthetic pilot task metrics |
| `pilot-sus-raw.csv` | Synthetic pilot SUS (feeds [pilot-findings.md](../pilot-findings.md)) |

Copy templates to `task-results-study-YYYY-MM.csv` (etc.) for real sessions.

## Analysis

```bash
python scripts/calculate_sus.py docs/user-testing/data/pilot-sus-raw.csv
```

See [results-schema.md](../results-schema.md) for column definitions.
