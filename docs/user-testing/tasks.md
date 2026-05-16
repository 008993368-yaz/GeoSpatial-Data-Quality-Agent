# Task Scenarios and Success Criteria

Use the same test file for every participant: [`datasets/examples/sample.geojson`](../../datasets/examples/sample.geojson).

Record `participant_id`, `task_id`, `completed` (Y/N), `time_seconds`, `assistance` (`none` | `verbal` | `demo`), and `notes` in `data/task-results-*.csv`.

## Hypothesis (formative)

For participants with basic GIS familiarity, **≥ 80%** of task attempts across the study should complete **without demo-level assistance**.

---

## T1 — Upload dataset

**Goal:** Load the sample dataset into the application.

**Steps (participant-facing):**

1. Open the **Upload** page.
2. Upload `sample.geojson` from the path provided by the moderator.
3. Confirm the file is accepted.

**Success criteria:**

- Upload completes without error.
- User can navigate to **Dashboard** (or sees indication that a dataset is loaded).

**Target time:** &lt; 3 minutes, assistance `none`.

---

## T2 — Run validation

**Goal:** Execute validation on the uploaded dataset.

**Steps:**

1. Go to **Dashboard**.
2. Click **Run validation**.
3. Wait until validation finishes.

**Success criteria:**

- Validation completes (no error alert).
- **Issues** panel and **Summary** show at least one issue.

**Target time:** &lt; 2 minutes after dashboard is visible, assistance `none`.

**Note:** Re-run validation clears correction choices; only use if T2 failed and you need a clean retry.

---

## T3 — Explore and inspect an issue

**Goal:** Find a critical issue and read its details and suggested fix.

**Steps:**

1. On the Dashboard, use issue filters to show **critical** severity (if available).
2. Select one critical issue from the list or map.
3. Read the **Issue details** panel.

**Success criteria:**

- Detail panel shows issue description.
- If a correction exists for that issue, a suggested fix (method/explanation) is visible.

**Target time:** &lt; 3 minutes, assistance `none`.

---

## T4 — Decide on corrections

**Goal:** Record approve/reject decisions for at least two issues.

**Steps:**

1. For one issue with a suggestion, choose **Approve**.
2. For a different issue with a suggestion, choose **Reject**.
3. Confirm decisions appear in the issues list (e.g., A/R badges).

**Success criteria:**

- At least one **Approve** and one **Reject** recorded.
- Optional: **Custom** + saved override counts as success if participant attempts it.

**Target time:** &lt; 5 minutes, assistance `none` or `verbal`.

---

## T5 — Apply corrections

**Goal:** Send correction choices to the server.

**Steps:**

1. Click **Apply corrections** on the Dashboard.
2. Wait for completion.

**Success criteria:**

- Apply succeeds (apply results panel or success message).
- No blocking error about pending custom edits.

**Prerequisite:** Live backend API; mocked-only frontends are insufficient for this task.

**Target time:** &lt; 2 minutes, assistance `none`.

---

## T6 — Quality report and export

**Goal:** Review and export the quality report.

**Steps:**

1. Open **Report** (from nav or **View report** on Dashboard).
2. Review summary sections.
3. Export at least one format: **Download JSON**, **Download Markdown**, or **Print / Save as PDF**.

**Success criteria:**

- Report page loads with dataset and validation summary.
- At least one export or print action is attempted successfully (file download or print dialog).

**Target time:** &lt; 4 minutes, assistance `none`.

---

## Task ID reference

| task_id | Name |
|---------|------|
| T1 | Upload |
| T2 | Validate |
| T3 | Explore issue |
| T4 | Decide corrections |
| T5 | Apply corrections |
| T6 | Report export |
