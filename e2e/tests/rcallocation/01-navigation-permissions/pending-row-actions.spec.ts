import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, readTable } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

function expectedActions(id: number | string) {
  return [
    { text: 'Edit request', href: `/allocation/requests/edit_request/${id}/` },
    { text: 'View history', href: `/allocation/requests/view/${id}/history` },
  ];
}

test.describe('Navigation & permissions: Pending Requests', () => {
  test('1.8 Pending Requests row actions and links', async ({
    page,
    allocations,
  }) => {
    const submitted = await allocations.create();
    const amendment = await allocations.createAmendmentPending();

    await page.goto('/allocation/requests/');

    // 'Edit request' is the primary action; 'View history' sits in the
    // row's dropdown menu.
    const r137133 = page.locator('#DataTableOptions__row__137133');
    await expect(r137133.locator('td').nth(1).getByRole('link')).toHaveAttribute(
      'href',
      '/allocation/requests/view/137133/',
    );
    await expect(
      r137133.locator('#DataTableOptions__row_137133__action_edit'),
    ).toHaveAttribute('href', '/allocation/requests/edit_request/137133/');
    await expect(
      r137133.locator(
        'ul.dropdown-menu #DataTableOptions__row_137133__action_view_history',
      ),
    ).toHaveAttribute('href', '/allocation/requests/view/137133/history');

    const rows = await readTable(page);
    const byId = new Map(rows.map((r) => [r.id, r]));
    for (const id of [137133, 135408, submitted.id, amendment.id]) {
      const r = byId.get(String(id));
      expect(r, `row ${id} listed`).toBeDefined();
      expect(r!.nameHref).toBe(`/allocation/requests/view/${id}/`);
      expect(r!.actions).toEqual(expectedActions(id));
    }
    expect(byId.get(String(submitted.id))!.cells[0]).toBe('E');
    expect(byId.get(String(amendment.id))!.cells[0]).toBe('X');

    // Every pending row offers both actions.
    for (const r of rows) {
      expect(r.actions, `row ${r.id}`).toEqual(expectedActions(r.id));
    }
  });
});
