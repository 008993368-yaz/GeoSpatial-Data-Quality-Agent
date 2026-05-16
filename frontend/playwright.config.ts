import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig, devices } from "@playwright/test";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const backendDir = path.resolve(__dirname, "../backend");

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  timeout: 120_000,
  expect: { timeout: 15_000 },
  use: {
    ...devices["Desktop Chrome"],
    baseURL: "http://127.0.0.1:4173",
    trace: "on-first-retry",
    acceptDownloads: true,
  },
  webServer: [
    {
      command: "python -m uvicorn main:app --host 127.0.0.1 --port 8000",
      cwd: backendDir,
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: true,
      timeout: 180_000,
    },
    {
      command: "npm run build && npm run preview -- --host 127.0.0.1 --port 4173",
      cwd: __dirname,
      url: "http://127.0.0.1:4173",
      reuseExistingServer: !process.env.CI,
      timeout: 180_000,
    },
  ],
});
