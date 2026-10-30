import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, expectForbidden, open, readTable } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

// Derived from code, not verified live.  MANAGED_ID must be an allocation
// for a project the user is TenantManager of, with a different contact.
const MANAGED_ID = Number(process.env.TENANTMANAGER_ALLOCATION ?? 0);

test.describe('Navigation & permissions: TenantManager', () => {
  test('1.22 TenantManager access', async ({ page }) => {
    test.fixme(
      true,
      'needs a non-admin TenantManager login: the test user is an allocation admin',
    );

    // check_tm_or_alloc_admin uses manuka users.projects(user, 'TenantManager').
    await open(page, '/allocation/user_requests/');
    const rows = await readTable(page);
    const managed = rows.find((r) => r.id === String(MANAGED_ID));
    expect(managed, 'managed allocation listed').toBeDefined();

    for (const view of ['view', 'edit_request', 'edit_change_request']) {
      const url = `/allocation/user_requests/${view}/${MANAGED_ID}/`;
      const response = await open(page, url);
      expect(response.status(), url).toBe(200);
    }

    // The admin-only requests/* URLs stay denied.
    await expectForbidden(page, `/allocation/requests/view/${MANAGED_ID}/`);
    await expectForbidden(
      page,
      `/allocation/requests/edit_request/${MANAGED_ID}/`,
    );
  });
});
