import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, readTable, row } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: Pending Requests', () => {
  test('1.5 Pending Requests State column and CSS classes', async ({ page }) => {
    await page.goto('/allocation/requests/');

    const submitted = row(page, 137133).locator('td').first();
    await expect(submitted).toHaveClass(/\btext-center\b/);
    expect(await submitted.innerHTML()).toBe(
      '<p title="Submitted" class="alloc-icon alloc-icon-wip">' +
        '<strong>E</strong></p>',
    );

    const updateRequested = row(page, 135408).locator('td').first();
    await expect(updateRequested).toHaveClass(/\btext-center\b/);
    const icon = updateRequested.locator('p');
    await expect(icon).toHaveText('X');
    await expect(icon).toHaveAttribute('title', 'Update requested');
    await expect(icon).toHaveAttribute('class', 'alloc-icon alloc-icon-wip');

    // Approved allocations are not pending, so no row uses the 'ok' icon.
    const rows = await readTable(page);
    expect(rows.length).toBeGreaterThan(0);
    for (const r of rows) {
      expect(r.stateClass, `row ${r.id}`).toBe('alloc-icon alloc-icon-wip');
      expect(r.cellClasses[0], `row ${r.id}`).toMatch(/\btext-center\b/);
    }
    await expect(page.locator('#datatableoptions .alloc-icon-ok')).toHaveCount(0);
  });
});
