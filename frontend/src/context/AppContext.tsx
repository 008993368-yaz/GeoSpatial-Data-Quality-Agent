import { createContext, useContext, useState, type ReactNode } from "react";
import type {
  GeometryIssue,
  ValidationResult,
  UploadResponse,
  ValidationJobStatus,
} from "../types/api";

const POLL_INTERVAL_MS = 1500;

type AppContextValue = {
  currentDataset: UploadResponse | null;
  setCurrentDataset: (d: UploadResponse | null) => void;
  isUploading: boolean;
  error: string | null;
  validationResult: ValidationResult | null;
  /** Stored validation issues (for map/symbolize). Empty when no result or no issues. */
  validationIssues: GeometryIssue[];
  isValidating: boolean;
  validationError: string | null;
  handleFileChange: (event: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
  /** Upload a single file (used by file input and drag-drop). */
  handleUploadFile: (file: File) => Promise<void>;
  handleValidate: () => Promise<void>;
  clearValidation: () => void;
};

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentDataset, setCurrentDataset] = useState<UploadResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  async function handleUploadFile(file: File) {
    setError(null);
    setIsUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("/api/v1/upload", { method: "POST", body: form });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const detail =
          typeof data.detail === "string" ? data.detail : data.detail?.detail ?? res.statusText;
        throw new Error(detail);
      }
      const data = (await res.json()) as UploadResponse;
      setCurrentDataset(data);
      setValidationResult(null);
      setValidationError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    await handleUploadFile(file);
    event.target.value = "";
  }

  async function handleValidate() {
    if (!currentDataset?.dataset_id) return;
    setValidationError(null);
    setValidationResult(null);
    setIsValidating(true);
    try {
      const startRes = await fetch("/api/v1/validate/async", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: currentDataset.dataset_id }),
      });
      if (!startRes.ok) {
        const data = await startRes.json().catch(() => ({}));
        const detail =
          typeof data.detail === "string" ? data.detail : data.detail?.detail ?? startRes.statusText;
        throw new Error(detail);
      }
      const { job_id } = (await startRes.json()) as ValidationJobStatus;

      for (;;) {
        await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
        const jobRes = await fetch(`/api/v1/validate/jobs/${job_id}`);
        if (!jobRes.ok) {
          setValidationError("Failed to get validation status");
          break;
        }
        const job = (await jobRes.json()) as ValidationJobStatus;
        if (job.status === "completed" && job.result) {
          setValidationResult(job.result);
          break;
        }
        if (job.status === "failed") {
          setValidationError(job.error ?? "Validation failed");
          break;
        }
      }
    } catch (e) {
      setValidationError(e instanceof Error ? e.message : "Validation failed");
    } finally {
      setIsValidating(false);
    }
  }

  function clearValidation() {
    setValidationResult(null);
    setValidationError(null);
  }

  return (
    <AppContext.Provider
      value={{
        currentDataset,
        setCurrentDataset,
        isUploading,
        error,
        validationResult,
        validationIssues: validationResult?.issues ?? [],
        isValidating,
        validationError,
        handleFileChange,
        handleUploadFile,
        handleValidate,
        clearValidation,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
