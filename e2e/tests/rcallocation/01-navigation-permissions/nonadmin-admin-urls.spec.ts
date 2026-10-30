import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, expectForbidden, open } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

// Derived from code, not verified live.  Capture the exact status and
// text on the first run with a non-admin account.
test.describe('Navigation & permissions: regular user and admin URLs', () => {
  test('1.20 Regular user is denied admin URLs', async ({ page }) => {
    test.fixme(true, 'needs a non-admin login: the test user is an allocation admin');

    // Panel list URLs are blocked by Horizon panel permissions; the exact
    // form (redirect or 403) is not verified.
    for (const url of [
      '/allocation/requests/',
      '/allocation/approved_requests/',
    ]) {
      const response = await open(page, url);
      const blocked =
        response.status() === 403 ||
        !page.url().endsWith(url);
      expect(blocked, `${url} is blocked`).toBe(true);
    }

    // Detail, edit, approve, decline and notes views check
    // user_is_allocation_admin in test_func, so expect the Forbidden page.
    // Since the access-check fix (75886a2) the edit, approve and reject
    // views also deny non-admins in the view itself.
    const submitted = 137133;
    const amendment = 135408;
    for (const url of [
      `/allocation/requests/view/${submitted}/`,
      `/allocation/requests/view/${submitted}/history`,
      `/allocation/requests/edit_request/${submitted}/`,
      `/allocation/requests/approve_request/${submitted}/`,
      `/allocation/requests/reject_request/${submitted}/`,
      `/allocation/requests/approve_change_request/${amendment}/`,
      `/allocation/requests/edit_notes/${submitted}/`,
    ]) {
      await expectForbidden(page, url);
    }
  });
});
