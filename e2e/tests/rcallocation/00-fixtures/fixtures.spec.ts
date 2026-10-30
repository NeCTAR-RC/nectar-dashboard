import { test, expect } from '../../../support/fixtures';
import { declineViaUi } from '../../../support/allocations';

// Sanity checks for the allocation fixtures the other suites rely on.
test.describe('Allocation fixtures', () => {
  test('create, approve, amend and decline fresh allocations', async ({
    page,
    allocations,
  }) => {
    const submitted = await allocations.create();
    expect(submitted.status).toBe('E');
    expect(submitted.project_name).toMatch(/^pwtest-/);

    const pending = await allocations.createAmendmentPending();
    expect(pending.status).toBe('X');
    const history = await allocations.history(pending.id);
    expect(history.map((h) => h.status).sort()).toEqual(['A', 'E']);

    await declineViaUi(page, submitted.id, 'Playwright fixture decline');
    expect((await allocations.get(submitted.id)).status).toBe('R');

    await declineViaUi(page, pending.id, 'Playwright fixture decline');
    expect((await allocations.get(pending.id)).status).toBe('J');

    await page.goto('/allocation/user_requests/');
    await expect(page.getByRole('link', { name: submitted.project_name })).toBeVisible();
  });

  test('non-admin user session and allocations', async ({
    user,
    userPage,
    userAllocations,
    allocations,
  }) => {
    const own = await userAllocations.create();
    expect(own.status).toBe('E');
    expect(own.contact_email).toBe(user.username);

    // The admin can create an allocation for the user's project with
    // someone else as the contact, for the TenantManager scenarios.
    const managed = await allocations.create({
      project_id: user.project_id,
      contact_email: 'pwtest-other@example.org',
    });
    expect(managed.project_id).toBe(user.project_id);
    expect(managed.contact_email).toBe('pwtest-other@example.org');

    await userPage.goto('/allocation/');
    const sidebar = userPage.locator('#sidebar-accordion-allocation-default');
    await expect(sidebar.getByRole('link', { name: 'My Requests' })).toBeVisible();
    await expect(sidebar.getByRole('link', { name: 'Pending Requests' })).toHaveCount(0);
  });
});
