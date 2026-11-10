import { test, expect } from '../../../support/fixtures';
import {
  SAVE_TIMEOUT,
  acceptDialogsOnce,
  addInvestigator,
  clickAndWaitForURL,
  expectForbidden,
  expectGuarded400,
  open,
  readTable,
} from './helpers';

test.beforeEach(({ userPage }) => acceptDialogsOnce(userPage));

// Verified live with the non-admin e2e user.  OTHER_ID is an allocation
// where the user is neither the contact nor a TenantManager of its
// project; HISTORY_ID is a history record.
const OTHER_ID = 137133;
const HISTORY_ID = 146946;

test.describe('Navigation & permissions: regular user views', () => {
  test('1.21 Regular user My Requests and user views', async ({
    userPage: page,
    user,
    userAllocations,
  }) => {
    // One UI save, which can be slow under load.
    test.setTimeout(SAVE_TIMEOUT + 180_000);
    const own = await userAllocations.create();
    // The edit form rejects an allocation without a Chief Investigator.
    await addInvestigator(user.id, own.id);

    // Step 1: any user may list; the list is limited to their own (contact)
    // allocations and their TenantManager projects, ordered by status.
    const response = await open(page, '/allocation/user_requests/');
    expect(response.status()).toBe(200);
    await expect(page).toHaveTitle('Allocation Requests - Nectar Dashboard');
    await expect(page.locator('h1')).toHaveText(['My Requests']);
    const rows = await readTable(page);
    const states = rows.map((r) => r.cells[0]);
    expect(states).toEqual([...states].sort());
    const ids = rows.map((r) => r.id);
    expect(ids).not.toContain(String(OTHER_ID));
    const row = rows.find((r) => r.id === String(own.id));
    expect(row, `row ${own.id} listed`).toBeDefined();
    expect(row!.cells[0]).toBe('E');
    expect(row!.cells[4]).toBe(user.username);
    expect(row!.nameHref).toBe(`/allocation/user_requests/view/${own.id}/`);
    expect(row!.actions).toEqual([
      {
        text: 'Edit request',
        href: `/allocation/user_requests/edit_request/${own.id}/`,
      },
    ]);

    // Step 2: user detail views.
    const view = await open(page, `/allocation/user_requests/view/${own.id}/`);
    expect(view.status()).toBe(200);
    await expect(page).toHaveTitle('View allocation request - Nectar Dashboard');
    await expectForbidden(page, `/allocation/user_requests/view/${OTHER_ID}/`);
    await expectForbidden(page, `/allocation/user_requests/view/${HISTORY_ID}/`);

    // Step 3: since the access-check fix (NECTAR-17317), the edit views deny
    // another user's allocation.  Before it, any logged-in user got 200
    // and could save.  The POST half of this step (403, no history record
    // created) is covered by the unit tests; it is not repeated here
    // because it would write to someone else's allocation if it regressed.
    await expectForbidden(
      page,
      `/allocation/user_requests/edit_request/${OTHER_ID}/`,
    );
    await expectForbidden(
      page,
      `/allocation/user_requests/edit_change_request/${OTHER_ID}/`,
    );

    // Since the allocation status fix (NECTAR-17320) the amend view only
    // opens for A, X and J, matching the list's actions; before it this
    // returned 200.
    await expectGuarded400(
      page,
      `/allocation/user_requests/edit_change_request/${own.id}/`,
      'Allocation cannot be amended in its current state',
    );

    // The user's own Submitted allocation opens in the edit view.  The e2e
    // user has an ORCID linked, so the 'You must connect to ORCID' modal,
    // which is always in the page, stays closed.  Step 4 uses this page.
    const r = await open(page, `/allocation/user_requests/edit_request/${own.id}/`);
    expect(r.status(), 'edit_request').toBe(200);
    await expect(page).toHaveTitle('Edit Allocation Request - Nectar Dashboard');
    await expect(page.locator('#orcid_modal')).toBeAttached();
    await expect(page.locator('#orcid_modal')).toBeHidden();

    // Step 4: the user can save a valid edit of their own allocation
    // (verified live): the POST redirects to My Requests, stores the
    // change and keeps a history record of the previous version.
    const appended = ' [nonadmin edit 01]';
    await page
      .getByRole('link', { name: '2. Usage Information', exact: true })
      .click();
    await expect(page.locator('#panelTwo')).toHaveClass(/\bin\b/);
    const useCase = page.locator('#id_use_case');
    await useCase.fill(`${await useCase.inputValue()}${appended}`);
    await clickAndWaitForURL(
      page,
      page.locator('input[type=submit].submit-form-button[value="Submit"]'),
      '/allocation/user_requests/',
      SAVE_TIMEOUT,
    );
    const saved = await userAllocations.get(own.id);
    expect(saved.status).toBe('E');
    expect(saved.use_case).toBe(`${own.use_case}${appended}`);
    const history = await userAllocations.history(own.id);
    expect(history.map((h) => h.status)).toEqual(['E']);
  });
});
