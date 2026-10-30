import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: sidebar', () => {
  test('1.1 Allocations sidebar group lists four panels in order', async ({
    page,
  }) => {
    await page.goto('/allocation/');
    await expect(page).toHaveURL('/allocation/');
    await expect(page).toHaveTitle('Allocation Request - Nectar Dashboard');
    // The New Request panel has no page title, so the breadcrumb shows
    // the literal 'None' (observed live).
    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'None',
    ]);

    const group = page.locator('#sidebar-accordion-allocation');
    const links = group.locator('a.openstack-panel');
    await expect(links).toHaveText([
      'New Request',
      'Pending Requests',
      'Approved Requests',
      'My Requests',
    ]);
    const hrefs = await links.evaluateAll((as) =>
      as.map((a) => a.getAttribute('href')),
    );
    expect(hrefs).toEqual([
      '/allocation/',
      '/allocation/requests/',
      '/allocation/approved_requests/',
      '/allocation/user_requests/',
    ]);
    await expect(links.first()).toHaveClass(/\bactive\b/);

    // Both admin panels are listed, so the test user holds
    // openstack.roles.allocationadmin.
    await expect(group.getByRole('link', { name: 'Pending Requests' })).toBeVisible();
    await expect(group.getByRole('link', { name: 'Approved Requests' })).toBeVisible();
  });
});
