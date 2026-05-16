import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sampleGeojson = path.resolve(__dirname, "../../backend/resources/sample.geojson");

const MOCK_JOB_ID = "e2e-mock-validation-job-apply";

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

function applyCorrectionsButton(page: Page) {
  return page.getByRole("button", { name: /Apply correction choices to the server/i });
}

test("dashboard shows empty state with upload link before dataset loaded", async ({ page }) => {
  await page.goto("/#/dashboard");
  const dashboard = page.getByLabel("Validation dashboard");
  await expect(page.getByRole("heading", { name: /Validation dashboard/i })).toBeVisible();
  await expect(dashboard.getByText(/No dataset loaded/i)).toBeVisible();
  const uploadLink = dashboard.getByRole("link", { name: "Upload" });
  await expect(uploadLink).toBeVisible();
  await uploadLink.click();
  await expect(page).toHaveURL(/#\/upload/);
});

test.describe("Apply corrections disabled hints (issue #116)", () => {
  test("shows hint to run validation before validation has run", async ({ page }) => {
    await uploadDataset(page);
    await page.goto("/#/dashboard");

    await expect(page.getByText(/Run validation to load issues and correction suggestions/i)).toBeVisible();
    await expect(applyCorrectionsButton(page)).toBeDisabled();
  });

  test("shows hint to approve or reject when validated with no decisions", async ({ page }) => {
    mockValidationSuccess(page);
    await uploadDataset(page);
    await page.goto("/#/dashboard");
    await page.getByRole("button", { name: /^Run validation$/i }).click();
    await expect(page.getByText(/Validation in progress/i)).toBeHidden({ timeout: 30_000 });
    await expect(page.getByRole("button", { name: /Open quality report/i })).toBeVisible({
      timeout: 15_000,
    });

    await expect(
      page.getByText(/Approve or reject at least one suggested correction in Issue details/i),
    ).toBeVisible();
    await expect(applyCorrectionsButton(page)).toBeDisabled();
  });

  test("shows pending custom hint when Custom is chosen but not saved", async ({ page }) => {
    mockValidationSuccess(page);
    await uploadDataset(page);
    await page.goto("/#/dashboard");
    await page.getByRole("button", { name: /^Run validation$/i }).click();
    await expect(page.getByText(/Validation in progress/i)).toBeHidden({ timeout: 30_000 });
    await expect(page.getByRole("button", { name: /Open quality report/i })).toBeVisible({
      timeout: 15_000,
    });

    await page.locator(".issues-panel-item").first().click();
    await expect(page.getByRole("button", { name: /Use a custom fix you will edit before apply/i })).toBeVisible();
    await page.getByRole("button", { name: /Use a custom fix you will edit before apply/i }).click();

    await expect(
      page.getByText(/Save custom fixes for all Custom issues before applying corrections/i),
    ).toBeVisible();
    await expect(applyCorrectionsButton(page)).toBeDisabled();
  });
});
