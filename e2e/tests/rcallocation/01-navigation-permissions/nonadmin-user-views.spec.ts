import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, expectForbidden, open, readTable } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

// Derived from code and unit tests, not verified live.  OWN_ID must be an
// allocation whose contact is the non-admin user; OTHER_ID one where the
// user is neither the contact nor a TenantManager of its project.
const OWN_ID = Number(process.env.NONADMIN_OWN_ALLOCATION ?? 0);
const OTHER_ID = 137133;
const HISTORY_ID = 146946;

test.describe('Navigation & permissions: regular user views', () => {
  test('1.21 Regular user My Requests and user views', async ({ page }) => {
    test.fixme(true, 'needs a non-admin login: the test user is an allocation admin');

    // Step 1: any user may list; the list is limited to their own (contact)
    // allocations and their TenantManager projects, ordered by status.
    const response = await open(page, '/allocation/user_requests/');
    expect(response.status()).toBe(200);
    const rows = await readTable(page);
    const states = rows.map((r) => r.cells[0]);
    expect(states).toEqual([...states].sort());
    expect(rows.map((r) => r.id)).toContain(String(OWN_ID));
    expect(rows.map((r) => r.id)).not.toContain(String(OTHER_ID));

    // Step 2: user detail views.
    const own = await open(page, `/allocation/user_requests/view/${OWN_ID}/`);
    expect(own.status()).toBe(200);
    await expect(page).toHaveTitle('View allocation request - Nectar Dashboard');
    await expectForbidden(page, `/allocation/user_requests/view/${OTHER_ID}/`);
    await expectForbidden(page, `/allocation/user_requests/view/${HISTORY_ID}/`);

    // Step 3: since the access-check fix (75886a2), the edit views deny
    // another user's allocation.  Before it, any logged-in user got 200
    // and could save.  The POST half of this step (403, no history record
    // created) is covered by the unit tests; it is not repeated here
    // because it would write to someone else's allocation if it regressed.
    await expectForbidden(
      page,
      `/allocation/user_requests/edit_request/${OTHER_ID}/`,
    );
    await expectForbidden(
      page,
      `/allocation/user_requests/edit_change_request/${OTHER_ID}/`,
    );
    for (const view of ['edit_request', 'edit_change_request']) {
      const r = await open(page, `/allocation/user_requests/${view}/${OWN_ID}/`);
      expect(r.status(), view).toBe(200);
    }
  });
});
