import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, expectForbidden, open } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: history records', () => {
  test('1.16 User view denied for a history record (403 look)', async ({
    page,
  }) => {
    // 146946 is an Approved history record of 135408.
    await expectForbidden(page, '/allocation/user_requests/view/146946/');

    // The admin view does not deny history records.
    const response = await open(page, '/allocation/requests/view/146946/');
    expect(response.status()).toBe(200);
    // The h1 is in the page but hidden by the theme (observed live).
    await expect(page.locator('h1')).toHaveText('View Allocation Request');
    await expect(
      page.locator('h2', { hasText: 'Assimilated responsive archive' }),
    ).toBeVisible();

    // Since the access-check fix (NECTAR-17317), the user edit views deny
    // history records too, even for an allocation admin.  Before it, both
    // returned 200.
    await expectForbidden(page, '/allocation/user_requests/edit_request/146946/');
    await expectForbidden(
      page,
      '/allocation/user_requests/edit_change_request/146946/',
    );
  });
});
