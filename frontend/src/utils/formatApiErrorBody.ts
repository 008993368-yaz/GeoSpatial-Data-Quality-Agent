/**
 * Extract a human-readable message from typical FastAPI / app JSON error bodies.
 */
export function formatApiErrorBody(data: unknown, fallback: string): string {
  if (!data || typeof data !== "object") return fallback;
  const d = data as Record<string, unknown>;
  const detail = d.detail;

  if (typeof detail === "string") return detail;

  if (detail && typeof detail === "object" && !Array.isArray(detail)) {
    const obj = detail as Record<string, unknown>;
    if (typeof obj.detail === "string") return obj.detail;
  }

  if (Array.isArray(detail)) {
    const parts = detail.map((item) => {
      if (item && typeof item === "object" && "msg" in item) {
        return String((item as { msg: unknown }).msg);
      }
      return typeof item === "string" ? item : JSON.stringify(item);
    });
    return parts.filter(Boolean).join("; ") || fallback;
  }

  return fallback;
}
