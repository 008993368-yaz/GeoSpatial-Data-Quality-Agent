import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sampleGeojson = path.resolve(__dirname, "../../backend/resources/sample.geojson");

const MOCK_JOB_ID = "e2e-mock-validation-job";

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
            {
              feature_id: 2,
              type: "attribute_typo",
              severity: "warning",
              description: "E2E mock attribute issue",
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

async function uploadAndValidate(page: Page) {
  mockValidationSuccess(page);
  await uploadDataset(page);

  await page.goto("/#/dashboard");
  await page.getByRole("button", { name: /^Run validation$/i }).click();
  await expect(page.getByText(/Validation in progress/i)).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText(/Validation in progress/i)).toBeHidden({ timeout: 30_000 });
  await expect(page.getByRole("button", { name: /Open quality report/i })).toBeVisible({
    timeout: 15_000,
  });
}

function viewReportButton(page: Page) {
  return page.getByRole("button", { name: /Open quality report/i });
}

test.describe("Quality report (issue #12)", () => {
  test("validation config API is available", async ({ request }) => {
    const res = await request.get("/api/v1/validation/config");
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data.pipeline_steps).toContain("geometry_validation");
    expect(data.openai_model).toBeTruthy();
  });

  test("report page shows empty state before upload", async ({ page }) => {
    await page.goto("/#/report");
    await expect(page.getByRole("heading", { name: /Quality report/i })).toBeVisible();
    await expect(page.getByText(/Upload a dataset on the/i)).toBeVisible();
  });

  test("report page shows empty state when dataset uploaded but not validated", async ({
    page,
  }) => {
    await uploadDataset(page);
    await page.goto("/#/report");
    await expect(page.getByText(/Run validation on the/i)).toBeVisible();
  });

  test("full flow: validate then view report with exports", async ({ page }) => {
    await uploadAndValidate(page);

    await viewReportButton(page).click();
    await expect(page).toHaveURL(/#\/report/);

    await expect(page.getByRole("heading", { name: /Quality assessment report/i })).toBeVisible();
    await expect(page.getByText(/sample\.geojson/i).first()).toBeVisible();
    await expect(page.getByText(/Validation configuration/i)).toBeVisible();
    await expect(page.getByText(/Total issues/i)).toBeVisible();
    await expect(page.getByRole("cell", { name: "invalid_geometry" }).first()).toBeVisible();

    await expect(page.getByRole("button", { name: /Download report as JSON/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Download report as Markdown/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Print or save as PDF/i })).toBeVisible();

    const [jsonDownload] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("button", { name: /Download report as JSON/i }).click(),
    ]);
    expect(jsonDownload.suggestedFilename()).toMatch(/report\.json$/i);

    const [mdDownload] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("button", { name: /Download report as Markdown/i }).click(),
    ]);
    expect(mdDownload.suggestedFilename()).toMatch(/report\.md$/i);
  });

  test("server export endpoint returns markdown attachment", async ({ request }) => {
    const payload = {
      generated_at: new Date().toISOString(),
      dataset: {
        dataset_id: "e2e-test",
        filename: "sample.geojson",
        feature_count: 3,
        geometry_type: "Point",
        crs: "EPSG:4326",
        bounds: [-122.43, 37.77, -122.41, 37.79],
      },
      validation: {
        dataset_id: "e2e-test",
        issues: [
          {
            feature_id: 0,
            type: "invalid_geometry",
            severity: "critical",
            description: "Test issue",
          },
        ],
        corrections: [],
      },
      summary: {
        totalIssues: 1,
        critical: 1,
        warning: 0,
        byCategory: { geometry: 1, attribute: 0, topology: 0 },
        byType: { invalid_geometry: 1 },
      },
    };

    const res = await request.post("/api/v1/reports/export?format=markdown", {
      data: payload,
    });
    expect(res.ok()).toBeTruthy();
    expect(res.headers()["content-type"]).toContain("text/markdown");
    const body = await res.text();
    expect(body).toContain("# Quality assessment report");
    expect(body).toContain("invalid_geometry");
  });
});
