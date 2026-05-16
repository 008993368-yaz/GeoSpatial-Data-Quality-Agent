export function correctionIndicesFromIssues(
  issuesLength: number,
  corrections: { issue_index: number }[] | null | undefined,
): Set<number> {
  const withSuggestion = new Set<number>();
  if (!corrections?.length) return withSuggestion;
  for (const c of corrections) {
    if (
      typeof c.issue_index === "number" &&
      c.issue_index >= 0 &&
      c.issue_index < issuesLength
    ) {
      withSuggestion.add(c.issue_index);
    }
  }
  return withSuggestion;
}

export function getFirstCorrectionIssueIndex(
  corrections: { issue_index: number }[] | null | undefined,
  issuesLength: number,
): number | null {
  const indices = correctionIndicesFromIssues(issuesLength, corrections);
  if (indices.size === 0) return null;
  return Math.min(...indices);
}
