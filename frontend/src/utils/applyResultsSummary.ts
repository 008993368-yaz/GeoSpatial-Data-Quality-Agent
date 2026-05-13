/**
 * Human-readable summary for apply-corrections counts (issue #105).
 */
export function summarizeApplyResults(applied: number, skipped: number): string {
  const total = applied + skipped;
  if (total === 0) {
    return "No correction decisions were returned in this response. Try applying again after selecting Approve or Reject for at least one suggested fix.";
  }
  if (applied === 0 && skipped > 0) {
    return "All submitted corrections were skipped (rejected). Nothing was approved for application in this run.";
  }
  if (applied > 0 && skipped === 0) {
    return "Every submitted correction was approved. The server recorded them for application.";
  }
  return `Mixed outcome: ${applied} approved for application and ${skipped} skipped (rejected).`;
}
