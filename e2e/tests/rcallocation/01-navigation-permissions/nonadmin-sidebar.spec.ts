import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

// Derived from code, not verified live.  These run with the admin session;
// they need a storage state for a user without
// openstack.roles.allocationadmin.
test.describe('Navigation & permissions: regular user sidebar', () => {
  test('1.19 Regular user sees only New Request and My Requests', async ({
    page,
  }) => {
    test.fixme(true, 'needs a non-admin login: the test user is an allocation admin');

    await page.goto('/allocation/');
    const links = page
      .locator('#sidebar-accordion-allocation')
      .locator('a.openstack-panel');
    // The admin panels have permissions = ('openstack.roles.allocationadmin',).
    await expect(links).toHaveText(['New Request', 'My Requests']);
    await expect(
      page.getByRole('link', { name: 'Pending Requests' }),
    ).toHaveCount(0);
    await expect(
      page.getByRole('link', { name: 'Approved Requests' }),
    ).toHaveCount(0);
  });
});
