import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    // @arcgis/core has no root entry and lazy-loads many submodules at runtime.
    // Excluding it from pre-bundling serves its ESM directly and avoids
    // "Failed to fetch dynamically imported module" basemap errors.
    exclude: ["@arcgis/core"],
  },
  build: {
    rollupOptions: {
      external: (id) =>
        id === "@arcgis/core" || id.startsWith("@arcgis/core/"),
    },
    commonjsOptions: {
      include: [/node_modules/],
      transformMixedEsModules: true,
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 4173,
    host: "127.0.0.1",
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
