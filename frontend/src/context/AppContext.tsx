import { createContext, useContext, useState, type ReactNode } from "react";
import type { ValidationResult } from "../types/api";

export type UploadResponse = {
  dataset_id: string;
  filename: string;
  bounds?: number[] | null;
};

type AppContextValue = {
  currentDataset: UploadResponse | null;
  setCurrentDataset: (d: UploadResponse | null) => void;
  isUploading: boolean;
  error: string | null;
  validationResult: ValidationResult | null;
  isValidating: boolean;
  validationError: string | null;
  handleFileChange: (event: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
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

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
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
      event.target.value = "";
    }
  }

  async function handleValidate() {
    if (!currentDataset?.dataset_id) return;
    setValidationError(null);
    setValidationResult(null);
    setIsValidating(true);
    try {
      const res = await fetch(`/api/v1/validate/${currentDataset.dataset_id}`);
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const detail =
          typeof data.detail === "string" ? data.detail : data.detail?.detail ?? res.statusText;
        throw new Error(detail);
      }
      const data = (await res.json()) as ValidationResult;
      setValidationResult(data);
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
        isValidating,
        validationError,
        handleFileChange,
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
