import { test, expect } from '../../../support/fixtures';
import {
  APPROVED_LOAD_TIMEOUT,
  acceptDialogsOnce,
  openApproved,
  readTable,
} from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: Approved Requests', () => {
  test('1.10 Approved Requests State column per status', async ({ page }) => {
    // The list renders ~1600 rows and takes about 30 s; load it once.
    test.setTimeout(APPROVED_LOAD_TIMEOUT + 120_000);
    await openApproved(page);
    const rows = await readTable(page);
    const byId = new Map(rows.map((r) => [r.id, r]));

    const expected: [string, string, string, string][] = [
      ['98355', 'A', 'Approved', 'alloc-icon alloc-icon-ok'],
      ['145272', 'X', 'Update requested', 'alloc-icon alloc-icon-wip'],
      ['132752', 'J', 'Update declined', 'alloc-icon alloc-icon-wip'],
    ];
    for (const [id, status, title, cls] of expected) {
      const r = byId.get(id);
      expect(r, `row ${id} listed`).toBeDefined();
      expect(r!.cells[0]).toBe(status);
      expect(r!.stateTitle).toBe(title);
      expect(r!.stateClass).toBe(cls);
      expect(r!.cellClasses[0]).toMatch(/\btext-center\b/);
    }

    // The same mapping holds for every row.
    const titles: Record<string, string> = {
      A: 'Approved',
      X: 'Update requested',
      J: 'Update declined',
    };
    for (const r of rows) {
      expect(r.stateTitle, `row ${r.id}`).toBe(titles[r.cells[0]]);
      expect(r.stateClass, `row ${r.id}`).toBe(
        r.cells[0] === 'A' ? 'alloc-icon alloc-icon-ok' : 'alloc-icon alloc-icon-wip',
      );
    }
  });
});
