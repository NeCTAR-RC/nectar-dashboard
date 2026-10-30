import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, row, visibleRows } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: Pending Requests', () => {
  test('1.7 Pending Requests name filter is client-side and matches any column', async ({
    page,
  }) => {
    await page.goto('/allocation/requests/');
    const total = await page.locator('#datatableoptions tbody tr').count();
    expect(total).toBeGreaterThan(3);

    const filter = page.locator('input[name="DataTableOptions__filter__q"]');
    await expect(filter).toHaveAttribute('placeholder', 'Filter');
    const navigations: string[] = [];
    page.on('framenavigated', (f) => {
      if (f === page.mainFrame()) navigations.push(f.url());
    });

    // fill() alone does not trigger the keyup-driven filter.
    await filter.pressSequentially('Intersect');
    for (const id of [135408, 58677, 135339]) {
      await expect(row(page, id)).toBeVisible();
    }
    // 'Intersect' only appears in the site column, so this checks the
    // filter matches any column, not just the name.
    await expect(visibleRows(page)).toHaveCount(3);
    for (const text of await visibleRows(page).allInnerTexts()) {
      expect(text).toContain('Intersect');
    }
    await expect(page).toHaveURL('/allocation/requests/');

    await filter.clear();
    await filter.pressSequentially('zzzzno');
    await expect(page.locator('#datatableoptions tbody')).toContainText(
      'No items to display.',
    );

    await filter.clear();
    await filter.pressSequentially('automated composite');
    await expect(visibleRows(page)).toHaveCount(1);
    await expect(row(page, 135408)).toBeVisible();

    await filter.clear();
    await filter.pressSequentially('135408');
    await expect(visibleRows(page)).toHaveCount(1);
    await expect(row(page, 135408)).toBeVisible();

    await filter.clear();
    await filter.press('Backspace');
    await expect(visibleRows(page)).toHaveCount(total);

    // Filtering never reloaded the page.
    expect(navigations).toEqual([]);
  });
});
