import { Page } from '@playwright/test';

import { test, expect } from '../../../support/fixtures';
import {
  AMEND_STATE_TEXT,
  EDIT_TITLE,
  LIST_URL,
  acceptDialogsOnce,
  amendUrl,
  createEditable,
  detailButtons,
  detailTables,
  editUrl,
  expandPanel,
  expectForbidden,
  expectGuarded400,
  findRow,
  gotoDetail,
  gotoList,
  open,
  readTable,
  submitButton,
  submitForm,
  viewUrl,
} from './helpers';

// Suite 03 as the non-admin e2e user: a member and TenantManager of one
// project, with no allocation admin role.  'Own' allocations have the user
// as contact; 'managed' ones belong to the user's project with someone
// else as contact.

// The dev dashboard is shared with other suites running at the same time;
// form posts and page loads (the My Requests list above all) can take
// minutes under that load.
test.describe.configure({ timeout: 600_000 });

test.beforeEach(({ userPage }) => acceptDialogsOnce(userPage));

const OTHER_CONTACT = 'pwtest-other@example.org';
// Someone else's allocation, in a project the user does not manage.
const OTHER = 135408;
const HISTORY = [146946, 138447, 137049];

// The e2e user's manuka record has an ORCID, so the allocation forms do
// not open the 'Action Required!' ORCID modal.  The modal is always in
// the DOM, so check that it stays hidden and the form takes clicks.
async function expectNoOrcidBlock(page: Page) {
  await expect(page.getByRole('heading', { name: 'ORCID Connected' })).toHaveCount(1);
  const panelLink = page.getByRole('link', { name: '2. Usage Information', exact: true });
  await panelLink.click();
  await expect(page.locator('#panelTwo')).toBeVisible();
  await expect(page.locator('#orcid_modal')).toBeHidden();
}

test.describe('My Requests as a non-admin user', () => {
  test('1.6 List scope: own and TenantManager allocations, top-level only', async ({
    userPage,
    user,
    userAllocations,
    allocations,
  }) => {
    const own = await userAllocations.create();
    const managed = await allocations.create({
      project_id: user.project_id,
      contact_email: OTHER_CONTACT,
    });
    // An amendment of a managed allocation leaves history records.
    const managedX = await allocations.createAmendmentPending({
      project_id: user.project_id,
      contact_email: OTHER_CONTACT,
    });
    const history = await allocations.history(managedX.id);
    expect(history.length).toBeGreaterThan(0);

    await gotoList(userPage);
    await expect(userPage.locator('h1')).toHaveText(['My Requests']);
    const rows = await readTable(userPage);
    const ids = rows.map((r) => r.id);

    const ownRow = findRow(rows, own.id);
    expect(ownRow.cells[4]).toBe(user.username);
    expect(ownRow.nameHref).toBe(viewUrl(own.id));
    expect(ownRow.actions.map((a) => [a.text, a.href])).toEqual([
      ['Edit request', editUrl(own.id)],
    ]);

    const managedRow = findRow(rows, managed.id);
    expect(managedRow.cells[4]).toBe(OTHER_CONTACT);
    expect(managedRow.actions.map((a) => [a.text, a.href])).toEqual([
      ['Edit request', editUrl(managed.id)],
    ]);
    const xRow = findRow(rows, managedX.id);
    expect(xRow.cells[0]).toBe('X');
    expect(xRow.actions.map((a) => [a.text, a.href])).toEqual([
      ['Edit amend/extend request', amendUrl(managedX.id)],
    ]);

    // History records and unrelated allocations are not listed.
    for (const h of history) {
      expect(ids, `history record ${h.id}`).not.toContain(String(h.id));
    }
    expect(ids).not.toContain(String(OTHER));

    // Ordered by status.
    const states = rows.map((r) => r.cells[0]);
    expect(states).toEqual([...states].sort());

    // The 'Request a new allocation' action is offered to any user.
    await expect(userPage.locator('.table_actions a')).toHaveText(
      'Request a new allocation',
    );
  });

  test('1.9 (2.2) User detail of own and TenantManager allocations', async ({
    userPage,
    user,
    userAllocations,
    allocations,
  }) => {
    const own = await userAllocations.create();
    const managed = await allocations.create({
      project_id: user.project_id,
      contact_email: OTHER_CONTACT,
    });

    for (const [alloc, contact] of [
      [own, user.username],
      [managed, OTHER_CONTACT],
    ] as const) {
      await gotoDetail(userPage, alloc.id);
      await expect(userPage.locator('.breadcrumb li')).toHaveText([
        'Allocations',
        'My Requests',
        'View Allocation Request',
      ]);
      const tables = await detailTables(userPage);
      expect(tables[0][0]).toBe(`Contact email ${contact}`);
      expect(tables[1][0]).toBe('State Submitted');
      expect(await detailButtons(userPage)).toEqual([
        {
          text: 'Edit request',
          href: editUrl(alloc.id),
          id: 'allocation_edit_view',
          className: 'btn btn-default',
        },
      ]);
      // No admin controls.
      for (const name of ['Review & Approve', 'Decline with Reason', 'View History']) {
        await expect(userPage.getByRole('link', { name })).toHaveCount(0);
      }
    }
  });

  test('1.11 (3.1) Edit forms of own and TenantManager allocations open', async ({
    userPage,
    user,
    userAllocations,
    allocations,
  }) => {
    const own = await userAllocations.create();
    const managed = await allocations.create({
      project_id: user.project_id,
      contact_email: OTHER_CONTACT,
    });
    for (const alloc of [own, managed]) {
      const response = await open(userPage, editUrl(alloc.id));
      expect(response.status(), `edit ${alloc.id}`).toBe(200);
      await expect(userPage).toHaveTitle(EDIT_TITLE);
      await expect(userPage.locator('form#new-allocation')).toHaveAttribute(
        'action',
        editUrl(alloc.id),
      );
      // The contact field shows the allocation's contact, read-only.
      await expect(userPage.locator('#id_contact_email')).toHaveValue(
        alloc.contact_email as string,
      );
      await expectNoOrcidBlock(userPage);
      // The amend view refuses an E record (1.21, NECTAR-17320); access
      // is checked first, so the 400 also confirms the user is allowed.
      await expectGuarded400(userPage, amendUrl(alloc.id), AMEND_STATE_TEXT);
    }
  });

  test('1.15 (3.5) Non-admin contact edits own allocation', async ({
    userPage,
    user,
    userAllocations,
  }) => {
    const own = await createEditable(userAllocations, {}, user.id);
    const response = await open(userPage, editUrl(own.id));
    expect(response.status()).toBe(200);
    await expandPanel(userPage, '2. Usage Information', 'panelTwo');
    await userPage.locator('#id_use_case').fill('PW 03 non-admin edit');
    const post = await submitForm(userPage, submitButton(userPage));
    expect(post.status()).toBe(302);

    await expect(userPage).toHaveURL(LIST_URL);
    const r = findRow(await readTable(userPage), own.id);
    expect(r.cells[0]).toBe('E');
    expect(r.cells[4]).toBe(user.username);

    const after = await userAllocations.get(own.id);
    expect(after.use_case).toBe('PW 03 non-admin edit');
    expect(after.contact_email).toBe(user.username);
    expect((await userAllocations.history(own.id)).length).toBe(1);
  });

  test('1.15 (3.5) TenantManager edit makes the editor the contact', async ({
    userPage,
    user,
    allocations,
  }) => {
    // The user edit views record the editor in contact_email, so a
    // TenantManager who edits someone else's request becomes its contact.
    const managed = await createEditable(allocations, {
      overrides: { project_id: user.project_id, contact_email: OTHER_CONTACT },
    });
    const response = await open(userPage, editUrl(managed.id));
    expect(response.status()).toBe(200);
    await expandPanel(userPage, '2. Usage Information', 'panelTwo');
    await userPage.locator('#id_use_case').fill('PW 03 TenantManager edit');
    const post = await submitForm(userPage, submitButton(userPage));
    expect(post.status()).toBe(302);
    await expect(userPage).toHaveURL(LIST_URL);

    const after = await allocations.get(managed.id);
    expect(after.use_case).toBe('PW 03 TenantManager edit');
    expect(after.contact_email).toBe(user.username);
    const r = findRow(await readTable(userPage), managed.id);
    expect(r.cells[4]).toBe(user.username);
  });

  test('1.20 (5.1) Non-admin is denied history records and other allocations', async ({
    userPage,
  }) => {
    for (const id of [...HISTORY, OTHER]) {
      await expectForbidden(userPage, viewUrl(id));
      await expectForbidden(userPage, editUrl(id));
      await expectForbidden(userPage, amendUrl(id));
    }
  });
});
