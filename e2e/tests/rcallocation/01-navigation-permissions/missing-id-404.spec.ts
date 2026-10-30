import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, expectNotFound } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: missing allocations', () => {
  test('1.17 Missing allocation id returns 404', async ({ page }) => {
    // Django debug 404 page; the dev deployment runs with DEBUG on.
    await expectNotFound(page, '/allocation/requests/view/99999999/');
    await expect(
      page.getByText('No allocation request found matching the query'),
    ).toBeVisible();
  });
});
