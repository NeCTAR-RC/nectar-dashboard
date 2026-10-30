import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, parseDjangoDate, readTable } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

const URGENCY = 8;

test.describe('Navigation & permissions: Pending Requests', () => {
  test('1.6 Pending Requests Urgency column values', async ({
    page,
    allocations,
  }) => {
    const fresh = await allocations.create();

    await page.goto('/allocation/requests/');
    const rows = await readTable(page);

    // The test user is not an approver for any site these allocations
    // relate to, so every value is parenthesised ('not relevant') and no
    // cell gets a pending_warn_level_N class.
    for (const r of rows) {
      expect(r.cells[URGENCY], `row ${r.id}`).toMatch(/^\(\w+\)$/);
      expect(r.cellClasses[URGENCY], `row ${r.id}`).toBe(
        'sortable normal_column',
      );
    }
    await expect(
      page.locator('#datatableoptions td[class*="pending_warn_level"]'),
    ).toHaveCount(0);

    const byId = new Map(rows.map((r) => [r.id, r]));
    expect(byId.get('137133')?.cells[URGENCY]).toBe('(Overdue)');
    expect(byId.get('135408')?.cells[URGENCY]).toBe('(Danger)');

    // Long-standing records: Submitted ones are Overdue (waiting more
    // than three weeks) and the Update requested ones are past their
    // expiry and at risk of auto-decline.
    const old = rows.filter(
      (r) => parseDjangoDate(r.cells[6]).getFullYear() <= 2025,
    );
    expect(old.length).toBeGreaterThan(0);
    for (const r of old) {
      const expected = r.cells[0] === 'X' ? '(Danger)' : '(Overdue)';
      expect(r.cells[URGENCY], `row ${r.id}`).toBe(expected);
    }

    // A request submitted today is New (observed live; not in the plan).
    expect(byId.get(String(fresh.id))?.cells[URGENCY]).toBe('(New)');
  });
});
