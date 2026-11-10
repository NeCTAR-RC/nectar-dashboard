import { test, expect } from '../../../support/fixtures';
import {
  acceptDialogsOnce,
  expectGuarded400,
  expectNotAuthorized,
  open,
  readTable,
} from './helpers';

test.beforeEach(({ userPage }) => acceptDialogsOnce(userPage));

const OTHER_CONTACT = 'pwtest-other@example.org';

// Verified live with the non-admin e2e user, who is TenantManager of its
// project.  The admin creates an allocation for that project with someone
// else as the contact.
test.describe('Navigation & permissions: TenantManager', () => {
  test('1.22 TenantManager access', async ({
    userPage: page,
    user,
    allocations,
  }) => {
    const managed = await allocations.create({
      project_id: user.project_id,
      contact_email: OTHER_CONTACT,
    });

    // check_tm_or_alloc_admin uses manuka users.projects(user, 'TenantManager').
    const response = await open(page, '/allocation/user_requests/');
    expect(response.status()).toBe(200);
    const rows = await readTable(page);
    const row = rows.find((r) => r.id === String(managed.id));
    expect(row, 'managed allocation listed').toBeDefined();
    expect(row!.cells[0]).toBe('E');
    expect(row!.cells[4]).toBe(OTHER_CONTACT);
    expect(row!.nameHref).toBe(`/allocation/user_requests/view/${managed.id}/`);
    expect(row!.actions).toEqual([
      {
        text: 'Edit request',
        href: `/allocation/user_requests/edit_request/${managed.id}/`,
      },
    ]);

    for (const [view, title] of [
      ['view', 'View allocation request - Nectar Dashboard'],
      ['edit_request', 'Edit Allocation Request - Nectar Dashboard'],
    ]) {
      const url = `/allocation/user_requests/${view}/${managed.id}/`;
      const r = await open(page, url);
      expect(r.status(), url).toBe(200);
      await expect(page).toHaveTitle(title);
    }
    // The TenantManager passes the access check for the amend view, but
    // since the allocation status fix (NECTAR-17320) it only opens for A,
    // X and J; before it this returned 200 for this Submitted allocation.
    await expectGuarded400(
      page,
      `/allocation/user_requests/edit_change_request/${managed.id}/`,
      'Allocation cannot be amended in its current state',
    );

    // The admin-only requests/* URLs stay denied, with Horizon's
    // NotAuthorized page.
    await expectNotAuthorized(page, `/allocation/requests/view/${managed.id}/`);
    await expectNotAuthorized(
      page,
      `/allocation/requests/edit_request/${managed.id}/`,
    );
  });
});
