import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sampleGeojson = path.resolve(__dirname, "../../backend/resources/sample.geojson");

const MOCK_JOB_ID = "e2e-mock-validation-job-map-dashboard";

function mockValidationSuccess(page: Page) {
  let capturedDatasetId = "";

  page.route("**/api/v1/validate/async", async (route) => {
    const body = route.request().postDataJSON() as { dataset_id: string };
    capturedDatasetId = body.dataset_id;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        job_id: MOCK_JOB_ID,
        dataset_id: capturedDatasetId,
        status: "pending",
        error: null,
        result: null,
      }),
    });
  });

  page.route(`**/api/v1/validate/jobs/${MOCK_JOB_ID}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        job_id: MOCK_JOB_ID,
        dataset_id: capturedDatasetId,
        status: "completed",
        error: null,
        result: {
          dataset_id: capturedDatasetId,
          issues: [
            {
              feature_id: 1,
              type: "invalid_geometry",
              severity: "critical",
              description: "E2E mock geometry issue",
            },
          ],
          corrections: [
            {
              method: "buffer(0)",
              confidence: 0.9,
              explanation: "Fix invalid polygon",
              issue_index: 0,
            },
          ],
        },
      }),
    });
  });
}

async function uploadDataset(page: Page) {
  await page.goto("/#/upload");
  await page.locator('input[type="file"]').setInputFiles(sampleGeojson);
  await expect(page.getByText(/Loaded:\s*sample\.geojson/i)).toBeVisible({ timeout: 30_000 });
}

test("map page links to dashboard after validation (issue #120)", async ({ page }) => {
  mockValidationSuccess(page);
  await uploadDataset(page);
  await page.goto("/#/map");

  const validateBlock = page.locator("calcite-block.map-validate-block");
  await validateBlock.evaluate((el) => {
    (el as HTMLElement & { expanded: boolean }).expanded = true;
  });
  await validateBlock.getByRole("button", { name: /^Validate dataset$/i }).last().click();

  const reviewButton = page.getByRole("button", { name: /Review issues on Dashboard/i });
  await expect(reviewButton).toBeVisible({ timeout: 30_000 });
  await reviewButton.click();

  await expect(page).toHaveURL(/#\/dashboard/);
  await expect(page.getByRole("heading", { name: /Validation dashboard/i })).toBeVisible();
  await expect(page.locator(".dashboard-panel--issues")).toBeVisible();
});
