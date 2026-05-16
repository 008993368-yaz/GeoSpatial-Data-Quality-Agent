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
  geometry_type?: string | null;
  crs?: string | null;
  bounds?: number[] | null;
};

/** GET /validation/config — public validation pipeline settings (issue #12). */
export type ValidationConfigResponse = {
  pipeline_steps: string[];
  geometry_validation_enabled: boolean;
  attribute_sample_size: number;
  attribute_max_records_in_prompt: number;
  openai_model: string;
  topology_checks: {
    gaps: boolean;
    overlaps: boolean;
    connectivity: boolean;
  };
};

export type CorrectionSuggestion = {
  method: string;
  confidence: number;
  explanation: string;
  issue_index: number;
};

/** User choice for a suggested correction (issue #103); persisted until apply or reset. */
export type CorrectionDecision = "approve" | "reject" | "custom";

/** Manual override for a custom correction (issue #106); sent on apply when action is approve. */
export type CorrectionOverride = {
  feature_id?: unknown;
  geometry_wkt?: string;
  attributes?: Record<string, unknown>;
};

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
