# System Usability Scale (SUS)

Administer **after** all tasks. Ask participants to rate **agreement** with each statement for the **overall system** based on today's session.

**Scale:** 1 = Strongly disagree … 5 = Strongly agree

| # | Statement |
|---|-----------|
| 1 | I think that I would like to use this system frequently. |
| 2 | I found the system unnecessarily complex. |
| 3 | I thought the system was easy to use. |
| 4 | I think that I would need the support of a technical person to be able to use this system. |
| 5 | I found the various functions in this system were well integrated. |
| 6 | I thought there was too much inconsistency in this system. |
| 7 | I would imagine that most people would learn to use this system very quickly. |
| 8 | I found the system very cumbersome to use. |
| 9 | I felt very confident using the system. |
| 10 | I needed to learn a lot of things before I could get going with this system. |

## Scoring

Record responses as `q1`…`q10` in `data/sus-raw-*.csv` (integers 1–5).

```text
For odd items (1,3,5,7,9):  contribution = score - 1
For even items (2,4,6,8,10): contribution = 5 - score
SUS = (sum of 10 contributions) × 2.5
```

**Interpretation (approximate):**

| SUS | Grade |
|-----|-------|
| &lt; 50 | F |
| 50–70 | D–C |
| 70–80 | B |
| &gt; 80 | A |

Compute batch scores:

```bash
python scripts/calculate_sus.py docs/user-testing/data/pilot-sus-raw.csv
```

Reference: Brooke, J. (1996). SUS: A quick and dirty usability scale.
