import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce, columnHeaders, open, readTable } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

async function expectPage(
  page: import('@playwright/test').Page,
  url: string,
  title: string,
) {
  const response = await open(page, url);
  expect(response.status(), url).toBe(200);
  await expect(page).toHaveURL(url);
  await expect(page).toHaveTitle(`${title} - Nectar Dashboard`);
}

test.describe('Navigation & permissions: admin views', () => {
  test('1.13 Admin detail and history views', async ({ page, allocations }) => {
    // Step 1: the three detail views of the long-standing own allocation.
    for (const url of [
      '/allocation/requests/view/152179/',
      '/allocation/approved_requests/view/152179/',
      '/allocation/user_requests/view/152179/',
    ]) {
      await expectPage(page, url, 'View allocation request');
      // The h1 is in the page but hidden by the theme (observed live).
      await expect(page.locator('h1')).toHaveText('View Allocation Request');
      await expect(page.locator('h2', { hasText: 'fsdgfdsgdsfg' })).toBeVisible();
      await expect(
        page.locator('h3', { hasText: /^\s*Current Resources\s*$/ }),
      ).toBeVisible();
    }

    // Step 2: history views.
    const historyColumns = [
      'Project name',
      'Approver',
      'Bundle',
      'SUs',
      'Cores',
      'RAM',
      'Object Storage',
      'Volume Storage',
      'Status',
      'Modification time',
    ];
    await expectPage(page, '/allocation/approved_requests/view/152179/history',
      'Allocation Requests');
    await expect(page.locator('h1')).toHaveText('History');
    expect(await columnHeaders(page)).toEqual(historyColumns);

    await expectPage(page, '/allocation/requests/view/135408/history',
      'Allocation Requests');
    await expect(page.locator('h1')).toHaveText('History');
    expect(await columnHeaders(page)).toEqual(historyColumns);
    const history = await readTable(page);
    expect(history.map((r) => r.id)).toEqual([
      '135408',
      '146946',
      '138447',
      '137049',
      '135915',
      '135885',
      '135543',
      '135411',
    ]);
    const statuses = history.map((r) => r.cells[8]);
    expect(statuses).toContain('Update requested');
    expect(statuses).toContain('Approved');
    expect(history[0].cells[8]).toBe('Update requested');
    expect(history[1].cells[8]).toBe('Approved');
    for (const r of history) {
      expect(r.nameHref, `row ${r.id}`).toBe(`/allocation/requests/view/${r.id}/`);
    }

    // Step 3: notes and decline pages (GET only, never submitted).
    await expectPage(page, '/allocation/requests/edit_notes/152179/',
      'Edit allocation Admin notes');
    // Since the allocation status fix (NECTAR-17320) the decline page only
    // opens for requests awaiting approval, so use the Submitted 137133
    // rather than the Approved 152179 (guarded-400.spec.ts covers that).
    await expectPage(page, '/allocation/requests/reject_request/137133/',
      'Decline or Request Amendment from User');

    // Steps 4 and 5: approve and edit pages for Submitted and Update
    // requested records, both long-standing and freshly created.
    const submitted = await allocations.create();
    const amendment = await allocations.createAmendmentPending();
    for (const id of [137133, submitted.id]) {
      await expectPage(page, `/allocation/requests/approve_request/${id}/`,
        'Approve Request');
      await expectPage(page, `/allocation/requests/edit_request/${id}/`,
        'Edit Allocation Request');
    }
    for (const id of [135408, amendment.id]) {
      await expectPage(page,
        `/allocation/requests/approve_change_request/${id}/`,
        'Approve Request');
    }
  });
});
