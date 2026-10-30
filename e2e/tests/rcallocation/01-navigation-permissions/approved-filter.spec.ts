import { test, expect } from '../../../support/fixtures';
import {
  APPROVED_LOAD_TIMEOUT,
  acceptDialogsOnce,
  openApproved,
  readTable,
  row,
  visibleRows,
} from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: Approved Requests', () => {
  test('1.11 Approved Requests name filter', async ({ page }) => {
    // The list renders ~1600 rows and takes about 30 s; load it once.
    test.setTimeout(APPROVED_LOAD_TIMEOUT + 120_000);
    await openApproved(page);
    const rows = await readTable(page);
    const total = rows.length;

    // Expected matches, computed from the table itself so the counts can
    // drift with the dev data.  The filter matches any column text.
    const matching = (q: string) =>
      rows.filter((r) => r.cells.join(' ').toLowerCase().includes(q)).length;
    const accusantium = matching('accusantium');
    const intersect = matching('intersect');
    expect(accusantium).toBeGreaterThan(0);
    expect(accusantium).toBeLessThan(total);
    expect(intersect).toBeGreaterThan(0);
    expect(intersect).toBeLessThan(total);

    const navigations: string[] = [];
    page.on('framenavigated', (f) => {
      if (f === page.mainFrame()) navigations.push(f.url());
    });
    const filter = page.locator('input[name="DataTableOptions__filter__q"]');
    await expect(filter).toHaveAttribute('placeholder', 'Filter');

    await filter.pressSequentially('accusantium');
    await expect(visibleRows(page)).toHaveCount(accusantium, { timeout: 60_000 });
    for (const text of await visibleRows(page).allInnerTexts()) {
      expect(text.toLowerCase()).toContain('accusantium');
    }

    await filter.clear();
    await filter.pressSequentially('Intersect');
    await expect(visibleRows(page)).toHaveCount(intersect, { timeout: 60_000 });
    const firstIntersect = rows.find((r) =>
      r.cells.join(' ').toLowerCase().includes('intersect'),
    )!;
    await expect(row(page, Number(firstIntersect.id))).toBeVisible();

    await filter.clear();
    await filter.press('Backspace');
    await expect(visibleRows(page)).toHaveCount(total, { timeout: 60_000 });

    await expect(page).toHaveURL('/allocation/approved_requests/');
    expect(navigations).toEqual([]);
  });
});
