import { test, expect } from '../../../support/fixtures';
import {
  TABLE,
  acceptDialogsOnce,
  columnHeaders,
  parseDjangoDate,
  readTable,
} from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: Pending Requests', () => {
  test('1.4 Pending Requests table layout and headings', async ({ page }) => {
    await page.goto('/allocation/');
    await page
      .locator('#sidebar-accordion-allocation')
      .getByRole('link', { name: 'Pending Requests' })
      .click();
    await expect(page).toHaveURL('/allocation/requests/');
    await expect(page).toHaveTitle('Allocation Requests - Nectar Dashboard');
    await expect(page.locator('h1')).toHaveText(['Allocation Requests']);
    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'Allocation Requests',
    ]);

    await expect(page.locator(TABLE)).toBeVisible();
    const headers = await columnHeaders(page);
    expect(headers).toEqual([
      'State',
      'Name',
      'Current Associated Site',
      'National',
      'Previous Approver',
      'Contact',
      'Last Updated',
      'Expiry Date',
      'Urgency',
      'Actions',
    ]);
    expect(headers).not.toContain('Approver');

    const rows = await readTable(page);
    // The item count tracks the rows; the number itself drifts.
    await expect(page.locator(`${TABLE} .table_count`).first()).toHaveText(
      `Displaying ${rows.length} items`,
    );

    // Only New, Submitted and Update requested allocations are pending.
    for (const r of rows) {
      expect(['N', 'E', 'X'], `row ${r.id}`).toContain(r.cells[0]);
    }

    // Ordered by submission date, which shows as Last Updated ascending.
    const lastUpdated = rows.map((r) => parseDjangoDate(r.cells[6]).getTime());
    for (let i = 1; i < lastUpdated.length; i++) {
      expect(
        lastUpdated[i],
        `row ${rows[i].id} is earlier than row ${rows[i - 1].id}`,
      ).toBeGreaterThanOrEqual(lastUpdated[i - 1]);
    }
    expect(rows[0].id).toBe('137133');
    expect(rows[0].cells[1]).toBe('qui Assimilated composite help-desk');
    expect(rows[0].cells[6]).toBe('March 1, 2024');

    // Date format and the '-' placeholder for empty site and expiry.
    expect(rows[0].cells[2]).toBe('-');
    expect(rows[0].cells[7]).toBe('-');
    const dates = rows.map((r) => r.cells[6]);
    expect(dates).toContain('Aug. 11, 2024');
    expect(dates).toContain('Sept. 2, 2024');
  });
});
