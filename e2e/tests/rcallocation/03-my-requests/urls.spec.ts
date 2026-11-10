import { test, expect } from '../../../support/fixtures';
import {
  AMEND_TITLE,
  EDIT_TITLE,
  acceptDialogsOnce,
  AMEND_STATE_TEXT,
  amendUrl,
  EDIT_STATE_TEXT,
  editUrl,
  expectForbidden,
  expectGuarded400,
  expectNotFound,
  open,
  viewUrl,
} from './helpers';

// Suite 03: access to the user views by URL, as the allocation admin.
// GET only; nothing is submitted.

// The dev dashboard is shared with other suites running at the same time;
// form posts and page loads (the My Requests list above all) can take
// minutes under that load.
test.describe.configure({ timeout: 600_000 });

test.beforeEach(({ page }) => acceptDialogsOnce(page));

// Long-standing history records of other allocations.
const HISTORY = [146946, 138447, 137049];

test.describe('My Requests URL guards', () => {
  test('1.20 (5.1) View, edit and amend URLs for history records are denied', async ({
    page,
    allocations,
  }) => {
    // Plus a history record of the admin's own fresh allocation.
    const a = await allocations.createApproved();
    const own = (await allocations.history(a.id)).map((h) => h.id);
    expect(own.length).toBeGreaterThan(0);

    for (const id of [...HISTORY, ...own]) {
      await expectForbidden(page, viewUrl(id));
      // Since the access-check fix (NECTAR-17317) the edit views deny history
      // records too; before it they returned 200.
      await expectForbidden(page, editUrl(id));
      await expectForbidden(page, amendUrl(id));
    }
  });

  test('1.21 (5.2) Edit URLs check the status; a missing id is 404', async ({
    page,
    allocations,
  }) => {
    const a = await allocations.createApproved();
    const e = await allocations.create();

    // Each view opens only for the status whose list action links to it.
    // Before the allocation status fix (NECTAR-17320) both views accepted
    // any status.
    for (const [url, title] of [
      [editUrl(e.id), EDIT_TITLE],
      [amendUrl(a.id), AMEND_TITLE],
    ]) {
      const response = await open(page, url);
      expect(response.status(), url).toBe(200);
      await expect(page).toHaveTitle(title);
    }
    await expectGuarded400(page, editUrl(a.id), EDIT_STATE_TEXT);
    await expectGuarded400(page, amendUrl(e.id), AMEND_STATE_TEXT);

    await expectNotFound(page, viewUrl(99999999));
  });
});
