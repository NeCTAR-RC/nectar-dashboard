import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, expectNotFound } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: /allocation/request/', () => {
  test('1.3 /allocation/request/ is not a valid URL (404)', async ({ page }) => {
    await expectNotFound(page, '/allocation/request/');

    // The Django debug 404 page has no Horizon chrome, so reach the
    // sidebar from a normal page and follow 'New Request' from there.
    await page.goto('/allocation/user_requests/');
    await page
      .locator('#sidebar-accordion-allocation')
      .getByRole('link', { name: 'New Request' })
      .click();
    await expect(page).toHaveURL('/allocation/');
    await expect(page).toHaveTitle('Allocation Request - Nectar Dashboard');
  });
});
