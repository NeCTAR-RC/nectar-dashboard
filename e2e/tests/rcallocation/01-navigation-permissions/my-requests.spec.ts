import { test, expect } from '../../../support/fixtures';
import { declineViaUi } from '../../../support/allocations';
import {
  TABLE,
  acceptDialogsOnce,
  columnHeaders,
  readTable,
} from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: My Requests', () => {
  test('1.12 My Requests table for an allocation admin', async ({
    page,
    allocations,
  }) => {
    const submitted = await allocations.create();
    const approved = await allocations.createApproved();
    const amendment = await allocations.createAmendmentPending();
    const declined = await allocations.create();
    await declineViaUi(page, declined.id, 'Playwright 01 My Requests');
    const amendDeclined = await allocations.createAmendmentPending();
    await declineViaUi(page, amendDeclined.id, 'Playwright 01 My Requests');

    await page
      .locator('#sidebar-accordion-allocation')
      .getByRole('link', { name: 'My Requests' })
      .click();
    await expect(page).toHaveURL('/allocation/user_requests/');
    await expect(page).toHaveTitle('Allocation Requests - Nectar Dashboard');
    await expect(page.locator('h1')).toHaveText(['My Requests']);
    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'My Requests',
    ]);
    expect(await columnHeaders(page)).toEqual([
      'State',
      'Name',
      'Current Associated Site',
      'National',
      'Contact',
      'Last Updated',
      'Expiry Date',
      'Actions',
    ]);

    // No filter box; one table action.
    await expect(
      page.locator('input[name="DataTableOptions__filter__q"]'),
    ).toHaveCount(0);
    await expect(
      page.getByRole('link', { name: 'Request a new allocation' }),
    ).toHaveAttribute('href', '/allocation/');

    const rows = await readTable(page);
    await expect(page.locator(`${TABLE} .table_count`).first()).toHaveText(
      rows.length === 1 ? 'Displaying 1 item' : `Displaying ${rows.length} items`,
    );

    // Ordered by status code.
    const states = rows.map((r) => r.cells[0]);
    expect(states).toEqual([...states].sort());

    // The long-standing own allocation.
    const own = rows.find((r) => r.id === '152179');
    expect(own, 'row 152179 listed').toBeDefined();
    expect(own!.cells.slice(0, 7)).toEqual([
      'A',
      'gdfgdfgdf fsdgfdsgdsfg',
      'QCIF',
      'True',
      'sorrison@gmail.com',
      'April 30, 2026',
      '-',
    ]);
    expect(own!.nameHref).toBe('/allocation/user_requests/view/152179/');
    expect(own!.actions).toEqual([
      {
        text: 'Amend/Extend allocation',
        href: '/allocation/user_requests/edit_change_request/152179/',
      },
    ]);

    // The row action depends on the status (observed live with fresh
    // allocations): E and R edit the request, A amends, X and J edit the
    // pending amendment.
    const cases: [number, string, string, string][] = [
      [submitted.id, 'E', 'Edit request', 'edit_request'],
      [declined.id, 'R', 'Edit request', 'edit_request'],
      [approved.id, 'A', 'Amend/Extend allocation', 'edit_change_request'],
      [amendment.id, 'X', 'Edit amend/extend request', 'edit_change_request'],
      [amendDeclined.id, 'J', 'Edit amend/extend request', 'edit_change_request'],
    ];
    for (const [id, status, text, view] of cases) {
      const r = rows.find((x) => x.id === String(id));
      expect(r, `row ${id} listed`).toBeDefined();
      expect(r!.cells[0], `row ${id}`).toBe(status);
      expect(r!.cells[4], `row ${id}`).toBe('sorrison@gmail.com');
      expect(r!.nameHref).toBe(`/allocation/user_requests/view/${id}/`);
      expect(r!.actions, `row ${id}`).toEqual([
        { text, href: `/allocation/user_requests/${view}/${id}/` },
      ]);
    }

    // Every row is the user's own: the admin role does not widen My
    // Requests (the test user manages no other projects).
    for (const r of rows) {
      expect(r.cells[4], `row ${r.id}`).toBe('sorrison@gmail.com');
    }
  });
});
