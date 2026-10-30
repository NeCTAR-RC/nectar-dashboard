import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce } from './helpers';

test.beforeEach(({ userPage }) => acceptDialogsOnce(userPage));

// Verified live with the non-admin e2e user (member and TenantManager of
// one project, no openstack.roles.allocationadmin).
test.describe('Navigation & permissions: regular user sidebar', () => {
  test('1.19 Regular user sees only New Request and My Requests', async ({
    userPage: page,
  }) => {
    await page.goto('/allocation/');
    await expect(page).toHaveURL('/allocation/');
    await expect(page).toHaveTitle('Allocation Request - Nectar Dashboard');

    const group = page.locator('#sidebar-accordion-allocation-default');
    const links = group.locator('a.openstack-panel');
    // The admin panels have permissions = ('openstack.roles.allocationadmin',).
    await expect(links).toHaveText(['New Request', 'My Requests']);
    const hrefs = await links.evaluateAll((as) =>
      as.map((a) => a.getAttribute('href')),
    );
    expect(hrefs).toEqual(['/allocation/', '/allocation/user_requests/']);
    await expect(links.first()).toHaveClass(/\bactive\b/);

    await expect(
      page.getByRole('link', { name: 'Pending Requests' }),
    ).toHaveCount(0);
    await expect(
      page.getByRole('link', { name: 'Approved Requests' }),
    ).toHaveCount(0);
  });
});
