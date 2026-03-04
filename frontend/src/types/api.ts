/** API response types (aligned with backend models). */

export type GeometryIssue = {
  feature_id: unknown;
  type: string;
  severity: string;
  location?: number[] | null;
  description?: string | null;
};

export type ValidationResult = {
  dataset_id: string;
  issues: GeometryIssue[];
};
