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
  corrections?: CorrectionSuggestion[] | null;
};

export type UploadResponse = {
  dataset_id: string;
  filename: string;
  /** Optional total feature count for the dataset (from upload metadata). */
  feature_count?: number;
  bounds?: number[] | null;
};

export type CorrectionSuggestion = {
  method: string;
  confidence: number;
  explanation: string;
  issue_index: number;
};

/** User choice for a suggested correction (issue #103); persisted until apply or reset. */
export type CorrectionDecision = "approve" | "reject" | "custom";

/** POST /corrections/apply response (aligned with backend ApplyCorrectionsResponse). */
export type ApplyCorrectionsResponse = {
  applied: number;
  skipped: number;
  download_url?: string | null;
  /** Server hint about what the download is (issue #105). */
  export_note?: string | null;
};

/** Async validation job status (GET /validate/jobs/{job_id}). */
export type ValidationJobStatus = {
  job_id: string;
  dataset_id: string;
  status: "pending" | "running" | "completed" | "failed";
  error?: string | null;
  result?: ValidationResult | null;
};
