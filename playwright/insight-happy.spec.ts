import { test, expect } from '@playwright/test';

test('insight happy path shows actions', async ({ page }) => {
  await page.route('**/ready', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ ready: true })
  }));

  await page.route('**/analyze', async route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        property: { domains: ['example.com'], confidence: 1, notes: [] },
        martech: { core: ['GTM'] },
        cms: [],
        degraded: false
      })
    });
  });

  await page.route('**/insight', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ result: { insight: 'Test insight' } })
  }));

  await page.route('**/postprocess-report', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ downloads: {} })
  }));

  await page.route('**/generate-insight-and-personas', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      result: {
        insight: {
          evidence: 'Flow',
          actions: { a1: { title: 'Do it', reasoning: 'why', benefit: 'gain' } }
        },
        personas: { p1: { name: 'P1' } },
        degraded: false
      }
    })
  }));

  await page.goto('/');
  await page.fill('input[aria-label="URL to analyze"]', 'example.com');
  await page.click('button[aria-label="analyze"]');

  await page.getByText('example.com');
  await page.getByRole('button', { name: /generate insights/i }).click();

  const actions = page.locator('button:has-text("Do it")');
  await expect(actions).toHaveCount(1);
});
