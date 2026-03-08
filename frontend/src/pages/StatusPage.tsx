import { useApp } from "../context/AppContext";

export function StatusPage() {
  const {
    currentDataset,
    validationResult,
    isValidating,
    validationError,
    handleValidate,
  } = useApp();

  return (
    <section className="page-section" aria-labelledby="status-heading">
      <h2 id="status-heading" className="page-heading">
        Validation status
      </h2>
      {!currentDataset ? (
        <p className="empty-state">
          Upload a dataset on the <strong>Upload</strong> tab, then run validation here.
        </p>
      ) : (
        <>
          <p className="status-dataset">
            Current dataset: <strong>{currentDataset.filename}</strong>
          </p>
          <button
            type="button"
            onClick={handleValidate}
            disabled={isValidating}
            aria-busy={isValidating}
            aria-describedby={validationError ? "validation-error" : undefined}
            className="btn btn--primary"
          >
            {isValidating ? "Validating…" : "Validate geometry"}
          </button>
          {validationError && (
            <p id="validation-error" className="status-message status-message--error" role="alert">
              {validationError}
            </p>
          )}
          {validationResult && (
            <div className="validation-summary" role="status" aria-live="polite">
              {validationResult.issues.length === 0 ? (
                <p className="status-message status-message--success">
                  No geometry issues found for this dataset.
                </p>
              ) : (
                <p className="status-message status-message--error">
                  Found {validationResult.issues.length} geometry issue
                  {validationResult.issues.length !== 1 ? "s" : ""}.
                </p>
              )}
            </div>
          )}
        </>
      )}
    </section>
  );
}
