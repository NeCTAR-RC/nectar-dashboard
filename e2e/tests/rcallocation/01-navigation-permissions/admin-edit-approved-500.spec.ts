import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, open } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: admin edit of approved records', () => {
  // Current baseline, which looks like a pre-existing bug.  The 'Edit
  // request' row action is not offered for Approved rows, so the page is
  // unreachable from the UI.  Flag any change after the refactor.
  test('1.15 Admin edit_request on an Approved record currently returns 500', async ({
    page,
    allocations,
  }) => {
    const approved = await allocations.createApproved();

    // A fresh Approved allocation and an Approved history record of 135408.
    for (const id of [approved.id, 146946]) {
      const url = `/allocation/requests/edit_request/${id}/`;
      const response = await open(page, url);
      expect(response.status(), url).toBe(500);
      await expect(page).toHaveTitle(`TypeError at ${url}`);
      await expect(
        page.getByRole('heading', { name: `TypeError at ${url}` }),
      ).toBeVisible();
      // The debug page shows the quotes double-escaped (observed live).
      await expect(page.locator('.exception_value').first()).toHaveText(
        '&#x27;NoneType&#x27; object is not callable',
      );
    }
  });
});
