import { test, expect } from './support/fixtures';

// Seed for the Playwright test agents: an authenticated page on the
// Allocations dashboard with the blocking widgets disabled.
test.describe('Test group', () => {
  test('seed', async ({ page }) => {
    await page.goto('/allocation/');
    await expect(page).not.toHaveURL(/\/auth\/login/);
  });
});
