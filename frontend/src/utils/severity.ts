export type SeverityTone = "critical" | "warning" | "info";

/** Normalize a raw severity string to a known tone for color-coding. */
export function severityTone(severity: string | undefined | null): SeverityTone {
  const s = (severity || "").toLowerCase();
  if (s === "critical") return "critical";
  if (s === "warning") return "warning";
  return "info";
}
