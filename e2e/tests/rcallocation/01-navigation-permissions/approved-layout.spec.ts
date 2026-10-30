import { test, expect } from '../../../support/fixtures';
import {
  APPROVED_LOAD_TIMEOUT,
  TABLE,
  acceptDialogsOnce,
  columnHeaders,
  readTable,
} from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: Approved Requests', () => {
  test('1.9 Approved Requests table layout', async ({ page, allocations }) => {
    // The list renders ~1600 rows and takes about 30 s; load it once.
    test.setTimeout(APPROVED_LOAD_TIMEOUT + 120_000);
    const approved = await allocations.createApproved();

    await page.goto('/allocation/user_requests/');
    await page
      .locator('#sidebar-accordion-allocation')
      .getByRole('link', { name: 'Approved Requests' })
      .click({ timeout: APPROVED_LOAD_TIMEOUT });
    await expect(page).toHaveURL('/allocation/approved_requests/');
    await expect(page).toHaveTitle('Allocation Requests - Nectar Dashboard');
    await expect(page.locator('h1')).toHaveText(['Approved Requests']);
    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'Approved Requests',
    ]);
    expect(await columnHeaders(page)).toEqual([
      'State',
      'Name',
      'Current Associated Site',
      'National',
      'Approver',
      'Contact',
      'Last Updated',
      'Expiry Date',
      'Actions',
    ]);

    const rows = await readTable(page);
    // One unpaginated page: the count covers every row.
    await expect(page.locator(`${TABLE} .table_count`).first()).toHaveText(
      `Displaying ${rows.length} items`,
    );
    await expect(page.locator('.pagination, a[href*="marker="]')).toHaveCount(0);

    // Only top-level Approved, Update requested and Update declined
    // allocations, with all three present.
    const statuses = new Set(rows.map((r) => r.cells[0]));
    expect([...statuses].sort()).toEqual(['A', 'J', 'X']);

    // Sorted by project name ascending.
    expect(rows[0].id).toBe('98355');
    expect(rows[0].cells[1]).toBe('a Enhanced mission-critical synergy');
    for (let i = 1; i < rows.length; i++) {
      const order = rows[i - 1].name.localeCompare(rows[i].name, 'en', {
        sensitivity: 'base',
      });
      expect(
        order,
        `row ${rows[i].id} '${rows[i].name}' sorts before ` +
          `row ${rows[i - 1].id} '${rows[i - 1].name}'`,
      ).toBeLessThanOrEqual(0);
    }
    expect(rows.some((r) => r.name.startsWith('accusantium'))).toBe(true);

    // Name links use the admin requests/view URL; the only row action is
    // 'View history'.
    for (const r of rows) {
      expect(r.nameHref, `row ${r.id}`).toBe(`/allocation/requests/view/${r.id}/`);
      expect(r.actions, `row ${r.id}`).toEqual([
        {
          text: 'View history',
          href: `/allocation/requests/view/${r.id}/history`,
        },
      ]);
    }

    // The allocation approved by this test is listed.
    const mine = rows.find((r) => r.id === String(approved.id));
    expect(mine, 'fresh approved allocation listed').toBeDefined();
    expect(mine!.cells[0]).toBe('A');
    expect(mine!.cells[1]).toBe(
      `${approved.project_name} ${approved.project_description}`,
    );
  });
});
