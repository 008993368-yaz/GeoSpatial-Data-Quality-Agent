import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

class AppErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  state = { hasError: false, error: null as Error | null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return (
        <div style={{ padding: "1rem", fontFamily: "system-ui, sans-serif", maxWidth: "600px" }}>
          <h1 style={{ color: "#b00020" }}>Something went wrong</h1>
          <pre style={{ overflow: "auto", fontSize: "0.85rem" }}>
            {this.state.error.message}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

const root = document.getElementById("root");
if (!root) {
  document.body.innerHTML = "<p>Root element #root not found.</p>";
} else {
  try {
    ReactDOM.createRoot(root).render(
      <React.StrictMode>
        <AppErrorBoundary>
          <App />
        </AppErrorBoundary>
      </React.StrictMode>
    );
  } catch (e) {
    root.innerHTML = `<p style="padding:1rem;font-family:system-ui,sans-serif;color:#b00020">Failed to start: ${e instanceof Error ? e.message : String(e)}</p>`;
  }
}
